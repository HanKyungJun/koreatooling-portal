#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
재연마 정가표 → 「보기 좋은」 엑셀 내보내기

왜 스크립트인가:
  정가표는 개정마다 블록 제목·구간·배치가 바뀐다(2026-09-01 밑옆날→밑골수리,
  2026-09-22 밑옆날→밑외경/밑날외경). 한 번 만든 정리 파일은 곧 낡는다.
  → **제목을 하드코딩하지 않고 시트를 훑어서** 블록을 찾고, 매번 다시 돌린다.

산출:
  ① 롱포맷   — 한 행 = 재질·계열·가공부·코팅·날수·직경구간·정가 (필터·피벗용)
  ② 조회용   — 계열별 매트릭스 시트 (직경 × 코팅/날수). 원본 배치를 베끼지 않고 재구성
  ③ 블록목록 — 인식한 블록과 좌표 (누락 점검용)

⚠️ 정가표는 읽기 전용이다. 이 스크립트는 읽기만 한다.

사용:
  python scripts/pricelist_export.py
  python scripts/pricelist_export.py --sheet '정가표(26.05)' --out outputs/정가표_26.05_정리.xlsx
"""
import argparse, collections, datetime, os, re, sys
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from price_audit import PriceList, in_discount_zone, canon_coat   # 판독 엔진 재사용

MG = "맑은 고딕"
F_T  = Font(name=MG, size=22, bold=True)
F_S  = Font(name=MG, size=15, bold=True)
F_B  = Font(name=MG, size=13)
F_BH = Font(name=MG, size=13, bold=True)
FILL_H = PatternFill("solid", fgColor="DDEBF7")
FILL_G = PatternFill("solid", fgColor="F2F2F2")
FILL_W = PatternFill("solid", fgColor="FFF2CC")
_t = Side(style="thin", color="BFBFBF")
BD = Border(_t, _t, _t, _t)

# ── 제목 → 속성 파싱 ────────────────────────────────────────────
def attrs(title):
    """블록 제목에서 재질·계열·가공부·코팅을 뽑는다. 규칙은 제목 텍스트만 본다."""
    t = re.sub(r"\s+", " ", title).strip()
    mat = "초경" if "초경" in t else ("HSS" if "HSS" in t else "-")
    lap = "라핑" in t
    if "리머" in t:                       fam = "리머"
    elif "TAPER" in t:                    fam = "테이퍼"
    elif "원통" in t:                     fam = "원통연삭"
    elif "절단" in t:                     fam = "절단"
    elif "카운터" in t:                   fam = "카운터싱크"
    elif "날붙이" in t:                   fam = "날붙이초경"
    elif re.search(r"코너|BALL|볼", t):   fam = "코너·볼"
    elif re.search(r"FLAT|평", t):        fam = "평"
    else:                                 fam = "형상공통"
    if lap and fam in ("코너·볼", "평", "형상공통"): fam = "라핑 " + fam
    # 가공부 — 개명 이력을 모두 받는다
    if   re.search(r"밑날외경|밑골수리|밑옆날|밑외경|밑날\+외경", t): part = "밑옆날(밑골수리)"
    elif re.search(r"외경연삭", t):                                   part = "외경연삭(밑날/옆날 단일작업)"
    elif re.search(r"밑날", t):                                       part = "밑날"
    else:                                                             part = "-"
    if   "고경도" in t: coat = "고경도코팅"
    elif "비코팅" in t: coat = "비코팅"
    elif "일반" in t:   coat = "일반코팅"
    elif "코팅" in t:   coat = "코팅"
    else:               coat = "비코팅"   # 🟢 제목에 코팅 표기가 없으면 비코팅 가격이다
                                          #    (한경준님 확인 2026-09-22 + price_audit.py 검증 매핑
                                          #     `^초경 E/M 외경연삭$` → ('초경','*','외경','비코팅') 등)
    return mat, fam, part, coat

def band_label(v, k):
    n = int(v) if float(v).is_integer() else v
    return f"{n}{k}" if k else str(n)

NOTE = re.compile(r"^[*※]|Long|지정치수|제작|동시작업|수량")

# 제외 — 한경준님 지시 (2026-09-22)
#   · 테이퍼: 건마다 조건이 달라 정가표로 관리하지 않는다
#   · 원통연삭: 한경준님이 따로 정리한다
EXCLUDE_TITLE = re.compile(r"TAPER|원통\s*연삭|날붙이\(BG\)\s*초경\s*BALL")

# 🔴 정가표 블록은 코너와 볼을 한 블록에 묶는다(가격 동일). 하지만 **품목명은 따로**다
#    (품목 실측: 코너 2,381 · 볼 1,357 · 라핑볼 454 · 라핑코너 124).
#    블록 이름만 쓰면 「볼」로 찾는 사람이 못 찾는다 → 품목 형상으로 전개한다.
#    「라핑」(492건)은 「라핑평」과 혼용 중인 표기이고 가격은 같은 블록이다
#    (wiki/standards/재연마-정가표-읽는법.md §1).
# 나열 순서 — 한경준님 지정 (2026-09-22)
#   초경 → HSS, 형상은 평·코너·볼 → 라핑평·라핑코너·라핑볼 → 날붙이초경 → 테이퍼
#   지정하지 않은 것(리머·원통연삭·절단·형상공통)은 그 뒤에 붙인다.
MAT_ORDER   = ["초경", "HSS", "-"]
SHAPE_ORDER = ["평", "코너", "볼",
               "라핑평", "라핑", "라핑코너", "라핑볼",
               "날붙이초경",
               "리머", "절단", "라핑 형상공통", "형상공통", "코팅단가"]
# 코팅 나열 순서 — 한경준님 지정 (2026-09-22): 비코팅 → 일반 → 고경도
# 「코팅」은 블록 제목이 일반/고경도를 구분하지 않은 것이라 맨 뒤에 둔다(성격 확인 대기).
COAT_ORDER = ["비코팅", "일반코팅", "고경도코팅", "코팅"]
def coat_key(x):  return (COAT_ORDER.index(x) if x in COAT_ORDER else 99, x)
# 가공부 나열 순서 — 한경준님 지정 (2026-09-22): 밑날 → 옆날 → 밑옆날
PART_ORDER = ["밑날", "외경연삭(밑날/옆날 단일작업)", "밑옆날(밑골수리)", "코팅 추가비용"]
def part_key(x):  return (PART_ORDER.index(x) if x in PART_ORDER else 99, x)
def blade_key(x): return (0 if x == "2날" else 1 if x == "3·4·6날" else 2, x)
def mat_key(m):   return (MAT_ORDER.index(m) if m in MAT_ORDER else 99, m)
def shape_key(x): return (SHAPE_ORDER.index(x) if x in SHAPE_ORDER else 99, x)

# 🔴 제목에 형상이 빠진 블록 — price_audit.py 의 검증된 매핑을 따른다
#    (그 매핑은 2026-09-02 품목 10,744건 대조 통과로 확인된 것이다).
#    2026-09-22 개정에서 「밑옆날 → 밑외경」으로 제목이 바뀌어 양쪽 표기를 다 받는다.
#      · `HSS 밑옆날/밑외경`      = HSS 평 (코너·볼은 별도 블록이 있다)
#      · `라핑 (평) 밑외경/밑골수리` = HSS 라핑평
#    그리고 `E/M 일반코팅/고경도코팅` 은 연삭 정가가 아니라 **코팅 추가비용** 표다
#    (날경별 단가, A95~A101·O31~O35 — 초경과 HSS 가 각각 있다).
TITLE_OVERRIDE = [
    (re.compile(r"^HSS\s*(밑옆날|밑외경)"),             (None, "평",      None)),
    (re.compile(r"^라핑\s*(평\s*)?(밑외경|밑골수리)"),  ("HSS", "라핑평",  None)),
    (re.compile(r"^E/M\s*(고경도코팅|일반코팅|코팅)$"),  (None, "코팅단가", "코팅 추가비용")),
    # `날붙이(BG) 초경 BALL E/M` — 제목에 형상·가공부가 없다.
    # 품목 `2BB1601100`(Ø16 밑날 19,000)·`2BB2501100`(Ø25 23,700)·`2BB2601100`(Ø26 30,700)
    # 3건이 이 블록 값과 일치해 **날붙이초경볼 · 밑날** 로 확정 [실측 검증 2026-09-22].
    (re.compile(r"^날붙이\(BG\)\s*초경\s*BALL"),         (None, "날붙이초경볼", "밑날")),
]

FAM_TO_SHAPES = {
    "평":            ["평"],
    "코너·볼":        ["코너", "볼"],
    "라핑 평":        ["라핑평", "라핑"],
    "라핑 형상공통":   ["라핑 형상공통"],
    "코팅단가":       ["코팅단가"],
    "날붙이초경볼":     ["날붙이초경볼"],
    "라핑 코너·볼":    ["라핑코너", "라핑볼"],
    "리머":           ["리머"],
}

def harvest(pl):
    """시트 전체를 훑어 블록을 인식하고 (블록, 행들) 로 돌려준다."""
    out, seen = [], set()
    for title, pos_list in pl.titles.items():
        if NOTE.search(title) or EXCLUDE_TITLE.search(title): continue
        for (r, c) in pos_list:
            if in_discount_zone(r, c): continue
            if (r, c) in seen: continue
            seen.add((r, c))
            recs = []
            # 세로형 먼저
            try:
                seg, cols = pl.vtable(r, c)
            except Exception:
                seg, cols = None, {}
            if seg and cols:
                # 🔴 alias_groups() 가 코팅 그룹을 별칭으로 부풀린다(감사 조회용).
                #    내보내기에서 그대로 쓰면 「일반코팅 값이 고경도로 복제」된다.
                #    → 시트 tr+1 행에 **실제로 적힌** 라벨만 남긴다.
                span = max((cc for d in cols.values()
                            for cc in (d.get("2"), d.get("4")) if cc), default=c) + 1
                literal = set()
                for cc in range(c, min(span, pl.ws.max_column) + 1):
                    vv = pl.ws.cell(r + 1, cc).value
                    if isinstance(vv, str) and canon_coat(vv.strip()):
                        literal.add(re.sub(r"\s+", "", vv.strip()))
                for g, d in cols.items():
                    if literal and re.sub(r"\s+", "", str(g)) not in literal:
                        continue
                    axis = d.get("S") or seg
                    for n_key, label in (("2", "2날"), ("4", "3·4·6날")):
                        col = d.get(n_key)
                        if not col: continue
                        for v, k, rr in axis:
                            val = pl.ws.cell(rr, col).value
                            if isinstance(val, (int, float)):
                                recs.append((g, label, band_label(v, k), round(float(val))))
            if not recs:
                try:
                    hseg, rows = pl.htable(r, c)
                except Exception:
                    hseg, rows = None, {}
                if hseg and rows:
                    # 가로형도 alias_rows() 로 부풀려져 있다 → **행 번호 기준으로 중복 제거**.
                    # 가로형 블록은 제목이 코팅을 담고 있으므로(예: `… 외경연삭 코팅`)
                    # 코팅은 제목에서 받고, 그룹 라벨은 쓰지 않는다.
                    best = {}
                    for key, rr in rows.items():
                        if key.startswith("P"): continue          # 위치 기반 중복 키
                        blade = "2날" if key.endswith("2") else ("3·4·6날" if key.endswith("4") else "-")
                        prev = best.get((rr, blade))
                        if prev is None: best[(rr, blade)] = key
                    for (rr, blade), key in sorted(best.items()):
                        for v, k, cc in hseg:
                            val = pl.ws.cell(rr, cc).value
                            if isinstance(val, (int, float)):
                                recs.append(("(제목기준)", blade, band_label(v, k), round(float(val))))
            if recs:
                out.append(((r, c), title, recs))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pricelist", default="raw/단가표/26.09 재연마정가표_정리.xlsx")
    ap.add_argument("--sheet", default="정가표(26.09)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    pl = PriceList(a.pricelist, a.sheet)
    blocks = harvest(pl)
    rev = re.search(r"\((\d{2}\.\d{2})\)", a.sheet)
    rev = rev.group(1) if rev else a.sheet
    out = a.out or f"outputs/정가표_{rev}_정리.xlsx"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    # 🔴 재질이 제목에 없는 블록이 있다 (예: `BALL, 코너R 밑날 (고경도)` — 「초경」이 빠져 있다).
    #    고경도 블록은 관례상 자기 일반코팅 짝의 **오른쪽 같은 행**에 놓인다.
    #    → 같은 행 왼쪽 → 위쪽 순으로 재질이 적힌 블록을 찾아 물려받는다.
    known = sorted(((rr, cc, attrs(t)[0]) for (rr, cc), t, _ in blocks), key=lambda x: (x[0], x[1]))
    def resolve_mat(r, c):
        same = [m for (rr, cc, m) in known if rr == r and cc < c and m != "-"]
        if same: return same[-1]
        up = [m for (rr, cc, m) in known if rr < r and m != "-"]
        return up[-1] if up else "-"

    long_rows = []
    for (r, c), title, recs in blocks:
        mat, fam, part, coat0 = attrs(title)
        t1 = re.sub(r"\s+", " ", title).strip()
        for rx, (om, of, op) in TITLE_OVERRIDE:
            if rx.match(t1):
                if om: mat = om
                if of: fam = of
                if op: part = op
                break
        if mat == "-":
            mat = resolve_mat(r, c)
        for g, blade, dia, val in recs:
            cg = canon_coat(g)
            if cg == "비코팅":     coat = "비코팅"
            elif cg == "고경도":   coat = "고경도코팅"
            elif cg == "일반":     coat = "일반코팅"
            elif cg == "코팅":
                # 그룹 라벨이 그냥 「코팅」이면 코팅 종류는 제목이 정한다
                coat = "고경도코팅" if "고경도" in title else "일반코팅"
            else:                  coat = coat0   # 제목 기준 (가로형)
            for shape in FAM_TO_SHAPES.get(fam, [fam]):
                long_rows.append([mat, shape, fam, part, coat, blade, dia, val,
                                  re.sub(r"\s+", " ", title).strip(),
                                  f"{get_column_letter(c)}{r}"])
    # 중복 제거 (같은 블록이 여러 제목으로 잡힐 수 있음)
    seen, dedup = set(), []
    for row in long_rows:
        k = tuple(row[:7])
        if k in seen: continue
        seen.add(k); dedup.append(row)
    long_rows = sorted(dedup, key=lambda x: (mat_key(x[0]), shape_key(x[1]), part_key(x[3]),
                                             coat_key(x[4]), blade_key(x[5]), _dnum(x[6])))

    wb = openpyxl.Workbook()

    # ── 요약 ──
    ws = wb.active; ws.title = "안내"
    ws["A1"] = f"재연마 정가표 {rev} — 정리본"; ws["A1"].font = F_T
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    NEW_PART = "외경연삭(밑날/옆날 단일작업)"
    info = [
        ("원본", a.pricelist, ""),
        ("원본 시트", a.sheet, ""),
        ("생성", f"{now:%Y-%m-%d %H:%M} KST", "scripts/pricelist_export.py"),
        ("", "", ""),
        ("시트 안내", "", ""),
        ("롱포맷", f"{len(long_rows)}행", "한 행 = 한 조합. 필터·피벗으로 쓰세요"),
        ("", "「품목 형상」으로 찾으세요", "정가표는 코너·볼을 한 블록에 묶지만(가격 동일) 품목명은 따로입니다 — 전개해 뒀습니다"),
        ("", "라핑 = 라핑평", "품목명에 혼용 중이며 가격은 같은 블록입니다"),
        ("조회용_초경 / 조회용_HSS", "재질별 2시트", "형상별 매트릭스(직경 × 코팅/날수). 원본 배치를 베끼지 않고 재구성"),
        ("형상 순서", "평·코너·볼 → 라핑평·라핑코너·라핑볼 → 날붙이초경 → 테이퍼", "한경준님 지정. 그 외(리머·원통연삭·절단·형상공통·코팅단가)는 뒤"),
        ("코팅 순서", "비코팅 → 일반코팅 → 고경도코팅", "한경준님 지정. 「코팅」은 블록 제목이 구분하지 않은 것이라 맨 뒤 — 성격 확인 대기"),
        ("빈 칸", "노란 「-」로 남겨 둠", "정가표에 그 조합이 없는 것입니다. 채우지 않았습니다"),
        ("블록목록", f"{len(blocks)}개", "인식한 블록과 좌표. 빠진 블록 점검용"),
        ("", "", ""),
        ("읽는 규칙 (중요)", "", ""),
        ("직경 구간", "전부 「이하」", "Ø10 → 「10이하」 · Ø10.5 → 「12이하」. 한 칸 위로 미는 실수가 가장 흔함"),
        ("날수", "3날 이상 = 4날", "정가표에는 2날·4날 행만 있음"),
        ("가공부 순서", "밑날 → 옆날 → 밑옆날", "한경준님 지정"),
        ("가공부 명칭", NEW_PART, "🔴 외경연삭은 「밑날 또는 옆날 중 한 가지만」 하는 단일작업 단가입니다 (한경준님 확인 2026-09-22)"),
        ("", "  ↳ 품목 조회 시", "가공부가 「옆날」·「골수리」면 이 블록을 봅니다. 「밑날」은 별도 밑날 블록이 있습니다"),
        ("", "  ↳ 예외 (블록 주석)", "HSS 라핑: 「밑날가격 = 옆날가격」 → 밑날도 이 블록 / 초경 라핑: 「밑날 = 초경밑날 × 1.1」"),
        ("", "밑옆날(밑골수리)", "= 밑옆날 = 밑골수리 = 밑외경. 개정마다 이름이 바뀜 — 같은 가공"),
        ("금액 성격", "정가 (공표)", "대외비 아님. 할인 적용가·견적 금액이 대외비"),
        ("", "", ""),
        ("제외 항목", "테이퍼 · 원통연삭 · 날붙이초경볼", "한경준님 지시 — 테이퍼는 건마다 조건이 달라 정가표 관리 대상 아님, 원통연삭은 별도 정리"),
        ("", "", ""),
        ("⚠️ 이 파일은 스냅샷입니다", "정가표가 바뀌면 다시 돌리세요", "python scripts/pricelist_export.py"),
    ]
    r = 3
    for k, v, note in info:
        ws.cell(r, 1, k); ws.cell(r, 2, v); ws.cell(r, 3, note)
        f = F_S if (k and not v and not note) else F_B
        for cc in (1, 2, 3):
            ws.cell(r, cc).font = f
            ws.cell(r, cc).alignment = Alignment(vertical="center", wrap_text=True)
        r += 1
    for col, w in zip("ABC", (24, 34, 62)): ws.column_dimensions[col].width = w

    # ── 롱포맷 ──
    ws = wb.create_sheet("롱포맷")
    hdr = ["재질", "품목 형상", "정가표 계열", "가공부", "코팅", "날수", "직경구간", "정가",
           "원본 블록 제목", "위치"]
    for i, h in enumerate(hdr, 1):
        cc = ws.cell(1, i, h); cc.font = F_BH; cc.fill = FILL_H; cc.border = BD
        cc.alignment = Alignment(horizontal="center")
    for j, row in enumerate(long_rows, 2):
        for i, v in enumerate(row, 1):
            cc = ws.cell(j, i, v); cc.font = F_B; cc.border = BD
            if i == 8: cc.number_format = "#,##0"
    for col, w in zip("ABCDEFGHIJ", (8, 12, 14, 24, 14, 11, 12, 12, 46, 8)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:J{len(long_rows)+1}"

    # ── 조회용 매트릭스 ──
    bymat = collections.OrderedDict()
    for row in long_rows:
        bymat.setdefault(row[0], collections.OrderedDict()).setdefault(row[1], []).append(row)
    for mat in sorted(bymat, key=mat_key):
      groups = collections.OrderedDict(
          (k, bymat[mat][k]) for k in sorted(bymat[mat], key=shape_key))
      ws = wb.create_sheet(f"조회용_{mat}")
      ws["A1"] = f"조회용 · {mat} — 형상별 정가 ({rev})"; ws["A1"].font = F_T
      ws["A2"] = ("직경 구간은 전부 「이하」입니다. 3날 이상은 4날 값을 씁니다. "
                  "나열 순서: 평·코너·볼 → 라핑평·라핑코너·라핑볼 → 날붙이초경 → 테이퍼 → 그 외"); ws["A2"].font = F_B
      r = 4
      for fam, rows in groups.items():
        ws.cell(r, 1, f"{mat} · {fam}").font = F_S
        ws.cell(r, 1).fill = FILL_G
        r += 1
        for part in sorted({x[3] for x in rows}, key=part_key):
            sub = [x for x in rows if x[3] == part]
            ws.cell(r, 1, part).font = F_BH; r += 1
            combos = sorted({(x[4], x[5]) for x in sub},
                            key=lambda t: (coat_key(t[0]), blade_key(t[1])))
            dias = sorted({x[6] for x in sub}, key=_dnum)
            ws.cell(r, 1, "직경").font = F_BH; ws.cell(r, 1).fill = FILL_H; ws.cell(r, 1).border = BD
            for i, (coat, blade) in enumerate(combos, 2):
                cc = ws.cell(r, i, f"{coat}\n{blade}"); cc.font = F_BH; cc.fill = FILL_H; cc.border = BD
                cc.alignment = Alignment(horizontal="center", wrap_text=True)
            r += 1
            lut = {(x[6], x[4], x[5]): x[7] for x in sub}
            for d in dias:
                cc = ws.cell(r, 1, d); cc.font = F_B; cc.border = BD
                for i, (coat, blade) in enumerate(combos, 2):
                    v = lut.get((d, coat, blade))
                    c2 = ws.cell(r, i, v if v is not None else "-")
                    c2.font = F_B; c2.border = BD; c2.number_format = "#,##0"
                    if v is None: c2.fill = FILL_W
                r += 1
            r += 1
        r += 1
      ws.column_dimensions["A"].width = 14
      for i in range(2, 14): ws.column_dimensions[get_column_letter(i)].width = 15
      ws.freeze_panes = "B5"

    # ── 블록목록 ──
    ws = wb.create_sheet("블록목록")
    ws["A1"] = "인식한 블록"; ws["A1"].font = F_T
    ws["A2"] = "빠진 블록이 있으면 제목이 개정된 것입니다 — price_audit.py 의 패턴도 같이 고쳐야 합니다."; ws["A2"].font = F_B
    hdr = ["위치", "블록 제목", "재질", "계열", "가공부", "코팅", "추출 행수"]
    for i, h in enumerate(hdr, 1):
        cc = ws.cell(4, i, h); cc.font = F_BH; cc.fill = FILL_H; cc.border = BD
    for j, ((rr, cc0), title, recs) in enumerate(sorted(blocks, key=lambda x: (x[0][1], x[0][0])), 5):
        mat, fam, part, coat = attrs(title)
        for i, v in enumerate([f"{get_column_letter(cc0)}{rr}", re.sub(r'\s+',' ',title).strip(),
                               mat, fam, part, coat, len(recs)], 1):
            c2 = ws.cell(j, i, v); c2.font = F_B; c2.border = BD
    for col, w in zip("ABCDEFG", (9, 50, 8, 14, 24, 14, 10)): ws.column_dimensions[col].width = w
    ws.freeze_panes = "A5"

    wb.save(out)
    print(f"저장: {out}")
    print(f"  블록 {len(blocks)}개 · 롱포맷 {len(long_rows)}행 · 조회용 그룹 {len(groups)}개")
    if pl.errors:
        print(f"  🔴 원본 오류값 {len(pl.errors)}곳: " +
              ", ".join(f"{get_column_letter(c)}{r}" for r, c, _ in pl.errors[:8]))

def _dnum(s):
    m = re.match(r"([\d.]+)", str(s))
    return float(m.group(1)) if m else 9999.0

if __name__ == "__main__":
    main()
