#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Weekly Calendar Overview 아티팩트 패치 — 2026-10-19
실행: python scripts/patch_calendar_20261019.py

반영 내용 (근거: 2026-10-19 한경준님 공지 + 사내 일정표 이미지 3종):
  1. KTWay 선서 11/03~12/29 정정 — 신규 일정표에서 순번이 1칸씩 당겨짐
       (기존 11/03 차은경 → 김선아 … 12/29 이승헌 → 이수민, 차은경은 2027-03-16 로 이동)
  2. 독서발표 11/17~12/29 신규 등재 — 순서표 26.11.17~27.01.19 확보로 공백 해소
       (11/10 은 두 순서표 사이 공백 + Claude 발표 2차일이라 미배정)
  3. 신규 행사 — 10/27 발표자료 마감 · 11/03 Claude 발표 1차 · 11/10 2차 ·
       11/28 워크샵 · 12/18 송년회
  4. 10/26 한경준 연차 → LEAVE_DAYS (holidays.md 선등록 완료, CLAUDE.md §13 순서 준수)

안전장치: 기대한 원본 문자열이 정확히 발견될 때만 치환한다. 하나라도 못 찾으면
          아무것도 쓰지 않고 중단 → PROD·CLAUDE_WORK 등 다른 블록 유실 위험 없음.
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

ARTIFACT = Path(r'C:\Users\TOOLKOREA\Documents\Claude\Artifacts\weekly-calendar-overview\index.html')

OLD_NOV_DEC = '''  /* ── 11월 ── */
  "2026-11-03":[{t:"meeting",l:"주간회의"},{t:"book",l:"◆독서발표 이소정·김경국"},{t:"submit",l:"🎗️ KTWay선서 차은경"}],
  "2026-11-05":[{t:"meeting",l:"부서장회의"}],
  "2026-11-10":[{t:"meeting",l:"주간회의"},{t:"report",l:"★미수금보고"},{t:"submit",l:"🎗️ KTWay선서 김선아"}],
  "2026-11-12":[{t:"meeting",l:"부서장회의"}],
  "2026-11-17":[{t:"meeting",l:"주간회의/KTHM/영업"},{t:"submit",l:"🎗️ KTWay선서 백승하"}],
  "2026-11-19":[{t:"meeting",l:"부서장회의"}],
  "2026-11-24":[{t:"meeting",l:"주간회의"},{t:"submit",l:"🎗️ KTWay선서 한경준"}],
  "2026-11-26":[{t:"meeting",l:"부서장회의"},{t:"submit",l:"11월실적/12월계획 제출"}],

  /* ── 12월 ── */
  "2026-12-01":[{t:"meeting",l:"주간회의"},{t:"submit",l:"🎗️ KTWay선서 김경태"}],
  "2026-12-03":[{t:"meeting",l:"부서장회의"}],
  "2026-12-08":[{t:"meeting",l:"주간회의"},{t:"submit",l:"🎗️ KTWay선서 전새봄"}],
  "2026-12-10":[{t:"meeting",l:"부서장회의"},{t:"report",l:"★미수금보고"}],
  "2026-12-15":[{t:"meeting",l:"주간회의/KTHM/영업"},{t:"submit",l:"🎗️ KTWay선서 최낙영"}],
  "2026-12-17":[{t:"meeting",l:"부서장회의"}],
  "2026-12-22":[{t:"meeting",l:"주간회의"},{t:"submit",l:"🎗️ KTWay선서 최한음"}],
  "2026-12-24":[{t:"meeting",l:"부서장회의"},{t:"submit",l:"12월실적/1월계획 제출"}],
  "2026-12-25":[{t:"holiday",l:"🎌 성탄절"}],
  "2026-12-29":[{t:"meeting",l:"주간회의"},{t:"submit",l:"🎗️ KTWay선서 이승헌"}],'''

NEW_NOV_DEC = '''  /* ── 11월 ── */
  "2026-11-03":[{t:"meeting",l:"주간회의"},{t:"submit",l:"🤖 Claude 발표 1차 (물류지원·기획·영업·해외영업)"},{t:"submit",l:"🎗️ KTWay선서 김선아"}],
  "2026-11-05":[{t:"meeting",l:"부서장회의"}],
  "2026-11-10":[{t:"meeting",l:"주간회의"},{t:"submit",l:"🤖 Claude 발표 2차 (기획마케팅·경영지원·물류·생산)"},{t:"report",l:"★미수금보고"},{t:"submit",l:"🎗️ KTWay선서 백승하"}],
  "2026-11-12":[{t:"meeting",l:"부서장회의"}],
  "2026-11-17":[{t:"meeting",l:"주간회의/KTHM/영업"},{t:"book",l:"◆독서발표 이소정·김경국"},{t:"submit",l:"🎗️ KTWay선서 한경준"}],
  "2026-11-19":[{t:"meeting",l:"부서장회의"}],
  "2026-11-24":[{t:"meeting",l:"주간회의"},{t:"book",l:"◆독서발표 박은정·김선아"},{t:"submit",l:"🎗️ KTWay선서 김경태"}],
  "2026-11-26":[{t:"meeting",l:"부서장회의"},{t:"submit",l:"11월실적/12월계획 제출"}],
  "2026-11-28":[{t:"submit",l:"🏕️ 워크샵"}],

  /* ── 12월 ── */
  "2026-12-01":[{t:"meeting",l:"주간회의"},{t:"book",l:"◆독서발표 백승하·한경준"},{t:"submit",l:"🎗️ KTWay선서 전새봄"}],
  "2026-12-03":[{t:"meeting",l:"부서장회의"}],
  "2026-12-08":[{t:"meeting",l:"주간회의"},{t:"book",l:"◆독서발표 이재건·최낙영"},{t:"submit",l:"🎗️ KTWay선서 최낙영"}],
  "2026-12-10":[{t:"meeting",l:"부서장회의"},{t:"report",l:"★미수금보고"}],
  "2026-12-15":[{t:"meeting",l:"주간회의/KTHM/영업"},{t:"book",l:"◆독서발표 이수민·전새봄"},{t:"submit",l:"🎗️ KTWay선서 최한음"}],
  "2026-12-17":[{t:"meeting",l:"부서장회의"}],
  "2026-12-18":[{t:"submit",l:"🥂 송년회"}],
  "2026-12-22":[{t:"meeting",l:"주간회의"},{t:"book",l:"◆독서발표 권은정·최한음"},{t:"submit",l:"🎗️ KTWay선서 이승헌"}],
  "2026-12-24":[{t:"meeting",l:"부서장회의"},{t:"submit",l:"12월실적/1월계획 제출"}],
  "2026-12-25":[{t:"holiday",l:"🎌 성탄절"}],
  "2026-12-29":[{t:"meeting",l:"주간회의"},{t:"book",l:"◆독서발표 이승현·권은영"},{t:"submit",l:"🎗️ KTWay선서 이수민"}],'''

OLD_1027 = '''  "2026-10-27":[{t:"meeting",l:"주간회의"},{t:"book",l:"◆독서발표 이재상·차은경"},{t:"submit",l:"🎗️ KTWay선서 조정숙"}],'''
NEW_1027 = '''  "2026-10-27":[{t:"meeting",l:"주간회의"},{t:"book",l:"◆독서발표 이재상·차은경"},{t:"submit",l:"🎗️ KTWay선서 조정숙"},{t:"report",l:"📮 Claude 발표자료 제출 마감"}],'''

OLD_LEAVE = 'const LEAVE_DAYS = new Set(["2026-04-13","2026-08-26"]);'
NEW_LEAVE = 'const LEAVE_DAYS = new Set(["2026-04-13","2026-08-26","2026-10-26"]);'

PATCHES = [
    ('11~12월 블록 (KTWay 정정 + 독서발표 + 신규 행사)', OLD_NOV_DEC, NEW_NOV_DEC),
    ('10/27 발표자료 제출 마감 추가',                     OLD_1027,    NEW_1027),
    ('10/26 연차 → LEAVE_DAYS',                           OLD_LEAVE,   NEW_LEAVE),
]


def main():
    if not ARTIFACT.exists():
        print('[patch] ERROR - artifact not found'); sys.exit(1)
    html = ARTIFACT.read_text(encoding='utf-8')

    missing = [name for name, old, _ in PATCHES if html.count(old) != 1]
    if missing:
        print('[patch] ABORT - 기대한 원본을 1회 정확히 찾지 못함 (아무것도 쓰지 않음):')
        for n in missing:
            print(f'          - {n}')
        print('        아티팩트가 이미 수정됐거나 포맷이 바뀐 상태입니다. 수동 확인 필요.')
        sys.exit(2)

    for name, old, new in PATCHES:
        html = html.replace(old, new, 1)
        print(f'[patch] OK - {name}')

    ARTIFACT.write_text(html, encoding='utf-8')
    print(f'[patch] DONE - {ARTIFACT}')


if __name__ == '__main__':
    main()
