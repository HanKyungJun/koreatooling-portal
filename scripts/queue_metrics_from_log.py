# -*- coding: utf-8 -*-
"""워크숍 효과 측정용 — generate.log 에서 날짜별 운영 지표를 뽑는다 (2026-09-29, Cowork)

목적: 「장비별 투입 목록」(2026-09-28 도입) 전후로 셋업 횟수·지연 건수를 비교한다.
      지표는 generate.py 가 매 실행 generate.log 에 이미 남기고 있으므로 새로 수집하지 않는다.
규칙:
  - 날짜 = 그 실행이 읽은 월간생산일지 최신 시트 날짜(「→ YYYY-MM-DD 재연마_월간생산일지」 줄)
  - 하루에 여러 번 돌았으면 **오전(12시 이전) 첫 실행**을 대표값으로 쓴다
    (지연은 오전·오후 차가 크다 — 09-28 16:07 8건 → 09-29 08:02 21건. 비교는 같은 회차로)
  - 「오늘 할 일」(2026-09-04~) · 「장비별 투입 목록」(2026-09-28~) 줄이 없는 날은 빈칸
출력: wiki/reports/09_업무일정/워크숍_투입목록_운영지표.csv (UTF-8 BOM, 엑셀에서 바로 열림) + 화면 표
실행: python scripts\\queue_metrics_from_log.py
"""
import csv, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(BASE, 'wiki', 'reports', 'daily', 'generate.log')
OUT = os.path.join(BASE, 'wiki', 'reports', '09_업무일정', '워크숍_투입목록_운영지표.csv')

R_START = re.compile(r'^\[(\d\d):(\d\d):\d\d .*generate\.py 시작')
R_DATE = re.compile(r'→ (\d{4}-\d\d-\d\d) 재연마_월간생산일지')
R_TODO = re.compile(r'미출하 (\d+)건 / ([\d,]+)개 · 지연 (\d+)건 · 임박 (\d+)건')
R_Q = re.compile(r'→ FG (\d+)품목/([\d,]+)개 \(셋업 (\d+)회\) · GX7 (\d+)품목/([\d,]+)개 \(셋업 (\d+)회\)')
R_FGOK = re.compile(r'🟢 FG 실적')   # 참고: 배지 합계는 로그에 없음 — 현황판에서만 확인


def runs(path):
    cur = None
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = R_START.match(line)
            if m:
                if cur:
                    yield cur
                cur = dict(hh=int(m.group(1)), mm=int(m.group(2)))
                continue
            if cur is None:
                continue
            if 'date' not in cur and (m := R_DATE.search(line)):
                cur['date'] = m.group(1)
            if 'late' not in cur and (m := R_TODO.search(line)):
                cur.update(open_n=int(m.group(1)), open_q=int(m.group(2).replace(',', '')),
                           late=int(m.group(3)), near=int(m.group(4)))
            if 'fg_n' not in cur and (m := R_Q.search(line)):
                g = [int(x.replace(',', '')) for x in m.groups()]
                cur.update(fg_n=g[0], fg_q=g[1], fg_setup=g[2], gx_n=g[3], gx_q=g[4], gx_setup=g[5])
    if cur:
        yield cur


def main():
    best = {}
    for r in runs(LOG):
        d = r.get('date')
        if not d:
            continue
        key = (0 if r['hh'] < 12 else 1, r['hh'], r['mm'])   # 오전 첫 실행 우선
        if d not in best or key < best[d][0]:
            best[d] = (key, r)
    cols = ['날짜', '회차', '미출하_건', '미출하_개', '지연_건', '임박_건',
            'FG_품목', 'FG_개', 'FG_셋업', 'GX7_품목', 'GX7_개', 'GX7_셋업', '셋업_합계']
    rows = []
    for d in sorted(best):
        r = best[d][1]
        su = (r['fg_setup'] + r['gx_setup']) if 'fg_setup' in r else ''
        rows.append([d, f"{r['hh']:02d}:{r['mm']:02d}", r.get('open_n', ''), r.get('open_q', ''),
                     r.get('late', ''), r.get('near', ''), r.get('fg_n', ''), r.get('fg_q', ''),
                     r.get('fg_setup', ''), r.get('gx_n', ''), r.get('gx_q', ''), r.get('gx_setup', ''), su])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    shown = [r for r in rows if r[4] != '']
    print(' | '.join(cols))
    for r in shown:
        print(' | '.join(str(x) for x in r))
    print(f'\n저장: {OUT}  ({len(rows)}일, 「오늘 할 일」 있는 날 {len(shown)}일)')


if __name__ == '__main__':
    main()
