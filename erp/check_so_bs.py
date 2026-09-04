#!/usr/bin/env python3
"""
수주() 의 @f_so_bs 하드코딩 필터 확인
────────────────────────────────────
trico_client.수주() 는 @f_so_bs 에 "\'01\',\'10\'" 을 손으로 넣고 있다.
오늘(2026-09-04) 생산실적을 3개월간 0건으로 만든 @stat_bc 와 같은 유형이라
실제로 무엇이 걸러지는지 값을 바꿔가며 확인한다.

실행: python erp/check_so_bs.py
읽기 전용.
"""
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from trico_client import TricoClient
import pandas as pd

c  = TricoClient()
FR = "2026-08-01"        # 8월부터 — 9월은 표본이 너무 적다

def q(f_so_bs):
    return c.query("sdb100_jae_g10", {
        "@to_dt":      "",
        "@fr_dt":      FR,
        "@chk_detail": "0",
        "@co_cd":      "01",
        "@f_so_no":    None,
        "@f_so_bs":    f_so_bs,
        "@f_cust_cd":  None,
        "@f_cust2_cd": None,
        "@f_itm_cd":   None,
        "@f_so_rid":   None,
        "@f_stat_bc":  "",
        "@f_order_nm": None,
        "@f_rmks":     None,
        "@f_cust_nm":  None,
    })

CASES = [
    ("현재값  '01','10'", "'01','10'"),
    ("빈 문자열",          ""),
    ("DBNull(None)",       None),
    ("'01' 만",            "'01'"),
    ("'10' 만",            "'10'"),
]

print("=" * 72)
print(f"수주 @f_so_bs 값별 비교  (fr_dt={FR} ~)")
print("=" * 72)

res = {}
for label, v in CASES:
    try:
        df = q(v)
        n_case = df["so_no"].nunique() if len(df) else 0
        qty    = pd.to_numeric(df["so_qty"], errors="coerce").sum() if len(df) else 0
        res[label] = (len(df), n_case, qty)
        print(f"  {label:18} {len(df):5}행  {n_case:4}건  수량 {qty:8,.0f}")
    except Exception as e:
        print(f"  {label:18} 실패: {str(e)[:70]}")

print()
print("-" * 72)
base = res.get("현재값  '01','10'")
if base:
    print(f"  기준(현재 코드) = {base[1]}건 / {base[2]:,.0f}개")
    for label, (rows, cases, qty) in res.items():
        if label.startswith("현재값"):
            continue
        d = cases - base[1]
        if d > 0:
            print(f"  🔴 {label}: +{d}건 더 나옴 — 현재 필터가 {d}건을 걸러내고 있다")
        elif d < 0:
            print(f"     {label}: {d}건 (더 좁은 조건)")
        else:
            print(f"  ✅ {label}: 동일 — 필터가 실질적으로 아무것도 안 걸러냄")
print()
print("★ 8월 수주 실적은 1,123개(68행)로 이미 확정돼 있다 [decisions.md 2026-09-03 (4)].")
print("  위 수량이 그와 크게 다르면 필터가 범인이다.")
print("=" * 72)
