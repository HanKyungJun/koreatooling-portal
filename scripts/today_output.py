"""오늘(또는 지정일) 재연마 NC 생산량 빠른 확인 — ERP 작업실적(PPC120) 읽기 전용.

사용:
  python scripts\\today_output.py              (오늘, KST)
  python scripts\\today_output.py 2026-10-27   (지정일)
- 속보값: ERP 에 실적을 입력한 만큼만 나온다(작업 중인 날은 낮게 나옴).
- 파일을 쓰지 않는다(캐시 저장 없음). 일일보고서와 같은 함수(erp/erp_worklog.fetch_nc_results)를 쓴다.
- 월평균 = 이번 달 1일 ~ 전날 중 실적이 있는 날의 평균.
"""
import sys, os, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / 'erp'))
import erp_worklog as ew

KST = datetime.timezone(datetime.timedelta(hours=9))


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    d = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.datetime.now(KST).date()
    fr = d.replace(day=1)
    df = ew.fetch_nc_results(fr, d, use_cache=True, log=lambda *a: None)
    now = datetime.datetime.now(KST)
    print(f'재연마 NC 생산량 — {d} (조회 {now:%Y-%m-%d %H:%M} KST · ERP 작업실적 · 속보값)')
    if not len(df):
        print('  이번 달 실적 없음'); return
    df['qty'] = df['ok'] + df['bad']
    df['day'] = df['work_dt'].map(lambda x: x if isinstance(x, datetime.date) else datetime.date.fromisoformat(str(x)[:10]))
    t = df[df['day'] == d]
    if not len(t):
        print('  이날 입력된 실적 없음'); return
    ok, bad, qty = int(t['ok'].sum()), int(t['bad'].sum()), int(t['qty'].sum())
    print(f'  양품 {ok:,} 개 · 불량 {bad:,} 개 · 합계 {qty:,} 개 · 불량률 {bad / qty * 100:.1f} % · 작업지시 {t["wo_no"].nunique()} 건 · 실적 {len(t)} 줄')
    prev = df[df['day'] < d].groupby('day')['qty'].sum()
    prev = prev[prev > 0]
    if len(prev):
        avg = prev.mean()
        print(f'  {d.month}월 평균(이전 작업일 {len(prev)}일) {avg:,.0f} 개 → 이날은 평균의 {qty / avg * 100:.0f} %'
              f' · 전 작업일 {prev.index[-1]} {int(prev.iloc[-1]):,} 개')
    print('  설비별(양품 / 불량):')
    for mc, g in t.groupby('mc_cd'):
        print(f'    {mc}: {int(g["ok"].sum()):,} / {int(g["bad"].sum()):,}')
    shape = t['itm_nm'].astype(str).str.split('/').map(lambda s: '/'.join(s[:2]) if len(s) > 1 else s[0])
    print('  많이 한 품목(날수/형상, 상위 5):')
    for k, v in t.groupby(shape)['qty'].sum().sort_values(ascending=False).head(5).items():
        print(f'    {k}: {int(v):,} 개')
    last = t['mdt'].astype(str).max()
    print(f'  마지막 실적 입력: {last[:16].replace("T", " ")}')


if __name__ == '__main__':
    main()
