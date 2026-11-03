# -*- coding: utf-8 -*-
"""일일보고 ERP 작업실적 — g20 캐시 사용 전 · 후 결과 비교 (읽기 전용, 2026-10-27 Cowork)

erp_worklog.fetch_nc_results 의 g20 캐시(기본 꺼짐)를 켜도 결과가 같은지 확인한다.
  1) 캐시 없이 조회(지금 방식)            → 기준
  2) 시험용 캐시 파일로 조회(캐시 채우기) → 호출 수는 1) 과 같아야 함
  3) 같은 캐시로 다시 조회(캐시 재사용)   → 호출 수가 줄고, 줄 · 날짜별 양품 · 불량이 1) 과 완전히 같아야 함
ERP 에 쓰지 않는다. 시험용 캐시는 erp/snapshot/g20_cache_probe.json(.gitignore 의 erp/snapshot/), 결과는 erp/probe_g20_cache_result.txt.
실행 (cnc-wiki 폴더에서): python erp\\probe_g20_cache.py          ← 이번 달 1일 ~ 오늘
                          python erp\\probe_g20_cache.py 2026-10-01 2026-10-27
2 ~ 3분 걸린다(ERP 조회 약 1,200회).
"""
import sys, os, io, time
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pandas as pd
import erp_worklog as ew
from trico_client import TricoClient

OUT = io.StringIO()
def P(*a):
    s = " ".join(str(x) for x in a); print(s); OUT.write(s + "\n")

args = [a for a in sys.argv[1:] if not a.startswith('-')]
to = date.fromisoformat(args[1]) if len(args) > 1 else date.today()
fr = date.fromisoformat(args[0]) if args else to.replace(day=1)
cp = os.path.join(HERE, 'snapshot', 'g20_cache_probe.json')
if os.path.exists(cp):
    os.remove(cp)   # 시험용 파일만 지운다(실사용 캐시 g20_cache.json 은 건드리지 않음)
P(f"[실행] {time.strftime('%Y-%m-%d %H:%M:%S')} (PC 시각) · 작업일 {fr} ~ {to}")
c = TricoClient()

def run(tag, **kw):
    t0 = time.time()
    df = ew.fetch_nc_results(fr, to, client=c, log=P, **kw)
    P(f"  [{tag}] {time.time() - t0:.0f}s")
    return df

d0 = run('1 캐시 없음', use_cache=False)
d1 = run('2 캐시 채우기', use_cache=True, cache_path=cp)
d2 = run('3 캐시 재사용', use_cache=True, cache_path=cp)

cols = ['work_dt', 'wo_no', 'mc_cd', 'ok', 'bad', 'pw_tm', 'pw_no', 'pw_sq']
def norm(d):
    if not len(d):
        return pd.DataFrame(columns=cols)
    x = d[[k for k in cols if k in d.columns]].copy()
    x['work_dt'] = x['work_dt'].astype(str)
    for k in ('pw_no', 'pw_sq', 'mc_cd', 'wo_no'):
        if k in x: x[k] = x[k].astype(str)
    return x.sort_values(list(x.columns)).reset_index(drop=True)

same_23 = norm(d1).equals(norm(d2))
P(f"\n■ 2) ↔ 3) 줄 단위(캐시가 g20 을 그대로 돌려주는지): {'같음' if same_23 else '다름'} ({len(d1)}줄 ↔ {len(d2)}줄)")
same_rows = norm(d0).equals(norm(d2))
byday = lambda d: d.groupby(d['work_dt'].astype(str))[['ok', 'bad']].sum() if len(d) else pd.DataFrame()
same_day = byday(d0).equals(byday(d2))
P(f"■ 1) ↔ 3) 줄 단위: {'같음' if same_rows else '다름'} ({len(d0)}줄 ↔ {len(d2)}줄)")
P(f"■ 1) ↔ 3) 날짜별 양품 · 불량: {'같음' if same_day else '다름'}")
if not same_day:
    P(pd.concat([byday(d0).add_suffix('_캐시없음'), byday(d2).add_suffix('_캐시')], axis=1).fillna(0).to_string())
if not same_rows:
    a, b = norm(d0), norm(d2)
    m = a.merge(b, how='outer', indicator=True)
    P(m[m['_merge'] != 'both'].to_string())
P(f"\n■ 판정: {'✅ 같음 — 캐시 켜도 됨(G20_CACHE = True)' if (same_rows and same_day and same_23) else '❌ 다름 — 캐시 보류, 위 표 확인'}")
P("  (1 ↔ 2 사이에 ERP 입력이 들어오면 3 도 그만큼 달라질 수 있음 — 그때는 한 번 더 실행)")

with open(os.path.join(HERE, 'probe_g20_cache_result.txt'), 'w', encoding='utf-8') as f:
    f.write(OUT.getvalue())
