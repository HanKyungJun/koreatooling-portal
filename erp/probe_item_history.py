#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
품목 수불(구매 · 판매) 이력 조회 — 정가 이상 품목이 실제로 거래됐는지 가른다 (2026-11-13 신설)
═══════════════════════════════════════════════════════════════════════════
목적
  ERP 정가 이상 · 같은 규격 중복 품번 515개(게시판 #351~#369)가 실제로 사고판 적이 있는지 본다.
  이력 있음 → 정가 고침 대상 · 이력 없음 → 정리(사용 중지 · 통합) 후보.
  대상 목록: wiki/_private/erp_item_price/history_targets_20261113.csv

근거 캡처 (2026-11-13 한경준님 Fiddler — ERP 품목조회 DMA100P 에서 KER20090 행 선택)
  한 요청에 조회 9개가 함께 나간다. 모두 @itm_id(BigInt, 품목 내부 번호 — KER20090 = 117684 로 캡처)
    DMA100P_f10 · g20 · g30 · g35(@itm_id, @cust_cd=DBNull) · g37 · g40 · g55 · g57 · g50(@co_cd='01', @itm_id)
  화면 아래 탭: 창고별 재고현황 · 최종 매입/매출/견적 조회 · 수불 조회 · 재고/입출고예정 조회
  → 이 9개 중 어느 것이 「수불 조회」인지는 아직 모른다(추측하지 않음) → ① --columns 로 가린다.

🔴 가격 · 거래처
  - 수불 화면에는 매입단가 · 매입금액 · 매출단가 · 매출금액이 있다(대외비). 열 이름만 보고 값은 쓰지 않는다.
  - trico_client.query() 를 쓰지 않고 직접 보내지만, 받자마자 trico_client.is_price_col 로 가격 열을 버린다.
  - 거래처 · 작성자 값은 화면 · 파일에 쓰지 않는다. 결과는 날짜 · 구분 · 건수 · 수량만.
  - 결과는 git 추적 제외 폴더에만: wiki/_private/erp_item_history/
  - 읽기 전용(FillDataSetEx 조회만). 예약 작업에 넣지 않는다.

실행 (cnc-wiki 폴더, PowerShell)
  ① python erp/probe_item_history.py --columns
       KER20090 으로 9개 조회를 하나씩 보내 「행 수 · 열 이름 · 구분 값 · 날짜 범위」만 보여 준다.
       → wiki/_private/erp_item_history/columns.txt (Cowork 가 읽고 수불 조회 이름 · 열 이름을 정한다)
  ② python erp/probe_item_history.py --history
       대상 515개 품목마다 수불(g40) + 최종 매출(g35) · 최종 견적(g37)을 모아
       wiki/_private/erp_item_history/history_YYYYMMDD.csv 로 저장한다(날짜 · 구분 · 건수 · 수량 · 거래처 수만).
       조회 약 1,560번(품목당 3번) + 품목 찾기 19번 — 몇 분 걸린다.
"""
import sys, re, csv, json, argparse, collections
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import trico_client as tc

BASE      = Path(__file__).resolve().parent.parent
PRICE_DIR = BASE / "wiki" / "_private" / "erp_item_price"
OUT_DIR   = BASE / "wiki" / "_private" / "erp_item_history"
SPEC_G10  = PRICE_DIR / "spec.json"                       # 품목 검색(DMA100P_g10) 캡처 — itm_cd → itm_id 찾기용
TARGETS   = PRICE_DIR / "history_targets_20261113.csv"

# 캡처 그대로(순서 변경 금지). ("long", 값) = BigInt, None = DBNull, str = NVarChar
DETAIL_SETS = [
    ("DMA100P_f10", [("@itm_id", "ITM")]),
    ("DMA100P_g20", [("@itm_id", "ITM")]),
    ("DMA100P_g30", [("@itm_id", "ITM")]),
    ("DMA100P_g35", [("@itm_id", "ITM"), ("@cust_cd", None)]),
    ("DMA100P_g37", [("@itm_id", "ITM")]),
    ("DMA100P_g40", [("@itm_id", "ITM")]),
    ("DMA100P_g55", [("@itm_id", "ITM")]),
    ("DMA100P_g57", [("@itm_id", "ITM")]),
    ("DMA100P_g50", [("@co_cd", "01"), ("@itm_id", "ITM")]),
]
EXTRA_PRICE = re.compile(r"(^|_)b?up$|amt|margin|dc_rt|bdc_rt|_prc|price")
HIDE_VALUES = re.compile(r"cust|emp|reg|user|wr_|_id$|mnm|rnm|nm2|rmks|addr|tel", re.I)   # 값을 보이지 않을 열(rnm = 작성자, 11-13 추가)

# ── ① --columns 결과로 정한 것 (2026-11-13 13:42 KST, KER20090 실측) ───────────────
#   g40 = 「수불 조회」: dt(일자) · bc_nm(구분: 매출 …) · out_qty · 소계 줄(no = 「12개월 소계」 등, dt 비어 있음)
#         화면 소계가 12 · 6 · 3개월뿐이고 g40 행도 2026-01 ~ 09 만 → 최근 12개월 범위로 보인다(추정 — 확인 필요)
#         매입 줄 수량 열 이름은 KER20090 에 매입이 없어 못 봄 → 이름이 _qty 로 끝나는 열을 모두 더한다
#   g35 = 최종 매출내역 · g37 = 최종 견적내역 (2026-11-13 한경준님 화면 확인). 거래처별 1행 · last_dt(마지막 날짜)
#         KER20090: g35 19행(2022-10-02 ~ 2026-09-22) · g37 8행(2023-09-12 ~ 2026-09-21)
#   판정: 매출(수불 매출 또는 g35) → 「판매 있음」 / 수불 매입만 → 「매입만」 / g37 견적만 → 「견적만」 / 없음 → 「이력 없음」
#         ⚠️ 12개월보다 오래된 매입은 볼 곳이 없다(최종 매입내역 조회 이름은 캡처에 없음) → 「이력 없음」도 오래된 매입은 있을 수 있음
SUBUL, LAST_A, LAST_B = "DMA100P_g40", "DMA100P_g35", "DMA100P_g37"


def _today():
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d")


def is_price(c: str) -> bool:
    return tc.is_price_col(c) or bool(EXTRA_PRICE.search(c.lower()))


def _param(name, value):
    if value is None:
        val = f'<a:ParamaterValue i:type="b:DBNull" xmlns:b="{tc.NS_SYS}"/>'
        typ, size = "NVarChar", 0
    elif isinstance(value, int):
        val = f'<a:ParamaterValue i:type="b:long" xmlns:b="{tc.NS_XSD}">{value}</a:ParamaterValue>'
        typ, size = "BigInt", 0
    else:
        val = f'<a:ParamaterValue i:type="b:string" xmlns:b="{tc.NS_XSD}">{tc._esc(value)}</a:ParamaterValue>'
        typ, size = "NVarChar", len(value)
    return ('<a:SQLArray><a:ParamaterDataTable i:nil="true"/><a:ParamaterDirection>Input</a:ParamaterDirection>'
            f'<a:ParamaterName>{name}</a:ParamaterName><a:ParamaterPrecision>0</a:ParamaterPrecision>'
            f'<a:ParamaterScale>0</a:ParamaterScale><a:ParamaterSize>{size}</a:ParamaterSize>{val}'
            f'<a:Paramatertype>{typ}</a:Paramatertype><a:Paramatertypename/></a:SQLArray>')


def run_detail(client, workset, params, itm_id):
    """조회 1개 → DataFrame (가격 열은 받자마자 버림)"""
    pxml = "".join(_param(n, itm_id if v == "ITM" else v) for n, v in params)
    dc = (f'<a:DataCon>{client._macro_xml()}<a:SqlDesc i:nil="true"/><a:cataLog/><a:cmdText i:nil="true"/>'
          f'<a:cmdType>Text</a:cmdType><a:ex i:nil="true" xmlns:b="{tc.NS_SYS}"/>'
          f'<a:oPm i:nil="true" xmlns:b="{tc.NS_SER}"/><a:oPms i:nil="true"/>'
          f'<a:sqlArray>{pxml}</a:sqlArray><a:useTransaction>false</a:useTransaction>'
          f'<a:workSet_CD>{workset}</a:workSet_CD></a:DataCon>')
    resp = client.session.post(tc.SVC_URL, data=client._envelope(dc).encode("utf-8"),
                               headers={"SOAPAction": '"http://tempuri.org/ITricoService/FillDataSetEx"'}, timeout=20)
    resp.raise_for_status()
    text = resp.content
    try:
        import gzip
        text = gzip.decompress(text)
    except Exception:
        pass
    xml = text.decode("utf-8", errors="replace")
    if "<faultstring>" in xml or "faultstring" in xml[:2000]:
        raise RuntimeError(f"{workset}: SOAP Fault")
    try:
        df = tc._parse_dataset(xml)
    except Exception as e:                       # 0행 · 데이터셋 없음도 여기로 온다
        return None, str(e)[:120]
    cols = list(df.columns)
    return df.drop(columns=[c for c in cols if is_price(c)], errors="ignore"), [c for c in cols if is_price(c)]


# 대상 515개를 모두 덮는 앞자리(2026-11-13 확인: 빠지는 품목 0). 앞자리마다 1번 조회 — 짧게 잡으면 20 s 제한에 걸린다.
PREFIXES = ["1503ALPE", "245-041", "245-055", "245-0618", "245-067", "245-07", "245-99", "290-0096",
            "850JSK", "850NPU13", "850SK", "C-ABPF12", "CABPF12", "KER20", "KER32M14", "KER40", "KER50", "KUD", "MTD"]


def item_ids(client, codes):
    """품목코드 → itm_id. 품목 검색(DMA100P_g10) 캡처 파라미터 그대로, @itm_cd 만 앞자리% 로 바꿔 보낸다."""
    spec = json.loads(SPEC_G10.read_text(encoding="utf-8"))
    want, found = set(codes), {}
    pres = [p for p in PREFIXES if any(c.upper().startswith(p.upper()) for c in codes)]
    pres += [c for c in codes if not any(c.upper().startswith(p.upper()) for p in PREFIXES)]   # 목록 밖은 품목코드 그대로
    for pre in pres:
        params = {k: v for k, v in spec["params"]}
        params["@itm_cd"] = pre + "%"
        df = client.query(spec["workset"], params)            # 기본 차단(가격 열 버림)
        if df.empty or "itm_id" not in df.columns:
            continue
        for _, r in df.iterrows():
            if r["itm_cd"] in want:
                found[r["itm_cd"]] = int(float(r["itm_id"]))
    return found


def cmd_columns(code):
    client = tc.TricoClient()
    ids = item_ids(client, [code])
    if code not in ids:
        sys.exit(f"[중단] {code} 의 itm_id 를 찾지 못했습니다.")
    itm_id = ids[code]
    lines = [f"품목 {code} · itm_id {itm_id} (캡처값 117684 와 {'같음' if itm_id == 117684 else '다름'})", ""]
    for ws, params in DETAIL_SETS:
        try:
            df, blocked = run_detail(client, ws, params, itm_id)
        except Exception as e:
            lines.append(f"■ {ws}: 오류 {e}"); continue
        if df is None:
            lines.append(f"■ {ws}: 0행 또는 데이터셋 없음 ({blocked})"); continue
        lines.append(f"■ {ws}: {len(df)}행 · 💰 버린 가격 열 {blocked}")
        for c in df.columns:
            s = df[c].dropna().astype(str)
            info = ""
            if c.lower().endswith("_dt") or "date" in c.lower():
                d = s[s.str.match(r"\d{4}-\d{2}-\d{2}")]
                info = f"  날짜 {d.min()[:10]} ~ {d.max()[:10]}" if len(d) else ""
            elif not HIDE_VALUES.search(c) and 0 < s.nunique() <= 8 and s.str.len().max() <= 12:
                info = "  값: " + " · ".join(sorted(s.unique()))
            lines.append(f"    {c}{info}")
        lines.append("")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "columns.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"→ 저장: {OUT_DIR / 'columns.txt'}  (Cowork 에 「돌렸어」라고만 알려 주세요)")


def _sum(series) -> float:
    try:
        return float(series.astype(float).fillna(0).sum())
    except Exception:
        return 0.0


def _last(client, ws, itm_id):
    """g35 · g37 — 거래처 수 · 마지막 거래일(거래처 값은 쓰지 않는다)"""
    df, _ = run_detail(client, ws, dict(DETAIL_SETS)[ws], itm_id)
    if df is None or df.empty or "last_dt" not in df.columns:
        return 0, ""
    d = df["last_dt"].dropna().astype(str).str[:10]
    d = d[d.str.match(r"\d{4}-\d{2}-\d{2}")]
    return len(df), (d.max() if len(d) else "")


def cmd_history():
    targets = list(csv.DictReader(open(TARGETS, encoding="utf-8-sig")))
    codes = [t["품목코드"] for t in targets]
    client = tc.TricoClient()
    ids = item_ids(client, codes)
    print(f"itm_id 찾음 {len(ids)} / {len(codes)}")
    rows, kinds_seen, qty_seen = [], collections.Counter(), set()
    for n, t in enumerate(targets, 1):
        code = t["품목코드"]
        r = {"게시판": t["게시판"], "품목코드": code}
        if code not in ids:
            r["판정"] = "품목 못 찾음"; rows.append(r); continue
        iid = ids[code]
        df, _ = run_detail(client, SUBUL, dict(DETAIL_SETS)[SUBUL], iid)
        if df is not None and not df.empty and "dt" in df.columns:
            df = df[df["dt"].astype(str).str.match(r"\d{4}-\d{2}-\d{2}", na=False)]      # 소계 줄 제외
            qcols = [c for c in df.columns if c.lower().endswith("_qty")]
            qty_seen.update(qcols)
            key = "bc_nm" if "bc_nm" in df.columns else "gubun"
            for kind, g in df.groupby(key):
                kinds_seen[kind] += 1
                r[f"수불_{kind}_건수"] = len(g)
                r[f"수불_{kind}_수량"] = sum(_sum(g[c]) for c in qcols)
                r[f"수불_{kind}_마지막"] = g["dt"].astype(str).str[:10].max()
        r["최종매출_거래처수"], r["최종매출_마지막"] = _last(client, LAST_A, iid)
        r["최종견적_거래처수"], r["최종견적_마지막"] = _last(client, LAST_B, iid)
        sold = r["최종매출_거래처수"] or any(k.startswith("수불_매출") for k in r)
        bought = any(k.startswith("수불_") and not k.startswith("수불_매출") for k in r)
        r["판정"] = ("판매 있음" if sold else "매입만" if bought
                     else "견적만" if r["최종견적_거래처수"] else "이력 없음")
        rows.append(r)
        if n % 50 == 0:
            print(f"  {n} / {len(targets)}")
    cols = (["게시판", "품목코드", "판정"] + sorted({k for r in rows for k in r if k.startswith("수불_")})
            + ["최종매출_거래처수", "최종매출_마지막", "최종견적_거래처수", "최종견적_마지막"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / f"history_{_today()}.csv"
    with open(p, "w", encoding="utf-8-sig", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    jud = collections.Counter(r["판정"] for r in rows)
    print(f"✅ {len(rows)}개 품목 저장: {p}")
    print(f"   판정 {dict(jud)} · 수불 구분 값 {dict(kinds_seen)} · 수량 열 {sorted(qty_seen)}")
    print("   (Cowork 에 「돌렸어」라고만 알려 주세요)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--columns", action="store_true")
    ap.add_argument("--code", default="KER20090")
    ap.add_argument("--history", action="store_true")
    a = ap.parse_args()
    if a.columns:
        cmd_columns(a.code)
    elif a.history:
        cmd_history()
    else:
        ap.print_help()
