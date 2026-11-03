# -*- coding: utf-8 -*-
"""투입 목록 가공분 — g10 누계(ok_in_tot + bad_in_tot) vs g20 작업실적 합 비교 (읽기 전용, 2026-10-27 Cowork)

machine_queue.fetch_erp_worked 의 g20 호출(약 절반)을 빼도 되는지 확인한다.
  1) mode='both' 로 한 번 읽어 작업지시 키마다 g10 값 · g20 값을 나란히 비교
  2) mode='g10' 으로 한 번 더 읽어 호출 수 · 시간 측정
  3) 두 결과로 투입 목록을 각각 만들어 FG / GX7 품목 · 수량 · 줄이 같은지 비교
ERP · 파일에 쓰지 않는다. 결과 텍스트만 erp/probe_queue_g10_vs_g20_result.txt (.gitignore 의 erp/probe_*_result.txt).
실행 (cnc-wiki 폴더에서): python erp\\probe_queue_g10_vs_g20.py
"""
import sys, os, io, json, time
from datetime import date, timedelta
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pandas as pd
import machine_queue as mq
from trico_client import TricoClient

OUT = io.StringIO()
def P(*a):
    s = " ".join(str(x) for x in a); print(s); OUT.write(s + "\n")

P(f"[실행] {time.strftime('%Y-%m-%d %H:%M:%S')} (PC 시각)")
fr = (date.today() - timedelta(days=120)).strftime('%Y-%m-%d')
c = TricoClient()
df = c.query('sdb100_jae_g10', {'@to_dt': '', '@fr_dt': fr, '@chk_detail': '1', '@co_cd': '01', '@f_so_no': None,
     '@f_so_bs': "'01','10'", '@f_cust_cd': None, '@f_cust2_cd': None, '@f_itm_cd': None, '@f_so_rid': None,
     '@f_stat_bc': '', '@f_order_nm': None, '@f_rmks': None, '@f_cust_nm': None})
try:
    _h = json.load(open(os.path.join(HERE, 'hold_orders.json'), encoding='utf-8'))
    holds = {str(h['so_no']): str(h.get('reason', '보류')) for h in _h.get('holds', []) if h.get('so_no')}
except Exception:
    holds = {}
_fr = date.fromisoformat(fr)
try:
    wl_all = mq.load_worklog(min(_fr, date(date.today().year - 1, 1, 1)))
    wl = [r for r in wl_all if r['date'] >= _fr]
    cap = mq.build_fg_capability(wl_all)
except Exception as e:
    P(f"  ⚠️ 작업일지 읽기 실패 — 작업일지 없이 비교: {e}"); wl, cap = None, None
try:
    osrc = mq.load_outsource()
except Exception:
    osrc = []
P(f"  수주 품목 {len(df)}행 · 작업일지 {len(wl or [])}줄 · 보류 {len(holds)}건 · 외주 {len(osrc)}줄")

# 1) both
t0 = time.time()
ew20 = mq.fetch_erp_worked(df, fr, P, client=c, mode='both')
t_both = time.time() - t0
cmp_ = dict(mq.LAST_COMPARE)
diff = {k: v for k, v in cmp_.items() if abs(v[0] - v[1]) > 1e-9}
P(f"\n■ 키별 비교: {len(cmp_)}개 · 같음 {len(cmp_) - len(diff)} · 다름 {len(diff)}")
P(f"  합계 g10 {sum(v[0] for v in cmp_.values()):g} · g20 {sum(v[1] for v in cmp_.values()):g}")
for k, (a, b) in sorted(diff.items()):
    P(f"  다름 {k[0]} {k[1]} 코팅={k[2] or '-'} 각도={k[3] or '-'} : g10 {a:g} ↔ g20 {b:g}")

# 2) g10 only
t0 = time.time()
ew10 = mq.fetch_erp_worked(df, fr, P, client=c, mode='g10')
t_g10 = time.time() - t0
P(f"\n■ 시간: both(= 기존 g20 방식 + g10 계산) {t_both:.0f}s · g10 만 {t_g10:.0f}s")

# 3) 투입 목록 비교
q20 = mq.build_queue(df, holds, worklog=wl, fg_cap=cap, outsource=osrc, erp_worked=ew20)
q10 = mq.build_queue(df, holds, worklog=wl, fg_cap=cap, outsource=osrc, erp_worked=ew10)
key = lambda it: (it['so_no'], it['itm'], it['coat'], it['rest'])
same = True
P("\n■ 투입 목록")
for m in ('FG', 'GX7'):
    a = sorted(map(key, q20[m]['items'])); b = sorted(map(key, q10[m]['items']))
    ok = (a == b)
    same &= ok
    P(f"  {m}: g20 {q20[m]['n']}품목 {q20[m]['qty']}개 · g10 {q10[m]['n']}품목 {q10[m]['qty']}개 → {'같음' if ok else '다름'}")
    if not ok:
        for x in sorted(set(a) - set(b)): P(f"    g20 에만: {x}")
        for x in sorted(set(b) - set(a)): P(f"    g10 에만: {x}")
P(f"\n■ 판정: {'✅ 키 · 목록 모두 같음 — 기본값 g10 전환 가능' if (same and not diff) else '❌ 차이 있음 — 전환 보류, 위 목록 확인'}")

with open(os.path.join(HERE, 'probe_queue_g10_vs_g20_result.txt'), 'w', encoding='utf-8') as f:
    f.write(OUT.getvalue())
