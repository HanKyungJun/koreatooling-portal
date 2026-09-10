#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
재연마 A/S 코드 마스터 확보 — 탐침 + 수기매핑 대장 생성기
═══════════════════════════════════════════════════════════════════════════
목적
  `SDB117_g10` 이 돌려주는 값이 전부 코드(`SD200000`·`JA110DR`·`CS510200` …)라
  현황판에 한글로 띄울 수 없다. 이 스크립트는 **매핑을 스스로 만들어내지 않고**,
  아래 3가지를 실측으로 확인·정리한다.

  1단계  응답에 **테이블이 몇 개** 들어오는지 본다.
         → `trico_client._parse_dataset()` 은 diffgram 안의 모든 테이블을
           한 리스트로 **평탄화**한다. 콤보박스용 코드 테이블이 이미 함께
           오고 있다면 지금은 데이터 행과 섞여 버려지고 있다는 뜻이다.
           (그럴 경우 여기서 코드 마스터가 공짜로 나온다)
  2단계  실제로 **쓰이고 있는 코드만** 열별로 뽑아 대장 CSV 를 만든다.
         → 전체 마스터가 아니라 사용 중인 값만이므로 수기 매핑 분량이 크게 줄고,
           각 코드에 건수·예시(수주번호·거래처)를 붙여 화면 대조가 쉬워진다.
  3단계  코드 마스터 workSet 후보를 **소수만** 찔러본다.
         → ⚠️ 2026-09-04 교훈: 후보 추측은 이미 한 번 빗나갔다(17건 전부 실패,
           실제 답 `SDB117_g10` 은 Fiddler 캡처로 나왔다). 그래서 3단계는
           **보조**이며, 실패해도 정상이다. 확실한 길은 Fiddler 재캡처다.

성격
  🟢 **읽기 전용** — `FillDataSetEx` 조회만 한다. 등록·수정·삭제 없음.
  🟢 단가·금액 컬럼은 `trico_client.query()` 가 차단한다(이 화면엔 애초에 없음).
  ⚠️ 거래처명은 사내 기록이라 CSV 에 남는다. **대외 문서로 낼 때는 A/B/C 익명화.**

실행
  python erp/probe_code_master.py                 # 전체(1→2→3단계)
  python erp/probe_code_master.py --from 2025-01-01
  python erp/probe_code_master.py --no-probe      # 3단계 생략
산출
  outputs/erp_code_ledger_YYYYMMDD.csv            # 수기 매핑 대장(UTF-8 BOM)
"""
import sys, re, gzip, time, argparse
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent))
import trico_client as tc
from trico_client import TricoClient

# ── 코드가 들어오는 열 (2026-09-04 decisions.md (2) 기준 17열 중) ──────────────
CODE_COLS = [
    "stat_bc",        # 진행상태   SD200000 요청(미처리) / SD200100 처리
    "rtn_bc",         # 반송방법   CS510200 경동화물  ※「A/S 사유」가 아니다
    "jae_qty",        # 날수       JA1002 2날
    "jae_shape",      # 형상       JA110DR 드릴
    "jae_shank",      # 샹크경     JA1206 6이하 / JA1208 8이하 / JA12010 10이하
    "jae_angle",      # R
    "jae_material",   # 재질       JA1401 초경
    "jae_side",       # 공정       JA1701 밑날
    "jae_coating",    # 코팅       JA15001 일반
]
# 이미 확인된 것 — 대장에 미리 채워 넣어 중복 확인을 줄인다 (출처: trico_client 독스트링)
KNOWN = {
    ("stat_bc",      "SD200000"): "요청(미처리)",
    ("stat_bc",      "SD200100"): "처리",
    ("rtn_bc",       "CS510200"): "경동화물",
    ("jae_qty",      "JA1002"):   "2날",
    ("jae_shape",    "JA110DR"):  "드릴",
    ("jae_shank",    "JA1206"):   "6이하",
    ("jae_shank",    "JA1208"):   "8이하",
    ("jae_shank",    "JA12010"):  "10이하",
    ("jae_material", "JA1401"):   "초경",
    ("jae_side",     "JA1701"):   "밑날",
    ("jae_coating",  "JA15001"):  "일반",
}

AS_WORKSET  = "SDB117_g10"
CONTROL_OK  = "sdb100_jae_g10"     # 존재 확정
CONTROL_BAD = "zzz999_nope_g99"    # 존재하지 않음

# 3단계 후보 — 근거를 적어둔다. 근거 없는 것은 넣지 않는다.
CANDIDATES = [
    # SDB117 과 같은 계열의 다른 그리드 번호 (같은 화면의 콤보 소스가 여기 붙는 경우가 있다)
    "SDB117_g00", "SDB117_g20", "SDB117_g01",
    # 공통코드 조회로 흔히 쓰이는 이름 (근거 없음 — 순수 추측, 실패해도 정상)
    "com100_g00", "cmm100_g00", "bas100_g00", "code100_g00",
]


def raw_call(client, work_set, params):
    """HTTP 상태와 무관하게 본문을 돌려준다 (500 의 SOAP fault 를 버리지 않는다)."""
    env = client._envelope(client._data_con_xml(work_set, params)).encode("utf-8")
    try:
        r = client.session.post(
            tc.SVC_URL, data=env,
            headers={"SOAPAction": '"http://tempuri.org/ITricoService/FillDataSetEx"'},
            timeout=20)
    except Exception as e:
        return None, f"[전송실패] {type(e).__name__}: {e}", ""
    body = r.content
    try:
        body = gzip.decompress(body)
    except Exception:
        pass
    text = body.decode("utf-8", errors="replace")
    fault  = re.search(r"<[^>]*faultstring[^>]*>(.*?)</", text, re.S)
    detail = re.search(r"<[^>]*ExceptionMessage[^>]*>(.*?)</", text, re.S)
    msg = fault.group(1).strip() if fault else ""
    if detail:
        msg += (" | " if msg else "") + detail.group(1).strip()
    if not msg:
        msg = "(fault 메시지 없음)" if r.status_code != 200 else "(정상 응답)"
    return r.status_code, re.sub(r"\s+", " ", msg)[:300], text


def decode_payload(text):
    """FillDataSetExResult(base64+gzip) 를 풀어 실제 DataSet XML 을 돌려준다."""
    b64 = re.search(r'<[^>]*Result[^>]*>([A-Za-z0-9+/=\s]+)</[^>]*Result>', text)
    if not b64:
        return text
    import base64
    data = base64.b64decode(b64.group(1).strip())
    try:
        data = gzip.decompress(data)
    except Exception:
        pass
    return data.decode("utf-8", errors="replace")


def step1_tables(client, fr_dt):
    """1단계 — 응답 안의 테이블 개수·이름·행수를 센다."""
    from xml.etree import ElementTree as ET
    print("=" * 74)
    print("1단계) 응답 테이블 구조 — 코드 테이블이 함께 오고 있는지 확인")
    print("=" * 74)
    params = {"@fr_dt": fr_dt, "@to_dt": "", "@so_no": "", "@cust_cd": "",
              "@stat_bc": "", "@order_man": "", "@opt_show": "2"}
    st, msg, text = raw_call(client, AS_WORKSET, params)
    if st != 200:
        print(f"  [실패] HTTP {st} | {msg}")
        return None
    xml_str = decode_payload(text)

    # 스키마에 선언된 테이블 이름
    schema_tables = re.findall(r'<xs:element name="([^"]+)">\s*<xs:complexType>', xml_str)
    ns_diffgr = "urn:schemas-microsoft-com:xml-diffgram-v1"
    root = ET.fromstring(xml_str)
    diffgram = root.find(f'.//{{{ns_diffgr}}}diffgram')
    if diffgram is None:
        print("  ⚠️ diffgram 이 없다 — 데이터셋이 비어 있거나 형식이 다르다.")
        return None

    tables = {}
    for child in diffgram:
        if child.tag.split("}")[-1].lower() == "schema":
            continue
        for row_el in child:
            name = row_el.tag.split("}")[-1]
            tables.setdefault(name, []).append(
                {el.tag.split("}")[-1]: el.text for el in row_el})

    print(f"  스키마 선언 테이블: {schema_tables if schema_tables else '(추출 실패)'}")
    print(f"  실제 수신 테이블 {len(tables)}종:")
    for name, rows in tables.items():
        cols = sorted({c for r in rows for c in r})
        print(f"    - {name:22} {len(rows):5}행  {len(cols):3}열")
        print(f"      열: {', '.join(cols[:14])}{' …' if len(cols) > 14 else ''}")

    if len(tables) > 1:
        print()
        print("  \U0001F534 테이블이 2종 이상이다 — `_parse_dataset()` 은 이것을 한 DataFrame 으로")
        print("     평탄화하므로 지금은 서로 섞여 있다. 코드 목록이 여기 있으면 그대로 쓰면 된다.")
        print("     → `query()` 사용처의 행수 해석도 함께 재확인해야 한다.")
    else:
        print()
        print("  \U0001F7E2 테이블 1종 — 코드 목록은 이 응답에 없다. 2·3단계로 간다.")
    return tables


def step2_ledger(client, fr_dt, out_dir):
    """2단계 — 실제 사용 중인 코드만 열별로 모아 대장 CSV 를 만든다."""
    import pandas as pd
    print()
    print("=" * 74)
    print(f"2단계) 사용 중인 코드 수집 — fr_dt={fr_dt} 이후, opt_show 1·2·3 합집합")
    print("=" * 74)
    frames = []
    for v in ("1", "2", "3"):
        try:
            df = client.재연마AS(fr_dt=fr_dt, opt_show=v)
            print(f"  opt_show={v}  {len(df):5}행  {df['so_no'].nunique() if len(df) else 0:4}건")
            if len(df):
                frames.append(df)
        except Exception as e:
            print(f"  opt_show={v}  실패: {str(e)[:90]}")
        time.sleep(0.4)
    if not frames:
        print("  수집 0행 — 대장을 만들 수 없다.")
        return None

    all_df = pd.concat(frames, ignore_index=True).drop_duplicates()
    print(f"  합집합: {len(all_df)}행 / {all_df['so_no'].nunique()}건")

    recs = []
    for col in CODE_COLS:
        if col not in all_df.columns:
            print(f"  ⚠️ 열 없음: {col}")
            continue
        vc = all_df[col].dropna().astype(str).str.strip()
        vc = vc[vc != ""]
        for code, cnt in vc.value_counts().items():
            sample = all_df[all_df[col].astype(str).str.strip() == code].iloc[0]
            recs.append({
                "열":       col,
                "코드":     code,
                "한글명":   KNOWN.get((col, code), ""),      # 빈칸 = 확인 필요
                "건수":     int(cnt),
                "예시_수주번호": sample.get("so_no", ""),
                "예시_거래처":   sample.get("cust_nm", ""),
                "예시_비고":     (str(sample.get("jae_rmks", "") or "")[:40]),
                "확인상태": "확인됨" if (col, code) in KNOWN else "확인 필요",
            })
    led = pd.DataFrame(recs).sort_values(["열", "건수"], ascending=[True, False])

    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"erp_code_ledger_{date.today():%Y%m%d}.csv"
    led.to_csv(out, index=False, encoding="utf-8-sig")   # BOM — 엑셀에서 한글 정상

    todo = (led["확인상태"] == "확인 필요").sum()
    print()
    print(f"  ✅ 대장 저장: {out}")
    print(f"     총 {len(led)}개 코드 / **확인 필요 {todo}개** (이미 확인 {len(led)-todo}개)")
    print()
    print("  열별 확인 필요 개수:")
    for col, g in led.groupby("열"):
        n = (g["확인상태"] == "확인 필요").sum()
        print(f"    {col:14} {n:3}개 / 전체 {len(g):3}개")
    print()
    print("  ★ 화면(생산 > 생산관리 > 재연마A/S 현황)에서 「예시_수주번호」 를 조회하면")
    print("    그 행의 한글값이 그대로 보인다 → 「한글명」 칸만 채우면 매핑이 끝난다.")
    return led


def step3_probe(client):
    """3단계 — 코드 마스터 workSet 후보 (보조 수단, 실패해도 정상)."""
    print()
    print("=" * 74)
    print("3단계) 코드 마스터 workSet 후보 — ⚠️ 보조 수단")
    print("=" * 74)
    print("  2026-09-04 교훈: 후보 추측은 이미 17건 전부 빗나갔고, 정답은 Fiddler 로 나왔다.")
    print("  여기서 아무것도 안 나오는 것이 기본값이다. 실패를 실패로 읽는다.")
    print()
    _, mb, _ = raw_call(client, CONTROL_OK,  {})
    _, mc, _ = raw_call(client, CONTROL_BAD, {})
    print(f"  B. 있는 화면 {CONTROL_OK:20} | {mb[:90]}")
    print(f"  C. 없는 화면 {CONTROL_BAD:20} | {mc[:90]}")
    if mb == mc:
        print("  ==> B 와 C 가 같다 — 메시지로는 구분 불가. 아래는 참고용일 뿐이다.")
    print()
    hits = []
    for i, ws in enumerate(CANDIDATES, 1):
        st, msg, _ = raw_call(client, ws, {})
        mark = ""
        if mb != mc and msg == mb:
            mark = "  <<< '있는 화면' 과 동일"
            hits.append(ws)
        print(f"  [{i}/{len(CANDIDATES)}] {ws:16} HTTP {st}  {msg[:80]}{mark}")
        time.sleep(0.4)
    print()
    if hits:
        print(f"  후보 {len(hits)}건: {', '.join(hits)}")
        print("  → 알려주시면 파라미터를 맞춰 실제 조회까지 진행합니다.")
    else:
        print("  후보 없음. 추측을 더 늘리지 않는다.")
    print()
    print("  ✅ 확실한 길 — Fiddler 재캡처 (2026-09-04 에 SDB117 을 찾아낸 그 방법):")
    print("     ① Fiddler 를 켜고 ERP 클라이언트에서 「재연마A/S 현황」 화면을 연다")
    print("     ② 조회를 누르지 말고 **콤보박스(형상·재질·코팅·반송방법)를 하나씩 펼친다**")
    print("     ③ 펼칠 때 뜨는 FillDataSetEx 요청의 `workSet_CD` 와 파라미터를 캡처한다")
    print("        (콤보 목록은 보통 화면 진입 시 한 번에 미리 받아온다 — ①에서 이미")
    print("         여러 건이 잡혔다면 그 요청들의 workSet_CD 를 전부 보내주시면 됩니다)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="fr_dt", default="2025-01-01",
                    help="조회 시작일 (기본 2025-01-01 — 코드 커버리지를 넓힌다)")
    ap.add_argument("--no-probe", action="store_true", help="3단계 생략")
    a = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    client = TricoClient()

    print("재연마 A/S 코드 마스터 확보 — 읽기 전용 탐침")
    print(f"대상 workSet: {AS_WORKSET}   조회 시작일: {a.fr_dt}")
    print()
    tables = step1_tables(client, a.fr_dt)
    step2_ledger(client, a.fr_dt, root / "outputs")
    if not a.no_probe:
        step3_probe(client)
    print()
    print("=" * 74)
    print("끝. 산출물은 outputs/ 에 있습니다. ERP 에 쓰기 동작은 하지 않았습니다.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
