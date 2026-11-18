#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Weekly Calendar Overview — KTWay 선서 한 주씩 순연 (2026-11-18)
실행: python scripts/patch_calendar_ktway_shift_20261118.py

근거: 2026-11-18 한경준님 확인 — 「화요일 KTWAY선서가 한주씩 밀림, 24일 한경준으로」

변경 (발표자를 다음 화요일로 1주씩 이동):
    11/03 김선아 → (제거, 앞 순번 없음 · 당일 Claude 파일럿 발표 1차)
    11/10 백승하 → 김선아
    11/17 한경준 → 백승하
    11/24 김경태 → 한경준   ← 한경준님이 직접 확인한 기준점
    12/01 전새봄 → 김경태
    12/08 최낙영 → 전새봄
    12/15 최한음 → 최낙영
    12/22 이승헌 → 최한음
    12/29 이수민 → 이승헌
    (이수민은 2027-01-05 로 밀림 — 2027년분은 캘린더 미등재 범위)

안전장치: 기대 원본을 정확히 1회 찾을 때만 치환. 하나라도 불일치면 아무것도 쓰지 않고 중단.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

ARTIFACT = Path(r'C:\Users\TOOLKOREA\Documents\Claude\Artifacts\weekly-calendar-overview\index.html')

PATCHES = [
    # 11/03 — KTWay 태그 자체를 제거
    ('11/03 KTWay 제거',
     '''  "2026-11-03":[{t:"meeting",l:"주간회의"},{t:"submit",l:"🤖 Claude 발표 1차 (물류지원·기획·영업·해외영업)"},{t:"submit",l:"🎗️ KTWay선서 김선아"}],''',
     '''  "2026-11-03":[{t:"meeting",l:"주간회의"},{t:"submit",l:"🤖 Claude 발표 1차 (물류지원·기획·영업·해외영업)"}],'''),

    ('11/10 백승하 → 김선아', '🎗️ KTWay선서 백승하"}],\n  "2026-11-12"', '🎗️ KTWay선서 김선아"}],\n  "2026-11-12"'),
    ('11/17 한경준 → 백승하', '🎗️ KTWay선서 한경준"}],\n  "2026-11-19"', '🎗️ KTWay선서 백승하"}],\n  "2026-11-19"'),
    ('11/24 김경태 → 한경준', '🎗️ KTWay선서 김경태"}],\n  "2026-11-26"', '🎗️ KTWay선서 한경준"}],\n  "2026-11-26"'),
    ('12/01 전새봄 → 김경태', '🎗️ KTWay선서 전새봄"}],\n  "2026-12-03"', '🎗️ KTWay선서 김경태"}],\n  "2026-12-03"'),
    ('12/08 최낙영 → 전새봄', '🎗️ KTWay선서 최낙영"}],\n  "2026-12-10"', '🎗️ KTWay선서 전새봄"}],\n  "2026-12-10"'),
    ('12/15 최한음 → 최낙영', '🎗️ KTWay선서 최한음"}],\n  "2026-12-17"', '🎗️ KTWay선서 최낙영"}],\n  "2026-12-17"'),
    ('12/22 이승헌 → 최한음', '🎗️ KTWay선서 이승헌"}],\n  "2026-12-24"', '🎗️ KTWay선서 최한음"}],\n  "2026-12-24"'),
    ('12/29 이수민 → 이승헌', '🎗️ KTWay선서 이수민"}],\n};',                 '🎗️ KTWay선서 이승헌"}],\n};'),
]


def main():
    if not ARTIFACT.exists():
        print('[patch] ERROR - artifact not found'); sys.exit(1)
    html = ARTIFACT.read_text(encoding='utf-8')

    bad = [(n, html.count(o)) for n, o, _ in PATCHES if html.count(o) != 1]
    if bad:
        print('[patch] ABORT - 기대 원본을 1회 정확히 찾지 못함 (아무것도 쓰지 않음):')
        for n, c in bad:
            print(f'          - {n}  (발견 {c}회)')
        sys.exit(2)

    # 뒤에서부터 치환해야 앞 치환 결과가 다음 패턴을 깨지 않는다
    for n, o, w in reversed(PATCHES):
        html = html.replace(o, w, 1)
        print(f'[patch] OK - {n}')

    ARTIFACT.write_text(html, encoding='utf-8')
    print(f'[patch] DONE - {ARTIFACT}')


if __name__ == '__main__':
    main()
