# -*- coding: utf-8 -*-
"""ERP 작업실적(설비 · 시각 · 양품/불량) 줄 단위 조회 — 읽기 전용 (2026-10-23, Cowork)

Fiddler 캡처(outputs/fiddler/ppc120_20261023.saz, 생산실적 등록 화면)로 확인한 조회 3단계:
  PPC120_g00 (@fr_dt @to_dt …)          → 작업지시 목록 (wo_no)
  PPC120_g10 (@wo_no @dn_bc @capsule_mng_no @co_cd) → 작업지시 공정현황 (wo_id · prc_cd · mc_cd)
  PPC120_g20 (@wo_id[BigInt] @ent_bc='PP270100')    → 작업실적 줄 (work_dt · mc_cd · fr_tm · to_tm · pw_tm · ok_qty · bad_in_qty …)

- FillDataSetEx(조회)만 쓴다. ExecuteNonQuerys(저장)는 절대 부르지 않는다.
- 가격 컬럼은 trico_client 기본 차단. 거래처명은 결과 파일에 넣지 않는다.
- 결과: outputs/erp_pw_<시작>_<끝>.csv (outputs/ 는 .gitignore) + erp/probe_pw_detail_result.txt
실행 (cnc-wiki 폴더에서): python erp\\probe_pw_detail.py [시작일 끝일]   예) python erp\\probe_pw_detail.py 2026-10-01 2026-10-23
"""
import sys, os, io, time
from datetime import date, datetime, timedelta
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pandas as pd
import trico_client as tc
import warnings, builtins
from trico_client import TricoClient

# @wo_id 는 화면이 BigInt(long)로 보낸다 — int 값이면 long 으로 내보내도록 이 스크립트 안에서만 바꾼다(원본 파일은 그대로)
_orig = TricoClient._param_xml
def _param_xml(self, name, value, size=0, type_="NVarChar"):
    if isinstance(value, int) and not isinstance(value, bool):
        return (f'<a:SQLArray><a:ParamaterDataTable i:nil="true"/><a:ParamaterDirection>Input</a:ParamaterDirection>'
                f'<a:ParamaterName>{tc._esc(name)}</a:ParamaterName><a:ParamaterPrecision>0</a:ParamaterPrecision>'
                f'<a:ParamaterScale>0</a:ParamaterScale><a:ParamaterSize>0</a:ParamaterSize>'
                f'<a:ParamaterValue i:type="b:long" xmlns:b="{tc.NS_XSD}">{value}</a:ParamaterValue>'
                f'<a:Paramatertype>BigInt</a:Paramatertype><a:Paramatertypename/></a:SQLArray>')
    return _orig(self, name, value, size, type_)
TricoClient._param_xml = _param_xml

fr = sys.argv[1] if len(sys.argv) > 2 else date.today().replace(day=1).strftime("%Y-%m-%d")
to = sys.argv[2] if len(sys.argv) > 2 else date.today().strftime("%Y-%m-%d")
# 2026-10-23 수정: g00 의 기간은 「작업지시일」 기준이라, 9월에 낸 지시를 10월에 가공한 실적이 빠졌다(10-01 ~ 10-07 이 0 으로 나온 원인).
#   → 작업지시는 시작일 90일 전부터 넓게 읽고, 작업실적(g20)을 work_dt 로 [시작, 끝] 에 거른다.
LOOKBACK = 90
fr_wo = (datetime.strptime(fr, "%Y-%m-%d") - timedelta(days=LOOKBACK)).strftime("%Y-%m-%d")
OUT = io.StringIO()
def P(*a):
    s = " ".join(str(x) for x in a); print(s); OUT.write(s + "\n")

_print = builtins.print
def _quiet(*a, **k):
    if a and str(a[0]).startswith("  [경고]  가격 컬럼 차단"): return
    _print(*a, **k)
builtins.print = _quiet   # bad_rate · bad_in_rate 는 불량률(가격 아님)인데 키워드 'rate' 로 차단됨 — 출력만 줄인다
c = TricoClient(); t0 = time.time(); calls = 0
P(f"[실행] {date.today()} · 작업실적 조회 {fr} ~ {to} (작업지시는 {fr_wo} 부터, 읽기 전용)")
g00 = c.생산실적(fr_dt=fr_wo, to_dt=to); calls += 1
wos = sorted(set(g00["wo_no"].astype(str))) if len(g00) else []
P(f"  작업지시(g00) {len(g00)}행 · 작업지시번호 {len(wos)}개")

proc, pw = [], []
for i, wo in enumerate(wos, 1):
    try:
        g10 = c.query("PPC120_g10", {"@wo_no": wo, "@dn_bc": None, "@capsule_mng_no": None, "@co_cd": "01"}); calls += 1
    except Exception as e:
        P(f"  g10 실패 {wo}: {str(e)[:120]}"); continue
    if not len(g10): continue
    proc.append(g10)
    for _, r in g10.iterrows():
        done = pd.to_numeric(r.get("wrk_in_tot"), errors="coerce")
        if pd.isna(done) or done <= 0: continue
        try:
            g20 = c.query("PPC120_g20", {"@wo_id": int(float(r["wo_id"])), "@ent_bc": "PP270100"}); calls += 1
        except Exception as e:
            P(f"  g20 실패 wo_id={r['wo_id']}: {str(e)[:120]}"); continue
        if len(g20):
            g20 = g20.assign(wo_no=wo, so_no=r.get("so_no"), itm_nm=r.get("itm_nm"))
            pw.append(g20)
    time.sleep(0.03)
    if i % 50 == 0: P(f"  … {i}/{len(wos)} · 호출 {calls}회 · {time.time()-t0:.0f}s")

P(f"\n  조회 호출 {calls}회 · {time.time()-t0:.0f}s")
if not pw:
    P("  작업실적 0줄 — g20 파라미터를 다시 확인해야 함"); 
else:
    df = pd.concat(pw, ignore_index=True)
    _wd = df["work_dt"].astype(str).str[:10]
    P(f"  작업실적 전체 {len(df)}줄 중 작업일 {fr} ~ {to} 만 남김")
    df = df[(_wd >= fr) & (_wd <= to)].copy()
    keep = [k for k in ["work_dt","wo_no","so_no","itm_nm","prc_cd","mc_cd","fr_dt","fr_tm","to_tm","pw_tm","real_tm","stop_tm",
                        "wrk_in_qty","ok_in_qty","ok_qty","bad_in_qty","bad_rate","mng_no","done_yn","work_nm","pw_no","pw_sq","wo_id","mdt"] if k in df.columns]
    df = df[keep]
    df["work_dt"] = df["work_dt"].astype(str).str[:10]
    path = os.path.join(os.path.dirname(HERE), "outputs", f"erp_pw_{fr}_{to}.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    P(f"  작업실적 {len(df)}줄 → {path}")
    P("\n■ 공정(prc_cd) × 설비(mc_cd) 줄 수 · 양품 합")
    for col in ("ok_qty","bad_in_qty","pw_tm"): df[col] = pd.to_numeric(df[col], errors="coerce")
    P(df.groupby(["prc_cd","mc_cd"]).agg(줄=("pw_no","count"), 양품=("ok_qty","sum"), 불량=("bad_in_qty","sum"), 작업분=("pw_tm","sum")).to_string())
    P("\n■ 날짜 × 설비 양품 합 (NC 공정 prc_cd=20)")
    nc = df[df["prc_cd"].astype(str) == "20"]
    if len(nc): P(nc.pivot_table(index="work_dt", columns="mc_cd", values="ok_qty", aggfunc="sum", fill_value=0).to_string())
    P("\n■ 샘플 3줄"); P(df.head(3).to_string())
open(os.path.join(HERE, "probe_pw_detail_result.txt"), "w", encoding="utf-8").write(OUT.getvalue())
P("\n결과 파일: erp/probe_pw_detail_result.txt · CSV 는 outputs/ — 실행했다고 알려 주시면 Cowork 가 직접 읽습니다.")
