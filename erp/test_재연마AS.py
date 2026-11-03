#!/usr/bin/env python3
"""
재연마 A/S 현황 — 연동 검증
──────────────────────────
trico_client.재연마AS() 가 실제로 조회되는지 확인한다.
실행: python erp/test_재연마AS.py

읽기 전용. 등록/수정/삭제 없음.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from trico_client import TricoClient

c = TricoClient()

print("=" * 70)
print("1) 대조군 — 기존 화면이 정상인지 먼저 (조용한 성공 방지)")
print("=" * 70)
df0 = c.수주(fr_dt="2026-09-01")
print(f"  재연마수주: {len(df0)}행 / {len(df0.columns)}열")
print()

print("=" * 70)
print("2) 신규 — 재연마 A/S 현황 (SDB117_g10)")
print("=" * 70)
df = c.재연마AS(fr_dt="2026-09-01")
print(f"  결과: {len(df)}행 / {len(df.columns)}열")
print()
print("  컬럼 목록:")
for i, col in enumerate(df.columns, 1):
    print(f"    {i:2}. {col}")
print()

if len(df) == 0:
    print("  ⚠️ 0행입니다. 아래 둘 중 하나이며 서로 다릅니다:")
    print("     - 9월 A/S 실적이 실제로 없다  (정상)")
    print("     - 파라미터가 화면과 달라 안 걸린다 (문제)")
    print("     -> 기간을 넓혀 재확인합니다.")
    print()
    df2 = c.재연마AS(fr_dt="2026-01-01")
    print(f"  2026-01-01 이후 전체: {len(df2)}행")
    if len(df2) > 0:
        print("  -> 데이터는 있습니다. 9월만 없는 것이니 정상입니다.")
        df = df2
    else:
        print("  -> 연중 0행. opt_show 값이나 파라미터를 재확인해야 합니다.")

if len(df) > 0:
    print("=" * 70)
    print("3) 샘플 3행")
    print("=" * 70)
    import pandas as pd
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    print(df.head(3).to_string())

print()
print("=" * 70)
print("완료. 위 컬럼 목록을 그대로 붙여넣어 주시면 현황판 반영을 설계합니다.")
print("=" * 70)
