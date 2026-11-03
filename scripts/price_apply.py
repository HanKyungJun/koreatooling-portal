#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정가표 대조 결과로 품목 파일의 기준단가를 정정한다 (라핑 계열만, 기본값).

🔴 왜 openpyxl 로 저장하지 않는가 (wiki/standards/재연마-정가표-읽는법.md §8):
   openpyxl 로 다시 저장하면 **x14 드롭다운(dataValidation) 22건이 사라진다.**
   그래서 zip 을 직접 열어 `xl/worksheets/sheet1.xml` 의 해당 셀 <v> 만 고치고,
   나머지 엔트리는 **바이트 그대로** 재포장한다.

⚠️ 원본은 수정하지 않는다. `_완료.xlsx` 사본을 새로 만든다.
⚠️ 기본은 --only-lap (라핑만). 비라핑은 의도된 값일 수 있어 건드리지 않는다.

사용:
  python scripts/price_apply.py                # 드라이런 (파일 안 만듦)
  python scripts/price_apply.py --apply        # 실제 생성
"""
import argparse, collections, datetime, os, re, shutil, sys, zipfile
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from price_audit import PriceList, Blocks, parse_name, SHEET_ITEMS, ROW_START, \
                        COL_CODE, COL_NAME, COL_PRICE
from openpyxl.utils import get_column_letter

PRICE_COL = get_column_letter(COL_PRICE)      # = 'AB'

def targets(path, bl, only_lap=True):
    """(행 → 새 단가) 와 상세 내역."""
    ws = openpyxl.load_workbook(path, data_only=True)[SHEET_ITEMS]
    plan, detail = {}, []
    for r in range(ROW_START, ws.max_row + 1):
        nm = ws.cell(r, COL_NAME).value
        pr = ws.cell(r, COL_PRICE).value
        if not nm or not isinstance(pr, (int, float)): continue
        p = parse_name(nm)
        if not p: continue
        if only_lap and "라핑" not in p["shape"]: continue
        try: exp = bl.expect(**p)
        except Exception: exp = None
        if exp is None: continue
        exp = round(exp)
        if round(pr) == exp: continue
        plan[r] = exp
        detail.append((r, ws.cell(r, COL_CODE).value, str(nm), round(pr), exp))
    return plan, detail

CELL = re.compile(rf'<c r="{PRICE_COL}(\d+)"([^>]*?)(/>|>(.*?)</c>)', re.S)

def rewrite_sheet(xml, plan):
    hit = [0]
    def sub(m):
        r = int(m.group(1))
        if r not in plan: return m.group(0)
        attrs, tail, inner = m.group(2), m.group(3), m.group(4)
        if tail == "/>":                      # 빈 셀 — 대상이 아니어야 한다
            return m.group(0)
        if "<f" in (inner or ""):             # 수식 셀은 건드리지 않는다
            return m.group(0)
        new = re.sub(r'<v>[^<]*</v>', f'<v>{plan[r]}</v>', inner, count=1)
        if new == inner: return m.group(0)
        hit[0] += 1
        return f'<c r="{PRICE_COL}{r}"{attrs}>{new}</c>'
    return CELL.sub(sub, xml), hit[0]

def repack(src, dst, plan):
    zin = zipfile.ZipFile(src)
    xml = zin.read("xl/worksheets/sheet1.xml").decode("utf-8")
    dv_before = xml.count("x14:dataValidation")
    new_xml, hits = rewrite_sheet(xml, plan)
    dv_after = new_xml.count("x14:dataValidation")
    same_bytes = 0
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for zi in zin.infolist():
            data = zin.read(zi.filename)
            if zi.filename == "xl/worksheets/sheet1.xml":
                data = new_xml.encode("utf-8")
            else:
                same_bytes += 1
            zo = zipfile.ZipInfo(zi.filename, date_time=zi.date_time)
            zo.compress_type = zi.compress_type
            zo.external_attr = zi.external_attr
            zout.writestr(zo, data)
    zin.close()
    return hits, dv_before, dv_after, same_bytes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="raw/단가표/260922 단가 검수")
    ap.add_argument("--pricelist", default="raw/단가표/26.09 재연마정가표_정리.xlsx")
    ap.add_argument("--sheet", default="정가표(26.09)")
    ap.add_argument("--apply", action="store_true", help="실제로 _완료.xlsx 를 만든다")
    ap.add_argument("--all", action="store_true", help="라핑 외 계열까지 정정 (기본: 라핑만)")
    a = ap.parse_args()

    pl = PriceList(a.pricelist, a.sheet); bl = Blocks(pl)
    if bl.missing:
        sys.exit(f"🔴 못 찾은 블록 {len(bl.missing)}개 — 먼저 제목 패턴을 맞추세요")
    print(f"정가표 {os.path.basename(a.pricelist)} / {a.sheet}")
    print(f"대상  {'전 계열' if a.all else '라핑 계열만'}   모드 {'APPLY' if a.apply else 'DRY-RUN'}\n")

    tot = 0
    for fn in sorted(f for f in os.listdir(a.dir)
                     if f.endswith(".xlsx") and not f.startswith("~$") and "_완료" not in f):
        src = os.path.join(a.dir, fn)
        plan, detail = targets(src, bl, only_lap=not a.all)
        tot += len(plan)
        up = sum(1 for *_ , c, e in detail if e > c)
        dn = len(detail) - up
        print(f"  {fn}")
        print(f"     정정 대상 {len(plan):>5}건  (인상 {up} · 인하 {dn})")
        if not plan: continue
        if not a.apply:
            for r, code, nm, cur, exp in detail[:3]:
                print(f"       r{r:<6} {code:<14} {nm[:34]:<36} {cur:>7,} → {exp:>7,}")
            continue
        dst = os.path.join(a.dir, fn.replace(".xlsx", "_완료.xlsx"))
        hits, dvb, dva, same = repack(src, dst, plan)
        ok = (hits == len(plan)) and (dvb == dva)
        print(f"     → {os.path.basename(dst)}")
        print(f"        치환 {hits}/{len(plan)} {'✅' if hits==len(plan) else '🔴'}"
              f" · 드롭다운 {dvb}→{dva} {'✅' if dvb==dva else '🔴'}"
              f" · 그대로 복사된 엔트리 {same}개")
        if not ok: sys.exit("🔴 검증 실패 — 중단합니다")
    print(f"\n합계 {tot}건")
    if not a.apply: print("드라이런입니다. 실제 반영은 --apply")

if __name__ == "__main__":
    main()
