#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
캘린더 아티팩트(Weekly Calendar Overview) ↔ holidays.md 대조 결과 일회성 정정 (2026-10-12, Cowork)

고치는 것 (holidays.md 가 기준 — holidays.md §4):
  1. CO_EVENTS 현충일 2026-06-05 → 2026-06-06  (06-05 는 생산 50개 영업일 · 06-06 은 토요일)
     ※ holidays.md 에는 「2026-08-06 아티팩트도 정정」으로 기록돼 있으나 실물은 06-05 그대로였다
  2. PROD 누락 2일 추가 — 2026-04-29 · 2026-04-30 (일일보고 xlsx 는 있는데 PROD 에 없어 「보고서 누락」으로 표시되던 날)
     값은 update_calendar_artifact.py 의 parse_xlsx 로 일일보고에서 읽는다

실행 (경준님 PC):
    python scripts\fix_calendar_artifact_20261012.py            ← 미리보기(파일 안 바꿈)
    python scripts\fix_calendar_artifact_20261012.py --apply    ← 백업 후 적용 · 다시 읽어 확인
백업: 아티팩트 폴더에 index.html.bak_20261012 (이미 있으면 덮어쓰지 않음)
"""
import sys, io, shutil, importlib.util
from pathlib import Path
# stdout UTF-8 감싸기는 update_calendar_artifact.py 를 불러올 때 그쪽이 한다 — 여기서 또 감싸면 앞 래퍼가 정리되며 출력이 닫힌다(10-12 테스트에서 확인)

BASE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('uca', BASE / 'scripts' / 'update_calendar_artifact.py')
uca = importlib.util.module_from_spec(spec); spec.loader.exec_module(uca)

args = [a for a in sys.argv[1:]]
APPLY = '--apply' in args
art_arg = [a for a in args if a.startswith('--artifact=')]
ARTIFACT = Path(art_arg[0].split('=', 1)[1]) if art_arg else uca.ARTIFACT

OLD_HOL = '  "2026-06-05":[{t:"holiday",l:"🎌 현충일"}],\n'
NEW_HOL = '  "2026-06-06":[{t:"holiday",l:"🎌 현충일"}],\n'
PROD_DAYS = ['2026-04-29', '2026-04-30']
MARKER = '};\n\nconst REPORT_START'

def main():
    if not ARTIFACT.exists():
        print(f'❌ 아티팩트 파일 없음: {ARTIFACT}'); return 1
    html = ARTIFACT.read_text(encoding='utf-8')
    orig = html
    plan = []

    # 1) 현충일
    co = html[html.find('const CO_EVENTS'):html.find('const CLAUDE_WORK')]
    if OLD_HOL in co:
        if '"2026-06-06":[' in co:
            print('❌ CO_EVENTS 에 06-06 줄이 이미 있음 — 수동 확인 필요'); return 1
        html = html.replace(OLD_HOL, NEW_HOL, 1)
        plan.append('현충일 06-05 → 06-06')
    elif NEW_HOL in co:
        print('· 현충일: 이미 06-06 (변경 없음)')
    else:
        print('❌ 현충일 줄을 찾지 못함 — 형식이 바뀌었을 수 있음, 수동 확인 필요'); return 1

    # 2) PROD 누락일
    if MARKER not in html:
        print('❌ PROD 끝 표시를 찾지 못함'); return 1
    for k in PROD_DAYS:
        if f'"{k}":{{"fg":' in html:
            print(f'· PROD {k}: 이미 있음 (변경 없음)'); continue
        x = BASE / 'wiki' / 'reports' / 'daily' / f'{k}_일일보고.xlsx'
        if not x.exists():
            print(f'❌ 일일보고 없음: {x}'); return 1
        fg, gx7, total, avg, t = uca.parse_xlsx(x)
        line = f'  "{k}":{{"fg":{fg},"gx7":{gx7},"total":{total},"avg":{avg},"time":"{t}"}},\n'
        html = html.replace(MARKER, line + MARKER, 1)
        plan.append(f'PROD {k} 추가: FG {fg} · GX7 {gx7} · 합계 {total} · {t}')

    if not plan:
        print('✅ 바꿀 것 없음'); return 0
    print('바꿀 내용:'); [print('  -', p) for p in plan]
    if not APPLY:
        print('(미리보기 — 적용하려면 --apply)'); return 0

    bak = ARTIFACT.with_name(ARTIFACT.name + '.bak_20261012')
    if not bak.exists():
        shutil.copy2(ARTIFACT, bak); print(f'백업: {bak}')
    ARTIFACT.write_text(html, encoding='utf-8')

    # 다시 읽어 확인 (조용한 성공 방지)
    chk = ARTIFACT.read_text(encoding='utf-8')
    co2 = chk[chk.find('const CO_EVENTS'):chk.find('const CLAUDE_WORK')]
    ok = NEW_HOL in co2 and OLD_HOL not in co2 and all(f'"{k}":{{"fg":' in chk for k in PROD_DAYS)
    print('✅ APPLIED — 다시 읽어 확인 완료' if ok else '❌ 다시 읽은 결과가 기대와 다름 — 백업으로 되돌리세요')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
