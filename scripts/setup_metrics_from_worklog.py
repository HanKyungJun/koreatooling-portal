# -*- coding: utf-8 -*-
"""워크숍 효과 지표 — 작업일지에서 「실제 셋업」과 「셋업당 개수(개/셋업)」를 센다 (2026-10-06, Cowork)

배경: queue_metrics_from_log.py 의 「셋업」은 남은 투입 목록의 셋업 그룹 수(계획값)라
      대기 물량에 따라 늘고 준다. 실제로 장비를 다시 세팅한 횟수가 아니다.
      셋업 수는 생산량을 따라 늘므로 효과 지표는 **개/셋업** 으로 본다 (decisions.md 2026-10-06 (2)).

정의:
  - 입력: outputs/worklog_parsed/jobs_all.csv  (먼저 `python scripts/parse_worklog.py` 로 갱신)
  - 설비·날짜별로 작업 줄을 「순서」대로 놓고, 바로 앞 줄과 (형상, 날경, 날수) 가 다르면 셋업 1회
  - 수량 합이 0 인 설비-날짜는 제외(가동 없음)
  - 개/셋업 = 그날 수량 합 ÷ 셋업 수
비교 구간 (기본값):
  - 도입 전: 2026-09-01 ~ 09-26 (F 수리 09-14~16 제외)
  - 도입 후: 2026-09-29 ~ (마지막 데이터일)
출력: wiki/reports/09_업무일정/워크숍_셋업당개수_지표.csv (UTF-8 BOM) + 화면 요약
실행: python scripts\\parse_worklog.py              ← 연도 인자 없이(전체). 연도를 주면 jobs_all 이 그 해만으로 덮어써진다
      python scripts\\setup_metrics_from_worklog.py
주의: 오늘 날짜는 작업일지가 덜 찼을 수 있다 — 하루 끝난 뒤 값으로 비교할 것
"""
import csv, datetime as dt, os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'outputs', 'worklog_parsed', 'jobs_all.csv')
OUT = os.path.join(BASE, 'wiki', 'reports', '09_업무일정', '워크숍_셋업당개수_지표.csv')

START = dt.date(2026, 8, 13)                      # GX7 로더 금지 시작 — 이후만 본다
BEFORE = (dt.date(2026, 9, 1), dt.date(2026, 9, 26))
EXCLUDE = {dt.date(2026, 9, 14), dt.date(2026, 9, 15), dt.date(2026, 9, 16)}   # F 로더 수리
AFTER_FROM = dt.date(2026, 9, 29)                 # 장비별 투입 목록 1차 가동 다음 영업일


def qty(x):
    try:
        return int(float(x['수량'] or 0))
    except ValueError:
        return 0


def load():
    by = defaultdict(list)
    with open(SRC, encoding='utf-8-sig') as f:
        for x in csv.DictReader(f):
            d = dt.date(int(x['연']), int(x['월']), int(x['일']))
            if d >= START:
                by[(d, x['설비'])].append(x)
    days = []
    for (d, m), rows in sorted(by.items()):
        rows.sort(key=lambda x: int(x['순서']))
        q = sum(qty(x) for x in rows)
        if q == 0:
            continue
        setups, prev = 0, None
        for x in rows:
            k = (x['형상'].strip(), x['날경'].strip(), x['날수F'].strip())
            if k != prev:
                setups += 1
            prev = k
        days.append(dict(날짜=d.isoformat(), 설비=m, 줄=len(rows), 셋업=setups, 수량=q,
                         개_per_셋업=round(q / setups, 2)))
    return days


def summarize(days, lo, hi, excl=()):
    out = {}
    for m in ('FG', 'GX7'):
        sel = [r for r in days if r['설비'] == m and lo <= dt.date.fromisoformat(r['날짜']) <= hi
               and dt.date.fromisoformat(r['날짜']) not in excl]
        n = len(sel)
        s = sum(r['셋업'] for r in sel)
        q = sum(r['수량'] for r in sel)
        out[m] = (n, s / n if n else 0, q / n if n else 0, q / s if s else 0)
    return out


def main():
    days = load()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(days[0].keys()))
        w.writeheader()
        w.writerows(days)
    last = max(dt.date.fromisoformat(r['날짜']) for r in days)
    print(f'마지막 작업일: {last}')
    for name, lo, hi, ex in [('도입 전 9/1~9/26 (F수리 3일 제외)', *BEFORE, EXCLUDE),
                             (f'도입 후 9/29~{last.month}/{last.day}', AFTER_FROM, last, ())]:
        print(name)
        for m, (n, s, q, k) in summarize(days, lo, hi, ex).items():
            print(f'  {m}: 일수 {n} | 셋업/일 {s:.1f} | 개/일 {q:.1f} | 개/셋업 {k:.1f}')
    print(f'저장: {OUT}  ({len(days)}행)')


if __name__ == '__main__':
    main()
