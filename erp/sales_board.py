# -*- coding: utf-8 -*-
"""매출 현황판 — 재연마 출하 금액 · 수량 → HTML 한 장 (2026-11-18 신설, Cowork)

경준님 PC 전용. 결과 · 입력 · 캐시는 모두 wiki/_private/sales_board/ (git 추적 제외) 에만 쓴다.
공유폴더 현황판 · dist(github.io) 로 보내지 않는다 — 금액은 대외비(CLAUDE.md §4).

  python erp\\sales_board.py                 오늘(KST) 기준으로 만들고 끝
  python erp\\sales_board.py --open          만든 뒤 브라우저로 연다 (매출현황판.bat)
  python erp\\sales_board.py 2026-11-17      기준일 지정
  python erp\\sales_board.py --py full       전년 비교를 「같은 기간(1일 ~ 기준일)」 대신 「같은 달 전체」로
  python erp\\sales_board.py --refresh       지난달 이전 캐시까지 ERP 에서 다시 받음
  python erp\\sales_board.py --offline       ERP 조회 없이 캐시만으로 (시험용)

데이터
- 매출 · 수량: ERP 재연마 출하등록 lem120_jae_g00 (chk_detail=1) — 월 출하 마감(save_shipment.py)과 같은 원본.
    매출 = mov_amt 합 (공급가로 추정 — 첫 실행 때 수기 시트와 대조해 확정. 화면 아래 「확인 필요」)
    수량 = mov_own_qty 합 (출고, 연마불가 제외) — 출고합계(mov_qty)는 참고로 같이 보인다.
- 목표 · 외주 매입: 입력.xlsx 「월별입력」 시트 (경준님이 손으로 채움 — 외주 매입 ERP 조회 이름은 아직 캡처 전).
    이익 = 매출 − 외주합계, 이익률 = 이익 ÷ 매출 (수기 「생산팀 매출 현황」 시트 계산과 같게).

🔴 가격 열 차단 예외 (decisions 2026-11-13 (2) 와 같은 방식):
   trico_client.query(..., block_price=False) 는 fetch_month() 한 곳뿐이고, 받자마자 KEEP 8열만 남긴다.
   단가(*_up) · 할인 · 거래처 코드 · 담당자 등은 버린다. 콘솔 · 파일 모두 _private 밖으로 금액을 쓰지 않는다.
"""
import sys, os, json, argparse, calendar, html as _html
from datetime import datetime, date, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)

KST = timezone(timedelta(hours=9))
OUT_DIR = os.path.join(BASE, "wiki", "_private", "sales_board")
CACHE_DIR = os.path.join(OUT_DIR, "cache")
INPUT_XLSX = os.path.join(OUT_DIR, "입력.xlsx")
OUT_HTML = os.path.join(OUT_DIR, "매출현황판.html")

WORK_SET = "lem120_jae_g00"
KEEP = ("out_dt", "cust_nm", "mov_own_qty", "mov_qty", "bad_qty", "mov_amt", "vat_amt", "tot_amt")
NEED = {"out_dt", "cust_nm", "mov_own_qty", "mov_qty", "mov_amt"}
INPUT_SHEET = "월별입력"
FIXED_COLS = ("월", "매출목표", "이익목표")   # 그 뒤 「메모」 전까지 = 외주 매입 항목
# ERP 에 그 달 출하 기록이 없을 때만 쓰는 수기 값(예: ERP 이전 달). 열 위치는 상관없음 — 이름으로 찾는다
MANUAL_COLS = {"매출(수기)": "sales_manual", "수량(수기)": "qty_manual"}


# ── 날짜 ──────────────────────────────────────────────────────────────────
def ym_of(d: date) -> str:
    return f"{d.year}-{d.month:02d}"


def month_end(ym: str) -> date:
    y, m = int(ym[:4]), int(ym[5:7])
    return date(y, m, calendar.monthrange(y, m)[1])


def prev_ym(ym: str) -> str:
    y, m = int(ym[:4]), int(ym[5:7])
    return f"{y-1}-12" if m == 1 else f"{y}-{m-1:02d}"


# ── ERP ───────────────────────────────────────────────────────────────────
def fetch_month(client, ym: str):
    import pandas as pd
    fr, to = f"{ym}-01", month_end(ym).isoformat()
    df = client.query(WORK_SET, {
        "@to_dt": to, "@fr_dt": fr, "@co_cd": "01",
        "@f_out_bs": None, "@f_de_bc": None, "@f_sal_bc": None, "@f_mov_no": None,
        "@f_cust_cd": None, "@f_rmks": None, "@chk_detail": "1",
        "@f_itm_cd": None, "@f_cust_nm": None,
    }, block_price=False)          # 🔴 금액 열 허용은 여기뿐 — 바로 아래에서 KEEP 만 남긴다
    if df is None or df.empty:
        return pd.DataFrame(columns=list(KEEP))
    df.columns = [str(c) for c in df.columns]
    miss = NEED - set(df.columns)
    if miss:
        raise RuntimeError(f"missing columns {sorted(miss)}")
    return df[[c for c in KEEP if c in df.columns]].copy()


def load_months(yms, today_ym, refresh=False, offline=False, log=print):
    """달마다 (DataFrame | None, 출처). 지난달 이전 = 캐시 우선, 이번 달 · 지난달 = 매번 ERP."""
    import pandas as pd
    os.makedirs(CACHE_DIR, exist_ok=True)
    client = None
    out = {}
    fails = 0
    last_closed = prev_ym(today_ym)
    for ym in yms:
        path = os.path.join(CACHE_DIR, f"ship_{ym}.csv")
        has = os.path.exists(path)
        closed = ym < last_closed
        if has and (offline or (closed and not refresh)):
            out[ym] = (pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna(""), "캐시")
            continue
        if offline or fails >= 2:
            out[ym] = ((pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna(""), "캐시(조회 생략)")
                       if has else (None, "조회 생략" if fails >= 2 else "없음"))
            continue
        try:
            if client is None:
                from trico_client import TricoClient
                client = TricoClient()
            df = fetch_month(client, ym)
            df.to_csv(path + ".tmp", index=False, encoding="utf-8-sig")
            os.replace(path + ".tmp", path)
            out[ym] = (df.astype(str).fillna(""), "ERP")
            fails = 0
        except Exception as e:
            fails += 1
            log(f"  [경고] {ym} ERP 조회 실패: {type(e).__name__}: {str(e)[:120]}")
            if fails == 2:
                log("  [경고] 연속 2번 실패 — 남은 달은 ERP 조회를 건너뛰고 캐시만 씀(사내망 · ERP 접속 확인)")
            if has:
                out[ym] = (pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna(""), "캐시(조회 실패)")
            else:
                out[ym] = (None, "조회 실패")
    return out


def summarize(df, upto: str = None):
    """한 달 합계. upto='YYYY-MM-DD' 이면 그날까지. 행이 0 이면 None(ERP 기록 없음)."""
    import pandas as pd
    if df is None or len(df) == 0:
        return None
    d = df.copy()
    d["_day"] = d["out_dt"].astype(str).str[:10]
    if upto:
        d = d[d["_day"] <= upto]

    def num(c):
        return pd.to_numeric(d[c], errors="coerce").fillna(0) if c in d.columns else pd.Series([0.0] * len(d))

    vat = num("vat_amt"); amt = num("mov_amt"); tot = num("tot_amt")
    return dict(
        rows=int(len(d)), amt=float(amt.sum()), tot=float(tot.sum()), vat=float(vat.sum()),
        own=float(num("mov_own_qty").sum()), qty=float(num("mov_qty").sum()), bad=float(num("bad_qty").sum()),
        cust=int(d["cust_nm"].nunique()) if "cust_nm" in d.columns else 0,
        # 검산: 행마다 공급가 + 부가세 = 합계금액 인지 (1원 이내)
        amt_check_bad=int(((amt + vat - tot).abs() > 1).sum()) if "tot_amt" in d.columns else -1,
    )


def top_customers(df, upto: str, n=10):
    import pandas as pd
    if df is None or len(df) == 0:
        return []
    d = df.copy()
    d = d[d["out_dt"].astype(str).str[:10] <= upto]
    if d.empty:
        return []
    d["amt"] = pd.to_numeric(d["mov_amt"], errors="coerce").fillna(0)
    d["own"] = pd.to_numeric(d["mov_own_qty"], errors="coerce").fillna(0)
    g = d.groupby("cust_nm", dropna=False)[["amt", "own"]].sum().sort_values("amt", ascending=False)
    total = float(g["amt"].sum()) or 1.0
    rows = [(str(k), float(v.amt), float(v.own), float(v.amt) / total) for k, v in g.head(n).iterrows()]
    rest = g.iloc[n:]
    if len(rest):
        rows.append((f"그 밖 {len(rest)}곳", float(rest["amt"].sum()), float(rest["own"].sum()),
                     float(rest["amt"].sum()) / total))
    return rows


# ── 입력표 (목표 · 외주 매입) ─────────────────────────────────────────────
def make_input_template(path, years, outs=("외주1", "외주2")):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook()
    ws = wb.active
    ws.title = INPUT_SHEET
    head = list(FIXED_COLS) + list(outs) + ["메모"] + list(MANUAL_COLS)
    ws.append(head)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="DDE6F0")
        c.alignment = Alignment(horizontal="center")
    for y in years:
        for m in range(1, 13):
            ws.append([f"{y}-{m:02d}"] + [None] * (len(head) - 1))
    for row in ws.iter_rows(min_row=2, max_col=1):
        row[0].number_format = "@"
    for i in range(2, len(head)):
        for row in ws.iter_rows(min_row=2, min_col=i, max_col=i):
            row[0].number_format = "#,##0"
    ws.column_dimensions["A"].width = 10
    for col in "BCDEFGHIJ":
        ws.column_dimensions[col].width = 14
    ws.freeze_panes = "B2"
    info = wb.create_sheet("설명")
    for line in [
        "매출 현황판 입력표 — 단위 원. 빈칸은 「입력 필요」로 표시된다.",
        "월: YYYY-MM 글자 그대로 (바꾸지 말 것).",
        "매출목표 · 이익목표: 그 달 목표.",
        "「이익목표」 다음 열부터 「메모」 앞 열까지 = 외주 매입 항목. 열 이름(업체명)은 바꿔도 되고, 열을 더 넣어도 된다.",
        "이익 = 매출(ERP 출하 금액) − 외주 매입 합계. 이익률 = 이익 ÷ 매출.",
        "이번 달 외주 매입은 그날까지 들어온 금액을 넣는다 (수기 시트와 같게).",
        "매출(수기) · 수량(수기): ERP 에 그 달 출하 기록이 없을 때만 쓴다(ERP 이전 달 등). ERP 기록이 있으면 무시된다.",
        "이 파일은 wiki/_private/ 안이라 git 에 올라가지 않는다. 다른 곳으로 복사 · 메일 금지(대외비).",
    ]:
        info.append([line])
    info.column_dimensions["A"].width = 110
    wb.save(path)


def _num(v):
    if v is None or (isinstance(v, str) and not v.strip()):
        return None
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def read_inputs(path):
    """{ym: {'sales_target','profit_target','outs':{name:val|None},'memo'}}, 외주 이름 목록"""
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True, read_only=True)
    ws = wb[INPUT_SHEET] if INPUT_SHEET in wb.sheetnames else wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    if not rows:
        return {}, []
    head = [str(h).strip() if h is not None else "" for h in rows[0]]
    try:
        i_memo = head.index("메모")
    except ValueError:
        i_memo = len(head)
    out_idx = [(i, head[i]) for i in range(len(FIXED_COLS), i_memo) if head[i] and head[i] not in MANUAL_COLS]
    man_idx = {key: head.index(name) for name, key in MANUAL_COLS.items() if name in head}
    data = {}
    for r in rows[1:]:
        if not r or r[0] is None:
            continue
        k = r[0]
        ym = k.strftime("%Y-%m") if hasattr(k, "strftime") else str(k).strip()[:7]
        if len(ym) != 7 or ym[4] != "-":
            continue
        g = lambda i: r[i] if i < len(r) else None
        data[ym] = dict(
            sales_target=_num(g(1)), profit_target=_num(g(2)),
            outs={name: _num(g(i)) for i, name in out_idx},
            memo=str(g(i_memo) or "").strip(),
            **{key: _num(g(i)) for key, i in man_idx.items()},
        )
    return data, [n for _, n in out_idx]


# ── 계산 ──────────────────────────────────────────────────────────────────
def ratio(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def outs_total(inp):
    if not inp:
        return None
    vals = [v for v in inp["outs"].values() if v is not None]
    return sum(vals) if vals else None


def month_sum(months, inputs, ym, upto=None):
    """ERP 합계. ERP 기록이 없고 입력표에 매출(수기)가 있으면 그 값(달 전체 값, manual=True)."""
    s = summarize(months[ym][0], upto=upto) if ym in months else None
    if s is None:
        inp = inputs.get(ym) or {}
        if inp.get("sales_manual") is not None:
            q = inp.get("qty_manual")
            s = dict(rows=0, amt=inp["sales_manual"], tot=0.0, vat=0.0, own=q, qty=q, bad=None, cust=0,
                     amt_check_bad=-1, manual=True)
    return s


def build(base: date, months, inputs, out_names, py_mode="full"):
    y, m = base.year, base.month
    cur_ym, py_ym = f"{y}-{m:02d}", f"{y-1}-{m:02d}"
    base_iso = base.isoformat()
    same_day = min(base.day, calendar.monthrange(y - 1, m)[1])
    py_same_iso = f"{py_ym}-{same_day:02d}"

    cur = month_sum(months, inputs, cur_ym, upto=base_iso)
    py_full = month_sum(months, inputs, py_ym)
    py_same = month_sum(months, inputs, py_ym, upto=py_same_iso)
    py = py_same if py_mode == "same" else py_full

    i_cur, i_py = inputs.get(cur_ym), inputs.get(py_ym)
    s_cur = cur["amt"] if cur else None
    s_py = py["amt"] if py else None
    o_cur, o_py = outs_total(i_cur), outs_total(i_py)
    p_cur = s_cur - o_cur if (s_cur is not None and o_cur is not None) else None
    p_py = s_py - o_py if (s_py is not None and o_py is not None) else None
    t_s = i_cur["sales_target"] if i_cur else None
    t_p = i_cur["profit_target"] if i_cur else None

    # 올해 누계 (1월 ~ 기준일) vs 전년 같은 기간
    ytd = dict(cur_amt=0.0, py_amt=0.0, cur_qty=0.0, py_qty=0.0, cur_out=0.0, py_out=0.0,
               miss_cur=[], miss_py=[], miss_out=[])
    for mm in range(1, m + 1):
        a, b = f"{y}-{mm:02d}", f"{y-1}-{mm:02d}"
        sa = month_sum(months, inputs, a, upto=base_iso if mm == m else None)
        sb = month_sum(months, inputs, b, upto=py_same_iso if mm == m else None)
        if sa: ytd["cur_amt"] += sa["amt"]; ytd["cur_qty"] += sa["own"] or 0
        else: ytd["miss_cur"].append(a)
        if sb: ytd["py_amt"] += sb["amt"]; ytd["py_qty"] += sb["own"] or 0
        else: ytd["miss_py"].append(b)
        oa, ob = outs_total(inputs.get(a)), outs_total(inputs.get(b))
        if oa is None: ytd["miss_out"].append(a)
        else: ytd["cur_out"] += oa
        if ob is None: ytd["miss_out"].append(b)
        else: ytd["py_out"] += ob

    trend = []
    for mm in range(1, 13):
        a, b = f"{y}-{mm:02d}", f"{y-1}-{mm:02d}"
        sb = month_sum(months, inputs, b)
        sa = None
        if mm <= m:
            sa = month_sum(months, inputs, a, upto=base_iso if mm == m else None)
        tg = inputs.get(a, {}).get("sales_target") if inputs.get(a) else None
        trend.append(dict(m=mm, py=sb["amt"] if sb else None, cur=sa["amt"] if sa else None,
                          partial=(mm == m and base < month_end(a)), target=tg))

    days_in = calendar.monthrange(y, m)[1]
    return dict(
        base=base, y=y, m=m, cur_ym=cur_ym, py_ym=py_ym, py_mode=py_mode, same_day=same_day,
        cur=cur, py=py, py_full=py_full, py_same=py_same,
        s_cur=s_cur, s_py=s_py, t_s=t_s, t_p=t_p, p_cur=p_cur, p_py=p_py, o_cur=o_cur, o_py=o_py,
        i_cur=i_cur, i_py=i_py, out_names=out_names,
        elapsed=base.day / days_in, days_in=days_in,
        ytd=ytd, trend=trend,
        top=top_customers(months[cur_ym][0], base_iso),
        src={k: v[1] for k, v in months.items()},
        manual=[k for k in sorted(months) if summarize(months[k][0]) is None
                and (inputs.get(k) or {}).get("sales_manual") is not None],
    )


# ── HTML ──────────────────────────────────────────────────────────────────
def won(v):
    return "—" if v is None else f"{v:,.0f}"


def pct(v):
    return "—" if v is None else f"{v*100:.1f}%"


def esc(s):
    return _html.escape(str(s))


CSS = """
:root{--bg:#f6f6f4;--card:#fff;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--line:#e4e3de;
--cur:#2a78d6;--py:#b9b7ae;--tgt:#0b0b0b;--warn:#c4262e;--ok:#1a7f37;
--g-sales:#e8f0fb;--g-profit:#e9f5f8;--g-buy:#f1f1ef;--g-qty:#f3f7e3}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.5 "Malgun Gothic","Apple SD Gothic Neo",sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:20px}
header{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap;margin-bottom:14px}
h1{font-size:22px;margin:0}h2{font-size:16px;margin:0 0 10px}
.sub{color:var(--ink2);font-size:13px}.badge{display:inline-block;border:1px solid var(--warn);color:var(--warn);
border-radius:4px;padding:1px 6px;font-size:12px;margin-left:6px}
.grid{display:grid;grid-template-columns:400px 1fr;gap:14px}@media(max-width:900px){.grid{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px}
table{border-collapse:collapse;width:100%}td,th{padding:5px 8px;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}
th{font-weight:600;text-align:left;color:var(--ink2);font-size:13px}td.n,th.n{text-align:right}
.sheet td.grp{font-weight:700;text-align:center;width:62px;border-right:1px solid var(--line)}
.sheet tr.key td{font-weight:700}.sheet .p-low{color:var(--warn);font-weight:700}.sheet .p-rate{color:var(--cur);font-weight:700}
.sales{background:var(--g-sales)}.profit{background:var(--g-profit)}.buy{background:var(--g-buy)}.qty{background:var(--g-qty)}
.need{color:var(--muted);font-style:italic}.note{color:var(--ink2);font-size:12px;margin-top:8px}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px}
.tile{border:1px solid var(--line);border-radius:8px;padding:10px 12px}.tile .k{color:var(--ink2);font-size:12px}
.tile .v{font-size:22px;font-weight:700;font-variant-numeric:tabular-nums}.tile .d{font-size:12px;color:var(--ink2)}
.legend{display:flex;gap:14px;font-size:12px;color:var(--ink2);margin:4px 0 6px}
.sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px}
#tip{position:fixed;pointer-events:none;background:#fff;border:1px solid var(--line);border-radius:6px;
padding:6px 9px;font-size:12px;box-shadow:0 2px 8px rgba(0,0,0,.12);display:none;white-space:nowrap}
details summary{cursor:pointer;color:var(--ink2);font-size:12px;margin-top:6px}
.bar{height:6px;background:var(--line);border-radius:3px;overflow:hidden}.bar i{display:block;height:100%;background:var(--cur)}
footer{color:var(--muted);font-size:12px;margin-top:16px;line-height:1.7}
"""

JS = """
const tip=document.getElementById('tip');
document.querySelectorAll('[data-tip]').forEach(el=>{
 el.addEventListener('mousemove',e=>{tip.innerHTML=el.dataset.tip;tip.style.display='block';
  const x=Math.min(e.clientX+14,window.innerWidth-tip.offsetWidth-8);tip.style.left=x+'px';tip.style.top=(e.clientY+14)+'px'});
 el.addEventListener('mouseleave',()=>{tip.style.display='none'});});
"""


def sheet_table(r):
    yy, py2 = str(r["y"])[2:], str(r["y"] - 1)[2:]
    low = lambda v: ' class="n p-low"' if (v is not None and v < r["elapsed"]) else ' class="n"'
    need = '<span class="need">입력 필요</span>'
    rows = []

    def row(grp, label, val, vattr=' class="n"'):
        rows.append((grp, "<td>" + label + "</td><td" + vattr + ">" + val + "</td>"))

    # 매출
    rs_py = ratio(r["s_cur"], r["s_py"]); rs_t = ratio(r["s_cur"], r["t_s"])
    row("매출", f"{py2}년 매출", won(r["s_py"]))
    row("매출", "매출목표", won(r["t_s"]) if r["t_s"] is not None else need)
    row("매출", f"{yy}년 매출", won(r["s_cur"]))
    row("매출", "전년대비매출", pct(rs_py))
    row("매출", "목표대비매출", pct(rs_t), low(rs_t))
    # 이익
    rp_py = ratio(r["p_cur"], r["p_py"]); rp_t = ratio(r["p_cur"], r["t_p"])
    row("이익", f"{py2}년 이익", won(r["p_py"]) if r["p_py"] is not None else need)
    row("이익", "이익목표", won(r["t_p"]) if r["t_p"] is not None else need)
    row("이익", f"{yy}년 이익", won(r["p_cur"]) if r["p_cur"] is not None else need)
    row("이익", "전년대비이익", pct(rp_py))
    row("이익", "목표대비이익", pct(rp_t), low(rp_t))
    # 매입
    for label, inp, s, o, p in ((f"{r['y']-1}<br>매입", r["i_py"], r["s_py"], r["o_py"], r["p_py"]),
                                (f"{r['y']}<br>매입", r["i_cur"], r["s_cur"], r["o_cur"], r["p_cur"])):
        for name in r["out_names"] or ["외주"]:
            v = inp["outs"].get(name) if inp else None
            row(label, esc(name), won(v) if v is not None else need)
        row(label, "외주합계", won(o) if o is not None else need)
        row(label, "이익률", pct(ratio(p, s)), ' class="n p-rate"')
    # 수량
    q_py = r["py"]["own"] if r["py"] else None
    q_cur = r["cur"]["own"] if r["cur"] else None
    row("수량", f"{r['y']-1}년", won(q_py))
    row("수량", f"{r['y']}년", won(q_cur))
    row("수량", "전년대비", pct(ratio(q_cur, q_py)))

    cls = {"매출": "sales", "이익": "profit", "수량": "qty"}
    out, i = [], 0
    while i < len(rows):
        g = rows[i][0]
        j = i
        while j < len(rows) and rows[j][0] == g:
            j += 1
        c = cls.get(g, "buy")
        for k in range(i, j):
            first = f'<td class="grp {c}" rowspan="{j-i}">{g}</td>' if k == i else ""
            out.append(f'<tr class="{c}">{first}{rows[k][1]}</tr>')
        i = j
    return '<table class="sheet">' + "".join(out) + "</table>"


def trend_svg(trend, y):
    W, H, L, R, T, B = 720, 262, 46, 10, 22, 28
    vals = [v for t in trend for v in (t["py"], t["cur"], t["target"]) if v]
    top = max(vals) if vals else 1.0
    step = 10 ** max(0, len(str(int(top / 4))) - 1)
    for k in (1, 2, 2.5, 5, 10):
        if top / (step * k) <= 5:
            step *= k
            break
    ymax = step * (int(top / step) + 1)
    ph = H - T - B
    sy = lambda v: T + ph - (v / ymax) * ph
    gw = (W - L - R) / 12
    bw = min(22, (gw - 10) / 2)
    p = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="월별 매출 전년 대비">',
         '<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<rect width="6" height="6" fill="#2a78d6" opacity=".45"/><line x1="0" y1="0" x2="0" y2="6" stroke="#2a78d6" stroke-width="3"/></pattern></defs>']
    v = 0
    while v <= ymax + 1e-9:
        yy = sy(v)
        p.append(f'<line x1="{L}" x2="{W-R}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#e4e3de" stroke-width="1"/>')
        p.append(f'<text x="{L-6}" y="{yy+4:.1f}" font-size="11" fill="#8a8984" text-anchor="end">{v/1e6:,.0f}</text>')
        v += step
    p.append(f'<text x="{L-6}" y="11" font-size="10" fill="#8a8984" text-anchor="end">(백만원)</text>')

    def bar(x, val, fill, tipt):
        if val is None or val <= 0:
            return ""
        h = max(1.0, ph * val / ymax)
        yv = T + ph - h
        r = min(4, h)
        # 위쪽 모서리만 둥글게 (바닥에 붙임)
        d = (f"M{x:.1f},{T+ph:.1f} V{yv+r:.1f} Q{x:.1f},{yv:.1f} {x+r:.1f},{yv:.1f} "
             f"H{x+bw-r:.1f} Q{x+bw:.1f},{yv:.1f} {x+bw:.1f},{yv+r:.1f} V{T+ph:.1f} Z")
        return f'<path d="{d}" fill="{fill}" data-tip="{esc(tipt)}"/>'

    for i, t in enumerate(trend):
        gx = L + gw * i + (gw - (2 * bw + 2)) / 2
        p.append(bar(gx, t["py"], "#b9b7ae", f"{y-1}년 {t['m']}월 · {won(t['py'])} 원"))
        lab = f"{y}년 {t['m']}월{' (진행 중)' if t['partial'] else ''} · {won(t['cur'])} 원"
        if t["target"]:
            lab += f"<br>목표 {won(t['target'])} 원 · 달성 {pct(ratio(t['cur'], t['target']))}"
        p.append(bar(gx + bw + 2, t["cur"], "url(#hatch)" if t["partial"] else "#2a78d6", lab))
        if t["target"]:
            ty = sy(t["target"])
            p.append(f'<line x1="{gx+bw:.1f}" x2="{gx+2*bw+4:.1f}" y1="{ty:.1f}" y2="{ty:.1f}" '
                     f'stroke="#0b0b0b" stroke-width="2" data-tip="{esc(t["m"])}월 목표 {won(t["target"])} 원"/>')
        p.append(f'<text x="{L+gw*i+gw/2:.1f}" y="{H-9}" font-size="11" fill="#52514e" text-anchor="middle">{t["m"]}월</text>')
    p.append(f'<line x1="{L}" x2="{W-R}" y1="{T+ph}" y2="{T+ph}" stroke="#8a8984" stroke-width="1"/>')
    p.append("</svg>")
    return "".join(p)


def render(r, generated: datetime):
    base = r["base"]
    period = f"{r['m']}월 1 ~ {base.day}일"
    py_label = (f"{r['y']-1}년 {r['m']}월 1 ~ {r['same_day']}일 (같은 기간)" if r["py_mode"] == "same"
                else f"{r['y']-1}년 {r['m']}월 전체")
    ytd = r["ytd"]

    def tile(k, v, d):
        return f'<div class="tile"><div class="k">{k}</div><div class="v">{v}</div><div class="d">{d}</div></div>'

    tiles = "".join([
        tile(f"{r['m']}월 매출 (원)", won(r["s_cur"]),
             f"목표 {pct(ratio(r['s_cur'], r['t_s']))} · 달 경과 {pct(r['elapsed'])}"),
        tile(f"{r['m']}월 이익 (원)", won(r["p_cur"]) if r["p_cur"] is not None else "입력 필요",
             f"이익률 {pct(ratio(r['p_cur'], r['s_cur']))}"),
        tile(f"{r['m']}월 출고 수량 (개)", won(r["cur"]["own"] if r["cur"] else None),
             f"출고합계 {won(r['cur']['qty'] if r['cur'] else None)} · 연마불가 {won(r['cur']['bad'] if r['cur'] else None)}"),
    ])

    # 누계
    yt_rows = [
        ("매출 (원)", won(ytd["cur_amt"]), won(ytd["py_amt"]), pct(ratio(ytd["cur_amt"], ytd["py_amt"]))),
        ("출고 수량 (개)", won(ytd["cur_qty"]), won(ytd["py_qty"]), pct(ratio(ytd["cur_qty"], ytd["py_qty"]))),
    ]
    if not ytd["miss_out"]:
        pc, pp = ytd["cur_amt"] - ytd["cur_out"], ytd["py_amt"] - ytd["py_out"]
        yt_rows.append(("이익 (원)", won(pc), won(pp), pct(ratio(pc, pp))))
    ytd_html = ('<table><tr><th></th><th class="n">' + f"{r['y']}년 1월 1일 ~ {r['m']}월 {base.day}일"
                + '</th><th class="n">' + f"{r['y']-1}년 같은 기간" + '</th><th class="n">전년대비</th></tr>'
                + "".join(f'<tr><td>{a}</td><td class="n">{b}</td><td class="n">{c}</td><td class="n">{d}</td></tr>'
                          for a, b, c, d in yt_rows) + "</table>")
    notes = []
    if ytd["miss_out"]:
        notes.append(f"누계 이익은 외주 매입 입력이 빈 달이 있어 뺐다 ({len(ytd['miss_out'])}개 달).")
    if ytd["miss_cur"] or ytd["miss_py"]:
        notes.append("ERP 기록 없는 달: " + ", ".join(ytd["miss_py"] + ytd["miss_cur"]) + " — 0 으로 셈.")
    ytd_html += "".join(f'<div class="note">{n}</div>' for n in notes)

    # 거래처
    top = r["top"]
    top_html = '<table><tr><th>거래처</th><th class="n">매출 (원)</th><th class="n">비중</th><th style="width:22%"></th><th class="n">출고 (개)</th></tr>'
    for name, amt, own, sh in top:
        top_html += (f'<tr><td>{esc(name)}</td><td class="n">{won(amt)}</td><td class="n">{pct(sh)}</td>'
                     f'<td><div class="bar"><i style="width:{sh*100:.1f}%"></i></div></td><td class="n">{won(own)}</td></tr>')
    top_html += "</table>" if top else "<tr><td colspan=5 class='need'>이번 달 출하 없음</td></tr></table>"

    # 추이 표
    tr_tbl = ('<table><tr><th>월</th><th class="n">' + f"{r['y']-1}년" + '</th><th class="n">' + f"{r['y']}년"
              + '</th><th class="n">목표</th><th class="n">전년대비</th></tr>'
              + "".join(f'<tr><td>{t["m"]}월{" (진행 중)" if t["partial"] else ""}</td><td class="n">{won(t["py"])}</td>'
                        f'<td class="n">{won(t["cur"])}</td><td class="n">{won(t["target"])}</td>'
                        f'<td class="n">{pct(ratio(t["cur"], t["py"]))}</td></tr>' for t in r["trend"]) + "</table>")

    cur = r["cur"] or {}
    check = []
    if cur:
        if cur.get("amt_check_bad", -1) > 0:
            check.append(f"⚠ 공급가 + 부가세 ≠ 합계금액 인 행 {cur['amt_check_bad']}개 — 금액 칸 뜻 확인 필요")
    src = " · ".join(f"{k} {v}" for k, v in sorted(r["src"].items()) if v not in ("캐시",))
    if r["manual"]:
        check.append("입력표 매출(수기) 값을 쓴 달(ERP 기록 없음): " + ", ".join(r["manual"]))

    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>생산팀 매출 현황 — {base:%Y-%m-%d}</title>
<style>{CSS}</style></head><body><div class="wrap">
<header><div><h1>생산팀 매출 현황 <span class="sub">재연마</span><span class="badge">대외비 · 이 PC 밖으로 보내지 말 것</span></h1>
<div class="sub">기준일 {base:%Y-%m-%d} (KST) · 이번 달 {period} · 전년 비교 = {py_label}</div></div>
<div class="sub">만든 시각 {generated:%Y-%m-%d %H:%M} KST</div></header>
<div class="grid">
<section class="card"><h2>{r['m']}월 현황 ({period})</h2>{sheet_table(r)}
<div class="note">빨간 % = 달 경과율 {pct(r['elapsed'])} ({base.day}/{r['days_in']}일, 달력일)보다 낮음. 「입력 필요」 = 입력.xlsx 빈칸.</div></section>
<div>
<section class="card" style="margin-bottom:14px"><div class="tiles">{tiles}</div>
<h2>월별 매출 — {r['y']-1}년 vs {r['y']}년</h2>
<div class="legend"><span><span class="sw" style="background:#b9b7ae"></span>{r['y']-1}년</span>
<span><span class="sw" style="background:#2a78d6"></span>{r['y']}년</span>
<span><span class="sw" style="background:repeating-linear-gradient(45deg,#2a78d6 0 3px,#a9c8ee 3px 6px)"></span>진행 중인 달</span>
<span><span class="sw" style="background:#0b0b0b;height:2px;vertical-align:3px"></span>목표</span></div>
{trend_svg(r['trend'], r['y'])}
<details><summary>표로 보기</summary>{tr_tbl}</details></section>
<section class="card" style="margin-bottom:14px"><h2>올해 누계</h2>{ytd_html}</section>
<section class="card"><h2>{r['m']}월 거래처별 매출 (상위 10)</h2>{top_html}</section>
</div></div>
<footer>
매출 = ERP 재연마 출하등록({WORK_SET}, 상세) 출하금액 mov_amt 합 — 공급가(부가세 제외)로 추정, 수기 시트와 첫 대조 전 「확인 필요」.
수량 = 출고 mov_own_qty(연마불가 제외). 이익 = 매출 − 외주 매입 합계(입력.xlsx), 이익률 = 이익 ÷ 매출 — 수기 「생산팀 매출 현황」과 같은 계산.<br>
{'<br>'.join(check)}{'<br>' if check else ''}이번 실행에서 ERP 로 받은 달: {esc(src) or '없음(모두 캐시)'}<br>
erp/sales_board.py · 결과 wiki/_private/sales_board/ (git 추적 제외)
</footer></div><div id="tip"></div><script>{JS}</script></body></html>"""


# ── 실행 ──────────────────────────────────────────────────────────────────
def main(argv=None):
    ap = argparse.ArgumentParser(description="매출 현황판 (재연마, 경준님 PC 전용)")
    ap.add_argument("date", nargs="?", help="기준일 YYYY-MM-DD (기본 오늘 KST)")
    ap.add_argument("--py", choices=("full", "same"), default="same",
                    help="전년 비교: same=같은 기간(기본, 수기 시트와 같음 — 2026-11-18 경준님 확인), full=같은 달 전체")
    ap.add_argument("--refresh", action="store_true", help="지난 달 캐시도 ERP 에서 다시 받음")
    ap.add_argument("--offline", action="store_true", help="ERP 조회 없이 캐시만")
    ap.add_argument("--open", action="store_true", help="만든 뒤 브라우저로 열기")
    a = ap.parse_args(argv)

    now = datetime.now(KST)
    base = date.fromisoformat(a.date) if a.date else now.date()
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.exists(INPUT_XLSX):
        make_input_template(INPUT_XLSX, (base.year - 1, base.year))
        print(f"[sales_board] 입력표를 새로 만들었습니다 — 목표 · 외주 매입을 채우세요: {INPUT_XLSX}")
    inputs, out_names = read_inputs(INPUT_XLSX)

    yms = [f"{y}-{m:02d}" for y in (base.year - 1, base.year) for m in range(1, 13)
           if (y, m) <= (base.year, base.month)]
    months = load_months(yms, ym_of(now.date()), refresh=a.refresh, offline=a.offline)
    r = build(base, months, inputs, out_names, py_mode=a.py)

    with open(OUT_HTML + ".tmp", "w", encoding="utf-8") as f:
        f.write(render(r, now))
    os.replace(OUT_HTML + ".tmp", OUT_HTML)

    # 대조용 요약 — 콘솔 + wiki/_private/sales_board/last_run.txt (git 제외. run.log 등 다른 로그에는 쓰지 않음)
    # 여기 숫자는 ERP 값만(입력표 수기 값 섞지 않음) — 수기 시트와 맞춰 보기 위해
    c = summarize(months[r["cur_ym"]][0], upto=base.isoformat())
    pf = summarize(months[r["py_ym"]][0])
    ps = summarize(months[r["py_ym"]][0], upto=f"{r['py_ym']}-{r['same_day']:02d}")
    f = lambda s_, k: won(s_[k]) if (s_ and s_.get(k) is not None) else "기록 없음"
    L = [f"[sales_board] 기준일 {base} · {r['cur_ym']} vs {r['py_ym']} · 만든 시각 {now:%Y-%m-%d %H:%M} KST",
         f"  올해 {r['m']}월 1~{base.day}일   매출 mov_amt {f(c,'amt')} · tot_amt {f(c,'tot')} · vat {f(c,'vat')}"
         f" · 출고 {f(c,'own')} · 출고합계 {f(c,'qty')} · {c['rows'] if c else 0}행",
         f"  전년 {r['m']}월 1~{r['same_day']}일   매출 mov_amt {f(ps,'amt')} · tot_amt {f(ps,'tot')}"
         f" · 출고 {f(ps,'own')} · 출고합계 {f(ps,'qty')} · {ps['rows'] if ps else 0}행",
         f"  전년 {r['m']}월 전체     매출 mov_amt {f(pf,'amt')} · tot_amt {f(pf,'tot')}"
         f" · 출고 {f(pf,'own')} · 출고합계 {f(pf,'qty')}",
         f"  두 기간 합계        mov_amt {won((c or {}).get('amt',0) + (ps or {}).get('amt',0))}"
         f" · tot_amt {won((c or {}).get('tot',0) + (ps or {}).get('tot',0))}"]
    if c and c.get("amt_check_bad", 0) > 0:
        L.append(f"  [확인 필요] 공급가+부가세≠합계 행 {c['amt_check_bad']}개")
    # 월 평균 출하 수량 후보 (수기 시트 맨 아래 값의 기준 찾기용)
    L.append("  월별 출고 / 출고합계 (ERP):")
    per = []
    for ym in sorted(months):
        s_ = summarize(months[ym][0])
        if s_ is None:
            L.append(f"    {ym}  기록 없음 ({months[ym][1]})")
            continue
        part = ym == r["cur_ym"]
        if not part:
            per.append((ym, s_["own"], s_["qty"]))
        L.append(f"    {ym}  출고 {won(s_['own'])} · 출고합계 {won(s_['qty'])} · 매출 {won(s_['amt'])}{' (진행 중)' if part else ''}")

    def avg(sel, label):
        if sel:
            L.append(f"  월평균 {label} ({len(sel)}개월): 출고 {won(sum(x[1] for x in sel)/len(sel))}"
                     f" · 출고합계 {won(sum(x[2] for x in sel)/len(sel))}")
    py_, cy = str(base.year - 1), str(base.year)
    avg([x for x in per if x[0].startswith(py_)], f"{py_}년")
    avg([x for x in per if x[0].startswith(cy)], f"{cy}년 1~{base.month-1}월")
    avg(per[-12:], "최근 마감 12개월")
    avg(per, "받은 달 전체")
    L.append(f"  → {OUT_HTML}")
    print("\n".join(L))
    try:
        with open(os.path.join(OUT_DIR, "last_run.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(L) + "\n")
    except OSError:
        pass
    if a.open:
        try:
            os.startfile(OUT_HTML)   # Windows
        except AttributeError:
            import webbrowser
            webbrowser.open("file://" + OUT_HTML)
    return 0


if __name__ == "__main__":
    sys.exit(main())
