# -*- coding: utf-8 -*-
"""파일럿 2기 발표·워크숍 보고서 숫자 재측정 (읽기 전용, 파일을 쓰지 않는다) — 2026-10-19 신설

실행: python scripts/pilot_numbers.py [기준일 YYYY-MM-DD]
  기준일 생략 = 오늘(KST). 영업일 생성률은 기준일 「전」 영업일까지 센다(당일 16:00 전이면 아직 없으므로).
출력 항목과 PPT·보고서 위치:
  위키 페이지(overview 자동 집계) · 결정 건수(현재 + 보관) · Python 스크립트 수(scripts/ + erp/)
  일일보고 누적 · 최근 18/20 영업일 생성률(holidays.md 휴무 제외)
근거: decisions 2026-10-19 (3) — 10-23 숫자 재측정 후 PPT·보고서 함께 갱신 (10-26 연차로 당김)
"""
import re, glob, os, sys, io
from datetime import date, datetime, timedelta, timezone
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(BASE, *a)
rd = lambda f: open(f, encoding='utf-8-sig').read()

today = (datetime.strptime(sys.argv[1], '%Y-%m-%d').date() if len(sys.argv) > 1
         else datetime.now(timezone(timedelta(hours=9))).date())
print(f'기준일 {today} (KST)')

m = re.search(r'현재 \*\*(\d+)페이지\*\* \(([\d-]+)', rd(P('wiki', 'overview.md')))
print(f'위키 페이지: {m.group(1)} (overview 집계일 {m.group(2)})' if m else '위키 페이지: overview 에서 못 찾음')

HD = re.compile(r'^## 20\d\d-', re.M)
cur = len(HD.findall(rd(P('wiki', '_handoff', 'decisions.md'))))
arc = sum(len(HD.findall(rd(f))) for f in glob.glob(P('wiki', '_handoff', 'decisions-archive', '*.md')))
print(f'결정 기록: {cur + arc}건 (현재 {cur} + 보관 {arc})')

py = glob.glob(P('scripts', '*.py')) + glob.glob(P('erp', '*.py'))
print(f'Python 스크립트: {len(py)}개 (scripts/ + erp/)')

have = {f[:10] for f in os.listdir(P('wiki', 'reports', 'daily')) if f.endswith('_일일보고.xlsx')}
print(f'일일보고 누적: {len(have)}개 (최신 {max(have)})')

hol = set(re.findall(r'^\| (\d{4}-\d{2}-\d{2}) \|', rd(P('wiki', '_handoff', 'holidays.md')), re.M))
d, bd = today - timedelta(1), []
while len(bd) < 20:
    if d.weekday() < 5 and d.isoformat() not in hol:
        bd.append(d)
    d -= timedelta(1)
for n in (18, 20):
    s = bd[:n]
    miss = [x.isoformat() for x in s if x.isoformat() not in have]
    print(f'최근 {n}영업일({s[-1]} ~ {s[0]}): 생성 {n - len(miss)}/{n}' + (f' · 누락 {miss}' if miss else ''))
