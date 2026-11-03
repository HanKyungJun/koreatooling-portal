#!/usr/bin/env python3
"""
현황판용 ERP 데이터 탐색
────────────────────────
3단계(사내 현황판에 ERP 붙이기)의 0번 작업.
대조 코드를 쓰려면 컬럼 이름과 값의 형태를 먼저 알아야 한다.

실행: python erp/inspect_for_dashboard.py
읽기 전용. 파일을 쓰지 않는다.
"""
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from trico_client import TricoClient
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)

FIRST = date.today().replace(day=1).strftime("%Y-%m-%d")
TODAY = date.today().strftime("%Y-%m-%d")

c = TricoClient()


def show(title, fn, **kw):
    print()
    print("=" * 78)
    print(f"  {title}")
    print("=" * 78)
    try:
        df = fn(**kw)
    except Exception as e:
        print(f"  ❌ 조회 실패: {str(e)[:200]}")
        return None

    print(f"  {len(df)}행 / {len(df.columns)}열")
    if len(df) == 0:
        print("  (0행 — 이 기간에 데이터가 없거나 파라미터가 다름)")
        return df

    print()
    print("  컬럼 / 결측 / 고유값 / 샘플값")
    print("  " + "-" * 74)
    for col in df.columns:
        nn  = df[col].isna().sum()
        nu  = df[col].nunique()
        smp = df[col].dropna().astype(str).head(1).tolist()
        smp = smp[0][:28] if smp else ""
        print(f"  {col:16} 결측{nn:4}  고유{nu:4}  예: {smp}")

    # 수량으로 보이는 컬럼 합계 — 현황판 KPI 후보
    print()
    print("  숫자 컬럼 합계 (KPI 후보)")
    print("  " + "-" * 74)
    found = False
    for col in df.columns:
        v = pd.to_numeric(df[col], errors="coerce")
        if v.notna().sum() >= max(1, len(df) * 0.5):
            print(f"  {col:16} 합계 {v.sum():>12,.1f}   평균 {v.mean():>10,.2f}")
            found = True
    if not found:
        print("  (숫자로 읽히는 컬럼 없음)")

    print()
    print("  샘플 2행")
    print(df.head(2).to_string())
    return df


print(f"조회 기간: {FIRST} ~ {TODAY}")

show(f"1) 생산실적  PPC120_g00   ← 현황판 KPI(FAST/GX7 수량·가동시간)의 대체 후보",
     c.생산실적, fr_dt=FIRST, to_dt=TODAY)

show(f"2) 재연마 출하  lem120_jae_g00   ← 업체별 출하 차트의 대체 후보",
     c.출하, fr_dt=FIRST)

show(f"3) 재연마 수주  sdb100_jae_g10   ← 「오늘 할 일」(납기·잔량) 신규 블록용",
     c.수주, fr_dt=FIRST)

print()
print("=" * 78)
print("  이 출력을 붙여넣어 주시면 대조 코드를 작성합니다.")
print("  ※ 현황판 현재 값(엑셀 기준): 9월 누계 FAST 130 / GX7 48 / 합계 178 (3일 실적)")
print("=" * 78)
