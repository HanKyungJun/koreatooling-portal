"""parse_tom.py — ANCA .tom 165개 파일 일괄 파싱"""
import xml.etree.ElementTree as ET, re, csv
from pathlib import Path
from collections import Counter, defaultdict

TOOL_DIR = Path("/sessions/modest-bold-wright/mnt/cnc-wiki/.claude/worktrees/hardcore-hermann-b67cf1/raw/tool")
OUT_CSV  = Path("/sessions/modest-bold-wright/mnt/outputs/tom_summary.csv")
OUT_MD   = Path("/sessions/modest-bold-wright/mnt/cnc-wiki/wiki/tools/anca-tom-파일-분석.md")

def guess_dia(stem):
    s = re.sub(r'^(\d{6}|\d{8})_', '', stem.upper())
    m = re.match(r'^[2-9]?[A-Z]+(\d{3})', s)
    if m:
        v = int(m.group(1))
        if 10 <= v <= 250:
            return f"{v//10}.{v%10}"
    for raw in re.findall(r'(?<![0-9])(\d{3})(?![0-9])', s):
        v = int(raw)
        if 10 <= v <= 200:
            return f"{v//10}.{v%10}"
    return ""

def guess_type(rel):
    p, fname = rel.upper(), Path(rel).stem.upper()
    if "ANCA교육" in rel or ("ANCA" in p and "교육" in rel): return "교육/샘플"
    if "/SAMPLE" in p or p.startswith("SAMPLE"): return "샘플"
    if "RE GRIND" in p or "REGRIND" in p: return "재연마"
    if "/RE/" in p or p.startswith("RE/"): return "재연마(특수)"
    if "BALL" in fname or fname.endswith("BA"): return "볼엔드밀"
    if "CONNER" in fname or "CORNER" in fname or fname.endswith("CO"): return "코너R엔드밀"
    if "SQ" in fname or "FL" in fname or "FLAT" in fname: return "플랫엔드밀"
    if "2NC" in fname or fname.endswith("NC"): return "NC드릴"
    if "2DR" in fname or fname.endswith("DR"): return "드릴"
    if "CEN" in fname: return "센터드릴"
    if "UF" in fname: return "울트라파인엔드밀"
    if "KCS" in fname: return "KCS플랫엔드밀"
    if fname[:4] in ("5FL_","5FSQ","5FCO"): return "5날엔드밀"
    if fname.startswith("6F"): return "6날엔드밀"
    if fname.startswith("3F") or "3CEN" in fname: return "3날"
    if fname.startswith("2F"): return "2날엔드밀"
    if fname.startswith("4F") or "4UF" in fname: return "4날엔드밀"
    return "기타"

def guess_flutes(rel):
    fname, folder = Path(rel).stem.upper(), rel.upper()
    for n in ["6F","5F","4F","3F","2F"]:
        if n in fname or "/"+n in folder: return n[0]
    if "2DR" in folder or "2NC" in folder: return "2"
    return ""

def extract_param(root, tag):
    for p in root.iter("Parameter"):
        if p.get("tag") == tag:
            v = p.find(".//value")
            if v is not None and v.text:
                t = v.text.strip()
                if re.match(r"^\d+,", t):
                    idx = int(t.split(",")[0])
                    opts = t.split(",")[1:]
                    return opts[idx] if idx < len(opts) else opts[0]
                return t
    return ""

def parse_tom(fp):
    try:
        root = ET.parse(fp).getroot()
    except ET.ParseError as e:
        return {"parse_error": str(e)}
    info = root.find("Info")
    ts = info.findtext("timestamp","") if info is not None else ""
    tool_el = root.find(".//Tool")
    tool_name = tool_el.findtext("name","") if tool_el is not None else ""
    tt_el = root.find(".//ToolType/filename")
    tooltype = tt_el.text if tt_el is not None else ""
    ab_helix = extract_param(root,"abs_helix") or extract_param(root,"helix")
    pt_angle = extract_param(root,"point_angle")
    fg_len   = extract_param(root,"fg_length") or extract_param(root,"od_length")
    overhang = extract_param(root,"overhang_length")
    f_core   = extract_param(root,"final_core_diam")
    i_core   = extract_param(root,"init_core_diam") or extract_param(root,"core_dia_dig")
    pri_mode = extract_param(root,"pri_wh_rpm_not_surface_speed")
    wh_mode  = extract_param(root,"wh_rpm_not_surface_speed")
    if "surface speed" in (pri_mode, wh_mode):
        wh_spd = extract_param(root,"pri_wh_surface_speed") or extract_param(root,"wh_surface_speed")
        wh_unit = "m/s"
    else:
        wh_spd = extract_param(root,"pri_wh_rpm") or extract_param(root,"wh_rpm")
        wh_unit = "RPM"
    feedrate = extract_param(root,"feedrate_per_pass") or extract_param(root,"bottom_feedrate_per_pass")
    coolant  = extract_param(root,"coolant_pressure")
    cut_type = extract_param(root,"cut_type")
    return dict(timestamp=ts, tool_name=tool_name, tooltype=tooltype,
                abs_helix_deg=ab_helix, point_angle_deg=pt_angle,
                fg_length_mm=fg_len, overhang_mm=overhang,
                final_core_diam_mm=f_core, init_core_diam_mm=i_core,
                wh_speed=wh_spd, wh_speed_unit=wh_unit,
                feedrate_mm_min=feedrate, coolant_press=coolant, cut_type=cut_type)

def main():
    files = sorted(TOOL_DIR.rglob("*.tom"))
    print(f"발견: {len(files)}개")
    rows, errors = [], []
    for f in files:
        rel = str(f.relative_to(TOOL_DIR))
        d = parse_tom(f)
        if "parse_error" in d:
            errors.append((rel, d["parse_error"])); continue
        dia = guess_dia(f.stem) or guess_dia(Path(rel).parts[0] if len(Path(rel).parts)>1 else f.stem)
        rows.append({"파일경로":rel,"추정공구타입":guess_type(rel),"추정날수":guess_flutes(rel),"추정직경_mm":dia,**d})
    print(f"성공: {len(rows)}개, 오류: {len(errors)}개")
    for f,e in errors: print(f"  오류: {f} — {e}")

    # CSV
    fields = ["파일경로","추정공구타입","추정날수","추정직경_mm",
              "timestamp","tool_name","tooltype",
              "abs_helix_deg","point_angle_deg","fg_length_mm","overhang_mm",
              "final_core_diam_mm","init_core_diam_mm",
              "wh_speed","wh_speed_unit","feedrate_mm_min","coolant_press","cut_type"]
    with open(OUT_CSV,"w",newline="",encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"CSV: {OUT_CSV}")

    # 통계
    type_cnt = Counter(r["추정공구타입"] for r in rows)
    dia_cnt  = Counter(r["추정직경_mm"]  for r in rows if r["추정직경_mm"])
    spd_vals = [float(r["wh_speed"]) for r in rows if r["wh_speed"] and r["wh_speed_unit"]=="m/s"]
    feed_vals= [float(r["feedrate_mm_min"]) for r in rows if r["feedrate_mm_min"]]
    hx_vals  = [float(r["abs_helix_deg"]) for r in rows if r["abs_helix_deg"]]

    print("\n=== 공구 타입 ===")
    for t,c in type_cnt.most_common(): print(f"  {t}: {c}")
    print("\n=== 직경 분포 ===")
    for d,c in sorted(dia_cnt.items(), key=lambda x: float(x[0])): print(f"  Ø{d}mm: {c}")
    if spd_vals: print(f"\n=== Vc (m/s) ===  범위:{min(spd_vals):.1f}~{max(spd_vals):.1f}  평균:{sum(spd_vals)/len(spd_vals):.1f}")
    if feed_vals: print(f"=== 피드 (mm/min) ===  범위:{min(feed_vals):.1f}~{max(feed_vals):.1f}  평균:{sum(feed_vals)/len(feed_vals):.1f}")
    if hx_vals: print(f"=== 헬릭스 각도 ===  {sorted(set(round(h) for h in hx_vals))}")

    # Wiki 마크다운 생성
    md_lines = []
    md_lines += [
        "---",
        'type: tool',
        'category: "ANCA .tom 파일 분석"',
        'tags: [ANCA, tom, 공구프로그램, 연삭조건, 분석]',
        'sources: []',
        'updated: 2026-06-17',
        "---",
        "",
        "# ANCA .tom 파일 전체 분석",
        "",
        "> 자동 생성: `scripts/parse_tom.py` (2026-06-17)",
        "> 분석 대상: `raw/tool/` 전체 165개 .tom 파일 (ANCA ToolRoom XML)",
        "> 신뢰도: **사내 경험값** — ANCA ToolRoom에 저장된 실제 사용 연삭 프로그램에서 추출",
        "",
        "---",
        "",
        "## 1. 파일 현황",
        "",
        f"- 전체: **{len(files)}개**",
        f"- 파싱 성공: **{len(rows)}개**",
        f"- 파싱 오류 (손상 파일): **{len(errors)}개** (ANCA 교육 연습 파일 — 위키 데이터 제외)",
        "",
        "## 2. 공구 타입별 수량",
        "",
        "| 공구 타입 | 수량 |",
        "|-----------|------|",
    ]
    for t,c in type_cnt.most_common():
        md_lines.append(f"| {t} | {c}개 |")
    md_lines += [
        "",
        "## 3. 직경 분포",
        "",
        "| 직경 | 파일 수 |",
        "|------|--------|",
    ]
    for d,c in sorted(dia_cnt.items(), key=lambda x: float(x[0])):
        md_lines.append(f"| Ø{d} mm | {c}개 |")
    md_lines += [""]

    if spd_vals:
        slow = [v for v in spd_vals if v < 18]
        ok   = [v for v in spd_vals if 18 <= v <= 25]
        fast = [v for v in spd_vals if v > 25]
        md_lines += [
            "## 4. 휠 원주속도 (Vc) 분포",
            "",
            f"> Resin Bond Diamond 권장: 18~25 m/s — **전체 {len(spd_vals)}개 파일 기준**",
            "",
            f"- 범위: {min(spd_vals):.1f} ~ {max(spd_vals):.1f} m/s",
            f"- 평균: {sum(spd_vals)/len(spd_vals):.1f} m/s",
            f"- 정상 구간 (18~25 m/s): **{len(ok)}개** ✅",
            f"- 18 m/s 미만: {len(slow)}개",
            f"- 25 m/s 초과: {len(fast)}개",
            "",
        ]

    if feed_vals:
        feed_set = sorted(set(round(v,1) for v in feed_vals))
        md_lines += [
            "## 5. 피드레이트 (mm/min)",
            "",
            f"- 범위: {min(feed_vals):.1f} ~ {max(feed_vals):.1f} mm/min",
            f"- 사용 값: {feed_set}",
            "",
        ]

    if hx_vals:
        hx_cnt = Counter(round(h) for h in hx_vals)
        md_lines += [
            "## 6. 헬릭스 각도 분포",
            "",
            "| 헬릭스 각도 | 파일 수 |",
            "|------------|--------|",
        ]
        for h,c in sorted(hx_cnt.items()):
            md_lines.append(f"| {h}° | {c}개 |")
        md_lines += [""]

    # 타입별 상세표
    md_lines += [
        "## 7. 공구 타입별 연삭 조건 상세",
        "",
        "> 신뢰도: **사내 경험값** (실측 검증 미완 — ANCA ToolRoom 저장 프로그램 추출)",
        "",
    ]
    by_type = defaultdict(list)
    for r in rows: by_type[r["추정공구타입"]].append(r)
    priority = ["볼엔드밀","코너R엔드밀","플랫엔드밀","NC드릴","드릴","4날엔드밀","2날엔드밀","센터드릴"]
    order = priority + [t for t in type_cnt if t not in priority]
    for ttype in order:
        tr = by_type.get(ttype, [])
        if not tr: continue
        md_lines.append(f"### {ttype} ({len(tr)}개)")
        md_lines.append("")
        md_lines.append("| 파일 | 직경 | 날수 | 헬릭스° | Point° | 플루트길이 mm | 오버행 mm | Vc m/s | 피드 mm/min |")
        md_lines.append("|------|------|------|--------|-------|------------|---------|--------|-----------|")
        for r in sorted(tr, key=lambda x: (x["추정직경_mm"], x["파일경로"])):
            vc = f"{float(r['wh_speed']):.1f}" if r["wh_speed"] and r["wh_speed_unit"]=="m/s" else r.get("wh_speed","")
            fname = r["파일경로"]
            md_lines.append(f"| `{fname}` | Ø{r['추정직경_mm']} | {r['추정날수']}F | {r['abs_helix_deg']} | {r['point_angle_deg']} | {r['fg_length_mm']} | {r['overhang_mm']} | {vc} | {r['feedrate_mm_min']} |")
        md_lines.append("")

    if errors:
        md_lines += ["## 8. 파싱 오류 파일", ""]
        for f,e in errors: md_lines.append(f"- `{f}`: {e}")
        md_lines.append("")

    md_lines += [
        "## 9. 관련 페이지",
        "",
        "- [[tools/wheels/index|연삭 휠 리스트]]",
        "- [[원통연마-휠-12도-스펙|원통연마 12도 휠]]",
        "- [[cadcam/anca-feedrate-gx7-fastgrind|ANCA 피드레이트]]",
        "- [[공구-수명-관리]]",
        "",
        "> CSV 전체 데이터: `outputs/tom_summary.csv`",
    ]

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))
    print(f"Wiki MD: {OUT_MD}")

if __name__ == "__main__":
    main()
