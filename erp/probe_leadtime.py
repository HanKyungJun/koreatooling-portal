# -*- coding: utf-8 -*-
"""작업일지 ↔ ERP 오더 리드타임(수주일 → 작업일) 조사 — 읽기 전용 (2026-09-30, Cowork)

배경: 「장비별 투입 목록」의 「모호」 줄(끝 4자리가 같은 오더가 여럿이고 둘 다 잔량 남음)은
      후보끼리 수주일이 수십~수백 일 떨어진 경우가 많다(예: 0179 = 2606120179 vs 2609100179, 90일).
      「가장 가까운 수주가 다른 후보보다 N일 이상 최근이면 자동 확정」 규칙을 넣기 전에 N 을 실측으로 정한다.

뽑는 것
  ① 후보가 1건뿐인(확정) 작업일지 줄의 리드타임 분포 — 달력일·영업일
  ② 「모호」 줄의 후보 간 수주일 차이 분포 + N 별 「자동 확정으로 바뀌는 줄 / 확정 줄 중 리드타임 ≥ N 인 줄(위험)」
  ③ 최근 14일 「모호」 줄의 후보 오더별 품목 행 (수주량·출하량·작업일지 가공량·잔량) — 옛 오더에 잔량이 왜 남았는지

- ERP 에 쓰지 않는다. 조회만 한다. 가격 컬럼은 trico_client 기본 차단. machine_queue.py 는 고치지 않고 함수만 빌려 쓴다.
- ①은 ERP 를 넓게(기본 240일) 조회해 「조회 기간 밖 옛 오더」 때문에 가짜 확정이 생기는 것을 줄인다.
  ②③은 운영과 똑같이 120일 기준 후보만 쓴다.
- 결과: 화면 출력 + erp/probe_leadtime_result.txt (.gitignore 의 erp/probe_*_result.txt 로 제외됨)
실행 (cnc-wiki 폴더에서): python erp\\probe_leadtime.py
"""
import sys, os
from datetime import date, timedelta
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pandas as pd
import machine_queue as mq

PROD_DAYS = 120      # 운영(fetch_machine_queue) 조회 기간
ERP_DAYS = 240       # ① 리드타임용 넓은 조회
RECENT = 14          # ③ 상세를 볼 최근 일수
THRESH = (14, 21, 30, 45, 60, 90)

today = date.today()
fr_prod = today - timedelta(days=PROD_DAYS)
fr_erp = today - timedelta(days=ERP_DAYS)


def fetch(fr):
    from trico_client import TricoClient
    return TricoClient().query('sdb100_jae_g10', {
        '@to_dt': '', '@fr_dt': fr.strftime('%Y-%m-%d'), '@chk_detail': '1', '@co_cd': '01',
        '@f_so_no': None, '@f_so_bs': "'01','10'", '@f_cust_cd': None,
        '@f_cust2_cd': None, '@f_itm_cd': None, '@f_so_rid': None,
        '@f_stat_bc': '', '@f_order_nm': None, '@f_rmks': None, '@f_cust_nm': None,
    })


def prep(df):
    d = df.copy().reset_index(drop=True)
    d['so_no'] = d['so_no'].astype(str)
    d['so_q'] = pd.to_numeric(d['so_qty'], errors='coerce').fillna(0)
    d['out_q'] = pd.to_numeric(d['out_qty'], errors='coerce').fillna(0) if 'out_qty' in d else 0.0
    d['sdt'] = pd.to_datetime(d['so_dt'], errors='coerce', utc=True).dt.tz_convert('Asia/Seoul').dt.date
    d['so4'] = d['so_no'].str[-4:]
    d['dia'] = d['itm_nm'].map(lambda n: (mq.parse_item(n) or {}).get('dia'))
    d['sk'] = d['itm_nm'].map(lambda n: mq.shape_key((mq.parse_item(n) or {}).get('shape')))
    return d


def cands(d, r, c):
    """machine_queue.apply_worklog 와 같은 후보 조건 — 끝4자리 · 수주일 ≤ 작업일 · 직경 · (형상 우선)."""
    m = (d['so4'] == c) & d['sdt'].notna()
    m &= d['sdt'].map(lambda x: x is not None and not pd.isna(x) and x <= r['date'])
    if r['dia'] is not None:
        m &= d['dia'].map(lambda x: x is not None and not pd.isna(x) and abs(x - r['dia']) < 1e-6)
    cd = d[m]
    if len(cd) and r['skey']:
        same = cd[cd['sk'] == r['skey']]
        if len(same):
            cd = same
    return cd


def qstats(s, label):
    if len(s) == 0:
        return f'  {label}: 표본 없음'
    q = s.quantile([.5, .75, .9, .95, .99])
    return (f'  {label}: n={len(s)} · 최소 {s.min():.0f} · 중앙 {q[.5]:.0f} · 75% {q[.75]:.0f} · '
            f'90% {q[.9]:.0f} · 95% {q[.95]:.0f} · 99% {q[.99]:.0f} · 최대 {s.max():.0f}')


def mq_holds():
    import json
    try:
        data = json.load(open(os.path.join(HERE, 'hold_orders.json'), encoding='utf-8'))
        return {str(h['so_no']): str(h.get('reason', '보류')) for h in data.get('holds', []) if h.get('so_no')}   # generate.load_hold_orders 와 같은 형식
    except Exception:
        return {}


def main():
    hol = mq.load_holidays()
    wide = prep(fetch(fr_erp))
    prod = wide[wide['sdt'].map(lambda x: x is not None and not pd.isna(x) and x >= fr_prod)].copy()
    wl = mq.load_worklog(fr_prod, today=today)

    # 운영과 같은 가공분 누적 (잔량 계산용) — apply_worklog 는 so_q/so_no/so_dt/itm_nm/out_q 를 쓴다
    prod_q = prod.reset_index(drop=True)
    worked, _, st = mq.apply_worklog(prod_q, wl, mq_holds())
    prod_q['worked'] = worked
    prod_q['rest'] = (prod_q['so_q'] - prod_q[['out_q', 'worked']].max(axis=1)).clip(lower=0)

    lead = []
    for r in wl:
        for c in r['codes']:
            cw = cands(wide, r, c)            # ① 넓은 기간
            ow = cw['so_no'].unique()
            if len(ow) == 1:
                sd = cw['sdt'].iloc[0]
                lead.append(dict(date=r['date'], equip=r['equip'], shape=r['shape'], dia=r['dia'], qty=r['qty'],
                                 code=c, so=ow[0], cal=(r['date'] - sd).days,
                                 biz=mq.biz_days_late(sd, r['date'], hol)))
    L = [f'[실행] {pd.Timestamp.now(tz="Asia/Seoul"):%Y-%m-%d %H:%M} KST · 작업일지 {fr_prod} ~ {today} ({len(wl)}줄)',
         f'[ERP] 넓은 조회 {fr_erp} ~ (품목 {len(wide)}행 · 수주 {wide["so_no"].nunique()}건) · 운영 기준 {fr_prod} ~ (품목 {len(prod_q)}행)',
         f'[운영 통계] 코드 {st["codes"]} · 매칭 {st["matched"]} · 모호(후보 2+) {st["ambiguous"]} · 매칭 실패 {st["unmatched"]} · 번호 없음 {st["nocode"]}',
         '']

    # ① 리드타임
    lt = pd.DataFrame(lead)
    L.append('■ ① 확정 줄(후보 1건, 240일 조회) 리드타임 = 작업일 − 수주일')
    if len(lt):
        L.append(qstats(lt['cal'], '달력일'))
        L.append(qstats(lt['biz'], '영업일'))
        bins = [-1, 7, 14, 21, 30, 45, 60, 90, 10**6]
        labs = ['0~7', '8~14', '15~21', '22~30', '31~45', '46~60', '61~90', '91+']
        h = pd.cut(lt['cal'], bins=bins, labels=labs).value_counts().reindex(labs)
        L.append('  달력일 구간: ' + ' · '.join(f'{k} {int(v)}' for k, v in h.items()))
        for eq in ('FG', 'GX7'):
            s = lt[lt['equip'] == eq]['cal']
            L.append(qstats(s, f'{eq} 달력일'))
        L.append('  리드타임 45일 초과 확정 줄 (이런 게 많으면 「오래된 오더 = 가짜」 가정이 위험):')
        for _, x in lt[lt['cal'] > 45].sort_values('cal', ascending=False).head(30).iterrows():
            L.append(f"    {x['date']} | {x['equip']:<3} | {x['shape']} Ø{x['dia']} {x['qty']}개 | {x['so']} | {x['cal']}일(영업 {x['biz']})")
    else:
        L.append('  표본 없음')
    L.append('')

    # ② ③ — 2026-09-30 수정: 운영(apply_worklog)이 배정 순간 잔량으로 판정한 issues 를 그대로 쓴다.
    #   (첫 판은 실행 끝 잔량으로 다시 판정해 「모호 0건」이 나왔다 — 잘못)
    import re as _re
    def _sd(o):
        return date(2000 + int(o[:2]), int(o[2:4]), int(o[4:6]))   # 오더번호 앞 6자리 = 수주일
    amb = []
    for x in st['issues']:
        if x['kind'] not in ('모호', '상한 확정', '자동 확정', '후보 모두 완료'):
            continue
        m = _re.search(r'오더 \d+건: ([\d, ]+) →', x['why'])
        if not m:
            continue
        orders = [o.strip() for o in m.group(1).split(',')]
        leads = sorted(((x['date'] - _sd(o)).days, o) for o in orders)
        amb.append(dict(x, leads=leads))
    L.append(f"■ ② 운영 판정 — 모호 {sum(a['kind'] == '모호' for a in amb)} · 상한 확정 {sum(a['kind'] == '상한 확정' for a in amb)} · 자동 확정 {sum(a['kind'] == '자동 확정' for a in amb)} (LEAD_CAP_DAYS = {getattr(mq, 'LEAD_CAP_DAYS', None)})")
    L.append('  N 별 재계산 — 「리드타임 N일 초과 후보는 더 가까운 후보가 있으면 제외」 시 모호 줄이 몇 개 확정되나:')
    L.append('    N | 모호→확정 | 남는 모호 | 확정 줄 중 리드타임 > N (오판 위험 표본)')
    ms = [a for a in amb if a['kind'] == '모호']
    for n in THRESH:
        conv = sum(1 for a in ms if sum(1 for l, _ in a['leads'] if l <= n) == 1)
        risk = int((lt['cal'] > n).sum()) if len(lt) else 0
        L.append(f'    {n:>3}일 | {conv:>4} | {len(ms) - conv:>4} | {risk} / {len(lt)}')
    L.append('')
    rc = today - timedelta(days=RECENT)
    L.append(f'■ ③ 최근 {RECENT}일 모호·상한 확정 줄 — 후보 오더별 품목 행 (잔량은 이번 실행 끝 기준)')
    for a in [a for a in amb if a['date'] >= rc and a['kind'] in ('모호', '상한 확정')]:
        L.append(f"  ▶ {a['date']} | {a['equip']} | {a['shape']} Ø{a['dia']} {a['qty']}개 | {a['kind']} | 번호 {a['code']} | 후보(리드타임일): "
                 + ', '.join(f'{o} {l}일' for l, o in a['leads']))
        for l, o in a['leads']:
            for _, it in prod_q[prod_q['so_no'] == o].iterrows():
                L.append(f"      {o} | {str(it['itm_nm'])[:45]:<45} | 수주 {it['so_q']:.0f} · 출하 {it['out_q']:.0f} · 가공(작업일지) {it['worked']:.0f} · 잔량 {it['rest']:.0f}")
    # 2026-09-30: 운영과 같은 확인 필요 목록을 미리보기로 남긴다(운영 파일 erp/worklog_unmatched.txt 는 건드리지 않음)
    try:
        n1, n2, n3 = mq.write_unmatched_report(st['issues'], path=os.path.join(HERE, 'probe_unmatched_preview_result.txt'))
        L += ['', f"■ 미리보기 — erp/probe_unmatched_preview_result.txt (최근 14일 확인 필요 {n1}줄 · 그 이전 {n2}줄 · 참고 {n3}줄 · 초과 배정 품목 {st.get('overflow', 0)}행)"]
    except Exception as e:
        L += ['', f'⚠️ 미리보기 저장 실패: {type(e).__name__}: {e}']
    out = '\n'.join(L)
    print(out)
    with open(os.path.join(HERE, 'probe_leadtime_result.txt'), 'w', encoding='utf-8') as f:
        f.write(out + '\n')


if __name__ == '__main__':
    main()
