# -*- coding: utf-8 -*-
"""장비별 투입 목록 (FG / GX7) — 2026-09-28 신설 (Cowork, 워크숍 목표1 우선순위 1건)

ERP 재연마 수주 **품목 상세**(sdb100_jae_g10, @chk_detail=1)에서 미출하 잔량이 있는
품목을 장비별로 나누고, 납기 우선 + 같은 납기 구간 안에서 셋업(형상·직경) 묶기로 정렬한다.

배정 규칙 — 위에서부터 먼저 걸리는 것 (한경준님 확정 2026-09-28)
  근거: wiki/measurements/재연마_표준공수DB_2022-2026.xlsx 「원천데이터」 2025~2026 4,146행 [실측 검증]
  1) 품목명이 6필드(날수/형상/직경/소재/가공부/코팅)가 아님 → 기타(배정 제외)  예: 코팅만/…, 절단/…, 원통연삭/…
  2) 형상 == '드릴'                → GX7   (1,219개 중 1,218개)
  3) 소재 == 'HSS' 또는 형상에 '라핑' → GX7   (약 70%)
  4) 직경 > 8 mm                   → GX7   (88~100%)
  5) 그 외(직경 ≤ 8 mm)            → FG    (86~96%) — Ø8 은 경계로 표시
  ※ 'NC드릴' 은 2)에 걸리지 않고 직경 규칙을 따른다 (실측 FG 73%).

제외(「오늘 할 일」과 같은 기준)
  - 출하 보류 대장(erp/hold_orders.json) 에 있는 수주
  - 부분출하 자투리: 수주 단위로 출하 이력이 있고 잔량 < 수주량 10%

가공 완료분 차감 (2026-09-28 v2 — 한경준님 제안)
  월간생산일지 xls 의 특이사항 4자리 = ERP 오더번호 끝 4자리 [실측 검증 — 06-10 생산지시 export 303행 중 301행 일치].
  작업일지 행(작업일·직경·형상·수량·코드)을 ERP 수주 품목에 맞춰 붙이고,
  깎아야 할 수량 = 수주량 − max(작업일지 가공 수량, 출하 수량) 으로 계산한다.
  맞추는 조건: 끝 4자리 일치 + 직경 일치 + 수주일 ≤ 작업일 (+ 형상이 읽히면 형상 일치 우선).
  후보 오더가 여러 개면 작업일 기준 가장 최근 수주를 택하고 「모호」로 센다.
  5월 표본: 234코드 중 1건 확정 190 · 모호 0 · 직경 불일치 0 (나머지는 비교 기간 밖).

⚠️ 참고용 목록이다. 실제 투입은 현장 판단이 우선한다(장비 상태·긴급 요청·로더 사용 여부 등).
⚠️ 금액 열은 trico_client 기본 차단으로 들어오지 않는다.
"""
import re
from datetime import date, timedelta

FG, GX7, ETC = 'FG', 'GX7', '기타'


def parse_item(nm):
    """품목명 6필드 파싱. 규격 밖이면 None."""
    p = [x.strip() for x in str(nm or '').split('/')]
    if len(p) < 6:
        return None
    b = re.match(r'^(\d+)\s*날', p[0])
    m = re.match(r'^([\d.]+)', p[2])
    if not b or not m:
        return None
    return dict(blade=int(b.group(1)), shape=p[1], dia=float(m.group(1)),
                mat=p[3].upper() if p[3].upper() == 'HSS' else p[3],
                part=p[4], coat=p[5].replace(' ', ''))


def assign_machine(nm):
    """(장비, 경계여부, 파싱결과) 를 돌려준다."""
    p = parse_item(nm)
    if p is None:
        return ETC, False, None
    if p['shape'] == '드릴':
        return GX7, False, p
    if p['mat'] == 'HSS' or '라핑' in p['shape']:
        return GX7, False, p
    if p['dia'] > 8:
        return GX7, False, p
    return FG, abs(p['dia'] - 8) < 1e-9, p


def shape_key(s):
    """형상 표기를 비교용 키로. 작업일지(자유 입력)·ERP 품목명 공통. 모르면 None."""
    t = str(s or '').replace(' ', '').lower()
    if not t:
        return None
    if '드릴' in t:
        return 'NC드릴' if 'nc' in t else '드릴'
    if '볼' in t or 'ball' in t:
        return '볼'
    if '코너' in t or 'corner' in t or re.search(r'r\d', t):
        return '코너'
    if '면취' in t or '챔퍼' in t:
        return '면취'
    if '평' in t or '스퀘어' in t or '플랫' in t or 'flat' in t:
        return '평'
    return None


def load_worklog(since, today=None, base_dir=None):
    """since 이후 월간생산일지 작업 행 → list[dict]. 파싱 규칙은 scripts/parse_worklog.py 를 그대로 쓴다."""
    import os, sys
    from datetime import date as _d
    base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(base_dir, 'scripts'))
    from parse_worklog import parse_year
    today = today or _d.today()
    rows = []
    for y in range(since.year, today.year + 1):
        jobs, _, _ = parse_year(y)
        for j in jobs:
            try:
                d = _d(int(j[0]), int(j[1]), int(j[2]))
            except ValueError:
                continue
            if d < since or d > today:
                continue
            m = re.match(r'^\s*([\d.]+)', str(j[7]))
            rows.append(dict(date=d, equip=j[3], shape=j[5], skey=shape_key(j[5]),
                             dia=float(m.group(1)) if m else None, qty=int(j[13]),
                             codes=re.findall(r'(?<!\d)(\d{4})(?!\d)', str(j[10])), note=str(j[10])))
    return rows


def apply_worklog(d, wl):
    """ERP 품목 DataFrame(d: so_no·so_dt·itm_nm·so_q 필요)에 작업일지 가공 수량을 붙인다.
    반환: (worked Series[index=d.index], equip dict[index→set], stats dict)"""
    import pandas as pd
    so4 = d['so_no'].astype(str).str[-4:]
    sdt = pd.to_datetime(d['so_dt'], errors='coerce', utc=True).dt.tz_convert('Asia/Seoul').dt.date
    dia = d['itm_nm'].map(lambda n: (parse_item(n) or {}).get('dia'))
    sk = d['itm_nm'].map(lambda n: shape_key((parse_item(n) or {}).get('shape')))
    worked = pd.Series(0, index=d.index, dtype=float)
    equip = {}
    st = dict(rows=len(wl), codes=0, matched=0, ambiguous=0, amb_resolved=0, unmatched=0, nocode=0)
    for r in wl:
        if not r['codes']:
            st['nocode'] += 1
            continue
        left = r['qty']
        cands_all = []
        for i, c in enumerate(r['codes']):
            st['codes'] += 1
            m = (so4 == c) & sdt.notna()
            m &= sdt.map(lambda x: x is not None and not pd.isna(x) and x <= r['date'])
            if r['dia'] is not None:
                m &= dia.map(lambda x: x is not None and abs(x - r['dia']) < 1e-6)
            cand = d[m]
            if len(cand) and r['skey']:
                same = cand[sk[cand.index] == r['skey']]
                if len(same):
                    cand = same
            if len(cand) == 0:
                st['unmatched'] += 1
                continue
            orders = cand['so_no'].astype(str).unique()
            if len(orders) > 1:
                # 모호 — ① 아직 깎을(또는 출하할) 게 남은 오더를 우선 ② 그중 가장 최근 수주 (2026-09-28 보강)
                st['ambiguous'] += 1
                oq = d['out_q'] if 'out_q' in d else 0
                def _left(o):
                    ix = cand.index[cand['so_no'].astype(str) == o]
                    return float((d.loc[ix, 'so_q'] - pd.concat([worked[ix], pd.Series(oq, index=d.index)[ix]], axis=1).max(axis=1)).clip(lower=0).sum())
                live = [o for o in orders if _left(o) > 0]
                if live and len(live) < len(orders):
                    st['amb_resolved'] = st.get('amb_resolved', 0) + 1
                pool = live or list(orders)
                latest = max(pool, key=lambda o: sdt[cand.index[cand['so_no'].astype(str) == o][0]])
                cand = cand[cand['so_no'].astype(str) == latest]
            st['matched'] += 1
            cands_all.append(cand)
        # 수량 배분: 코드 순서대로 품목 잔량만큼 채우고, 남으면 마지막 후보에 얹는다
        for k, cand in enumerate(cands_all):
            for idx in cand.index:
                if left <= 0:
                    break
                cap = max(float(d.at[idx, 'so_q']) - worked[idx], 0)
                last = (k == len(cands_all) - 1 and idx == cand.index[-1])
                take = left if last else min(left, cap)
                if take > 0:
                    worked[idx] += take
                    left -= take
                    equip.setdefault(idx, set()).add(r['equip'])
    return worked, equip, st


def build_queue(df, holds=None, today=None, near_days=3, worklog=None):
    """상세 DataFrame → 장비별 정렬 목록 dict. 순수 함수(ERP 호출 없음) — 테스트 가능."""
    import pandas as pd
    holds = holds or {}
    today = today or date.today()
    dn = today + timedelta(days=near_days)

    d = df.copy()
    d['so_q'] = pd.to_numeric(d['so_qty'], errors='coerce').fillna(0)
    d['out_q'] = pd.to_numeric(d.get('out_qty'), errors='coerce').fillna(0) if 'out_qty' in d else 0
    d['so_no'] = d['so_no'].astype(str)
    wl_stats, wl_equip = None, {}
    if worklog is not None:
        d['worked'], wl_equip, wl_stats = apply_worklog(d, worklog)
    else:
        d['worked'] = 0
    d['done'] = d[['out_q', 'worked']].max(axis=1)
    d['rest'] = (d['so_q'] - d['done']).clip(lower=0)
    # 가공 꼬리 — 작업일지상 가공했고 남은 게 수주량의 10% 미만이면 연마불가·수량차로 보고 뺀다
    #   (「오늘 할 일」 자투리와 같은 10% 기준. 06-10 export 검증에서 32/33 같은 사례 확인)
    tail = (d['worked'] > 0) & (d['rest'] > 0) & (d['rest'] < d['so_q'] * 0.1)
    d['tail'] = tail
    d.loc[tail, 'rest'] = 0
    d['dlv'] = pd.to_datetime(d['dlv_dt'], errors='coerce', utc=True).dt.tz_convert('Asia/Seoul').dt.date

    # 수주 단위 자투리 판정
    d['ship_rest'] = (d['so_q'] - d['out_q']).clip(lower=0)
    agg = d.groupby('so_no').agg(so_sum=('so_q', 'sum'), out_sum=('out_q', 'sum'), rest_sum=('ship_rest', 'sum'))
    minor_so = set(agg[(agg.out_sum > 0) & (agg.rest_sum < agg.so_sum * 0.1)].index)

    open_ = d[d['rest'] > 0]
    ex_hold = open_[open_['so_no'].isin(holds)]
    ex_minor = open_[~open_['so_no'].isin(holds) & open_['so_no'].isin(minor_so)]
    act = open_[~open_['so_no'].isin(holds) & ~open_['so_no'].isin(minor_so)]

    items = {FG: [], GX7: [], ETC: []}
    for _, r in act.iterrows():
        mach, edge, p = assign_machine(r.get('itm_nm'))
        dl = r['dlv']
        if dl is None or pd.isna(dl):
            bucket, bkey, tag = 3, (9, date.max.toordinal()), '납기없음'
        elif dl < today:
            bucket, bkey, tag = 0, (0, 0), f'지연 {(today - dl).days}일'
        elif dl <= dn:
            bucket, bkey, tag = 1, (1, 0), ('오늘' if dl == today else f'D-{(dl - today).days}')
        else:
            bucket, bkey, tag = 2, (2, dl.toordinal()), f'D-{(dl - today).days}'
        items[mach].append(dict(
            so_no=r['so_no'], dlv=str(dl) if dl is not None and not pd.isna(dl) else '-',
            dlv_ord=dl.toordinal() if dl is not None and not pd.isna(dl) else date.max.toordinal(),
            bucket=bucket, bkey=bkey, tag=tag,
            cust=str(r.get('cust_nm', '') or ''), itm=str(r.get('itm_nm', '') or ''),
            coat='' if pd.isna(r.get('jae_coating')) else str(r.get('jae_coating') or ''),
            rest=int(r['rest']), edge=edge,
            worked=int(r['worked']), partial=bool(r['worked'] > 0),
            wl_equip='/'.join(sorted(wl_equip.get(_, set()))),
            setup=(p['shape'], p['dia']) if p else None,
        ))

    out = {}
    for mach in (FG, GX7):
        lst = items[mach]
        # 같은 납기 구간(bkey) 안에서 셋업 그룹의 가장 빠른 납기 → 그룹 → 품목 납기 순
        gmin = {}
        for it in lst:
            k = (it['bkey'], it['setup'])
            gmin[k] = min(gmin.get(k, it['dlv_ord']), it['dlv_ord'])
        lst.sort(key=lambda it: (it['bkey'], gmin[(it['bkey'], it['setup'])],
                                 str(it['setup']), it['dlv_ord'], it['cust']))
        setups, prev = 0, None
        for i, it in enumerate(lst, 1):
            it['seq'] = i
            k = (it['bkey'], it['setup'])
            it['new_setup'] = k != prev
            if it['new_setup']:
                setups += 1
            prev = k
        out[mach] = dict(items=lst, n=len(lst), qty=sum(x['rest'] for x in lst),
                         late=sum(1 for x in lst if x['bucket'] == 0),
                         near=sum(1 for x in lst if x['bucket'] == 1),
                         setups=setups, edge=sum(1 for x in lst if x['edge']))
    out['etc'] = dict(n=len(items[ETC]), qty=sum(x['rest'] for x in items[ETC]),
                      names=sorted({x['itm'].split('/')[0] for x in items[ETC]}))
    out['excluded'] = dict(hold=int(ex_hold['so_no'].nunique()), minor=int(ex_minor['so_no'].nunique()))
    # 가공 완료(작업일지) 로 목록에서 빠진 품목 — 출하 전
    ground = d[(d['ship_rest'] > 0) & (d['rest'] <= 0) & ~d['so_no'].isin(holds)]
    out['worklog'] = dict(stats=wl_stats, ground_items=int(len(ground)), ground_qty=int(ground['ship_rest'].sum()),
                          tail_items=int(d['tail'].sum()))
    return out


def fetch_machine_queue(holds=None, lookback_days=120, log=print):
    """ERP 조회 + build_queue. 실패하면 None (현황판 나머지는 그대로 진행)."""
    try:
        import os, sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from trico_client import TricoClient
        fr = (date.today() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
        df = TricoClient().query('sdb100_jae_g10', {
            '@to_dt': '', '@fr_dt': fr, '@chk_detail': '1', '@co_cd': '01',
            '@f_so_no': None, '@f_so_bs': "'01','10'", '@f_cust_cd': None,
            '@f_cust2_cd': None, '@f_itm_cd': None, '@f_so_rid': None,
            '@f_stat_bc': '', '@f_order_nm': None, '@f_rmks': None, '@f_cust_nm': None,
        })
    except Exception as e:
        log(f'  ⚠️ 장비별 투입 목록 — ERP 상세 조회 실패, 생략: {str(e)[:120]}')
        return None
    if len(df) == 0:
        log('  ⚠️ 장비별 투입 목록 — 상세 0행, 생략')
        return None
    wl = None
    try:
        from datetime import datetime as _dt
        wl = load_worklog(_dt.strptime(fr, '%Y-%m-%d').date())
    except Exception as e:
        log(f'  ⚠️ 장비별 투입 목록 — 작업일지 읽기 실패, 가공분 차감 없이 진행: {type(e).__name__}: {e}')
    try:
        q = build_queue(df, holds, worklog=wl)
        q['since'] = fr
        return q
    except Exception as e:
        log(f'  ⚠️ 장비별 투입 목록 집계 실패: {type(e).__name__}: {e}')
        return None
