#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
품목 정가 조회 — Fiddler 캡처로 조회 이름을 확정하고 정가 열만 꺼낸다 (2026-11-13 신설)
═══════════════════════════════════════════════════════════════════════════
목적
  마이다스툴 몰(midastool.co.kr) 정가가 ERP 정가와 같은지 대조한다.
  (계기: 고칠 곳 게시판 #351~#365 — 정가 이상 14건, 2026-11-13 올림)

🔴 가격 차단 예외 — 좁게만 연다 (decisions 2026-11-13)
  - trico_client.query() 의 가격 열 차단은 기본값 그대로 둔다. 이 스크립트만 block_price=False 로 부른다.
  - 꺼낸 뒤 바로 「품번 · 품명 · 규격 · 정가」 열만 남긴다. 단가 · 할인 · 매입가 · 금액 열은 버린다.
  - 결과는 git 추적 제외 폴더에만 쓴다: wiki/_private/erp_item_price/  (조회 설정 spec.json 도 여기)
  - 예약 작업에 넣지 않는다. 경준님 PC 에서 손으로만 실행한다.
  - 정가는 대외비가 아니다(CLAUDE.md §4-1). 실거래 단가는 대외비 — 그래서 열을 골라 남긴다.

조회 이름(workSet)은 추측하지 않는다 — 2026-09-04 후보 추측 17건 전패, Fiddler 캡처만이 확실한 길.

실행 순서 (cnc-wiki 폴더에서, PowerShell)
  ① Fiddler 로 ERP 품목 화면 조회 1회를 캡처 → 요청 Raw 전체를 outputs\\erp_capture_item_price.txt 로 저장
  ② python erp/probe_item_price.py --parse
       캡처를 해석해 wiki/_private/erp_item_price/spec.json 을 만든다(조회 이름 · 파라미터 · 매크로).
  ③ python erp/probe_item_price.py --columns
       ERP 에 1회 조회해 「행 수 + 열 이름」만 보여 준다. 값은 출력하지 않는다(가격 열은 이름만).
     (2026-11-13 캡처 확정: 조회 이름 DMA100P_g10 — 경준님이 연 품목 화면, 파라미터 20개)
     🔴 PowerShell 에서는 @ 로 시작하는 값을 반드시 따옴표로 감싼다 — 맨 @ 는 스플래팅으로 읽혀 빈 값이 된다.
        예) --set "@itm_cd=KER%"   --each-prefix "@itm_cd"
  ④ python erp/probe_item_price.py --price-col <정가 열 이름> --each-prefix "@itm_cd"
       KER · SP1Q · KUD · MTD · SK · KD · 3ALPE · 245-0618 · NPU13 로 시작하는 품목만 남겨
       wiki/_private/erp_item_price/erp_item_price_YYYYMMDD.csv 로 저장한다.
  ⑤ python erp/probe_item_price.py --compare "outputs\\06.마이다스 검수\\site_price_YYYYMMDD.csv"
       사이트 CSV 열: board_no, site_code, site_code2, site_name, site_price (사이트 값은 Cowork 가 브라우저로 모아 둔다)
       ④ 결과와 사이트 정가를 품번으로 맞춰 대조표를 만든다(outputs\\06.마이다스 검수\\정가대조_YYYYMMDD.csv).

성격
  🟢 읽기 전용 — FillDataSetEx 조회만. 등록 · 수정 · 삭제 없음.
  🔴 0행이면 크게 알린다 — 오타난 workSet 은 예외 없이 0행을 돌려준다(2026-09 「조용한 실패」).
"""
import sys, re, json, argparse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


def _today() -> str:
    """파일명 날짜는 KST 기준(리눅스 VM 의 date.today() 는 UTC 라 하루 어긋날 수 있다)."""
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d")

sys.path.insert(0, str(Path(__file__).parent))

BASE     = Path(__file__).resolve().parent.parent
PRIV_DIR = BASE / "wiki" / "_private" / "erp_item_price"
SPEC     = PRIV_DIR / "spec.json"
CAPTURE  = BASE / "outputs" / "erp_capture_item_price.txt"
CMP_DIR  = BASE / "outputs" / "06.마이다스 검수"

PREFIXES = ["KER", "SP1Q", "KUD", "17.5_", "MTD", "SK10", "SK16", "KD", "3ALPE", "1503ALPE", "245-0618",
            "NPU13", "CABPF", "C-ABPF", "245-04134", "290-00966", "245-0583"]   # 게시판 #351~#369 대상
CODE_CANDIDATES = ["itm_cd", "itm_no", "item_cd", "itm_code", "part_no"]
NAME_CANDIDATES = ["itm_nm", "item_nm", "itm_name"]
SPEC_CANDIDATES = ["itm_spec", "spec", "itm_std", "std"]


# ── 캡처 해석 ───────────────────────────────────────────────────────────────
def _tag(block: str, name: str):
    m = re.search(rf"<(?:\w+:)?{name}\b[^>]*?(?:/>|>(.*?)</(?:\w+:)?{name}>)", block, re.S)
    if not m:
        return None
    return m.group(1) if m.group(1) is not None else ""


def _unesc(s: str) -> str:
    return (s.replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&amp;", "&"))


def parse_capture(text: str) -> list:
    """캡처 원문에서 DataCon 별 {workset, params(순서 유지), macro} 목록을 돌려준다."""
    i = text.find("<")
    body = text[i:] if i >= 0 else text
    out = []
    for dc in re.findall(r"<(?:\w+:)?DataCon\b.*?</(?:\w+:)?DataCon>", body, re.S):
        ws = _tag(dc, "workSet_CD")
        macro = {}
        for kv in re.findall(r"<(?:\w+:)?KeyValueOfstringstring>(.*?)</(?:\w+:)?KeyValueOfstringstring>", dc, re.S):
            k, v = _tag(kv, "Key"), _tag(kv, "Value")
            if k is not None:
                macro[_unesc(k)] = _unesc(v or "")
        params = []
        for sa in re.findall(r"<(?:\w+:)?SQLArray>(.*?)</(?:\w+:)?SQLArray>", dc, re.S):
            name = _tag(sa, "ParamaterName")
            vm = re.search(r"<(?:\w+:)?ParamaterValue\b([^>]*?)(/>|>(.*?)</(?:\w+:)?ParamaterValue>)", sa, re.S)
            if vm is None or "DBNull" in vm.group(1):
                val = None
            else:
                val = _unesc(vm.group(3) or "")
            params.append([_unesc(name or ""), val])
        out.append({"workset": _unesc(ws or ""), "params": params, "macro": macro})
    return out


def cmd_parse(capture: Path, pick: str = None):
    if not capture.exists():
        sys.exit(f"[중단] 캡처 파일이 없습니다: {capture}")
    raw = capture.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "cp949"):
        try:
            text = raw.decode(enc)
            if "<" in text:
                break
        except UnicodeDecodeError:
            continue
    cons = [c for c in parse_capture(text) if c["workset"]]
    if not cons:
        sys.exit("[중단] 캡처에서 workSet_CD 를 찾지 못했습니다. Fiddler 「요청」 쪽 Raw 전체를 저장했는지 확인하세요.")
    print(f"캡처 안의 조회 {len(cons)}개:")
    for n, c in enumerate(cons, 1):
        print(f"  {n}. {c['workset']}  (파라미터 {len(c['params'])}개)")
    if len(cons) > 1 and not pick:
        sys.exit("[중단] 조회가 여러 개입니다. --workset <이름> 으로 하나를 고르세요.")
    c = cons[0] if not pick else next((c for c in cons if c["workset"] == pick), None)
    if c is None:
        sys.exit(f"[중단] 캡처에 {pick} 이 없습니다.")
    PRIV_DIR.mkdir(parents=True, exist_ok=True)
    SPEC.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n저장: {SPEC.relative_to(BASE)}  (git 추적 제외 폴더)")
    print(f"조회 이름: {c['workset']}")
    print("파라미터 (캡처 순서):")
    for k, v in c["params"]:
        print(f"  {k} = {'(NULL)' if v is None else repr(v)}")
    print("\n※ 품번 칸에 값이 들어 있으면(화면에서 품번으로 조회한 경우) 다음 단계에서 --blank 로 비워 전체를 받으세요.")


# ── 조회 ────────────────────────────────────────────────────────────────────
def _load_spec() -> dict:
    if not SPEC.exists():
        sys.exit("[중단] spec.json 이 없습니다. 먼저 --parse 를 실행하세요.")
    return json.loads(SPEC.read_text(encoding="utf-8"))


def _run(spec: dict, blank: list, sets: dict = None, allow_empty: bool = False):
    import trico_client as tc
    sets = sets or {}
    unknown = [k for k in sets if k not in dict(spec["params"])]
    if unknown:
        sys.exit(f"[중단] 캡처에 없는 파라미터: {unknown}")
    params = {k: (None if k in blank else sets.get(k, v)) for k, v in spec["params"]}
    client = tc.TricoClient(macro=spec.get("macro") or None)
    df = client.query(spec["workset"], params, block_price=False)   # 🔴 이 스크립트에서만 차단 해제
    if df.empty and not allow_empty:
        sys.exit(f"[경고] 0행입니다 — 조회 이름({spec['workset']}) · 파라미터를 확인하세요. "
                 "오타난 조회 이름도 0행을 돌려줍니다(조용한 실패).")
    return df, tc.is_price_col


def _pick(cols, cands, override=None):
    if override:
        if override not in cols:
            sys.exit(f"[중단] 열 {override} 이 없습니다. --columns 로 이름을 확인하세요.")
        return override
    low = {c.lower(): c for c in cols}
    for c in cands:
        if c in low:
            return low[c]
    return None


# trico_client.is_price_col 은 「_up(단가) · _bup(매입단가) · margin」 열을 못 잡는다(2026-11-13 DMA100P_g10 실측:
# list_up · std_up · app_itm_up · std_bup · margin 이 표시 없이 통과). 이 화면 표시용으로 따로 본다.
_EXTRA_PRICE = re.compile(r"(^|_)b?up$|margin|dc_rt|bdc_rt")


def cmd_columns(blank, sets):
    df, _is = _run(_load_spec(), blank, sets)
    is_price = lambda c: _is(c) or bool(_EXTRA_PRICE.search(c.lower()))
    lines = [f"✅ {len(df):,}행 × {len(df.columns)}열 — 열 이름만 표시(값 없음)"]
    lines += [f"  {'💰' if is_price(c) else '  '} {c}" for c in df.columns]
    print("\n".join(lines))
    PRIV_DIR.mkdir(parents=True, exist_ok=True)
    (PRIV_DIR / "columns.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")   # Cowork 가 읽도록 남김(값 없음)
    print("\n💰 = 가격으로 보이는 열. 이 중 「정가」에 해당하는 열 이름 하나를 --price-col 로 넘기세요.")


def _norm(s) -> str:
    return re.sub(r"[\s\-_]", "", str(s or "")).upper()


def cmd_extract(price_col, code_col, name_col, blank, sets, each_prefix=None, tpl="{}%", tag=""):
    import pandas as pd
    spec = _load_spec()
    if each_prefix:
        # 품번 앞자리마다 따로 조회해 합친다(전체 품목을 한 번에 받으면 20 s 제한에 걸릴 수 있음)
        parts, log = [], []
        for p in PREFIXES:
            d, _ = _run(spec, blank, {**sets, each_prefix: tpl.format(p)}, allow_empty=True)
            log.append(f"{p}:{len(d)}")
            if not d.empty:
                parts.append(d)
        print("앞자리별 행 수 — " + " · ".join(log))
        if not parts:
            sys.exit("[경고] 모든 앞자리에서 0행 — --each-prefix 대상 파라미터 · --tpl 을 확인하세요.")
        df = pd.concat(parts, ignore_index=True).drop_duplicates()
    else:
        df, _ = _run(spec, blank, sets)
    if price_col not in df.columns:
        sys.exit(f"[중단] 열 {price_col} 이 없습니다. --columns 로 이름을 확인하세요.")
    cc = _pick(df.columns, CODE_CANDIDATES, code_col)
    if not cc:
        sys.exit("[중단] 품번 열을 못 찾았습니다. --code-col 로 지정하세요.")
    nc = _pick(df.columns, NAME_CANDIDATES, name_col)
    sc = _pick(df.columns, SPEC_CANDIDATES)
    keep = [c for c in (cc, nc, sc, price_col) if c]
    out = df[keep].copy()                                         # 🔴 정가 외 가격 열은 여기서 버려진다
    pref = [_norm(p) for p in PREFIXES]
    # 품번 · 규격 · 품명 중 하나라도 앞자리가 맞으면 남긴다(SK · KD 처럼 품번이 245-… 이고 규격에 SK16-11 이 있는 경우)
    hit = lambda v: any(_norm(v).startswith(p) for p in pref)
    m = out[cc].map(hit)
    for c in (sc, nc):
        if c:
            m = m | out[c].map(hit)
    out = out[m]
    out = out.rename(columns={cc: "erp_code", price_col: "erp_list_price",
                              **({nc: "erp_name"} if nc else {}), **({sc: "erp_spec"} if sc else {})})
    PRIV_DIR.mkdir(parents=True, exist_ok=True)
    path = PRIV_DIR / f"erp_item_price_{_today()}{('_' + tag) if tag else ''}.csv"
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"✅ 대상 품목 {len(out):,}행 저장: {path.relative_to(BASE)}  (전체 {len(df):,}행 중)")
    if out.empty:
        print("[경고] 대상 0행 — 품번 열이 맞는지(--code-col) 확인하세요.")


# ── 대조 ────────────────────────────────────────────────────────────────────
def _num(v):
    try:
        return float(str(v).replace(",", "").replace("원", "").strip())
    except ValueError:
        return None


def cmd_compare(site_csv: Path, erp_csv: Path = None):
    import pandas as pd
    if erp_csv is None:
        files = sorted(PRIV_DIR.glob("erp_item_price_????????.csv"))
        if not files:
            sys.exit("[중단] ERP 정가 파일이 없습니다. 먼저 --price-col 단계를 실행하세요.")
        erp_csv = files[-1]
    site = pd.read_csv(site_csv, dtype=str, encoding="utf-8-sig")
    erp  = pd.read_csv(erp_csv,  dtype=str, encoding="utf-8-sig")
    erp["_k"]  = erp["erp_code"].map(_norm)
    dup = erp[erp["_k"].duplicated(keep=False)]
    eidx = erp.drop_duplicates("_k").set_index("_k")
    # 사이트 품번 → 없으면 사이트 두 번째 코드(ERP 품목코드로 보이는 값)로 맞춘다
    def key(r):
        for c in ("site_code", "site_code2"):
            k = _norm(r.get(c)) if c in r and isinstance(r.get(c), str) else ""
            if k and k in eidx.index:
                return k
        return _norm(r.get("site_code"))
    site["_k"] = site.apply(key, axis=1)
    m = site.merge(eidx.reset_index(), on="_k", how="left")

    def judge(r):
        s, e = _num(r.get("site_price")), _num(r.get("erp_list_price"))
        if pd.isna(r.get("erp_code")):
            return "ERP에 없음"
        if s is None and e is None:
            return "둘 다 정가 없음"
        if s is None:
            return "사이트 정가 없음"
        if e is None:
            return "ERP 정가 없음"
        return "같음" if abs(s - e) < 0.5 else "다름"

    m["판정"] = m.apply(judge, axis=1)
    cols = [c for c in ("board_no", "site_code", "site_name", "site_price",
                        "erp_code", "erp_name", "erp_list_price", "판정") if c in m.columns]
    out = m[cols]
    path = CMP_DIR / f"정가대조_{_today()}.csv"
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"✅ 대조 {len(out)}행 → {path.relative_to(BASE)}")
    print(out["판정"].value_counts().to_string())
    if not dup.empty:
        print(f"[주의] ERP 쪽에 정규화 후 같은 품번이 {dup['_k'].nunique()}개 있습니다(첫 행으로 대조).")


def main():
    ap = argparse.ArgumentParser(description="품목 정가 조회 (캡처 → 열 확인 → 추출 → 대조)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--parse", action="store_true", help="캡처 해석 → spec.json")
    g.add_argument("--columns", action="store_true", help="열 이름만 보기")
    g.add_argument("--price-col", help="정가 열 이름 → 대상 품목 CSV 저장")
    g.add_argument("--compare", help="사이트 정가 CSV 경로 → 대조표")
    ap.add_argument("--capture", default=str(CAPTURE))
    ap.add_argument("--workset", help="캡처에 조회가 여러 개일 때 고르기")
    ap.add_argument("--blank", default="", help="비울 파라미터(쉼표 구분), 예: @itm_cd,@itm_nm")
    ap.add_argument("--set", default="", help="파라미터 값 바꾸기(쉼표 구분), 예: @itm_cd=KER%%")
    ap.add_argument("--each-prefix", help="품번 앞자리마다 이 파라미터에 넣어 따로 조회, 예: @itm_cd")
    ap.add_argument("--tpl", default="{}%", help="--each-prefix 값 틀(기본 {}%%)")
    ap.add_argument("--tag", default="", help="결과 파일 이름 꼬리표(덮어쓰기 방지), 예: spec")
    ap.add_argument("--code-col"); ap.add_argument("--name-col")
    ap.add_argument("--erp-csv")
    a = ap.parse_args()
    blank = [b.strip() for b in a.blank.split(",") if b.strip()]
    sets = dict(x.split("=", 1) for x in a.set.split(",") if "=" in x)
    sets = {k.strip(): v for k, v in sets.items()}
    if a.parse:
        cmd_parse(Path(a.capture), a.workset)
    elif a.columns:
        cmd_columns(blank, sets)
    elif a.price_col:
        cmd_extract(a.price_col, a.code_col, a.name_col, blank, sets, a.each_prefix, a.tpl, a.tag)
    else:
        cmd_compare(Path(a.compare), Path(a.erp_csv) if a.erp_csv else None)


if __name__ == "__main__":
    main()
