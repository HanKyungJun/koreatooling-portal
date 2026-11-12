#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
캘린더 아티팩트(Weekly Calendar Overview) — ERP 기준 일일보고 대응 일회성 정정 (2026-10-27, Cowork)

배경: 10-23 16:00 회차에 update_calendar_artifact.py(옛판)가 PROD 에
      "2026-10-23":{"fg":None,"gx7":None,"total":0,...,"time":"3:26:39 (표준공수 추정)"} 를 넣었다.
      JS 에 None 은 없는 이름이라 `const PROD` 에서 ReferenceError → 화면 전체가 멈춘다.

고치는 것:
  1. PROD 2026-10-23 줄 → 일일보고에서 다시 읽은 값 (fg·gx7 = null, total = 합계 수량, time = H:MM:SS, est)
  2. 화면 JS — 수량을 fg+gx7 대신 prodTotal(p) 로 (ERP 기준일은 total)
              배지 아래 줄: 엑셀 기준일 「F·G 시간」 그대로 / ERP 기준일 「NC n  시간 (추정)」
              월 합계 가공시간: 시간 문자열에서 H:MM:SS 만 읽음 (NaN 방지)
  3. PROD 에 None 이 하나라도 남으면 적용하지 않음

실행 (경준님 PC, cnc-wiki 폴더에서):
    python scripts\fix_calendar_erp_20261027.py            ← 미리보기(파일 안 바꿈)
    python scripts\fix_calendar_erp_20261027.py --apply    ← 백업 후 적용 · 다시 읽어 확인
백업: 아티팩트 폴더에 index.html.bak_20261027 (이미 있으면 덮어쓰지 않음)
"""
import sys, re, shutil, importlib.util
from pathlib import Path
# stdout UTF-8 감싸기는 update_calendar_artifact.py 를 불러올 때 그쪽이 한다 (10-12 스크립트와 같음)

BASE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('uca', BASE / 'scripts' / 'update_calendar_artifact.py')
uca = importlib.util.module_from_spec(spec); spec.loader.exec_module(uca)

args = sys.argv[1:]
APPLY = '--apply' in args
art_arg = [a for a in args if a.startswith('--artifact=')]
ARTIFACT = Path(art_arg[0].split('=', 1)[1]) if art_arg else uca.ARTIFACT
FIX_DAYS = ['2026-10-23']

HELPERS = (
    "// 2026-10-27: ERP 기준 일일보고(fg·gx7 = null) 대응 — 수량은 total, 시간은 H:MM:SS 만 읽음\n"
    "function prodTotal(p){ return (p.fg==null && p.gx7==null) ? (Number(p.total)||0) : (Number(p.fg)||0)+(Number(p.gx7)||0); }\n"
    "function prodSec(p){ const m=String(p.time||'').match(/(\\d+):(\\d{2}):(\\d{2})/); return m ? (+m[1])*3600+(+m[2])*60+(+m[3]) : 0; }\n"
    "function prodDetail(p){ const t=(String(p.time||'').match(/\\d+:\\d{2}:\\d{2}/)||[''])[0];\n"
    "  return (p.fg==null && p.gx7==null) ? `NC ${prodTotal(p)}  ${t}${p.est?' (추정)':''}` : `F${p.fg}·G${p.gx7}  ${t}`; }\n"
    "\n"
)
JS_EDITS = [   # (설명, 옛 문자열, 새 문자열)
    ('배지 수량', '  const displayTotal = p.fg + p.gx7;\n', '  const displayTotal = prodTotal(p);\n'),
    ('배지 아랫줄', '<span class="prod-time">F${p.fg}·G${p.gx7}  ${p.time}</span>',
                   '<span class="prod-time">${prodDetail(p)}</span>'),
    ('월 합계', "    if(p){ totalProd+=p.fg+p.gx7; const [h,mi,s]=p.time.split(':').map(Number); totalSec+=h*3600+mi*60+s; }\n",
               "    if(p){ totalProd+=prodTotal(p); totalSec+=prodSec(p); }\n"),
    ('도우미 함수', 'function renderProdBadge(key){\n', HELPERS + 'function renderProdBadge(key){\n'),
]


def prod_block(html):
    s = html.find('const PROD = {')
    return html[s:html.find(uca.MARKER, s)] if s >= 0 else ''


def main():
    if not ARTIFACT.exists():
        print(f'❌ 아티팩트 파일 없음: {ARTIFACT}'); return 1
    html = ARTIFACT.read_text(encoding='utf-8')
    plan = []

    # 1) JS
    if 'function prodTotal(p)' in html:
        print('· 화면 JS: 이미 고쳐져 있음 (변경 없음)')
    else:
        for name, old, new in JS_EDITS:
            n = html.count(old)
            if n != 1:
                print(f'❌ 화면 JS 「{name}」 자리를 찾지 못함(일치 {n}곳) — 형식이 바뀌었을 수 있음, 수동 확인 필요'); return 1
            html = html.replace(old, new, 1)
            plan.append(f'화면 JS: {name}')

    # 2) PROD 줄
    for k in FIX_DAYS:
        x = BASE / 'wiki' / 'reports' / 'daily' / f'{k}_일일보고.xlsx'
        if not x.exists():
            print(f'❌ 일일보고 없음: {x}'); return 1
        line = uca.prod_line(k, uca.parse_report(x))
        if line in html:
            print(f'· PROD {k}: 이미 바른 값 (변경 없음)'); continue
        old = re.findall(rf'  "{k}":\{{[^\n]+\}},\n', html)
        if len(old) > 1:
            print(f'❌ PROD {k} 줄이 {len(old)}개 — 수동 확인 필요'); return 1
        if old:
            html = html.replace(old[0], line, 1)
            plan.append(f'PROD {k}\n      옛: {old[0].strip()}\n      새: {line.strip()}')
        else:
            html = html.replace(uca.MARKER, line + uca.MARKER, 1)
            plan.append(f'PROD {k} 추가: {line.strip()}')

    # 3) None 남았는지
    left = re.findall(r'  "[\d-]+":\{[^\n]*:\s*None\b[^\n]*\n', prod_block(html))
    if left:
        print('❌ PROD 에 None 이 남아 있음 — 적용 중단:'); [print('   ', l.strip()) for l in left]; return 1

    if not plan:
        print('✅ 바꿀 것 없음'); return 0
    print('바꿀 내용:'); [print('  -', p) for p in plan]
    if not APPLY:
        print('(미리보기 — 적용하려면 --apply)'); return 0

    bak = ARTIFACT.with_name(ARTIFACT.name + '.bak_20261027')
    if not bak.exists():
        shutil.copy2(ARTIFACT, bak); print(f'백업: {bak}')
    else:
        print(f'백업 이미 있음(덮어쓰지 않음): {bak}')
    ARTIFACT.write_text(html, encoding='utf-8', newline='\r\n')

    # 다시 읽어 확인 (조용한 성공 방지)
    chk = ARTIFACT.read_text(encoding='utf-8')
    ok = ('function prodTotal(p)' in chk
          and all(uca.prod_line(k, uca.parse_report(BASE / 'wiki' / 'reports' / 'daily' / f'{k}_일일보고.xlsx')) in chk for k in FIX_DAYS)
          and not re.search(r':\s*None\b', prod_block(chk)))
    print('✅ 적용 확인 완료 — 캘린더를 다시 열어 10월 화면을 확인하세요' if ok else '❌ 다시 읽은 결과가 기대와 다름 — 백업으로 되돌리고 알려 주세요')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
