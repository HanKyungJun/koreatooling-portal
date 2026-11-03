# -*- coding: utf-8 -*-
"""재연마 수주 품목 상세(chk_detail=1) 조회 가능 여부 점검 — 읽기 전용 (2026-09-28, Cowork)

목적: 장비별 투입 목록 자동 생성을 위해, 수주 1건에 여러 품목이 있을 때
      (예: "2날/평/12mm/초경/밑날/일반 코팅 외 21종") 품목별 행을 받을 수 있는지 확인한다.
- ERP 에 쓰지 않는다. 조회만 한다.
- 가격 컬럼은 trico_client 기본 동작(block_price=True)으로 제거된다.
실행: python erp\\probe_so_detail.py
"""
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trico_client import TricoClient
import pandas as pd

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_colwidth", 40)

fr = (date.today() - timedelta(days=60)).strftime("%Y-%m-%d")
cl = TricoClient()
base = {
    "@to_dt": "", "@fr_dt": fr, "@co_cd": "01", "@f_so_no": None,
    "@f_so_bs": "'01','10'", "@f_cust_cd": None, "@f_cust2_cd": None,
    "@f_itm_cd": None, "@f_so_rid": None, "@f_stat_bc": "", "@f_order_nm": None,
    "@f_rmks": None, "@f_cust_nm": None,
}
h = cl.query("sdb100_jae_g10", dict(base, **{"@chk_detail": "0"}))
d = cl.query("sdb100_jae_g10", dict(base, **{"@chk_detail": "1"}))
print(f"[기간] {fr} ~ 오늘")
print(f"[헤더 chk_detail=0] {len(h)}행 / 수주번호 {h['so_no'].nunique() if 'so_no' in h else '?'}건")
print(f"[상세 chk_detail=1] {len(d)}행 / 수주번호 {d['so_no'].nunique() if 'so_no' in d else '?'}건")
print("[상세 컬럼]", list(d.columns))
multi = h[h.get("itm_nm", pd.Series(dtype=str)).astype(str).str.contains(" 외 ")] if "itm_nm" in h else h.iloc[0:0]
if len(multi) and "so_no" in d:
    so = str(multi.iloc[0]["so_no"])
    print(f"\n[다품목 수주 예시] {so} — 헤더 품목명: {multi.iloc[0]['itm_nm']}")
    print(d[d["so_no"].astype(str) == so].head(30).to_string())
else:
    print("\n[다품목 수주 예시] 없음 — 상세 앞 10행:")
    print(d.head(10).to_string())
