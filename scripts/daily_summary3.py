"""일일보고 맨 위 3줄(결론 · 근거 · 요청) 만들기 — 시안 (2026-10-30 Cowork)

양식: wiki/templates/보고서양식-C-정기업무보고.md §1 · decisions 2026-10-28 (5) 8번
  ① 결론 : 오늘 합계 · 양품 · 불량, 월평균 대비(%)
  ② 근거 : 이번 달 누계 수량 · 작업일, 데이터 기준
  ③ 요청 : 기본 「요청 없음」. 불량 1개 이상 또는 합계가 월평균 ±20 % 초과면 「확인 요청, (사유)」
월평균 = 그날 이전 작업일(합계 > 0) 평균 — scripts/daily_report.py make_report_erp 와 같은 기준.

⚠️ 아직 daily_report.py 에 연결하지 않았다(양식 C: 1주 나란히 확인한 뒤 켠다). 연결할 때는
   make_report_erp() 안에서 summary3(summary, rows, d, m) 결과 3줄을 「일일 요약」 시트 제목 아래에 쓰면 된다.

시험(PC 또는 Cowork): python scripts/daily_summary3.py 2026-10-27 2026-10-28
  → erp/snapshot/pw_nc_*.csv(가장 최근) 로 계산해 3줄을 출력한다(ERP 직접 조회 없음).
"""
import glob
import os
import sys
from datetime import date

import pandas as pd

BAND = 0.20   # ±20 % — 사내 경험값, 1달 운영 후 조정(decisions 2026-10-28 (5) 8번)


def daily_from_rows(rows: pd.DataFrame) -> pd.DataFrame:
    """NC 작업실적 줄(work_dt · ok · bad) → 일별 양품 · 불량 · 합수량."""
    df = rows.copy()
    df['work_dt'] = pd.to_datetime(df['work_dt']).dt.date
    df['일'] = df['work_dt'].map(lambda x: x.day)
    df['qty'] = df['ok'] + df['bad']
    g = df.groupby('일').agg(양품=('ok', 'sum'), 불량=('bad', 'sum'), 합수량=('qty', 'sum')).reset_index()
    for k in ('양품', '불량', '합수량'):
        g[k] = g[k].round().astype(int)
    return g


def summary3(summary: pd.DataFrame, rows: pd.DataFrame, d: int, m: int) -> list:
    """summary: 일별(일 · 양품 · 불량 · 합수량), rows: 그날 NC 작업실적 줄(wo_no · bad), d: 일, m: 월 → 3줄."""
    t = summary[summary['일'] == d]
    if t.empty or int(t.iloc[0]['합수량']) <= 0:
        return []
    t = t.iloc[0]
    tot, ok, bad = int(t['합수량']), int(t['양품']), int(t['불량'])
    prev = summary[(summary['일'] < d) & (summary['합수량'] > 0)]
    avg = float(prev['합수량'].mean()) if len(prev) else 0.0
    if avg > 0:
        diff = tot / avg - 1
        word = '많음' if diff > 0.0005 else ('적음' if diff < -0.0005 else '같음')
        cmp_txt = f'월평균 {avg:,.1f}개 대비 {abs(diff) * 100:.1f} % {word}' if word != '같음' else f'월평균 {avg:,.1f}개와 같음'
    else:
        diff, cmp_txt = 0.0, '월평균 없음(이달 첫 작업일)'
    cum = summary[(summary['일'] <= d) & (summary['합수량'] > 0)]
    l1 = f'① 결론 : {m}월 {d}일 NC 생산 {tot:,}개(양품 {ok:,}개, 불량 {bad:,}개), {cmp_txt}'
    l2 = f'② 근거 : {m}월 누계 {int(cum["합수량"].sum()):,}개(작업일 {len(cum)}일), ERP 작업실적 기준 속보값'
    why = []
    if bad > 0:
        wos = []
        if rows is not None and len(rows) and 'wo_no' in rows:
            wos = [str(w) for w in rows.loc[rows['bad'] > 0, 'wo_no'].astype(str).drop_duplicates().tolist()]
        why.append(f'불량 {bad:,}개 발생' + (f'(작업지시 {", ".join(wos[:3])}' + (f' 외 {len(wos) - 3}건' if len(wos) > 3 else '') + ')' if wos else ''))
    if avg > 0 and abs(diff) > BAND:
        why.append(f'합계가 월평균 대비 {diff * 100:+.0f} %')
    l3 = '③ 요청 : ' + ('확인 요청, ' + ' · '.join(why) if why else '요청 없음')
    return [l1, l2, l3]


def _snapshot_rows(target: date) -> pd.DataFrame:
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fs = sorted(glob.glob(os.path.join(here, 'erp', 'snapshot', f'pw_nc_{target:%Y-%m}-01_*.csv')))
    if not fs:
        sys.exit('erp/snapshot 에 이달 pw_nc 스냅샷 없음')
    df = pd.read_csv(fs[-1], encoding='utf-8-sig')
    df['work_dt'] = pd.to_datetime(df['work_dt']).dt.date
    df = df[df['work_dt'] <= target]
    for k in ('ok', 'bad'):
        df[k] = pd.to_numeric(df[k], errors='coerce').fillna(0)
    print(f'(데이터: {os.path.basename(fs[-1])})')
    return df


if __name__ == '__main__':
    for a in sys.argv[1:] or [date.today().isoformat()]:
        dt = date.fromisoformat(a)
        rows = _snapshot_rows(dt)
        lines = summary3(daily_from_rows(rows), rows[rows['work_dt'] == dt], dt.day, dt.month)
        print(f'[{dt}]'); print('\n'.join(lines) if lines else '  그날 NC 작업실적 없음 — 일일보고도 만들지 않음')
