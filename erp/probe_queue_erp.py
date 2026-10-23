# -*- coding: utf-8 -*-
"""투입 목록 — 엑셀 작업일지만 vs 엑셀 + ERP 작업실적 비교 (읽기 전용, 2026-10-23 Cowork)

엑셀 입력을 10-23 부터 멈춰서 machine_queue.py 에 ERP NC 양품 차감을 넣었다(decisions 2026-10-23 (5)).
이 스크립트는 같은 ERP 조회 결과로 목록을 두 번 만들어 무엇이 빠지는지 보여 준다. 파일 · ERP 에 쓰지 않는다.
(결과 텍스트만 erp/probe_queue_erp_result.txt 에 남긴다 — .gitignore 의 erp/probe_*_result.txt 로 제외)
실행 (cnc-wiki 폴더에서): python erp\\probe_queue_erp.py
"""
import sys, os, io, json
from datetime import date, timedelta
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pandas as pd
import machine_queue as mq
from trico_client import TricoClient

OUT = io.StringIO()
def P(*a):
    s = " ".join(str(x) for x in a); print(s); OUT.write(s + "\n")

fr = (date.today() - timedelta(days=120)).strftime('%Y-%m-%d')
c = TricoClient()
df = c.query('sdb100_jae_g10', {'@to_dt': '', '@fr_dt': fr, '@chk_detail': '1', '@co_cd': '01', '@f_so_no': None,
     '@f_so_bs': "'01','10'", '@f_cust_cd': None, '@f_cust2_cd': None, '@f_itm_cd': None, '@f_so_rid': None,
     '@f_stat_bc': '', '@f_order_nm': None, '@f_rmks': None, '@f_cust_nm': None})
try:   # generate.load_hold_orders 와 같은 형식
    _h = json.load(open(os.path.join(HERE, 'hold_orders.json'), encoding='utf-8'))
    holds = {str(h['so_no']): str(h.get('reason', '보류')) for h in _h.get('holds', []) if h.get('so_no')}
except Exception:
    holds = {}
_fr = date.fromisoformat(fr)
wl = [r for r in mq.load_worklog(_fr) if r['date'] >= _fr]
ew = mq.fetch_erp_worked(df, fr, P, client=c)
q0 = mq.build_queue(df, holds, worklog=wl)
q1 = mq.build_queue(df, holds, worklog=wl, erp_worked=ew)
P(f"\n[실행] {date.today()} · 수주 품목 {len(df)}행 · 작업일지 {len(wl)}줄 · 보류 {len(holds)}건")
P(f"  ERP 붙임: {q1.get('erp_worked')}")
for m in ('FG', 'GX7'):
    P(f"  {m}: 엑셀만 {q0[m]['n']}품목 {q0[m]['qty']}개 → 엑셀+ERP {q1[m]['n']}품목 {q1[m]['qty']}개 (−{q0[m]['qty'] - q1[m]['qty']}개)")
P(f"  가공 완료로 빠진 품목: {q0['worklog']['ground_items']} → {q1['worklog']['ground_items']}")
k = lambda it: (it['so_no'], it['itm'], it['coat'])
for m in ('FG', 'GX7'):
    a = {k(it): it for it in q0[m]['items']}; b = {k(it): it for it in q1[m]['items']}
    ch = [(key, a[key]['rest'], b[key]['rest'] if key in b else 0) for key in a if key not in b or b[key]['rest'] != a[key]['rest']]
    P(f"\n■ {m} — ERP 로 줄거나 빠진 품목 {len(ch)}개 (수주번호 · 품목 · 코팅 · 남은 수량 엑셀만 → 엑셀+ERP)")
    for key, x, y in sorted(ch)[:40]:
        P(f"  {key[0]} | {key[1][:30]:<30} | {key[2] or '-':<6} | {x} → {y}")
# 2026-10-23 추가: 엑셀 입력을 멈춘 뒤의 모습 — 작업일지 없이 ERP 만으로 만든 목록(q2)을 엑셀만(q0)과 견준다
q2 = mq.build_queue(df, holds, worklog=None, erp_worked=ew)
P("\n[ERP 만 (엑셀 입력 중단 후 모습)]")
for m in ('FG', 'GX7'):
    P(f"  {m}: 엑셀만 {q0[m]['n']}품목 {q0[m]['qty']}개 · ERP만 {q2[m]['n']}품목 {q2[m]['qty']}개 · 엑셀+ERP {q1[m]['n']}품목 {q1[m]['qty']}개")
for m in ('FG', 'GX7'):
    a = {k(it): it for it in q0[m]['items']}; b = {k(it): it for it in q2[m]['items']}
    more = [(key, a[key]['rest'] if key in a else 0, b[key]['rest']) for key in b if key not in a or a[key]['rest'] < b[key]['rest']]
    less = [(key, a[key]['rest'], b[key]['rest'] if key in b else 0) for key in a if key not in b or b[key]['rest'] < a[key]['rest']]
    P(f"\n■ {m} — ERP만이면 더 남는 품목 {len(more)}개 (엑셀엔 가공, ERP 실적엔 없음 · 남은 수량 엑셀만 → ERP만)")
    for key, x, y in sorted(more)[:40]:
        P(f"  {key[0]} | {key[1][:30]:<30} | {key[2] or '-':<6} | {x} → {y}")
    P(f"■ {m} — ERP만이면 덜 남는 품목 {len(less)}개 (ERP 실적엔 있고 엑셀엔 없음)")
    for key, x, y in sorted(less)[:40]:
        P(f"  {key[0]} | {key[1][:30]:<30} | {key[2] or '-':<6} | {x} → {y}")
open(os.path.join(HERE, 'probe_queue_erp_result.txt'), 'w', encoding='utf-8').write(OUT.getvalue())
P("\n결과 파일: erp/probe_queue_erp_result.txt — 실행했다고 알려 주시면 Cowork 가 읽습니다.")
