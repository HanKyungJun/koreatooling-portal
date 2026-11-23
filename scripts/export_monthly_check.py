#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
「월초 마감 점검」용 측정값 → 구글 드라이브 (Claude 예약 작업 「월초 마감 점검 v3」가 읽음)
실행: python scripts/export_monthly_check.py [YYYY-MM] [--force] [--no-upload]
      매월 1 ~ 5일(KST)에 16:00 배치가 부른다. 그달 첫 실행 한 번만 잰다(상태 outputs/.monthly_check_state.json).
      YYYY-MM = 점검할 달(기본: 전월). --force = 날짜 · 상태와 무관하게 다시 잼(시험용).
출력: private_local\monthly_check\<전월>.txt → 드라이브 「cnc-wiki-auto/monthly_check.txt」

2026-11-23 신규 — 새 PC 이전(예약 실행이 PC 폴더를 못 읽음, 11-23 예약 진단 2회: 연결 폴더 0개)
  옛 「월초 마감 점검 v2」 예약 프롬프트가 device_bash 로 하던 ① ~ ⑥ 측정을 16:00 배치가 대신 하고 결과만 올린다.
  🔴 읽기 · 드라이런만 — archive_handoff.py · ship_month_close.py 는 --apply 없이, git 은 읽기만.
  🔴 거래처 실명은 올리지 않는다 — ship_month_close 출력의 상위 5 줄 · 새 납품처 이름 목록은 빼고 개수만.
  금액 · 단가 없음(ERP 스냅샷은 수량 열만 읽음).
"""
import sys, io, os, re, csv, json, subprocess, statistics
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE    = Path(__file__).resolve().parent.parent
WIKI    = BASE / 'wiki'
HANDOFF = WIKI / '_handoff'
DAILY   = WIKI / 'reports' / 'daily'
SNAP    = BASE / 'erp' / 'snapshot'
OUTDIR  = BASE / 'private_local' / 'monthly_check'
STATE   = BASE / 'outputs' / '.monthly_check_state.json'
LOG     = DAILY / 'run.log'
KST     = timezone(timedelta(hours=9))
ENV     = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
ERP_FROM = '2026-10-23'   # 일일보고 ERP 기준 시작일(decisions 2026-10-23 (7)) — 그 전 날은 기준이 달라 대조에서 뺌


def log(msg):
    print(msg)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass


def run(args, timeout=300):
    try:
        p = subprocess.run(args, cwd=BASE, capture_output=True, timeout=timeout, env=ENV)
        out = (p.stdout or b'').decode('utf-8', 'replace') + (p.stderr or b'').decode('utf-8', 'replace')
        return p.returncode, out
    except Exception as ex:
        return -1, f'{type(ex).__name__}: {ex}'


def tail(text, n=15):
    lines = [l for l in text.splitlines() if l.strip()]
    return '\n'.join(lines[-n:]) if lines else '(출력 없음)'


def prev_month(d: date):
    first = d.replace(day=1)
    return (first - timedelta(days=1)).strftime('%Y-%m')


def month_days(ym: str):
    y, m = int(ym[:4]), int(ym[5:7])
    d = date(y, m, 1)
    while d.month == m:
        yield d
        d += timedelta(days=1)


def holidays():
    p = HANDOFF / 'holidays.md'
    if not p.exists():
        return set()
    return set(re.findall(r'^\|\s*(\d{4}-\d{2}-\d{2})', p.read_text(encoding='utf-8-sig'), re.M))


def latest_snapshot(ym: str):
    c = sorted(SNAP.glob(f'pw_nc_{ym}-01_*.csv'))
    return c[-1] if c else None


def snapshot_by_day(path):
    out = {}
    with open(path, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            d = str(r.get('work_dt', ''))[:10]
            out[d] = out.get(d, 0) + int(float(r.get('ok') or 0)) + int(float(r.get('bad') or 0))
    return out


def report_value(d: str):
    x = DAILY / f'{d}_일일보고.xlsx'
    if not x.exists():
        return None
    try:
        import openpyxl
        ws = openpyxl.load_workbook(x, data_only=True, read_only=True)['일일 요약']
        for row in ws.iter_rows(values_only=True):
            a = row[0] if row else None
            if isinstance(a, str) and a.startswith('합계') and '수량' in a:
                return int(row[1] or 0)
    except Exception as ex:
        return f'읽기 실패 {type(ex).__name__}'
    return '합계 행 없음'


def sec1(ym, hol):
    out = [f'## ① {ym} 일일보고 16:00 속보값 ↔ ERP 스냅샷 대조']
    snap = latest_snapshot(ym)
    if not snap:
        return out + [f'- 기준 스냅샷 없음(erp/snapshot/pw_nc_{ym}-01_*.csv) — 확인 필요'], None
    by = snapshot_by_day(snap)
    out.append(f'- 기준 스냅샷: {snap.name} (가장 늦은 파일 — 말일 16:00 뒤 입력분은 대조 안 됨)')
    out.append('- 표: 날짜 | 보고서값 | 스냅샷값 | 차이(스냅샷−보고서) | 차이%')
    n, plus, minus_days, missing, excel_days = 0, 0, [], [], 0
    biggest = None
    for d in month_days(ym):
        ds = d.isoformat()
        if ds < ERP_FROM:
            excel_days += 1
            continue
        sv = by.get(ds, 0)
        rv = report_value(ds)
        workday = d.weekday() < 5 and ds not in hol
        if rv is None:
            if workday or sv:
                missing.append(f'{ds}(스냅샷 {sv})')
            continue
        if not isinstance(rv, int):
            out.append(f'| {ds} | {rv} | {sv} | - | - |')
            continue
        diff = sv - rv
        n += 1
        pct = f'{diff / rv * 100:+.1f}%' if rv else '-'
        out.append(f'| {ds} | {rv} | {sv} | {diff:+d} | {pct} |')
        if diff > 0:
            plus += diff
            if biggest is None or diff > biggest[1]:
                biggest = (ds, diff)
        if diff < 0:
            minus_days.append(f'{ds}({diff:+d})')
    out.append(f'- 요약: 대조 {n}일 · 늦은 입력 합계 +{plus}' + (f' (최대 {biggest[0]} +{biggest[1]})' if biggest else '')
               + f' · 🔴 감소 {len(minus_days)}일 {" ".join(minus_days)} · 보고서 없는 날 {len(missing)} {" ".join(missing)}')
    if excel_days:
        out.append(f'- {ERP_FROM} 이전 {excel_days}일은 엑셀 기준이라 대조에서 뺌')
    return out, by


def stats(by, ym, hol):
    vals = [by.get(d.isoformat(), 0) for d in month_days(ym) if d.weekday() < 5 and d.isoformat() not in hol]
    if not vals:
        return None
    return len(vals), statistics.median(vals), sum(vals) / len(vals), sum(vals)


def sec3(ym, by, hol):
    out = [f'## ③ {ym} 영업일 수량(ok+bad, 평일 − holidays.md 날짜, 실적 0 인 날 포함)']
    if by is None:
        return out + ['- 스냅샷 없음 — 확인 필요']
    s = stats(by, ym, hol)
    out.append(f'- {ym}: 영업일 {s[0]} · 중앙값 {s[1]:.0f} · 평균 {s[2]:.1f} · 합계 {s[3]}')
    pym = prev_month(date(int(ym[:4]), int(ym[5:7]), 1))
    ps = latest_snapshot(pym)
    if ps:
        p = stats(snapshot_by_day(ps), pym, hol)
        out.append(f'- {pym}: 영업일 {p[0]} · 중앙값 {p[1]:.0f} · 평균 {p[2]:.1f} · 합계 {p[3]} (스냅샷 {ps.name}'
                   + (' — ERP 기준 시작 전 날 포함, 비교 주의' if pym <= ERP_FROM[:7] else '') + ')')
        out.append(f'- 합계 차이 {s[3] - p[3]:+d}')
    else:
        out.append(f'- {pym}: 스냅샷 없음 — 비교 불가')
    return out


def sec2(today):
    cur = today.strftime('%Y-%m')
    out = ['## ② ERP 스냅샷 · 일일보고 생성 상태']
    s = latest_snapshot(cur)
    out.append(f'- 이번 달 스냅샷: {s.name if s else "아직 없음"}')
    try:
        rl = [l for l in LOG.read_bytes().decode('utf-8', 'replace').splitlines() if '[step5-end]' in l]
        out.append(f'- run.log 마지막 step5: {rl[-1].strip() if rl else "없음"}')
    except Exception as ex:
        out.append(f'- run.log 읽기 실패: {ex}')
    try:
        gl = [l for l in (DAILY / 'generate.log').read_bytes().decode('utf-8', 'replace').splitlines() if '[git] push' in l]
        out.append(f'- generate.log 마지막 push: {gl[-1].strip() if gl else "없음"}')
    except Exception as ex:
        out.append(f'- generate.log 읽기 실패: {ex}')
    return out


LINK_RE = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]')
SRC_RE  = re.compile(r'\[((?:STD|ACA|VEN|CAT|IND|SYS)-[A-Za-z0-9][A-Za-z0-9\-_.]*)\]')
SKIP    = ('_handoff/', '_backup/', '_private/', 'reports/09_업무일정/주간브리핑/')
SKIP_F  = {'index.md', 'log.md', 'overview.md'}


def sec5():
    out = ['## ⑤ 위키 검수(간이 — 제외: _handoff · _backup · _private · 주간브리핑 · index · log · overview · 아카이브)']
    pages = {}
    for p in WIKI.rglob('*.md'):
        rel = p.relative_to(WIKI).as_posix()
        if rel.startswith(SKIP) or rel in SKIP_F or 'archive' in rel.lower():
            continue
        pages[rel] = p.read_text(encoding='utf-8-sig', errors='replace')
    all_md = {p.relative_to(WIKI).as_posix()[:-3] for p in WIKI.rglob('*.md')}
    files_all = {p.name for p in WIKI.rglob('*') if p.is_file() and p.suffix != '.md'}
    stems = {}
    for r in all_md:
        stems.setdefault(r.split('/')[-1], []).append(r)
    src_text = (HANDOFF / 'sources.md').read_text(encoding='utf-8-sig', errors='replace') if (HANDOFF / 'sources.md').exists() else ''
    no_fm, red, unreg, inbound = [], [], set(), {r[:-3]: 0 for r in pages}
    for rel, t in pages.items():
        if not t.startswith('---'):
            no_fm.append(rel)
        for raw in LINK_RE.findall(t):
            tgt = raw.strip().removesuffix('.md')
            if re.search(r'\.[A-Za-z0-9]{2,5}$', tgt):   # 첨부 파일 링크(xlsx · pdf · png 등) — 파일이 있으면 통과
                name = tgt.split('/')[-1]
                if not ((WIKI / tgt).exists() or (p_dir := (WIKI / rel).parent / tgt).exists() or name in files_all):
                    red.append(f'{rel} → [[{tgt}]]')
                continue
            hit = tgt in all_md or tgt.split('/')[-1] in stems
            if not hit:
                red.append(f'{rel} → [[{tgt}]]')
                continue
            keys = [tgt] if tgt in all_md else stems[tgt.split('/')[-1]]
            for k in keys:
                if k in inbound and k != rel[:-3]:
                    inbound[k] += 1
        for sid in SRC_RE.findall(t):
            if f'[{sid}]' not in src_text and sid not in src_text:
                unreg.add(sid)
    # index · log 등 제외 파일에서 오는 링크도 인바운드로 친다
    for p in [WIKI / f for f in SKIP_F]:
        if p.exists():
            for raw in LINK_RE.findall(p.read_text(encoding='utf-8-sig', errors='replace')):
                tgt = raw.strip().removesuffix('.md')
                for k in ([tgt] if tgt in inbound else stems.get(tgt.split('/')[-1], [])):
                    if k in inbound:
                        inbound[k] += 1
    orphan = sorted(k for k, v in inbound.items() if v == 0)
    out.append(f'- 대상 {len(pages)}쪽 · 프론트매터 없음 {len(no_fm)} · 출처 ID 미등재 {len(unreg)} · 빨간 링크 {len(red)} · 고아 {len(orphan)}')
    for name, lst in (('프론트매터 없음', no_fm), ('출처 ID 미등재', sorted(unreg)), ('빨간 링크', red), ('고아', orphan)):
        if lst:
            out.append(f'- {name} (최대 15): ' + ' · '.join(lst[:15]))
    return out


def sec6(ym, today):
    out = [f'## ⑥ {ym} 출하현황 반영 점검 (ship_month_close 드라이런 — 실명 줄은 뺌)']
    if ym.endswith('-01'):
        return out + ['- 1월분 — 새 연도 파일 준비 필요, 대화 세션에서']
    csvp, meta = SNAP / f'shipment_{ym}.csv', SNAP / f'shipment_{ym}.meta.json'
    if not csvp.exists():
        return out + [f'- shipment_{ym}.csv 없음 → PowerShell `python erp\\save_shipment.py {ym}` 필요']
    saved = ''
    try:
        saved = json.loads(meta.read_text(encoding='utf-8-sig')).get('saved_kst', '')
    except Exception:
        pass
    out.append(f'- shipment_{ym}.csv 저장 시각(meta saved_kst): {saved or "없음"}'
               + (' ⚠️ 당월 1일 전 저장 — 다시 저장 필요' if saved and saved[:10] < today.replace(day=1).isoformat() else ''))
    rc, o = run([sys.executable, 'scripts/ship_month_close.py', ym], timeout=180)
    for l in o.splitlines():
        if '상위 5' in l or not l.strip():
            continue
        l = re.sub(r'(새 납품처 \d+곳) \[.*?\]', r'\1', l)
        if re.search(r'\[[^\]]*\'[^\]]*\]', l):   # 이름 목록이 남아 있으면 줄째 뺀다
            continue
        out.append(f'  {l}')
    state = ('이미 반영됨(요약에 이 달 값 있음)' if rc == 1 and '이미 이 달 값' in o else
             '반영 가능 — 대화 세션에서 --apply' if rc == 0 else f'점검 오류 rc={rc} — 대화 세션에서 원문 확인')
    out.append(f'- 판정: rc={rc} · {state}')
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    force = '--force' in sys.argv
    today = datetime.now(KST).date()
    if not force and not (1 <= today.day <= 5):
        return
    ym = args[0] if args else prev_month(today)
    if not force and STATE.exists():
        try:
            if json.loads(STATE.read_text(encoding='utf-8')).get('done_for') == ym:
                return
        except Exception:
            pass
    now = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
    hol = holidays()
    out = [f'# 월초 마감 점검 측정값 — {ym}', f'date: {today.isoformat()}', f'month_for: {ym}', f'generated: {now} KST', '']
    s1, by = sec1(ym, hol)
    out += s1 + [''] + sec2(today) + [''] + sec3(ym, by, hol) + ['']
    out += ['## ④ 핸드오프 크기 · archive_handoff.py 드라이런']
    for n in ('tasks.md', 'decisions.md', 'worklog.md'):
        p = HANDOFF / n
        out.append(f'- {n}: {p.stat().st_size / 1024:.1f} KB' if p.exists() else f'- {n}: 없음')
    rc, o = run([sys.executable, 'scripts/archive_handoff.py'])
    out += [f'- rc={rc}, 끝 12줄:', tail(o, 12), '']
    try:
        out += sec5()
    except Exception as ex:
        out.append(f'## ⑤ 위키 검수 실패: {type(ex).__name__}: {ex}')
    out.append('')
    out += sec6(ym, today) + ['']
    rc, o = run([sys.executable, 'scripts/anonymize_public.py', '--check'])
    out += ['## 실명 검사 (anonymize_public.py --check)', f'- 종료 코드 {rc} (0 = 실명 없음)', '', '## END']

    OUTDIR.mkdir(parents=True, exist_ok=True)
    path = OUTDIR / f'{ym}.txt'
    path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    log(f'[monthly-check] OK - {ym} -> {path.name}')
    if '--no-upload' in sys.argv:
        return
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from drive_upload import upload_text
        action, _ = upload_text(path, 'monthly_check.txt')
        log(f'[monthly-check] DRIVE {action} - cnc-wiki-auto/monthly_check.txt')
        if not force:
            STATE.parent.mkdir(parents=True, exist_ok=True)
            STATE.write_text(json.dumps({'done_for': ym, 'at': now}, ensure_ascii=False), encoding='utf-8')
    except Exception as ex:
        log(f'[monthly-check] ERROR - drive upload failed: {type(ex).__name__}: {ex}')


if __name__ == '__main__':
    main()
