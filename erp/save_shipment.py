# -*- coding: utf-8 -*-
"""월 출하 저장 — ERP 재연마 출하등록(lem120_jae_g00, 상세) 을 erp/snapshot/shipment_YYYY-MM.csv 로 저장 (2026-11-10 신설, Cowork)

왜: Cowork(리눅스 VM)는 ERP 에 직접 접속할 수 없다(403). PC 자동 실행이 전월 출하를 파일로 남기면
    월초 점검 ⑥ 이 scripts/ship_month_close.py 로 출하현황 xlsx 를 채운다(decisions 2026-11-10 (1) · (2)).
근거: 같은 조회의 2026-09 값이 TricoERP export 와 전부 일치(출고 1,358 · 출고합계 1,423 · 연마불가 65 · 293행 · 29곳) [실측 검증]

  python erp\\save_shipment.py            KST 1 ~ 5일에만 전월을 저장(그 밖의 날은 바로 끝남) — daily_and_upload.bat 에서 호출
  python erp\\save_shipment.py 2026-10    그 달을 저장(수동)

- 읽기 전용 조회. 가격 · 금액 열은 trico_client 기본 차단 + 저장 직전 is_price_col 로 한 번 더 뺀다.
- 1 ~ 5일 동안은 실행마다 덮어쓴다(말일 늦은 입력 반영). 결과 한 줄을 출력(run.log 로 감).
- 실패해도 종료 코드 0 — 일일 자동 실행을 멈추지 않는다.
"""
import sys, os, json
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
args = [a for a in sys.argv[1:] if not a.startswith("-")]
if args:
    ym = args[0]
else:
    if now.day > 5:
        print(f"[save_shipment] {now:%Y-%m-%d %H:%M} KST - skip (day > 5)")
        sys.exit(0)
    prev = now.replace(day=1) - timedelta(days=1)
    ym = f"{prev:%Y-%m}"
try:
    import calendar
    import pandas as pd
    from trico_client import TricoClient, is_price_col
    y, m = int(ym[:4]), int(ym[5:7])
    fr, to = f"{ym}-01", f"{ym}-{calendar.monthrange(y, m)[1]:02d}"
    df = TricoClient().query("lem120_jae_g00", {
        "@to_dt": to, "@fr_dt": fr, "@co_cd": "01",
        "@f_out_bs": None, "@f_de_bc": None, "@f_sal_bc": None, "@f_mov_no": None,
        "@f_cust_cd": None, "@f_rmks": None, "@chk_detail": "1",
        "@f_itm_cd": None, "@f_cust_nm": None,
    })
    need = {"cust_nm", "mov_qty", "mov_own_qty", "out_dt"}
    miss = need - set(map(str, df.columns))
    if miss:
        raise RuntimeError(f"missing columns {sorted(miss)}")
    df = df[[c for c in df.columns if not is_price_col(str(c))]]
    base = os.path.join(HERE, "snapshot")
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, f"shipment_{ym}.csv")
    df.to_csv(path + ".tmp", index=False, encoding="utf-8-sig")
    os.replace(path + ".tmp", path)
    own = pd.to_numeric(df["mov_own_qty"], errors="coerce").fillna(0).sum()
    tot = pd.to_numeric(df["mov_qty"], errors="coerce").fillna(0).sum()
    meta = dict(saved_kst=f"{now:%Y-%m-%d %H:%M:%S}", fr_dt=fr, to_dt=to, rows=int(len(df)),
                out_own=float(own), out_total=float(tot), customers=int(df["cust_nm"].nunique()))
    with open(os.path.join(base, f"shipment_{ym}.meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(f"[save_shipment] {now:%Y-%m-%d %H:%M} KST - {ym} saved: {len(df)} rows, out {own:,.0f} / total {tot:,.0f}, customers {meta['customers']}")
except Exception as e:
    print(f"[save_shipment] {now:%Y-%m-%d %H:%M} KST - {ym} FAILED: {type(e).__name__}: {str(e)[:150]}")
sys.exit(0)
