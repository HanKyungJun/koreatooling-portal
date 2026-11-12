# -*- coding: utf-8 -*-
"""ERP 재연마 출하등록(lem120_jae_g00) 조회 확인 — 읽기 전용 (2026-11-10, Cowork)

배경: 10월 마감에 쓸 출하현황을 TricoERP 화면 export 없이 자동으로 받을 수 있는지 확인한다.
      9월 export(raw/출하현황/출하현황_9월.xlsx) 합계 행 = 출고합계 1,423 · 연마불가 65 · 출고 1,358 (294행, 2026-09-01 ~ 09-30).
      이 조회의 9월 값이 위 세 숫자와 맞으면, 같은 조회로 10월을 받아 마감에 쓴다.

확인하는 것
  1) 9월 · 10월 행 수, 컬럼 이름(가격 컬럼 제외)
  2) 숫자 컬럼별 9월 합계 — 1,423 / 65 / 1,358 과 맞는 컬럼이 어느 것인가
  3) chk_detail 0 이 맞지 않으면 1 로 다시 조회(가격 컬럼은 자동 차단)
  4) 9월 · 10월 결과를 erp/snapshot/shipment_YYYY-MM.csv 로 저장(.gitignore 의 erp/snapshot/ 로 제외)

- ERP 에 쓰지 않는다. 가격·금액 컬럼은 저장 · 출력하지 않는다(trico_client.is_price_col).
- 결과: 화면 출력 + erp/probe_shipment_result.txt (.gitignore 의 erp/probe_*_result.txt 로 제외)
실행 (cnc-wiki 폴더에서): python erp\\probe_shipment.py
"""
import sys, os, io
from datetime import datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pandas as pd
from trico_client import TricoClient, is_price_col

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)
OUT = io.StringIO()
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s); OUT.write(s + "\n")

REF = {1423: "출고합계", 65: "연마불가", 1358: "출고"}
MONTHS = {"2026-09": ("2026-09-01", "2026-09-30"), "2026-10": ("2026-10-01", "2026-10-31")}
SNAP = os.path.join(HERE, "snapshot")

c = TricoClient()
P(f"[실행] {datetime.now():%Y-%m-%d %H:%M} · 재연마 출하등록 lem120_jae_g00 조회 확인 (읽기 전용)")


def fetch(fr, to, detail):
    return c.query("lem120_jae_g00", {
        "@to_dt": to, "@fr_dt": fr, "@co_cd": "01",
        "@f_out_bs": None, "@f_de_bc": None, "@f_sal_bc": None, "@f_mov_no": None,
        "@f_cust_cd": None, "@f_rmks": None, "@chk_detail": detail,
        "@f_itm_cd": None, "@f_cust_nm": None,
    })


def num_sums(df):
    res = {}
    for col in df.columns:
        if is_price_col(str(col)):
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        if s.notna().sum() >= max(1, len(df) * 0.8):
            res[str(col)] = s.sum()
    return res


best = None
for detail in ("0", "1"):
    P(f"\n■ chk_detail={detail}")
    try:
        sep = fetch(*MONTHS["2026-09"], detail)
    except Exception as e:
        P(f"  9월 조회 실패: {str(e)[:200]}")
        continue
    keep = [col for col in sep.columns if not is_price_col(str(col))]
    P(f"  9월 {len(sep)}행 · 컬럼 {len(sep.columns)}개(가격 제외 {len(keep)}개)")
    P("  컬럼:", ", ".join(map(str, keep)))
    sums = num_sums(sep)
    hit = {}
    for col, v in sums.items():
        mark = ""
        for ref, name in REF.items():
            if abs(v - ref) < 0.5:
                mark = f"  ← export「{name}」{ref:,} 와 일치"
                hit[name] = col
        P(f"    {col:20} 합계 {v:,.0f}{mark}")
    for col in keep:
        if "dt" in str(col).lower():
            s = sep[col].dropna().astype(str)
            if len(s):
                P(f"    날짜 {col:15} {s.min()[:10]} ~ {s.max()[:10]}")
    P(f"  일치: {hit if hit else '없음'}")
    if len(hit) >= 2 or (hit and best is None):
        best = (detail, keep, hit)
    if len(hit) == 3:
        break

if best is None:
    P("\n✖ 9월 export 숫자와 맞는 조합을 찾지 못함 — 결과 파일을 Cowork 에 알려 주세요.")
else:
    detail, keep, hit = best
    P(f"\n■ 저장 (chk_detail={detail} · 일치 {list(hit)})")
    os.makedirs(SNAP, exist_ok=True)
    for ym, (fr, to) in MONTHS.items():
        try:
            df = fetch(fr, to, detail)
        except Exception as e:
            P(f"  {ym} 조회 실패: {str(e)[:200]}")
            continue
        df = df[[col for col in df.columns if not is_price_col(str(col))]]
        path = os.path.join(SNAP, f"shipment_{ym}.csv")
        df.to_csv(path, index=False, encoding="utf-8-sig")
        sums = num_sums(df)
        line = " · ".join(f"{name} {sums.get(col, 0):,.0f}" for name, col in hit.items())
        P(f"  {ym}: {len(df)}행 · {line} → erp/snapshot/shipment_{ym}.csv")

open(os.path.join(HERE, "probe_shipment_result.txt"), "w", encoding="utf-8").write(OUT.getvalue())
P("\n결과 파일: erp/probe_shipment_result.txt — 「실행했어」라고만 알려 주세요(파일은 Cowork 가 직접 읽습니다).")
