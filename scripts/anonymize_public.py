# -*- coding: utf-8 -*-
"""공개 저장소 거래처 실명 익명화 (2026-11-03 신설 — decisions 2026-11-03)

공개 GitHub 저장소(= github.io 공개 위키)에 올라가는 파일에서 거래처 실명을
「거래처 A · B · … · AA」 코드로 바꾼다. 실명 ↔ 코드 대조표와 실명 원본은
wiki/_private/ (gitignore) 에만 둔다.

  python scripts/anonymize_public.py --check            추적 파일 + 새 파일(.gitignore 제외) 전체에서 실명 찾기 (있으면 종료 코드 1)
  python scripts/anonymize_public.py --apply 파일...      실명 원본을 _private 에 복사한 뒤 그 파일을 익명화
  python scripts/anonymize_public.py --map               대조표 갱신만 (ERP 저장본의 새 거래처에 다음 코드 부여)

다른 스크립트에서:  from anonymize_public import publish ;  publish('wiki/comparisons/x.xlsx')

- 코드 순서 = 출하현황 2022 ~ 2026 출고 합계 순(많은 곳이 A). 한 번 정한 코드는 바꾸지 않는다(새 거래처는 뒤에 붙음).
- 자사 「코리아툴링」은 익명화하지 않는다.
- xlsx · docx · pptx 는 압축 안 XML 글자만 바꾼다(서식 · 수식 · 그림 보존).
"""
import csv, io, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PRIV = BASE / 'wiki' / '_private'
MAP_CSV = PRIV / '거래처_익명코드표.csv'
ERP_HEAD = BASE / 'erp' / 'snapshot' / 'jae_head_latest.csv'
OWN = ('코리아툴링',)
TEXT_EXT = {'md', 'py', 'csv', 'html', 'htm', 'js', 'json', 'txt', 'gs', 'css', 'yml', 'yaml', 'xml', 'tsv'}
ZIP_EXT = {'xlsx', 'docx', 'pptx', 'xlsm'}
SKIP = ('wiki/_private/', 'erp/snapshot/', 'raw/', 'outputs/', '_to_delete/')


def core(name):
    c = re.sub(r'\(주\)|㈜|주식회사|\(유\)|유한회사', '', name)
    c = re.sub(r'\(.*?\)|-.*$', '', c).strip()
    return c


def code_of(i):
    a = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return '거래처 ' + (a[i] if i < 26 else a[i // 26 - 1] + a[i % 26])


def _shipping_totals():
    """출하현황 xlsx(실명판: _private 우선) 의 납품처별 합계."""
    import openpyxl
    tot = {}
    for y in range(2022, 2031):
        rel = Path('wiki/comparisons') / f'출하현황_납품처별_월별분석_{y}.xlsx'
        p = PRIV / 'comparisons' / rel.name
        if not p.exists():
            p = BASE / rel
        if not p.exists():
            continue
        ws = openpyxl.load_workbook(p, read_only=True, data_only=True)['요약']
        for row in ws.iter_rows(min_row=3, values_only=True):
            if not row or not row[1]:
                break
            n = str(row[1]).strip()
            if n.startswith('거래처 '):
                continue
            tot[n] = tot.get(n, 0) + sum(v for v in row[2:14] if isinstance(v, (int, float)))
    return tot


def load_map(update=True):
    """대조표 읽기. update=True 면 ERP 저장본 · 출하현황에서 새 이름을 찾아 뒤에 붙인다."""
    rows = []
    if MAP_CSV.exists():
        with open(MAP_CSV, encoding='utf-8-sig', newline='') as fh:
            rows = list(csv.DictReader(fh))
    by_core = {r['core']: r for r in rows}
    if update:
        names = {}
        try:
            for n, t in _shipping_totals().items():
                names[n] = names.get(n, 0) + t
        except Exception as e:
            print(f'  (출하현황 읽기 생략: {e})')
        if ERP_HEAD.exists():
            with open(ERP_HEAD, encoding='utf-8-sig', newline='') as fh:
                for r in csv.DictReader(fh):
                    for k in ('cust_nm', 'cust_nm2'):
                        if r.get(k):
                            names.setdefault(r[k].strip(), 0)
        groups = {}
        for n, t in names.items():
            c = core(n)
            if len(c) < 3 or any(o in c for o in OWN):
                continue
            g = groups.setdefault(c, [set(), 0])
            g[0].add(n); g[1] += t
            for old in re.findall(r'\(구[,.]?\s*([^)]+)\)', n):   # 이름 뒤 괄호 속 옛 상호 「(구,○○상사)」 도 같은 코드
                if len(old.strip()) >= 3:
                    g[0].add(old.strip())
        new = [c for c in groups if c not in by_core]
        new.sort(key=lambda c: (-groups[c][1], c))
        for c in new:
            r = {'code': code_of(len(rows)), 'core': c, 'variants': '|'.join(sorted(groups[c][0])),
                 'ship_total': str(int(groups[c][1]))}
            rows.append(r); by_core[c] = r
        changed = False
        for c, g in groups.items():          # 기존 코드의 새 표기 추가
            r = by_core[c]
            old = set(filter(None, r['variants'].split('|')))
            v = old | g[0]
            if v != old:
                r['variants'] = '|'.join(sorted(v)); changed = True
        if new or changed or not MAP_CSV.exists():
            PRIV.mkdir(parents=True, exist_ok=True)
            with open(MAP_CSV, 'w', encoding='utf-8-sig', newline='') as fh:
                w = csv.DictWriter(fh, fieldnames=['code', 'core', 'variants', 'ship_total'])
                w.writeheader(); w.writerows(rows)
            if new:
                print(f'  대조표: 새 거래처 {len(new)}곳 추가 → {MAP_CSV.relative_to(BASE)}')
    return rows


_PAT = None


def _pattern():
    global _PAT
    if _PAT is None:
        pairs = {}
        for r in load_map():
            for s in [r['core']] + r['variants'].split('|'):
                if s:
                    pairs[s] = r['code']
        keys = sorted(pairs, key=len, reverse=True)
        _PAT = (re.compile('|'.join(re.escape(k) for k in keys)), pairs)
    return _PAT


def anon_text(s):
    pat, pairs = _pattern()
    s2 = pat.sub(lambda m: pairs[m.group(0)], s)
    s2 = re.sub(r'(?:\(주\)|㈜|주식회사)\s*(거래처 [A-Z]{1,2})(?![A-Z])', r'\1', s2)
    s2 = re.sub(r'(거래처 [A-Z]{1,2})(?![A-Z])\s*(?:\(주\)|주식회사)', r'\1', s2)
    return s2


def find_names(s):
    pat, pairs = _pattern()
    return pat.findall(s)


def _unref(t):
    """XML 숫자 문자 참조(&#50896; · &#xC6D0;)를 글자로 — 0x80 미만(& < > 등)은 그대로 둔다."""
    def r(m):
        v = int(m.group(1)[1:], 16) if m.group(1)[0] in 'xX' else int(m.group(1))
        return chr(v) if v >= 0x80 else m.group(0)
    return re.sub(r'&#([xX][0-9a-fA-F]+|[0-9]+);', r, t)


def _zip_texts(p):
    with zipfile.ZipFile(p) as z:
        for n in z.namelist():
            if n.endswith(('.xml', '.rels')):
                yield n, _unref(z.read(n).decode('utf-8', 'ignore'))


def file_names(p):
    p = Path(p); ext = p.suffix.lower().lstrip('.')
    if ext in TEXT_EXT:
        return find_names(p.read_bytes().decode('utf-8', 'ignore'))
    if ext in ZIP_EXT:
        out = []
        for _, t in _zip_texts(p):
            out += find_names(t)
        return out
    return []


def anonymize_file(p):
    """그 자리에서 익명화. 바뀐 개수 반환."""
    p = Path(p); ext = p.suffix.lower().lstrip('.')
    before = len(file_names(p))
    if not before:
        return 0
    if ext in TEXT_EXT:
        raw = p.read_bytes()
        bom = raw.startswith(b'\xef\xbb\xbf')
        t = raw.decode('utf-8-sig' if bom else 'utf-8')
        p.write_bytes((b'\xef\xbb\xbf' if bom else b'') + anon_text(t).encode('utf-8'))
    elif ext in ZIP_EXT:
        buf = io.BytesIO()
        with zipfile.ZipFile(p) as zin, zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = zin.read(info.filename)
                if info.filename.endswith(('.xml', '.rels')):
                    t = data.decode('utf-8')
                    if find_names(_unref(t)):
                        data = anon_text(_unref(t)).encode('utf-8')
                zout.writestr(info, data)
        p.write_bytes(buf.getvalue())
    return before


def private_copy(p):
    """실명 원본을 wiki/_private/ 아래 같은 하위 경로에 복사(wiki/comparisons/x → wiki/_private/comparisons/x)."""
    p = Path(p).resolve()
    rel = p.relative_to(BASE)
    dst = PRIV.joinpath(*rel.parts[1:]) if rel.parts[0] == 'wiki' else PRIV.joinpath('_root', *rel.parts)
    if dst.suffix == '.md':   # Obsidian 위키링크가 공개판과 헷갈리지 않게 이름을 바꿔 둔다
        dst = dst.with_name(dst.stem + '_실명원본.md')
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dst)
    return dst


def publish(path):
    """생성 스크립트용: 실명판은 _private 로 복사, 공개 경로 파일은 익명화."""
    p = BASE / path if not Path(path).is_absolute() else Path(path)
    if not file_names(p):
        return 0
    dst = private_copy(p)
    n = anonymize_file(p)
    print(f'  익명화: {p.relative_to(BASE)} ({n}곳) · 실명판 → {dst.relative_to(BASE)}')
    return n


def tracked_files():
    try:
        out = subprocess.run(['git', '-C', str(BASE), 'ls-files', '--cached', '--others', '--exclude-standard'], capture_output=True, timeout=60)  # 2026-11-05: 새 파일도 검사 (git add -A 대상)
        files = out.stdout.decode('utf-8').splitlines()
        if files:
            return files
    except Exception:
        pass
    return [str(q.relative_to(BASE)).replace('\\', '/') for q in (BASE / 'wiki').rglob('*') if q.is_file()]


def check():
    bad = {}
    for f in tracked_files():
        f = f.strip('"')
        if f.startswith(SKIP):
            continue
        p = BASE / f
        if not p.is_file():
            continue
        try:
            n = file_names(p)
        except Exception as e:
            print(f'  읽기 실패 {f}: {e}'); continue
        if n:
            bad[f] = n
    for f, n in sorted(bad.items(), key=lambda x: -len(x[1])):
        print(f'  {len(n):4d}곳  {f}   예: {", ".join(sorted(set(n))[:3])}')
    print(f'거래처 실명 남은 파일: {len(bad)}개')
    return bad


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--check':
        sys.exit(1 if check() else 0)
    elif a[0] == '--map':
        print(f'대조표 {len(load_map())}곳')
    elif a[0] == '--apply':
        for f in a[1:]:
            publish(f)
    else:
        print(__doc__)
