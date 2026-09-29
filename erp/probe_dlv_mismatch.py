# -*- coding: utf-8 -*-
"""수주 머리(chk_detail=0) 납기 vs 품목 상세(chk_detail=1) 납기 불일치 점검 — 읽기 전용 (2026-09-29, Cowork)

배경: 「오늘 할 일」은 머리 납기, 「장비별 투입 목록」은 품목 납기를 쓴다.
      신우툴스 라핑코너 16MM 이 한쪽은 09-24, 다른 쪽은 09-14 로 나왔다.
- ERP 에 쓰지 않는다. 조회만 한다. 가격 컬럼은 trico_client 기본 차단.
- 결과: 화면 출력 + erp/probe_dlv_mismatch_result.txt (거래처명 포함 — .gitignore 등재)
실행: python erp\\probe_dlv_mismatch.py
"""
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trico_client import TricoClient
import pandas as pd

fr = (date.today() - timedelta(days=120)).strftime("%Y-%m-%d")
cl = TricoClient()
base = {
    "@to_dt": "", "@fr_dt": fr, "@co_cd": "01", "@f_so_no": None,
    "@f_so_bs": "'01','10'", "@f_cust_cd": None, "@f_cust2_cd": None,
    "@f_itm_cd": None, "@f_so_rid": None, "@f_stat_bc": "", "@f_order_nm": None,
    "@f_rmks": None, "@f_cust_nm": None,
}
h = cl.query("sdb100_jae_g10", dict(base, **{"@chk_detail": "0"}))
d = cl.query("sdb100_jae_g10", dict(base, **{"@chk_detail": "1"}))

def kst(s):
    return pd.to_datetime(s, errors="coerce", utc=True).dt.tz_convert("Asia/Seoul").dt.date

for x in (h, d):
    x["so_no"] = x["so_no"].astype(str)
    x["dlv"] = kst(x["dlv_dt"])
    x["rest"] = (pd.to_numeric(x["so_qty"], errors="coerce").fillna(0)
                 - pd.to_numeric(x.get("out_qty"), errors="coerce").fillna(0)).clip(lower=0)

hh = h.groupby("so_no").agg(cust=("cust_nm", "first"), h_dlv=("dlv", "first"),
                            h_itm=("itm_nm", "first"), h_rest=("rest", "sum"))
dd = d.groupby("so_no").agg(d_min=("dlv", "min"), d_max=("dlv", "max"),
                            n=("itm_nm", "size"), d_rest=("rest", "sum"))
m = hh.join(dd, how="inner")
bad = m[(m["h_dlv"] != m["d_min"]) | (m["h_dlv"] != m["d_max"])]
open_bad = bad[bad["d_rest"] > 0]

lines = [f"[기간] {fr} ~ {date.today()}  (실행 {pd.Timestamp.now(tz='Asia/Seoul'):%Y-%m-%d %H:%M} KST)",
         f"수주 {len(hh)}건 · 품목 {len(d)}행 · 머리/품목 납기 불일치 {len(bad)}건 (그중 미출하 잔량 있는 것 {len(open_bad)}건)",
         ""]
for so, r in bad.sort_values("h_dlv").iterrows():
    lines.append(f"{so} | {r['cust']} | 머리 {r['h_dlv']} | 품목 {r['d_min']}~{r['d_max']} ({r['n']}행) "
                 f"| 잔량 머리 {int(r['h_rest'])} / 품목 {int(r['d_rest'])} | {str(r['h_itm'])[:40]}")
sw = d[d["cust_nm"].astype(str).str.contains("신우", na=False) & (d["rest"] > 0)]
lines += ["", "── 신우툴스 미출하 품목 행 ──"]
for _, r in sw.iterrows():
    lines.append(f"{r['so_no']} | 수주일 {kst(pd.Series([r['so_dt']]))[0]} | 품목 납기 {r['dlv']} | "
                 f"머리 납기 {hh['h_dlv'].get(r['so_no'])} | {r['itm_nm']} | 잔량 {int(r['rest'])}")
out = "\n".join(lines)
print(out)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe_dlv_mismatch_result.txt"), "w", encoding="utf-8") as f:
    f.write(out + "\n")
