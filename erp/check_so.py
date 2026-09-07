# -*- coding: utf-8 -*-
"""특정 수주번호가 ERP 조회 결과에 남아 있는지 확인한다.

용도: 삭제·취소 처리가 조회 경로(sdb100_jae_g10)에 실제로 반영됐는지 판정.
      「지연 목록에서 빠졌다」와 「ERP 에서 삭제됐다」는 다른 사건이므로,
      rest>0 필터 이전의 **원본 행 존재 여부**로 본다.

사용: python erp\\check_so.py 2606090162 [2605110029 ...]
      인자 없으면 2026-09-07 기준 관심 2건을 확인한다.
"""
import os, sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from trico_client import TricoClient

TODAY = date.today()
DEFAULT = ['2606090162', '2605110029']   # 다영툴링 · 유비툴


def main():
    targets = sys.argv[1:] or DEFAULT
    fr = (TODAY - timedelta(days=365)).strftime('%Y-%m-%d')   # 넓게 본다
    print(f'기준일(KST): {TODAY}   조회범위: {fr} ~ (365일)')

    df = TricoClient().수주(fr_dt=fr)
    df['so_no'] = df['so_no'].astype(str)
    print(f'전체 {len(df)}행 / 수주 {df["so_no"].nunique()}건\n')

    for so in targets:
        hit = df[df['so_no'] == so]
        if len(hit) == 0:
            print(f'  {so} : ❌ 조회 결과에 없음 — 삭제·취소 반영됨')
            continue
        so_q  = pd.to_numeric(hit['so_qty'],  errors='coerce').fillna(0).sum()
        out_q = pd.to_numeric(hit['out_qty'], errors='coerce').fillna(0).sum()
        cust  = str(hit.iloc[0].get('cust_nm', ''))
        stat  = str(hit.iloc[0].get('stat_bc', ''))
        dlv   = str(hit.iloc[0].get('dlv_dt', ''))[:10]
        print(f'  {so} : 🟢 아직 있음 — {cust} · 납기 {dlv} · '
              f'수주 {int(so_q)} / 출하 {int(out_q)} / 잔량 {int(so_q-out_q)} · 상태 {stat}')

    # 현재 지연 요약 (현황판과 같은 120일 기준)
    fr2 = (TODAY - timedelta(days=120)).strftime('%Y-%m-%d')
    d = TricoClient().수주(fr_dt=fr2)
    d['so_q']  = pd.to_numeric(d['so_qty'],  errors='coerce').fillna(0)
    d['out_q'] = pd.to_numeric(d['out_qty'], errors='coerce').fillna(0)
    d['rest']  = (d['so_q'] - d['out_q']).clip(lower=0)
    d['dlv']   = pd.to_datetime(d['dlv_dt'], errors='coerce', utc=True) \
                   .dt.tz_convert('Asia/Seoul').dt.date
    op = d[d['rest'] > 0]
    late = op[op['dlv'].notna() & (op['dlv'] < TODAY)]
    print(f'\n[120일 기준] 미출하 {op["so_no"].nunique()}건 {int(op["rest"].sum()):,}개 · '
          f'지연(분류 전) {late["so_no"].nunique()}건 {int(late["rest"].sum()):,}개')


if __name__ == '__main__':
    main()
