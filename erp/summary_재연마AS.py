#!/usr/bin/env python3
"""
재연마 A/S 현황 — 규모 파악
────────────────────────────
현황판에 뭘 띄울지 정하려면 먼저 "얼마나 되는 데이터인지" 를 알아야 한다.
실행: python erp/summary_재연마AS.py

읽기 전용.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from trico_client import TricoClient
import pandas as pd

pd.set_option("display.width", 200)
c = TricoClient()

print("=" * 70)
print("2026년 전체 재연마 A/S")
print("=" * 70)
df = c.재연마AS(fr_dt="2026-01-01")
print(f"  명세 행: {len(df)}행")

if len(df) == 0:
    print("  0행 — 파라미터 재확인 필요")
    sys.exit(0)

# so_no 하나에 여러 행(사양별 명세)이 붙는 구조다. 건수는 so_no 기준으로 센다.
n_case = df["so_no"].nunique()
print(f"  A/S 건수(so_no 기준): {n_case}건")
print(f"  총 수량: {df['qty'].astype(float).sum():,.0f}개")
print()

print("-" * 70)
print("월별 추이 (so_dt 기준)")
print("-" * 70)
d = df.copy()
d["ym"] = pd.to_datetime(d["so_dt"], errors="coerce", utc=True).dt.tz_convert("Asia/Seoul").dt.strftime("%Y-%m")
m = d.groupby("ym").agg(건수=("so_no", "nunique"),
                        명세행=("so_no", "size"),
                        수량=("qty", lambda x: float(pd.to_numeric(x, errors="coerce").sum())))
print(m.to_string())
print()

print("-" * 70)
print("진행상태 stat_bc 분포  (코드 의미는 확인 필요)")
print("-" * 70)
print(df.groupby("stat_bc")["so_no"].nunique().sort_values(ascending=False).to_string())
print()

print("-" * 70)
print("rtn_bc 분포  (A/S 사유 코드로 추정 — 확인 필요)")
print("-" * 70)
print(df.groupby("rtn_bc")["so_no"].nunique().sort_values(ascending=False).to_string())
print()

print("-" * 70)
print("거래처별 (상위 10)")
print("-" * 70)
print(df.groupby("cust_nm")["so_no"].nunique().sort_values(ascending=False).head(10).to_string())
print()

print("-" * 70)
print("결측 현황 — 화면에 띄울 수 있는 항목인지 판단용")
print("-" * 70)
for col in df.columns:
    null_n = df[col].isna().sum()
    print(f"  {col:14} 결측 {null_n:3}/{len(df)}  고유값 {df[col].nunique()}")

print()
print("=" * 70)
print("이 출력을 붙여넣어 주시면 현황판 설계로 넘어갑니다.")
print("=" * 70)
