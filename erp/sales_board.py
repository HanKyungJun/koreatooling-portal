# -*- coding: utf-8 -*-
"""매출 현황판 — 재연마 출하 금액 · 수량 → HTML 한 장 (2026-11-18 신설, Cowork)

경준님 PC 전용. 결과 · 입력 · 캐시는 모두 private_local/sales_board/ (git 추적 제외) 에만 쓴다.
공유폴더 현황판 · dist(github.io) 로 보내지 않는다 — 금액은 대외비(CLAUDE.md §4).

  python erp\\sales_board.py                 오늘(KST) 기준으로 만들고 끝
  python erp\\sales_board.py --open          만든 뒤 브라우저로 연다 (매출현황판.bat)
  python erp\\sales_board.py 2026-11-17      기준일 지정
  python erp\\sales_board.py --py full       전년 비교를 「같은 기간(1일 ~ 기준일)」 대신 「같은 달 전체」로
  python erp\\sales_board.py --refresh       지난달 이전 캐시까지 ERP 에서 다시 받음
  python erp\\sales_board.py --offline       ERP 조회 없이 캐시만으로 (시험용)
  python erp\\sales_board.py --weekly        주간 실행 — 기준일 = 직전 화요일, 엑셀을 화면에 연다
                                            (예약 작업 CNC_Sales_Weekly · 수 09:00 KST, scripts/register_sales_weekly_task.ps1)

엑셀(2026-11-18~): 실행마다 private_local/sales_board/엑셀/매출현황_YYYYMMDD.xlsx (기준일) — 수기 「생산팀 매출 현황」
시트와 같은 모양 · 같은 칸. 입력 값(매출 · 목표 · 외주 · 수량)만 숫자이고 이익 · 비율은 엑셀 수식.

데이터
- 매출 · 수량: ERP 재연마 출하등록 lem120_jae_g00 (chk_detail=1) — 월 출하 마감(save_shipment.py)과 같은 원본.
    매출 = mov_amt 합 (공급가, 부가세 제외 — 2026-11-18 수기 시트와 대조 일치 [실측 검증])
    수량 = mov_own_qty 합 (출고, 연마불가 제외) — 출고합계(mov_qty)는 참고로 같이 보인다.
- 외주 매입: ERP 매입(입고) 조회 lea110_g00 (2026-11-18 Fiddler 캡처 → probe_purchase.py --parse 가 만든
    private_local/sales_board/purchase_spec.json 의 파라미터 그대로, 날짜만 바꿈) 의 in_amt(공급가) 를
    외주업체.json(같은 폴더, git 제외)에 적은 업체명으로 묶어 더한다. 둘 중 하나라도 없으면 입력표 값을 쓴다.
    2026-11-18 대조: 25년 · 26년 11월 1~17일 외주 2곳 4칸이 수기 시트와 일치 [실측 검증].
- 목표: 입력.xlsx 「월별입력」 시트 (경준님이 손으로 채움).
    이익 = 매출 − 외주합계, 이익률 = 이익 ÷ 매출 (수기 「생산팀 매출 현황」 시트 계산과 같게).

🔴 가격 열 차단 예외 (decisions 2026-11-13 (2) 와 같은 방식):
   trico_client.query(..., block_price=False) 는 fetch_month() 한 곳뿐이고, 받자마자 KEEP 8열만 남긴다.
   단가(*_up) · 할인 · 거래처 코드 · 담당자 등은 버린다. 콘솔 · 파일 모두 private_local 밖으로 금액을 쓰지 않는다(git · Drive 동기화 모두 제외되는 곳).
"""
import sys, os, json, argparse, calendar, html as _html
from datetime import datetime, date, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)

KST = timezone(timedelta(hours=9))
OUT_DIR = os.path.join(BASE, "private_local", "sales_board")   # wiki/ 밖 — 16:30 Drive 동기화가 wiki/ 전체(_private 포함)를 올리기 때문 (2026-11-18)
CACHE_DIR = os.path.join(OUT_DIR, "cache")
INPUT_XLSX = os.path.join(OUT_DIR, "입력.xlsx")
OUT_HTML = os.path.join(OUT_DIR, "매출현황판.html")
XLSX_DIR = os.path.join(OUT_DIR, "엑셀")
WEEKLY_LOG = os.path.join(OUT_DIR, "weekly.log")

WORK_SET = "lem120_jae_g00"
KEEP = ("out_dt", "cust_nm", "mov_own_qty", "mov_qty", "bad_qty", "mov_amt", "vat_amt", "tot_amt")
NEED = {"out_dt", "cust_nm", "mov_own_qty", "mov_qty", "mov_amt"}
PUR_KEEP = ("in_dt", "cust_nm", "in_amt", "vat_amt")
PUR_NEED = {"in_dt", "cust_nm", "in_amt"}
PUR_SPEC = os.path.join(OUT_DIR, "purchase_spec.json")     # probe_purchase.py --parse 결과 (캡처 파라미터)
VENDOR_CFG = os.path.join(OUT_DIR, "외주업체.json")         # {"항목 이름": ["ERP 거래처명", ...]} — 업체명은 여기에만
INPUT_SHEET = "월별입력"
FY_START = 4    # 회계연도 시작 월 — 회사 목표표가 4월 ~ 3월 (2026-11-18 경준님 「4월로 진행」)
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


def fetch_pur_month(client, ym: str, spec: dict):
    import pandas as pd
    p = {k: v for k, v, *_ in spec["params"]}
    p["@fr_dt"], p["@to_dt"] = f"{ym}-01", month_end(ym).isoformat()
    df = client.query(spec["workset"], p, block_price=False)   # 🔴 매입 금액 — 바로 아래에서 PUR_KEEP 만 남긴다
    if df is None or df.empty:
        return pd.DataFrame(columns=list(PUR_KEEP))
    df.columns = [str(c) for c in df.columns]
    miss = PUR_NEED - set(df.columns)
    if miss:
        raise RuntimeError(f"missing columns {sorted(miss)}")
    return df[[c for c in PUR_KEEP if c in df.columns]].copy()


def load_months(yms, today_ym, refresh=False, offline=False, log=print, kind="ship", spec=None):
    """달마다 (DataFrame | None, 출처). 지난달 이전 = 캐시 우선, 이번 달 · 지난달 = 매번 ERP.
    kind="ship" 출하(매출 · 수량) / "pur" 매입(외주, spec 필요)."""
    import pandas as pd
    os.makedirs(CACHE_DIR, exist_ok=True)
    client = None
    out = {}
    fails = 0
    last_closed = prev_ym(today_ym)
    for ym in yms:
        path = os.path.join(CACHE_DIR, f"{kind}_{ym}.csv")
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
                client = TricoClient(macro=(spec or {}).get("macro") or None) if kind == "pur" else TricoClient()
            df = fetch_pur_month(client, ym, spec) if kind == "pur" else fetch_month(client, ym)
            df.to_csv(path + ".tmp", index=False, encoding="utf-8-sig")
            os.replace(path + ".tmp", path)
            out[ym] = (df.astype(str).fillna(""), "ERP")
            fails = 0
        except Exception as e:
            fails += 1
            log(f"  [경고] {kind} {ym} ERP 조회 실패: {type(e).__name__}: {str(e)[:120]}")
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
        "이 파일은 private_local/ 안이라 git · Drive 동기화에 올라가지 않는다. 다른 곳으로 복사 · 메일 금지(대외비).",
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


def read_vendors(path=None):
    try:
        with open(path or VENDOR_CFG, encoding="utf-8") as f:
            cfg = json.load(f)
        return {str(k): [str(n).strip() for n in v] for k, v in cfg.items() if not str(k).startswith("_")}
    except (OSError, ValueError):
        return None


def read_vendor_labels():
    """외주업체.json 의 "_표시": {"항목": ["전년 칸 이름", "올해 칸 이름"]} (수기 시트 표기). 없으면 항목 이름."""
    try:
        with open(VENDOR_CFG, encoding="utf-8") as f:
            return {str(k): list(v) for k, v in (json.load(f).get("_표시") or {}).items()}
    except (OSError, ValueError, AttributeError):
        return {}


def erp_outs(pur, vendors, ym, upto=None):
    """ERP 매입에서 항목별 외주 금액. 그 달 매입 자료가 없으면 None."""
    import pandas as pd
    if not vendors or not pur or ym not in pur or pur[ym][0] is None:
        return None
    d = pur[ym][0]
    if upto is not None and len(d):
        d = d[d["in_dt"].astype(str).str[:10] <= upto]
    amt = pd.to_numeric(d["in_amt"], errors="coerce").fillna(0) if len(d) else pd.Series(dtype=float)
    names = d["cust_nm"].astype(str).str.strip() if len(d) else pd.Series(dtype=str)
    return {k: float(amt[names.isin(v)].sum()) if len(d) else 0.0 for k, v in vendors.items()}


def fy_start_year(d: date) -> int:
    return d.year if d.month >= FY_START else d.year - 1


def fy_months(fy: int):
    """회계연도 fy 의 12개월 [(년, 월), ...] — fy 년 4월 ~ fy+1 년 3월."""
    return [(fy + (FY_START - 1 + i) // 12, (FY_START - 1 + i) % 12 + 1) for i in range(12)]


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


def build(base: date, months, inputs, out_names, py_mode="full", pur=None, vendors=None):
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

    def outs_of(ym, upto=None):
        """(항목별 dict | None, 출처) — ERP 매입 우선, 없으면 입력표."""
        e = erp_outs(pur, vendors, ym, upto)
        if e is not None:
            return e, "ERP"
        inp = inputs.get(ym)
        if inp and any(v is not None for v in inp["outs"].values()):
            return dict(inp["outs"]), "입력표"
        return None, "없음"

    def tot(d):
        vals = [v for v in (d or {}).values() if v is not None]
        return sum(vals) if vals else None

    outs_cur, src_cur = outs_of(cur_ym, base_iso)
    outs_py, src_py = outs_of(py_ym, py_same_iso if py_mode == "same" else None)
    s_cur = cur["amt"] if cur else None
    s_py = py["amt"] if py else None
    o_cur, o_py = tot(outs_cur), tot(outs_py)
    p_cur = s_cur - o_cur if (s_cur is not None and o_cur is not None) else None
    p_py = s_py - o_py if (s_py is not None and o_py is not None) else None
    t_s = i_cur["sales_target"] if i_cur else None
    t_p = i_cur["profit_target"] if i_cur else None

    # 회계연도 누계 (4월 1일 ~ 기준일) vs 전년 같은 기간
    fy = fy_start_year(base)
    fms = fy_months(fy)
    ytd = dict(cur_amt=0.0, py_amt=0.0, cur_qty=0.0, py_qty=0.0, cur_out=0.0, py_out=0.0,
               miss_cur=[], miss_py=[], miss_out=[])
    for yy, mm in fms:
        if (yy, mm) > (y, m):
            break
        a, b = f"{yy}-{mm:02d}", f"{yy-1}-{mm:02d}"
        sa = month_sum(months, inputs, a, upto=base_iso if mm == m else None)
        sb = month_sum(months, inputs, b, upto=py_same_iso if mm == m else None)
        if sa: ytd["cur_amt"] += sa["amt"]; ytd["cur_qty"] += sa["own"] or 0
        else: ytd["miss_cur"].append(a)
        if sb: ytd["py_amt"] += sb["amt"]; ytd["py_qty"] += sb["own"] or 0
        else: ytd["miss_py"].append(b)
        oa = tot(outs_of(a, base_iso if mm == m else None)[0])
        ob = tot(outs_of(b, py_same_iso if mm == m else None)[0])
        if oa is None: ytd["miss_out"].append(a)
        else: ytd["cur_out"] += oa
        if ob is None: ytd["miss_out"].append(b)
        else: ytd["py_out"] += ob

    trend = []
    for yy, mm in fms:
        a, b = f"{yy}-{mm:02d}", f"{yy-1}-{mm:02d}"
        sb = month_sum(months, inputs, b)
        sa = None
        if (yy, mm) <= (y, m):
            sa = month_sum(months, inputs, a, upto=base_iso if (yy, mm) == (y, m) else None)
        tg = inputs.get(a, {}).get("sales_target") if inputs.get(a) else None
        trend.append(dict(m=mm, ycur=yy, ypy=yy - 1, py=sb["amt"] if sb else None, cur=sa["amt"] if sa else None,
                          partial=((yy, mm) == (y, m) and base < month_end(a)), target=tg))

    days_in = calendar.monthrange(y, m)[1]
    return dict(
        base=base, y=y, m=m, cur_ym=cur_ym, py_ym=py_ym, py_mode=py_mode, same_day=same_day,
        cur=cur, py=py, py_full=py_full, py_same=py_same,
        s_cur=s_cur, s_py=s_py, t_s=t_s, t_p=t_p, p_cur=p_cur, p_py=p_py, o_cur=o_cur, o_py=o_py,
        i_cur=i_cur, i_py=i_py, outs_cur=outs_cur, outs_py=outs_py, outs_src=(src_py, src_cur),
        out_names=list(vendors) if vendors else out_names,
        elapsed=base.day / days_in, days_in=days_in,
        ytd=ytd, trend=trend, fy=fy,
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
    for label, od, s, o, p in ((f"{r['y']-1}<br>매입", r["outs_py"], r["s_py"], r["o_py"], r["p_py"]),
                               (f"{r['y']}<br>매입", r["outs_cur"], r["s_cur"], r["o_cur"], r["p_cur"])):
        for name in r["out_names"] or ["외주"]:
            v = od.get(name) if od else None
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
        p.append(bar(gx, t["py"], "#b9b7ae", f"{t['ypy']}년 {t['m']}월 · {won(t['py'])} 원"))
        lab = f"{t['ycur']}년 {t['m']}월{' (진행 중)' if t['partial'] else ''} · {won(t['cur'])} 원"
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
    ytd_html = ('<table><tr><th></th><th class="n">' + f"{r['fy']}년 {FY_START}월 1일 ~ {r['y']}년 {r['m']}월 {base.day}일"
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
    tr_tbl = ('<table><tr><th>월</th><th class="n">전년 같은 달</th><th class="n">올해</th>'
              + '<th class="n">목표</th><th class="n">전년대비</th></tr>'
              + "".join(f'<tr><td>{str(t["ycur"])[2:]}년 {t["m"]}월{" (진행 중)" if t["partial"] else ""}</td><td class="n">{won(t["py"])}</td>'
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
<div class="note">빨간 % = 달 경과율 {pct(r['elapsed'])} ({base.day}/{r['days_in']}일, 달력일)보다 낮음. 「입력 필요」 = 입력.xlsx 빈칸(목표) 또는 매입 자료 없음.</div></section>
<div>
<section class="card" style="margin-bottom:14px"><div class="tiles">{tiles}</div>
<h2>월별 매출 — {r['fy']}년 {FY_START}월 ~ {r['fy']+1}년 {FY_START-1}월 (회계연도)</h2>
<div class="legend"><span><span class="sw" style="background:#b9b7ae"></span>전년 같은 달</span>
<span><span class="sw" style="background:#2a78d6"></span>올해</span>
<span><span class="sw" style="background:repeating-linear-gradient(45deg,#2a78d6 0 3px,#a9c8ee 3px 6px)"></span>진행 중인 달</span>
<span><span class="sw" style="background:#0b0b0b;height:2px;vertical-align:3px"></span>목표</span></div>
{trend_svg(r['trend'], r['y'])}
<details><summary>표로 보기</summary>{tr_tbl}</details></section>
<section class="card" style="margin-bottom:14px"><h2>회계연도 누계 ({FY_START}월 시작)</h2>{ytd_html}</section>
<section class="card"><h2>{r['m']}월 거래처별 매출 (상위 10)</h2>{top_html}</section>
</div></div>
<footer>
매출 = ERP 재연마 출하등록({WORK_SET}, 상세) 출하금액 mov_amt 합 — 공급가(부가세 제외).
수량 = 출고 mov_own_qty(연마불가 제외). 외주 매입 = ERP 매입 lea110_g00 in_amt(공급가) 중 외주업체.json 업체
(출처 전년 {r['outs_src'][0]} · 올해 {r['outs_src'][1]}). 이익 = 매출 − 외주 매입 합계, 이익률 = 이익 ÷ 매출 — 수기 「생산팀 매출 현황」과 같은 계산.
2026-11-18 수기 시트(11월 1~17일)와 매출 · 수량 · 외주 8칸 대조 일치.<br>
{'<br>'.join(check)}{'<br>' if check else ''}이번 실행에서 ERP 로 받은 달: {esc(src) or '없음(모두 캐시)'}<br>
erp/sales_board.py · 결과 private_local/sales_board/ (git 추적 제외)
</footer></div><div id="tip"></div><script>{JS}</script></body></html>"""


# ── 엑셀 (수기 「생산팀 매출 현황」 시트와 같은 모양) ─────────────────────
def write_sheet_xlsx(r, path, generated: datetime, notes=()):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    F = "맑은 고딕"
    thin = Side(style="thin", color="808080")
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    fills = {"title": "BDD7EE", "매출": "DDEBF7", "이익": "DAEEF3", "py": "E7E6E6", "cur": "DCE6F1", "수량": "D8E4BC"}
    fill = lambda k: PatternFill("solid", fgColor=fills[k])
    NUM, PCT = "#,##0", "0.0%"
    red, blue = "FF0000", "0070C0"

    wb = Workbook()
    ws = wb.active
    ws.title = "매출현황"
    ws.column_dimensions["A"].width = 9
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 15
    ws.merge_cells("A1:C1")
    ws["A1"] = "생산팀 매출 현황"
    ws["A1"].font = Font(name=F, bold=True, size=13)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    base = r["base"]
    ws["B2"] = f"{r['y']}년"
    ws["C2"] = f"{r['m']}월 {base.day}일"
    ws["B2"].font = Font(name=F, bold=True)
    ws["C2"].font = Font(name=F, bold=True, color=red)
    for c in ("A1", "B1", "C1", "A2", "B2", "C2"):
        ws[c].fill = fill("title"); ws[c].border = box
    ws["B2"].alignment = ws["C2"].alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 22

    py2, yy = str(r["y"] - 1)[2:], str(r["y"])[2:]
    labels = read_vendor_labels()
    names = r["out_names"] or ["외주"]
    row = [3]
    cell = {}

    def put(key, label, value, fmt=NUM, color=None, bold=False):
        n = row[0]
        ws.cell(n, 2, label).font = Font(name=F, bold=bold)
        c = ws.cell(n, 3, value)
        c.number_format = fmt
        c.font = Font(name=F, bold=bold, color=color)
        cell[key] = f"C{n}"
        row[0] += 1
        return n

    def group(title, k, start):
        end = row[0] - 1
        ws.merge_cells(start_row=start, start_column=1, end_row=end, end_column=1)
        a = ws.cell(start, 1, title)
        a.font = Font(name=F, bold=True)
        a.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for n in range(start, end + 1):
            for col in (1, 2, 3):
                ws.cell(n, col).fill = fill(k)
                ws.cell(n, col).border = box

    v = lambda x: None if x is None else round(x)
    q_py = r["py"]["own"] if r["py"] else None
    q_cur = r["cur"]["own"] if r["cur"] else None
    # 매출 · 이익 칸 번호를 먼저 정해야 수식을 쓸 수 있다 — 매입 칸은 고정 순서로 뒤에 온다
    nv = len(names)
    r_sales = 3; r_profit = r_sales + 5; r_py = r_profit + 5; r_cur = r_py + nv + 2
    py_tot, cur_tot = f"C{r_py + nv}", f"C{r_cur + nv}"
    py_rng, cur_rng = f"C{r_py}:C{r_py + nv - 1}", f"C{r_cur}:C{r_cur + nv - 1}"

    s0 = row[0]
    put("s_py", f"{py2}년 매출", v(r["s_py"]))
    put("t_s", f"{py2}년 매출목표", v(r["t_s"]), bold=True)
    put("s_cur", f"{yy}년 매출", v(r["s_cur"]))
    put("rs_py", "전년대비매출", f'=IFERROR({cell["s_cur"]}/{cell["s_py"]},"")', PCT)
    put("rs_t", "목표대비매출", f'=IFERROR({cell["s_cur"]}/{cell["t_s"]},"")', PCT, color=red, bold=True)
    group("매출", "매출", s0)
    s0 = row[0]
    put("p_py", f"{py2}년 이익", f'=IF(COUNT({py_rng})=0,"",{cell["s_py"]}-{py_tot})')
    put("t_p", f"{py2}년 이익목표", v(r["t_p"]), bold=True)
    put("p_cur", f"{yy}년 이익", f'=IF(COUNT({cur_rng})=0,"",{cell["s_cur"]}-{cur_tot})')
    put("rp_py", "전년대비이익", f'=IFERROR({cell["p_cur"]}/{cell["p_py"]},"")', PCT)
    put("rp_t", "목표대비이익", f'=IFERROR({cell["p_cur"]}/{cell["t_p"]},"")', PCT, color=red, bold=True)
    group("이익", "이익", s0)
    for title, k, od, pkey, skey, idx in ((f"{r['y']-1}\n매입", "py", r["outs_py"], "p_py", "s_py", 0),
                                         (f"{r['y']}\n매입", "cur", r["outs_cur"], "p_cur", "s_cur", 1)):
        s0 = row[0]
        for nm in names:
            lab = (labels.get(nm) or [nm, nm])[idx] if len(labels.get(nm) or []) > idx else nm
            put(f"{k}_{nm}", lab, v(od.get(nm)) if od else None)
        put(f"{k}_tot", "외주합계", f"=IF(COUNT(C{s0}:C{row[0]-1})=0,\"\",SUM(C{s0}:C{row[0]-1}))")
        put(f"{k}_rate", "이익률", f'=IFERROR({cell[pkey]}/{cell[skey]},"")', PCT, color=blue, bold=True)
        group(title, k, s0)
    assert (cell["py_tot"], cell["cur_tot"]) == (py_tot, cur_tot), "수식 칸 번호 어긋남"
    s0 = row[0]
    put("q_py", f"{r['y']-1}년", v(q_py))
    put("q_cur", f"{r['y']}년", v(q_cur))
    put("q_r", "전년대비", f'=IFERROR({cell["q_cur"]}/{cell["q_py"]},"")', PCT)
    group("수량", "수량", s0)

    n = row[0] + 1
    small = Font(name=F, size=8, color="808080")
    lines = [f"기간: {r['m']}월 1일 ~ {base.day}일 · 전년 같은 기간 ({r['y']-1}년 {r['m']}월 1일 ~ {r['same_day']}일)",
             "매출 = ERP 재연마 출하 공급가 · 외주 = ERP 매입 공급가 (부가세 제외) · 수량 = 출고(연마불가 제외)",
             "목표 = 입력.xlsx · 이익 = 매출 − 외주합계 · 대외비 (회사 밖 · 공유폴더로 보내지 말 것)",
             f"만든 시각 {generated:%Y-%m-%d %H:%M} KST · erp/sales_board.py"] + list(notes)
    for i, t in enumerate(lines):
        c = ws.cell(n + i, 1, t)
        c.font = Font(name=F, size=8, color="C00000" if t.startswith("⚠") else "808080") if t else small
    ws.sheet_view.showGridLines = False
    ws.print_area = f"A1:C{row[0]-1}"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        wb.save(path)
    except PermissionError:          # 같은 파일이 엑셀에 열려 있으면 다른 이름으로
        path = path[:-5] + f"_{generated:%H%M}.xlsx"
        wb.save(path)
    return path


def last_tuesday(today: date) -> date:
    back = (today.weekday() - 1) % 7 or 7      # 화요일=1. 수 → 1일 전, 목 → 2일 전, 화 → 7일 전
    return today - timedelta(days=back)


# ── 실행 ──────────────────────────────────────────────────────────────────
def main(argv=None):
    ap = argparse.ArgumentParser(description="매출 현황판 (재연마, 경준님 PC 전용)")
    ap.add_argument("date", nargs="?", help="기준일 YYYY-MM-DD (기본 오늘 KST)")
    ap.add_argument("--py", choices=("full", "same"), default="same",
                    help="전년 비교: same=같은 기간(기본, 수기 시트와 같음 — 2026-11-18 경준님 확인), full=같은 달 전체")
    ap.add_argument("--refresh", action="store_true", help="지난 달 캐시도 ERP 에서 다시 받음")
    ap.add_argument("--offline", action="store_true", help="ERP 조회 없이 캐시만")
    ap.add_argument("--open", action="store_true", help="만든 뒤 브라우저로 열기")
    ap.add_argument("--weekly", action="store_true", help="주간 실행: 기준일 = 직전 화요일, 엑셀을 화면에 연다")
    a = ap.parse_args(argv)
    if a.weekly:
        try:
            return _main(a)
        except Exception:
            import traceback
            os.makedirs(OUT_DIR, exist_ok=True)
            with open(WEEKLY_LOG, "a", encoding="utf-8") as fh:
                fh.write(f"{datetime.now(KST):%Y-%m-%d %H:%M} KST FAILED\n{traceback.format_exc()}\n")
            return 1
    return _main(a)


def _main(a):

    now = datetime.now(KST)
    base = date.fromisoformat(a.date) if a.date else (last_tuesday(now.date()) if a.weekly else now.date())
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.exists(INPUT_XLSX):
        make_input_template(INPUT_XLSX, (base.year - 1, base.year))
        print(f"[sales_board] 입력표를 새로 만들었습니다 — 목표 · 외주 매입을 채우세요: {INPUT_XLSX}")
    inputs, out_names = read_inputs(INPUT_XLSX)

    # 전년 회계연도 시작(4월)부터 기준월까지 — 회계연도 누계 · 추이의 전년 같은 달까지 덮는다
    fy0 = fy_start_year(base) - 1
    yms = [f"{yy}-{mm:02d}" for yy, mm in fy_months(fy0) + fy_months(fy0 + 1) if (yy, mm) <= (base.year, base.month)]
    months = load_months(yms, ym_of(now.date()), refresh=a.refresh, offline=a.offline)
    vendors, pur = read_vendors(), None
    if vendors and os.path.exists(PUR_SPEC):
        with open(PUR_SPEC, encoding="utf-8") as fh:
            spec = json.load(fh)
        pur = load_months(yms, ym_of(now.date()), refresh=a.refresh, offline=a.offline, kind="pur", spec=spec)
    elif vendors:
        print(f"  [경고] {PUR_SPEC} 없음 — 외주 매입은 입력표 값을 씀 (probe_purchase.py --parse 먼저)")
    r = build(base, months, inputs, out_names, py_mode=a.py, pur=pur, vendors=vendors)

    with open(OUT_HTML + ".tmp", "w", encoding="utf-8") as f:
        f.write(render(r, now))
    os.replace(OUT_HTML + ".tmp", OUT_HTML)

    # 대조용 요약 — 콘솔 + private_local/sales_board/last_run.txt (git 제외. run.log 등 다른 로그에는 쓰지 않음)
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
    for lab, ym, up in ((f"올해 {r['m']}월 1~{base.day}일", r["cur_ym"], base.isoformat()),
                        (f"전년 {r['m']}월 1~{r['same_day']}일", r["py_ym"], f"{r['py_ym']}-{r['same_day']:02d}")):
        e = erp_outs(pur, vendors, ym, up)
        L.append(f"  외주 {lab}  " + (" · ".join(f"{k} {won(v)}" for k, v in e.items()) + f" · 합계 {won(sum(e.values()))}"
                                       if e is not None else "ERP 매입 자료 없음(입력표 사용)"))
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
    # 엑셀 — 실행마다 기준일 이름으로 (같은 날 다시 돌리면 덮어씀)
    notes = []
    if r["src"].get(r["cur_ym"]) != "ERP" and not a.offline:
        notes.append(f"⚠ 이번 달 출하 ERP 조회 실패 — {r['src'].get(r['cur_ym'])}")
    xp = write_sheet_xlsx(r, os.path.join(XLSX_DIR, f"매출현황_{base:%Y%m%d}.xlsx"), now, notes)
    print(f"  → {xp}")
    if a.weekly:
        with open(WEEKLY_LOG, "a", encoding="utf-8") as fh:
            fh.write(f"{now:%Y-%m-%d %H:%M} KST ok · 기준일 {base} · {os.path.basename(xp)}"
                     f"{' · ' + ' / '.join(notes) if notes else ''}\n")
        try:
            os.startfile(xp)         # Windows — 엑셀로 화면에 띄움
        except AttributeError:
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
