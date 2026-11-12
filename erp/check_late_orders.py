# -*- coding: utf-8 -*-
"""지연 14건 판정 — ERP 수주 미출하 잔량의 성격을 가린다.

배경: 2026-09-04 현황판 「오늘 할 일」 신설 이후 「납기 지연 14건」이
      3영업일 연속 같은 숫자로 떠 있다. 이것이
        ⓐ 진짜 지연(아직 안 만들었거나 못 보냄)
        ⓑ 출하했으나 ERP 미등록(유령)
      중 무엇인지 확인되지 않았다. decisions.md 2026-09-04 (6) 열린 항목.

판정 재료:
  - 경과일수: 납기가 한참 지난 건이 많으면 ⓑ 쪽 신호
  - 부분출하 여부: out_qty > 0 인데 잔량이 남으면 ⓐ 쪽 신호
  - 조회범위 민감도: 60/120/365일 결과를 비교해 범위 축소 효과를 본다

⚠️ 금액 컬럼은 trico_client 가 자동 차단한다(대외비 원칙, CLAUDE.md §4).
   이 스크립트도 금액을 출력하지 않는다.
"""
import os, sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from trico_client import TricoClient

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, 'outputs')
os.makedirs(OUT, exist_ok=True)

TODAY = date.today()


def load(lookback):
    fr = (TODAY - timedelta(days=lookback)).strftime('%Y-%m-%d')
    df = TricoClient().수주(fr_dt=fr)
    d = df.copy()
    d['so_q']  = pd.to_numeric(d['so_qty'],  errors='coerce').fillna(0)
    d['out_q'] = pd.to_numeric(d['out_qty'], errors='coerce').fillna(0)
    d['rest']  = (d['so_q'] - d['out_q']).clip(lower=0)
    d['dlv']   = pd.to_datetime(d['dlv_dt'], errors='coerce', utc=True) \
                   .dt.tz_convert('Asia/Seoul').dt.date
    return d


def summarize(d, label):
    op   = d[d['rest'] > 0]
    late = op[op['dlv'].notna() & (op['dlv'] < TODAY)]
    print(f'[{label}] 전체 {len(d)}행 / 미출하 {op["so_no"].nunique()}건 '
          f'{int(op["rest"].sum()):,}개 / 지연 {late["so_no"].nunique()}건 '
          f'{int(late["rest"].sum()):,}개')
    return late


def main():
    print(f'기준일(KST): {TODAY}')
    print('=' * 78)

    # 조회범위 민감도
    for lb in (60, 120, 365):
        try:
            summarize(load(lb), f'{lb}일')
        except Exception as e:
            print(f'[{lb}일] 조회 실패: {type(e).__name__}: {str(e)[:100]}')
    print('=' * 78)

    # 본 판정은 현황판과 동일한 120일 기준
    d = load(120)
    op = d[d['rest'] > 0]
    late = op[op['dlv'].notna() & (op['dlv'] < TODAY)].copy()
    late['경과일'] = late['dlv'].map(lambda x: (TODAY - x).days)
    late['부분출하'] = late['out_q'] > 0
    late = late.sort_values('경과일', ascending=False)

    cols = {
        'so_no': '수주번호', 'so_dt': '수주일', 'dlv': '납기', '경과일': '경과일',
        'cust_nm': '거래처', 'itm_nm': '품목',
        'so_q': '수주량', 'out_q': '출하량', 'rest': '잔량',
        '부분출하': '부분출하', 'stat_bc': '상태', 'rtn_bc': '반품구분',
    }
    use = [c for c in cols if c in late.columns]
    view = late[use].rename(columns=cols)

    print(f'\n■ 지연 상세 — {late["so_no"].nunique()}건 / {len(late)}행 / '
          f'{int(late["rest"].sum()):,}개  (경과일 큰 순)\n')
    with pd.option_context('display.max_rows', 200, 'display.width', 250,
                           'display.max_colwidth', 30):
        print(view.to_string(index=False))

    print('\n■ 경과일 분포')
    bins = [0, 7, 14, 30, 60, 9999]
    names = ['1~7일', '8~14일', '15~30일', '31~60일', '61일 이상']
    g = pd.cut(late['경과일'], bins=bins, labels=names, right=True)
    for k, v in late.groupby(g, observed=False)['rest'].agg(['count', 'sum']).iterrows():
        print(f'  {k:>9} : {int(v["count"]):3d}행  {int(v["sum"]):>6,}개')

    print('\n■ 부분출하 여부  (출하량>0 이면 실제 진행 중 = 진짜 지연 신호)')
    print(f'  부분출하 있음 : {int((late["out_q"] > 0).sum())}행')
    print(f'  출하 0        : {int((late["out_q"] == 0).sum())}행')

    p = os.path.join(OUT, f'late_orders_{TODAY:%Y%m%d}.csv')
    view.to_csv(p, index=False, encoding='utf-8-sig')
    print(f'\n저장: {p}')


if __name__ == '__main__':
    main()
