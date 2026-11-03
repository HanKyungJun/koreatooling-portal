#!/usr/bin/env python3
"""
@opt_show 값의 의미 확인
────────────────────────
화면 라디오버튼: 처리 / 미처리 / 전체
캡처된 값은 "2" 이고, 그때 화면은 [미처리] 가 선택돼 있었다.
1/2/3 을 각각 조회해 어느 값이 무엇인지 실측으로 확정한다.

실행: python erp/check_optshow.py
읽기 전용.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from trico_client import TricoClient

c = TricoClient()
FR = "2026-01-01"

print("=" * 66)
print(f"2026년 재연마 A/S — @opt_show 값별 비교 (fr_dt={FR})")
print("=" * 66)

results = {}
for v in ["1", "2", "3", "0", ""]:
    try:
        df = c.재연마AS(fr_dt=FR, opt_show=v)
        n_case = df["so_no"].nunique() if len(df) else 0
        stats  = sorted(df["stat_bc"].dropna().unique()) if len(df) else []
        results[v] = (len(df), n_case, stats)
        print(f"  opt_show={v!r:4}  {len(df):4}행  {n_case:3}건  stat_bc={stats}")
    except Exception as e:
        print(f"  opt_show={v!r:4}  실패: {str(e)[:80]}")

print()
print("-" * 66)
print("판정")
print("-" * 66)
base = results.get("2")
if base:
    print(f"  캡처된 값 '2' = {base[1]}건, stat_bc={base[2]}")
    for v, (rows, cases, stats) in results.items():
        if v == "2":
            continue
        if cases > base[1]:
            print(f"  -> opt_show={v!r} 가 더 많다({cases}건). '전체' 후보.")
        elif cases < base[1]:
            print(f"  -> opt_show={v!r} 가 더 적다({cases}건). 다른 필터.")
        else:
            print(f"  -> opt_show={v!r} 는 '2' 와 동일({cases}건).")

print()
print("★ 화면에서 [전체] 를 눌렀을 때의 건수와 대조하면 확정됩니다.")
print("=" * 66)
