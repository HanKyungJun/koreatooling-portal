# -*- coding: utf-8 -*-
"""월간 출하현황 마감 — ERP 출하 조회 저장본으로 월별분석 xlsx 의 해당 월을 채운다 (2026-11-10 신설, Cowork)

입력: erp/snapshot/shipment_YYYY-MM.csv  (erp/probe_shipment.py 가 저장. 재연마 출하등록 lem120_jae_g00 상세)
      2026-09 를 TricoERP export 와 대조해 출고 1,358 · 출고합계 1,423 · 연마불가 65 · 납품처 29곳 전부 일치 확인 [실측 검증]
집계: 납품처명(cust_nm) 기준, 출고 = mov_own_qty (= 출고합계 mov_qty − 연마불가 bad_qty). 2026-08-05 (3) · 10-01 방식과 같다.
대상: 실명판 wiki/_private/comparisons/출하현황_납품처별_월별분석_YYYY.xlsx 를 읽어
      ① 요약 해당 월 열 · 연간합계 순 재랭킹 ② 해당 월 시트 새로 작성 ③ 다른 월 시트 연간합계(F) 갱신
      → 공개 경로에 쓰고 anonymize_public.publish() 로 실명판은 _private, 공개판은 익명화.
기존 월 값은 바꾸지 않는다. 기본은 점검만(드라이런). --apply 일 때만 쓰고, 쓰기 전 .bak_YYYYMMDD 를 남긴다.

  python scripts/ship_month_close.py 2026-10            점검만
  python scripts/ship_month_close.py 2026-10 --apply    반영
"""
import sys, io, shutil
from copy import copy
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd
import openpyxl

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

ym = sys.argv[1] if len(sys.argv) > 1 else ""
apply = "--apply" in sys.argv
y, m = int(ym[:4]), int(ym[5:7])
MON = f"{m}월"
SRC = BASE / "erp" / "snapshot" / f"shipment_{ym}.csv"
NAME = f"출하현황_납품처별_월별분석_{y}.xlsx"
PRIV = BASE / "wiki" / "_private" / "comparisons" / NAME
PUB = BASE / "wiki" / "comparisons" / NAME

s = pd.read_csv(SRC, encoding="utf-8-sig")
bad = pd.to_numeric(s["bad_qty"], errors="coerce").fillna(0)
mis = ((s["mov_qty"] - bad - s["mov_own_qty"]).abs() > 0.01).sum()
dts = pd.to_datetime(s["out_dt"].astype(str).str[:10])
assert (dts.dt.year == y).all() and (dts.dt.month == m).all(), "다른 달 행이 섞여 있음"
g = s.groupby("cust_nm")["mov_own_qty"].sum()
g = g[g > 0]
print(f"[원본] {SRC.relative_to(BASE)} · {len(s)}행 · 출하일 {dts.min():%m-%d} ~ {dts.max():%m-%d} ({dts.dt.date.nunique()}일)")
print(f"  출고합계 {s['mov_qty'].sum():,.0f} − 연마불가 {bad.sum():,.0f} = 출고 {s['mov_own_qty'].sum():,.0f} · 납품처 {len(g)}곳 · 행 불일치 {mis}")

wb = openpyxl.load_workbook(PRIV)
ws = wb["요약"]
hdr = [c.value for c in ws[2]]
col = hdr.index(MON) + 1
first, last = 3, None
for r in range(3, ws.max_row + 1):
    if ws.cell(r, 1).value == "합계":
        last = r - 1
        break
rows = []
for r in range(first, last + 1):
    rows.append([ws.cell(r, 2).value] + [ws.cell(r, c).value or 0 for c in range(3, 15)])
before = {row[0]: list(row[1:]) for row in rows}
names = [row[0] for row in rows]
new = [n for n in g.index if n not in names]
nz = [n for n in names if (before[n][m - 1] or 0) != 0]
print(f"[요약] 납품처 {len(rows)}곳 · 새 납품처 {len(new)}곳 {new} · 기존 {MON} 값 있는 곳 {len(nz)}")
if nz:
    print("  ✖ 요약에 이미 이 달 값이 있음 — 덮어쓰지 않고 멈춤"); sys.exit(1)
for n in new:
    rows.append([n] + [0] * 12)
for row in rows:
    row[m] = float(g.get(row[0], 0))
order = sorted(range(len(rows)), key=lambda i: -sum(rows[i][1:]))  # 안정 정렬: 동률은 기존 순서
rows = [rows[i] for i in order]
annual = {row[0]: sum(row[1:]) for row in rows}
top = g.sort_values(ascending=False, kind="stable")
print(f"  {MON} 상위 5: " + " · ".join(f"{k} {v:,.0f}" for k, v in top.head(5).items()))
print(f"  {y} 누적 1~{m}월 {sum(annual.values()):,.0f}개")
if not apply:
    print("\n(점검만 — 반영하려면 --apply)"); sys.exit(0)

# ── 반영 ──
tag = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d")  # KST (VM 은 UTC)
for p in (PRIV, PUB):
    b = p.with_name(p.name + f".bak_{tag}")
    if not b.exists():
        shutil.copy2(p, b)
if new:
    tot_r = last + 1
    ws.insert_rows(tot_r, len(new))
    for k in range(len(new)):
        for c in range(1, 17):
            ws.cell(tot_r + k, c)._style = copy(ws.cell(last, c)._style)
    last += len(new)
    for c in range(3, 16):
        L = openpyxl.utils.get_column_letter(c)
        ws.cell(last + 1, c).value = f"=SUM({L}3:{L}{last})"
for k, row in enumerate(rows):
    r = first + k
    ws.cell(r, 1).value = k + 1
    ws.cell(r, 2).value = row[0]
    for j in range(12):
        v = row[1 + j]
        ws.cell(r, 3 + j).value = int(v) if float(v).is_integer() else v
    ws.cell(r, 15).value = f"=SUM(C{r}:N{r})"
    ws.cell(r, 16).value = f"=O{r}/O${last + 1}"

# 해당 월 시트 — 9월 시트 서식 복사
ref = wb[f"{m - 1}월"] if m > 1 else None
sh = wb[MON]
for mr in list(sh.merged_cells.ranges):
    sh.unmerge_cells(str(mr))
sh.delete_rows(1, sh.max_row)
n = len(top)
tot = 3 + n
sh.cell(1, 1).value = f"{y}년 {m}월 출하현황 — 납품처별 출고량  (단위: 개)"
for c in range(1, 7):
    sh.cell(1, c)._style = copy(ref.cell(1, c)._style)
    sh.cell(2, c)._style = copy(ref.cell(2, c)._style)
for c, v in enumerate(["순위", "납품처명", f"{m}월 출고(개)", "월간비율(%)", "누적비율(%)", "연간합계(개)"], 1):
    sh.cell(2, c).value = v
for k, (nm, q) in enumerate(top.items()):
    r = 3 + k
    src = 3 if k < 5 else 8
    for c in range(1, 7):
        sh.cell(r, c)._style = copy(ref.cell(src, c)._style)
    sh.cell(r, 1).value = k + 1
    sh.cell(r, 2).value = nm
    sh.cell(r, 3).value = int(q)
    sh.cell(r, 4).value = f"=C{r}/C${tot}"
    sh.cell(r, 5).value = "=D3" if k == 0 else f"=E{r - 1}+D{r}"
    sh.cell(r, 6).value = int(annual[nm])
rt = ref.max_row
for c in range(1, 7):
    sh.cell(tot, c)._style = copy(ref.cell(rt, c)._style)
sh.cell(tot, 1).value = "합계"
sh.cell(tot, 3).value = f"=SUM(C3:C{tot - 1})"
sh.cell(tot, 4).value = 1
sh.cell(tot, 6).value = f"=SUM(F3:F{tot - 1})"
sh.merge_cells("A1:F1")
sh.merge_cells(f"A{tot}:B{tot}")
sh.freeze_panes = "B3"
for L, d in ref.column_dimensions.items():
    sh.column_dimensions[L].width = d.width

# 다른 월 시트 연간합계(F) 갱신
fchg = 0
for k in range(1, 13):
    if k == m or f"{k}월" not in wb.sheetnames:
        continue
    w = wb[f"{k}월"]
    for r in range(3, w.max_row + 1):
        nm = w.cell(r, 2).value
        if nm in annual and isinstance(w.cell(r, 6).value, (int, float)):
            v = int(annual[nm])
            if w.cell(r, 6).value != v:
                w.cell(r, 6).value = v
                fchg += 1
wb.save(PUB)
print(f"[반영] 요약 {MON} 열 · 재랭킹 · {MON} 시트 {n}곳 · 다른 월 연간합계 {fchg}칸 → {PUB.relative_to(BASE)}")
from anonymize_public import publish
publish(str(PUB.relative_to(BASE)))
