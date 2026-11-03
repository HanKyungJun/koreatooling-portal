#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
캘린더 아티팩트(Weekly Calendar Overview) — 배지 가공시간 표시를 「H:MM:SS」 → 「가공 Hh Mm」 로 (2026-10-27, Cowork)

배경: 「NC 36  3:26:39 (추정)」 의 3:26:39 가 시계 시각(마지막 제품 시각)처럼 읽힌다.
      실제 뜻은 그날 가공시간 합계(ERP 기준일은 표준공수 × 수량 추정, 엑셀 기준일은 작업일지 실측 합계).
바꾸는 것: fix_calendar_erp_20261027.py 가 넣은 prodDetail() 한 함수만
    ERP 기준일   「NC 36 · 가공 3h 27m (추정)」
    엑셀 기준일 「F27·G14 · 가공 4h 23m」
    분은 반올림(3:26:39 → 3h 27m). PROD 데이터(time 값)는 그대로 둔다.

실행 (경준님 PC, cnc-wiki 폴더에서):
    python scripts\fix_calendar_timefmt_20261027.py            ← 미리보기
    python scripts\fix_calendar_timefmt_20261027.py --apply    ← 백업 후 적용 · 다시 읽어 확인
백업: 아티팩트 폴더에 index.html.bak_20261027b (이미 있으면 덮어쓰지 않음)
선행: fix_calendar_erp_20261027.py --apply (09:24 KST 완료)
"""
import sys, io, shutil
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ARTIFACT = Path(r'C:\Users\TOOLKOREA\Documents\Claude\Artifacts\weekly-calendar-overview\index.html')
art_arg = [a for a in sys.argv[1:] if a.startswith('--artifact=')]
if art_arg:
    ARTIFACT = Path(art_arg[0].split('=', 1)[1])
APPLY = '--apply' in sys.argv[1:]

OLD = ("function prodDetail(p){ const t=(String(p.time||'').match(/\\d+:\\d{2}:\\d{2}/)||[''])[0];\n"
       "  return (p.fg==null && p.gx7==null) ? `NC ${prodTotal(p)}  ${t}${p.est?' (추정)':''}` : `F${p.fg}·G${p.gx7}  ${t}`; }\n")
NEW = ("// 2026-10-27(b): 시간은 그날 가공시간 합계 — 시계 시각으로 읽히지 않게 「가공 Hh Mm」(분 반올림)\n"
       "function prodHM(p){ const mn=Math.round(prodSec(p)/60); return mn>0 ? `가공 ${Math.floor(mn/60)}h ${mn%60}m` : ''; }\n"
       "function prodDetail(p){ const hm=prodHM(p);\n"
       "  return (p.fg==null && p.gx7==null) ? `NC ${prodTotal(p)}${hm?' · '+hm:''}${p.est?' (추정)':''}` : `F${p.fg}·G${p.gx7}${hm?' · '+hm:''}`; }\n")


def main():
    if not ARTIFACT.exists():
        print(f'❌ 아티팩트 파일 없음: {ARTIFACT}'); return 1
    html = ARTIFACT.read_text(encoding='utf-8')
    if 'function prodHM(p)' in html:
        print('✅ 이미 적용됨 (변경 없음)'); return 0
    if 'function prodTotal(p)' not in html:
        print('❌ fix_calendar_erp_20261027.py 가 먼저 적용돼야 함'); return 1
    n = html.count(OLD)
    if n != 1:
        print(f'❌ prodDetail 자리를 찾지 못함(일치 {n}곳) — 수동 확인 필요'); return 1
    print('바꿀 내용:\n  - 배지 아랫줄 시간 표시: 「3:26:39」 → 「가공 3h 27m」 (PROD 데이터는 그대로)')
    if not APPLY:
        print('(미리보기 — 적용하려면 --apply)'); return 0
    bak = ARTIFACT.with_name(ARTIFACT.name + '.bak_20261027b')
    if not bak.exists():
        shutil.copy2(ARTIFACT, bak); print(f'백업: {bak}')
    else:
        print(f'백업 이미 있음(덮어쓰지 않음): {bak}')
    ARTIFACT.write_text(html.replace(OLD, NEW, 1), encoding='utf-8', newline='\r\n')
    chk = ARTIFACT.read_text(encoding='utf-8')
    ok = 'function prodHM(p)' in chk and OLD not in chk
    print('✅ 적용 확인 완료 — 캘린더를 다시 열어 확인하세요' if ok else '❌ 다시 읽은 결과가 기대와 다름 — 백업으로 되돌리고 알려 주세요')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
