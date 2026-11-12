# -*- coding: utf-8 -*-
"""ERP 생산실적(PPC120_g00) 조회 확인 — 읽기 전용 (2026-10-23, Cowork)

배경: ERP 단일 기록 전환을 검토 중이다(한경준님 10-23: 작업이 끝날 때마다 ERP 생산실적 입력).
      그런데 2026-09-04 에는 같은 조회가 9/1 ~ 9/4 를 0행으로 돌려줬다(decisions-archive 2026-09).
      ⓐ 그때는 ERP 에 입력하지 않았는지 ⓑ 조회 파라미터가 틀렸는지 아직 모른다.

확인하는 것
  1) 월별 행 수 (2026-06 ~ 오늘) — 언제부터 ERP 에 실적이 쌓였는가
  2) 컬럼 이름 · 샘플값 — 「생산설비」「시작/종료 시간」「작업(분)」「양품/불량」이 이 조회에 들어 있는가
  3) 0행이면 @fac_cd 를 바꿔 다시 조회
  4) 기준 오더 2610210088 (10-23 화면 캡처, 양품 1 · 572분 · NC-설비1(GX)) 이 보이는가

- ERP 에 쓰지 않는다. 가격·금액 컬럼은 출력하지 않는다(trico_client.is_price_col).
- 결과: 화면 출력 + erp/probe_prod_result_result.txt (.gitignore 의 erp/probe_*_result.txt 로 제외)
실행 (cnc-wiki 폴더에서): python erp\\probe_prod_result.py
"""
import sys, os, io
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pandas as pd
from trico_client import TricoClient, is_price_col

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)
OUT = io.StringIO()
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s); OUT.write(s + "\n")

c = TricoClient()
today = date.today()
P(f"[실행] {today} · 생산실적 PPC120_g00 조회 확인 (읽기 전용)")

months = [("2026-06-01", "2026-06-30"), ("2026-07-01", "2026-07-31"), ("2026-08-01", "2026-08-31"),
          ("2026-09-01", "2026-09-30"), ("2026-10-01", today.strftime("%Y-%m-%d"))]
frames = []
P("\n■ 1) 월별 행 수 (@fac_cd='01')")
for fr, to in months:
    try:
        df = c.생산실적(fr_dt=fr, to_dt=to)
        P(f"  {fr} ~ {to}: {len(df)}행")
        if len(df): frames.append(df)
    except Exception as e:
        P(f"  {fr} ~ {to}: 조회 실패 {str(e)[:150]}")

if not frames:
    P("\n■ 3) 0행 — @fac_cd 를 바꿔 10월만 다시 조회")
    for fac in ("", None, "02", "10"):
        try:
            df = c.생산실적(fr_dt=months[-1][0], to_dt=months[-1][1], fac_cd=fac)
            P(f"  fac_cd={fac!r}: {len(df)}행")
            if len(df): frames.append(df); break
        except Exception as e:
            P(f"  fac_cd={fac!r}: 조회 실패 {str(e)[:150]}")

if frames:
    df = pd.concat(frames, ignore_index=True)
    keep = [col for col in df.columns if not is_price_col(str(col))]
    P(f"\n■ 2) 컬럼 {len(df.columns)}개 중 가격 제외 {len(keep)}개 — 결측 / 고유 / 샘플")
    for col in keep:
        smp = df[col].dropna().astype(str).head(1).tolist()
        P(f"  {str(col):20} 결측{df[col].isna().sum():5}  고유{df[col].nunique():5}  예: {(smp[0][:30] if smp else '')}")
    hits = [col for col in keep if any(k in str(col).lower() for k in ("eqp", "equip", "mach", "fac", "res", "설비", "time", "tm", "min", "start", "end", "fr_", "to_"))]
    P(f"\n  설비 · 시간 후보 컬럼: {hits}")
    P("\n■ 4) 기준 오더 2610210088")
    mask = df.astype(str).apply(lambda r: r.str.contains("2610210088").any(), axis=1)
    P(df.loc[mask, keep].head(5).to_string() if mask.any() else "  찾지 못함 (이 조회는 다른 표를 돌려주거나, 오더번호 컬럼 형식이 다름)")
    P("\n■ 샘플 3행")
    P(df[keep].head(3).to_string())
else:
    P("\n  모든 조회가 0행 — 이 화면의 아래 「작업실적」 표는 다른 조회 이름일 수 있음. Fiddler 캡처가 필요할 수 있다.")

open(os.path.join(HERE, "probe_prod_result_result.txt"), "w", encoding="utf-8").write(OUT.getvalue())
P("\n결과 파일: erp/probe_prod_result_result.txt — 이 내용을 Cowork 에 알려 주세요(파일은 Cowork 가 직접 읽습니다).")
