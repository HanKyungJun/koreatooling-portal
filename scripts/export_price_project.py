#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""사내 Claude 프로젝트(재연마 정가 문의)용 지식 파일 만들기    2026-10-28 Cowork 신설

정가 엔진(scripts/price_lookup.py)과 **같은 판정**을 평평한 표 3개로 내보낸다.
Claude 프로젝트는 블록 · 셀 위치로 된 정가표 원본을 잘못 읽기 쉬워서, 한 줄에 답이 하나인 표로 바꾼다.

  1_정가표_구간표.csv     정가표 블록 형상(평 · 볼 · 코너 · 라핑 · 리머 · 2날 드릴) — 재질 · 형상 · 가공부 · 코팅 · 날수 · 직경 구간 → 정가
  2_등록품목_정가.csv     정가표 블록이 없는 형상(챔퍼 · 테이퍼 · 스탭드릴 · 고경도 드릴 등) — ERP 등록 품목명 → 정가
  3_확인필요_품목.csv     정가표 계산값 ≠ 등록 정가, 사업장끼리 정가가 다른 품목 — 금액을 말하지 않고 담당자 확인
  0_자료_안내.md          만든 시각 · 정가표 판 · 건수 · 정가표에서 못 찾은 블록

**정가만** 담는다 — 할인율 · 거래처 단가 · 견적 금액은 넣지 않는다(대외비, CLAUDE.md §4). 프로젝트는 공유받은 직원 모두가 파일을 열 수 있다.

사용(정가표 · ERP 내려받기가 바뀌면 다시 실행 → 프로젝트 지식 파일 3개를 통째로 교체):
  python scripts\export_price_project.py outputs\claude_project_price_YYYYMMDD
"""
import csv, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import price_lookup as pl
import price_audit as pa

BLOCK_SHAPES = ('평', '볼', '코너', '라핑평', '라핑볼', '라핑코너', '리머')
PARTS = ('밑날', '밑옆날', '골수리', '옆날')
COATS = ('비코팅', '일반코팅', '고경도코팅')
STEP, DMAX = 0.05, 60.0


def runs_for(fn):
    runs, last = [], None
    for i in range(1, int(round(DMAX / STEP)) + 1):
        d = round(i * STEP, 3)
        try:
            v = fn(d)
        except Exception:
            v = None
        if runs and v == last:
            runs[-1][1] = d
        else:
            runs.append([d, d, v]); last = v
    return [r for r in runs if r[2] is not None]


def band(lo, hi):
    # 마지막 구간이 DMAX(60 mm)까지 이어지면 정가표 「N 이상」 칸 — 상한 없음(빈칸)으로 쓴다(엔진은 Ø200 도 같은 값)
    if hi >= DMAX - 1e-9:
        hi = ''
    a = round(lo - STEP, 2)
    lo_t = '' if a <= 0 else f'Ø{a:g} 초과'
    hi_t = '' if hi == '' else f'Ø{hi:g} 이하'
    return a if a > 0 else 0, hi, ' ~ '.join(x for x in (lo_t, hi_t) if x)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), 'outputs', 'claude_project_price')
    os.makedirs(out, exist_ok=True)
    lk = pl.Lookup()

    # 1) 구간표
    rows1 = []
    for mat in ('초경', 'HSS'):
        for shape in BLOCK_SHAPES:
            for part in PARTS:
                for coat in COATS:
                    for blade in (2, 4):
                        for lo, hi, v in runs_for(lambda d: lk.blocks.expect(mat=mat, shape=shape, part=part, coat=coat, blade=blade, dia=d)):
                            a, b, txt = band(lo, hi)
                            rows1.append([mat, shape, part, pl.COAT_LABEL[coat], '2날' if blade == 2 else '1날·3날 이상', a, b, txt, int(v)])  # price_audit.expect: 2날만 2날 행, 그 밖(1 · 3 · 4 · 6날)은 4날 행
        for coat in ('비코팅', '일반코팅', '고경도코팅'):
            for lo, hi, v in runs_for(lambda d: lk.drill_price(d, coat, mat)):
                a, b, txt = band(lo, hi)
                rows1.append([mat, '드릴', '밑날', pl.COAT_LABEL[coat], '2날', a, b, txt, int(v)])
    # 볼 · 코너(라핑볼 · 라핑코너)는 같은 블록을 쓴다 — 줄이 완전히 같으면 「볼/코너」 한 줄로 합친다(파일 크기 ↓)
    def sig(r):
        return (r[0], r[2], r[3], r[4], r[5], r[6], r[8])
    merged, seen = [], {}
    pairs = {'볼': '코너', '라핑볼': '라핑코너'}
    by = {}
    for r in rows1:
        by.setdefault((r[0], r[1], r[2], r[3], r[4]), []).append(r)
    for key, rs in by.items():
        mat, shape, part, coat, bl = key
        if shape in pairs.values():
            continue
        if shape in pairs:
            other = by.get((mat, pairs[shape], part, coat, bl), [])
            if [sig(x) for x in rs] == [sig(x) for x in other]:
                merged += [[x[0], shape + '/' + pairs[shape]] + x[2:] for x in rs]
                continue
            merged += rs + other
            continue
        merged += rs
    rows1 = [r[:7] + [r[8]] for r in merged]
    h1 = ['재질', '형상', '가공부', '코팅', '날수', '직경_초과_mm', '직경_이하_mm', '정가_원']

    # 2) 등록 품목 / 3) 확인 필요 — price_one 판정을 그대로 따른다
    rows2, rows3 = [], []
    def readable(k):   # 비교 키(소문자 · mm 없음) → 표준 품목명 모양
        p = k.split('/')
        if len(p) < 6:
            return k
        p[2] = (p[2] + 'mm') if re.match(r'^[\d.]+$', p[2]) else p[2]
        p[3] = 'HSS' if p[3] == 'hss' else p[3]
        p[5] = {'일반코팅': '일반 코팅', '고경도코팅': '고경도 코팅'}.get(p[5], p[5])
        return '/'.join(p)
    for k in sorted(lk.conflict):
        ok6 = len([x for x in k.split('/') if x]) == 6 and k.count('/') == 5
        rows3.append([readable(k), '', '사업장 파일끼리 등록 정가가 다름' + ('' if ok6 else ' · 품목명 표기 오류(칸 누락 등) — 이름이 6칸 모두 같은 품목에만 해당')])
    for k, (pr, nm, code) in sorted(lk.master.items(), key=lambda x: x[1][1]):
        p = k.split('/')
        res = None
        if len(p) >= 6:
            try:
                b = int(re.match(r'\d+', p[0]).group()); d = float(p[2])
                mat = 'HSS' if p[3] == 'hss' else p[3]
                coat = {'비코팅': '비코팅', '일반코팅': '일반코팅', '고경도코팅': '고경도코팅'}.get(p[5])
                if coat:
                    res = lk.price_one(b, p[1], d, mat, p[4], coat)
            except Exception:
                res = None
        if res is None:
            if '/' in str(nm):                   # 품목명 자리에 숫자만 있는 오류 줄(예: 「0.57」)은 뺀다 — ERP 정가 점검 E 분류. 5칸 품목명(날붙이 · 절단 등)은 정상
                if str(nm).split('/')[1:2] in (['드릴'], ['드릴.2.5MM']):   # 2026-10-30: 표기가 깨진 드릴 품목(「//」 · 가공부 없음 등)은 26.10 개정에서 빠져 옛 정가 — 확인 필요로
                    rows3.append([nm, code, '드릴 품목명 표기 이상(「//」 · 가공부 없음 등) — 26.10 개정 반영 여부 담당자 확인'])
                else:
                    rows2.append([nm, code, int(pr)])
        elif res['status'] == '확인 필요':
            rows3.append([nm, code, res['note']])
        elif res['status'] == 'OK' and res['source'].startswith('등록 품목'):
            if len(p) >= 6 and p[1] == '드릴':   # 2026-10-30: 정가표(26.10) 드릴 표 밖(초경 20 mm 초과 · 3 · 4날 · 밑날 외)은 ERP 에 옛 정가가 남아 있음 — 한경준님 10-29 보류
                rows3.append([nm, code, '정가표 드릴 구간 밖(가격표 없음 · 보류) — 담당자 확인'])
            else:
                rows2.append([nm, code, int(pr)])
        # 정가표 계산과 같은 품목(OK · 정가표)은 구간표로 답하므로 넣지 않는다
    h2 = ['품목명', '품목코드', '정가_원']
    h3 = ['품목명', '품목코드', '사유']

    def w(name, head, rows):
        with open(os.path.join(out, name), 'w', encoding='utf-8-sig', newline='') as f:
            cw = csv.writer(f); cw.writerow(head); cw.writerows(rows)
    w('1_정가표_구간표.csv', h1, rows1)
    w('2_등록품목_정가.csv', h2, rows2)
    # 2026-10-30: 확인 필요 사유에 금액(ERP 옛 정가 등)을 남기지 않는다 — 프로젝트가 「사유만 답」할 때 옛 금액이 새지 않게(한경준님 테스트 검수)
    for r in rows3:
        r[2] = re.sub(r'ERP 등록 정가 [\d,]+원(은 옛 값일 수 있음)?,?\s*', '', str(r[2]))
    left = [r for r in rows3 if re.search(r'\d[\d,]*\s*원', str(r[2]))]
    if left:
        sys.exit(f'확인 필요 사유에 금액이 남음 {len(left)}줄 — 예: {left[0]}')
    w('3_확인필요_품목.csv', h3, rows3)
    made = pa.now_kst().strftime('%Y-%m-%d %H:%M KST')
    mtime = pa.datetime.datetime.fromtimestamp(os.path.getmtime(lk.pl_path), pa.KST).strftime('%Y-%m-%d %H:%M KST')
    miss = [re.sub(r'\.\*', ' … ', m).strip('^$') for m in lk.blocks.missing]
    with open(os.path.join(out, '0_자료_안내.md'), 'w', encoding='utf-8') as f:
        f.write(f"""# 재연마 정가 자료 안내

- 만든 시각: {made} (scripts/export_price_project.py)
- 정가표: {os.path.basename(lk.pl_path)} 「{lk.pl.name}」 (파일 수정 {mtime})
- 등록 정가: {lk.master_src} ({', '.join(lk.master_files)})
- 1_정가표_구간표.csv: {len(rows1):,}줄 · 2_등록품목_정가.csv: {len(rows2):,}줄 · 3_확인필요_품목.csv: {len(rows3):,}줄
- 정가만 담았습니다. 할인율 · 거래처 단가 · 견적 금액은 없습니다.
""" + (f"- ⚠️ 정가표에서 못 찾은 블록 {len(miss)}개 — 이 형상은 표에 없으므로 담당자 확인: " + ' · '.join(miss) + "\n" if miss else ''))
    print(f'{out}: 구간표 {len(rows1)} · 등록 품목 {len(rows2)} · 확인 필요 {len(rows3)} · 못 찾은 블록 {len(miss)}')


if __name__ == '__main__':
    main()
