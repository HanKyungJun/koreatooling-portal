# -*- coding: utf-8 -*-
"""외주 매입 대조 — 수기 「생산팀 매출 현황」 시트의 매입 칸을 ERP 에서 찾는다 (2026-11-18 신설, Cowork)

목적
  매출 현황판(erp/sales_board.py)의 외주 매입은 지금 입력표에 손으로 넣는다.
  ERP 매입 화면 조회를 한 번 캡처해, 수기 시트의 25년 · 26년 11월 1 ~ 17일 매입 값이 ERP 에서 그대로 나오는지 본다.
  맞으면 현황판이 입력표 대신 ERP 에서 매입을 가져오게 바꾼다(다음 단계).

조회 이름(workSet)은 추측하지 않는다 — 2026-09-04 후보 추측 17건 전패, Fiddler 캡처만 쓴다.

실행 (cnc-wiki 폴더, PowerShell)
  ① ERP 에서 외주 매입이 보이는 화면을 열고 기간 2026-11-01 ~ 2026-11-17 로 「조회」 1번
     → Fiddler 에서 그 요청(FillDataSetEx)의 Raw 전체를 outputs\\erp_capture_purchase.txt 로 저장
  ② python erp\\probe_purchase.py --parse
       캡처를 해석해 wiki/_private/sales_board/purchase_spec.json 을 만든다(조회 이름 · 파라미터 · 매크로).
       조회가 여러 개면 목록을 보여 주고 멈춘다 → --workset <이름> 으로 하나를 고른다.
  ③ python erp\\probe_purchase.py --check
       캡처의 날짜 칸만 바꿔 「2026-11-01 ~ 17」 · 「2025-11-01 ~ 17」 두 번 조회하고,
       거래처별로 금액 열을 모두 더해 wiki/_private/sales_board/purchase_check.txt 에 쓴다(Cowork 가 읽고 시트와 대조).

🔴 금액
  - 매입 금액은 대외비(CLAUDE.md §4). 이 스크립트에서만 block_price=False 로 받고, 결과는 git 추적 제외 폴더에만 쓴다.
  - 읽기 전용(FillDataSetEx 조회만). 등록 · 수정 · 삭제 없음. 예약 작업에 넣지 않는다.
"""
import sys, re, json, argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(HERE))

OUT_DIR = BASE / "wiki" / "_private" / "sales_board"
SPEC = OUT_DIR / "purchase_spec.json"
RESULT = OUT_DIR / "purchase_check.txt"
CAPTURE = BASE / "outputs" / "erp_capture_purchase.txt"
KST = timezone(timedelta(hours=9))

PERIODS = [("26년 11월 1~17일", "2026-11-01", "2026-11-17"),
           ("25년 11월 1~17일", "2025-11-01", "2025-11-17")]
DATE_RE = re.compile(r"^(\d{4})-?(\d{2})-?(\d{2})(.*)$")
AMT_RE = re.compile(r"amt|_up$|_bup$|price|cost|금액|단가|공급|부가|합계", re.I)


# ── 캡처 해석 (probe_item_price.py 와 같은 방식) ──────────────────────────
def _tag(block, name):
    m = re.search(rf"<(?:\w+:)?{name}\b[^>]*?(?:/>|>(.*?)</(?:\w+:)?{name}>)", block, re.S)
    if not m:
        return None
    return m.group(1) if m.group(1) is not None else ""


def _unesc(s):
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&amp;", "&")


def parse_capture(text):
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
            typ = re.search(r'i:type="(?:\w+:)?(\w+)"', vm.group(1)).group(1) if vm and 'i:type="' in vm.group(1) else ""
            val = None if (vm is None or "DBNull" in vm.group(1)) else _unesc(vm.group(3) or "")
            params.append([_unesc(name or ""), val, typ])
        out.append({"workset": _unesc(ws or ""), "params": params, "macro": macro})
    return out


def cmd_parse(capture, pick=None):
    if not capture.exists():
        sys.exit(f"[중단] 캡처 파일이 없습니다: {capture}")
    raw = capture.read_bytes()
    text = ""
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
        dates = [k for k, v, _ in c["params"] if v and DATE_RE.match(v)]
        print(f"  {n}. {c['workset']}  (파라미터 {len(c['params'])}개 · 날짜 칸 {dates})")
    if len(cons) > 1 and not pick:
        sys.exit("[중단] 조회가 여러 개입니다. 날짜 칸이 있는 것을 --workset <이름> 으로 고르세요.")
    c = cons[0] if not pick else next((c for c in cons if c["workset"] == pick), None)
    if c is None:
        sys.exit(f"[중단] 캡처에 {pick} 이 없습니다.")
    nonstr = [(k, t) for k, v, t in c["params"] if v is not None and t and t.lower() != "string"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SPEC.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n저장: {SPEC.relative_to(BASE)}  (git 추적 제외 폴더)")
    print(f"조회 이름: {c['workset']}")
    for k, v, t in c["params"]:
        print(f"  {k} = {'(NULL)' if v is None else repr(v)}{'  [' + t + ']' if (v is not None and t and t.lower() != 'string') else ''}")
    if nonstr:
        print(f"\n⚠ 문자열이 아닌 파라미터 {nonstr} — trico_client 는 문자열로 보낸다. --check 가 실패하면 Cowork 에 알려 주세요.")


# ── 조회 ──────────────────────────────────────────────────────────────────
def _date_slots(params):
    """날짜 값이 든 칸 → (시작 칸, 끝 칸). 이름(fr/st/from · to/ed/end)으로, 안 되면 값 순서로."""
    ds = [(k, v) for k, v, *_ in params if v and DATE_RE.match(v)]
    if len(ds) == 1:
        # 화면에서 끝 날짜를 비우고 조회한 경우(@to_dt = '') — 이름 짝(fr → to)으로 끝 칸을 찾는다 (2026-11-18 lea110_g00 캡처)
        names = [k for k, *_ in params]
        k0 = ds[0][0]
        for cand in (k0.replace("fr_", "to_"), k0.replace("fr", "to"), k0.replace("from", "to")):
            if cand != k0 and cand in names:
                return k0, cand
        return k0, None
    if len(ds) < 1:
        return None, None
    fr = [k for k, _ in ds if re.search(r"fr|st|from|beg", k, re.I)]
    to = [k for k, _ in ds if re.search(r"to_|_to|ed_|_ed|end", k, re.I)]
    if len(fr) == 1 and len(to) == 1:
        return fr[0], to[0]
    ds.sort(key=lambda kv: DATE_RE.match(kv[1]).group(1, 2, 3))
    return ds[0][0], ds[-1][0]


def _fmt_like(sample, iso):
    m = DATE_RE.match(sample)
    y, mo, d = iso.split("-")
    sep = "-" if "-" in sample[:10] else ""
    return f"{y}{sep}{mo}{sep}{d}{m.group(4)}"


def _num(v):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def summarize(df, label, lines):
    cols = [str(c) for c in df.columns]
    lines.append(f"\n■ {label}: {len(df):,}행 × {len(cols)}열")
    if df.empty:
        lines.append("  (0행 — 이 기간 매입이 없거나 조회 조건이 다름)")
        return
    vend = next((c for c in ("cust_nm", "cust_nm2", "vend_nm", "bp_nm") if c in cols), None) or \
        next((c for c in cols if "cust" in c.lower() and "nm" in c.lower()), None)
    amt_cols = []
    for c in cols:
        if AMT_RE.search(c):
            vals = df[c].map(_num)
            if vals.notna().mean() > 0.5:
                amt_cols.append(c)
    lines.append(f"  거래처 열: {vend or '(못 찾음)'} · 금액 열: {amt_cols or '(못 찾음)'}")
    other = [c for c in cols if c not in amt_cols]
    lines.append(f"  그 밖 열: {other}")
    if not amt_cols:
        return
    import pandas as pd
    d = df.copy()
    for c in amt_cols:
        d[c] = pd.to_numeric(d[c].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
    tot = d[amt_cols].sum()
    lines.append("  전체 합: " + " · ".join(f"{c} {tot[c]:,.0f}" for c in amt_cols))
    if vend:
        g = d.groupby(vend)[amt_cols].sum()
        g["_n"] = d.groupby(vend).size()
        g = g.sort_values(amt_cols[0], ascending=False)
        lines.append(f"  거래처별 ({len(g)}곳):")
        for k, row in g.iterrows():
            lines.append(f"    {k} ({int(row['_n'])}행): " + " · ".join(f"{c} {row[c]:,.0f}" for c in amt_cols))


def cmd_check():
    if not SPEC.exists():
        sys.exit("[중단] purchase_spec.json 이 없습니다. 먼저 --parse 를 실행하세요.")
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    fr_k, to_k = _date_slots(spec["params"])
    if fr_k is None:
        sys.exit("[중단] 캡처 파라미터에 날짜 값이 없습니다 — 화면에서 기간을 넣고 조회한 요청을 캡처했는지 확인하세요.")
    import trico_client as tc
    client = tc.TricoClient(macro=spec.get("macro") or None)
    now = datetime.now(KST)
    lines = [f"[probe_purchase] {now:%Y-%m-%d %H:%M} KST · 조회 {spec['workset']} · 날짜 칸 시작 {fr_k} · 끝 {to_k}"]
    base = {k: v for k, v, *_ in spec["params"]}
    for label, fr, to in PERIODS:
        p = dict(base)
        p[fr_k] = _fmt_like(base[fr_k], fr)
        if to_k:
            p[to_k] = _fmt_like(base[to_k] if (base[to_k] and DATE_RE.match(base[to_k])) else base[fr_k], to)
        try:
            df = client.query(spec["workset"], p, block_price=False)   # 🔴 금액 열 허용 — 결과는 _private 에만
        except Exception as e:
            lines.append(f"\n■ {label}: 조회 실패 — {type(e).__name__}: {str(e)[:200]}")
            continue
        summarize(df, f"{label} ({p[fr_k]} ~ {p.get(to_k, '')})", lines)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n→ {RESULT}")


def main():
    ap = argparse.ArgumentParser(description="외주 매입 대조 (읽기 전용)")
    ap.add_argument("--parse", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--workset", help="--parse 때 조회가 여러 개면 하나 고르기")
    ap.add_argument("--capture", default=str(CAPTURE))
    a = ap.parse_args()
    if a.parse:
        cmd_parse(Path(a.capture), a.workset)
    elif a.check:
        cmd_check()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
