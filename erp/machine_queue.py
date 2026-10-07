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
  (2026-10-01 (4) 변경: 작업일 기준 잔량 → 수량을 다 받는 후보 우선 → 오래된 수주. decisions.md 참조)
  2026-09-30: 후보가 여러 개일 때 리드타임(작업일−수주일) > LEAD_CAP_DAYS(30일) 후보는 더 가까운 후보가 있으면 뺀다(보류 대장 오더는 예외).
  2026-09-30: 형상 비교에서 작업일지 「면취」「NC」 = 드릴 · 날수가 같은 품목이 있으면 날수로도 좁힌다.
  5월 표본: 234코드 중 1건 확정 190 · 모호 0 · 직경 불일치 0 (나머지는 비교 기간 밖).

⚠️ 참고용 목록이다. 실제 투입은 현장 판단이 우선한다(장비 상태·긴급 요청·로더 사용 여부 등).
⚠️ 금액 열은 trico_client 기본 차단으로 들어오지 않는다.
"""
import re
from datetime import date, timedelta

FG, GX7, ETC = 'FG', 'GX7', '기타'


# ── 지연 일수 = 영업일 기준 (2026-09-29, 한경준님 확정) ─────────────────────
#   영업일 = 월~금 중 wiki/_handoff/holidays.md 에 없는 날.
#   토·일 제외 근거: 2025~2026 작업일지 작업 행 4,376건이 전부 월~금 [실측 검증 2026-09-29].
#   holidays.md 는 휴무일 단일 소스 — 법정공휴일(§1)·사내 휴무·개인 연차(§2) 날짜를 전부 읽는다.
#   파일을 못 읽으면 주말만 빼고 계산한다(목록 생성은 멈추지 않는다).
def load_holidays(base_dir=None):
    import os
    base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(base_dir, 'wiki', '_handoff', 'holidays.md')
    out = set()
    try:
        with open(p, encoding='utf-8') as f:
            for line in f:
                m = re.match(r'^\|\s*(\d{4})-(\d{2})-(\d{2})\s*\|', line)
                if m:
                    out.add(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
    except OSError:
        pass
    return out


def biz_days_late(dl, today, holidays=()):
    """납기(dl) 다음 날부터 오늘까지 영업일 수. 예) 납기 09-24(목), 오늘 09-29(화)
    → 09-25 추석·09-26 토·09-27 일 제외 → 09-28·09-29 = 2일"""
    n, d = 0, dl + timedelta(days=1)
    while d <= today:
        if d.weekday() < 5 and d not in holidays:
            n += 1
        d += timedelta(days=1)
    return n


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
            try:
                _ct = float(j[14] or 0)
            except (TypeError, ValueError):
                _ct = 0.0
            rows.append(dict(date=d, equip=j[3], shape=j[5], skey=shape_key(j[5]),
                             dia=float(m.group(1)) if m else None, qty=int(j[13]),
                             codes=re.findall(r'(?<!\d)(\d{4})(?!\d)', str(j[10])), note=str(j[10]),
                             blade=int(str(j[6]).strip()) if str(j[6]).strip().isdigit() else None,  # 2026-09-29
                             ct=_ct))
    return rows


# ── 리드타임 상한 (2026-09-30 신설, 한경준님 확정 — decisions.md 2026-09-30 (2)) ──────────────
#   근거: erp/probe_leadtime.py 실행(2026-09-30 08:52 KST) — 후보 1건 확정 811줄의 리드타임(작업일−수주일)
#         중앙 11일 · 99% 20일 · 최대 23일, 30일 초과 0줄 [실측 검증]. 여유 7일을 둬 30일.
#   효과(07:57 실행분 재계산): 모호 21줄 → 19줄 확정, 지금 배정과 다른 결과 0건. 남는 2줄은 두 후보가 모두 30일 이내.
#   후보가 하나뿐이면 절대 빼지 않는다. 보류 대장(hold_orders.json) 오더는 오래 걸리는 게 정상이라 빼지 않는다.
LEAD_CAP_DAYS = 30


# ── 작업일지 형상 → 매칭용 형상 (2026-09-30 신설, 한경준님 확정 — decisions.md 2026-09-30 (5)) ────────────
#   작업일지의 「면취」(챔퍼·면취_60` 등 포함)·「NC」(NC_HSS 등 포함)는 드릴 재연마 표기다.
#   근거 [실측 검증, 2026-09-30 10:37 스냅샷]: ERP 품목명에 「면취」 0행 · ERP 드릴 계열은 「드릴」 295행뿐.
#         작업일지 면취 줄 79/79 · NC 줄 21/21 이 후보 오더에 「드릴」 품목을 가진다. 면취 줄 86줄 중 84줄 2날.
#   매칭(apply_worklog)에서만 쓴다 — load_worklog 의 skey·FG 실적표(build_fg_capability)는 그대로 둔다.
def worklog_match_key(shape, skey=None):
    t = str(shape or '').replace(' ', '').lower()
    if '면취' in t or '챔퍼' in t or t.startswith('nc'):
        return '드릴'
    return skey if skey is not None else shape_key(shape)


def apply_worklog(d, wl, holds=None):
    """ERP 품목 DataFrame(d: so_no·so_dt·itm_nm·so_q 필요)에 작업일지 가공 수량을 붙인다.
    반환: (worked Series[index=d.index], equip dict[index→set], stats dict)"""
    import pandas as pd
    so4 = d['so_no'].astype(str).str[-4:]
    sdt = pd.to_datetime(d['so_dt'], errors='coerce', utc=True).dt.tz_convert('Asia/Seoul').dt.date
    dia = d['itm_nm'].map(lambda n: (parse_item(n) or {}).get('dia'))
    sk = d['itm_nm'].map(lambda n: shape_key((parse_item(n) or {}).get('shape')))
    worked = pd.Series(0, index=d.index, dtype=float)
    equip = {}
    st = dict(rows=len(wl), codes=0, matched=0, ambiguous=0, amb_resolved=0, unmatched=0, nocode=0, lead_cap=0)
    _holds = set(map(str, holds or ()))
    _contrib = {}   # 2026-09-30: 품목 행 → [(작업일, 장비, 수량, 번호, 특이사항)] — 초과 배정 경고용
    # 2026-09-29: 못 맞춘 줄을 사람이 확인할 수 있게 남긴다 (한경준님 확정) — write_unmatched_report()
    st['issues'] = []
    so4_set = set(so4)
    def _issue(r, kind, code='', why=''):
        st['issues'].append(dict(date=r['date'], equip=r['equip'], shape=r['shape'], dia=r['dia'],
                                 qty=r['qty'], code=code, note=r['note'], kind=kind, why=why))
    # 2026-10-07: 같은 날 안에서는 오더번호 1개 줄을 먼저 배정하고, 번호가 2개 이상인 줄은 남은 잔량을 채운다 (한경준님 확정)
    #   근거: 10-06 FG 「0160, 0141」 드릴 Ø6 9개 줄이 「0160」 14개 줄보다 먼저 처리돼 9개 전부 0160 에 들어감
    #         → 2609210160 드릴 6mm 수주 17 < 배정 23(+6), 2609180141 드릴 6mm 가 미가공으로 남음.
    #   회귀(10-07 07:50 스냅샷·오프라인 재현): 바뀐 것은 이 건뿐 — GX7 102→101품목 · 460→454개, 초과 배정 16→15.
    #   전역 정렬(날짜 무시)은 0166·0168 배정까지 바뀌어 기각. decisions.md 2026-10-07
    wl = sorted(wl, key=lambda r: (r['date'], len(r['codes']) > 1))
    for r in wl:
        if not r['codes']:
            st['nocode'] += 1
            # 2026-09-29: 「재가공」은 사내 재작업이라 오더가 없는 게 정상 — 확인 대상에서 뺀다(목록 맨 끝에 참고로만)
            if '재가공' in str(r['note']):
                _issue(r, '재가공', why='사내 재가공 — 오더번호 없음이 정상')
            else:
                _issue(r, '번호 없음', why='특이사항에 4자리 오더번호가 없다')
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
            _wk = worklog_match_key(r['shape'], r['skey'])   # 2026-09-30: 면취·NC → 드릴
            if len(cand) and _wk:
                same = cand[sk[cand.index] == _wk]
                if len(same):
                    cand = same
            # 2026-09-30 (6): 날수 비교 — 작업일지 날수와 같은 품목이 후보에 있으면 그 품목으로만 좁힌다(없으면 그대로)
            #   근거: 현장 확인 3건(2609180106 2날 코너 6mm 미가공 2 · 2609160118 4날 평 10mm 미가공 1 · 2609170166 3날 평 10mm 가공 완료)이
            #         모두 날수 미비교로 다른 품목에 붙거나 떨어져 나간 사례. decisions.md 2026-09-30 (6)
            if len(cand) and r.get('blade'):
                _bl = d.loc[cand.index, 'itm_nm'].map(lambda n: (parse_item(n) or {}).get('blade'))
                _sb = cand[_bl == r['blade']]
                if len(_sb):
                    cand = _sb
            if len(cand) == 0:
                st['unmatched'] += 1
                if c not in so4_set:
                    _why = '이 끝 4자리 오더가 조회 기간(120일) 수주에 없다 — 오타·기간 밖 의심'
                else:
                    _why = '끝 4자리 오더는 있으나 직경이 다르거나 수주일이 작업일보다 늦다'
                _issue(r, '매칭 실패', c, _why)
                continue
            orders = cand['so_no'].astype(str).unique()
            # 2026-09-30: 리드타임 상한 — 가까운 후보가 있을 때만 30일 초과 후보를 뺀다(보류 오더 예외)
            if len(orders) > 1 and LEAD_CAP_DAYS:
                _lead = {o: (r['date'] - sdt[cand.index[cand['so_no'].astype(str) == o][0]]).days for o in orders}
                _near = [o for o in orders if _lead[o] <= LEAD_CAP_DAYS]
                if _near and len(_near) < len(orders):
                    _keep = _near + [o for o in orders if o in _holds and o not in _near]
                    _drop = [o for o in orders if o not in _keep]
                    if _drop:
                        cand = cand[cand['so_no'].astype(str).isin(_keep)]
                        if len(_keep) == 1:
                            st['lead_cap'] += 1
                            _issue(r, '상한 확정', c, f'같은 끝 4자리 오더 {len(orders)}건: ' + ', '.join(sorted(orders))
                                   + f' → 리드타임 {LEAD_CAP_DAYS}일 초과 제외(' + ', '.join(f'{o} {_lead[o]}일' for o in sorted(_drop))
                                   + f') → {_keep[0]} 로 배정')
                        orders = cand['so_no'].astype(str).unique()
            if len(orders) > 1:
                # 모호 — ① 아직 깎을(또는 출하할) 게 남은 오더를 우선 ② 그중 가장 최근 수주 (2026-09-28 보강) → 2026-10-01 (4): ①을 작업일 기준으로 · ② 수량 적합 → 오래된 수주
                st['ambiguous'] += 1
                oq = d['out_q'] if 'out_q' in d else 0
                # 2026-10-01 (4): 출하량은 「작업일 이전(당일 포함)에 출하된 것」만 끝난 몫으로 본다 (한경준님 확정)
                #   근거: 0106 — 09-14 오더(09-29 출하)가 09-21 작업 당시엔 미출하였는데, 지금 출하 완료라는 이유로
                #         후보에서 밀려 09-18 오더에 30개가 몰렸다(초과 배정 +30·+10). decisions.md 2026-10-01 (4)
                _od = pd.to_datetime(d['out_dt'], errors='coerce', utc=True).dt.tz_convert('Asia/Seoul').dt.date if 'out_dt' in d else None
                def _left(o):
                    ix = cand.index[cand['so_no'].astype(str) == o]
                    _oq = pd.Series(oq, index=d.index)[ix]
                    if _od is not None:
                        _oq = _oq.where(_od[ix].map(lambda x: x is not None and not pd.isna(x) and x <= r['date']), 0)
                    return float((d.loc[ix, 'so_q'] - pd.concat([worked[ix], _oq], axis=1).max(axis=1)).clip(lower=0).sum())
                live = [o for o in orders if _left(o) > 0]
                if live and len(live) < len(orders):
                    st['amb_resolved'] = st.get('amb_resolved', 0) + 1
                pool = live or list(orders)
                # 2026-10-01 (4): 이 줄 수량을 다 받을 수 있는 후보(잔량 ≥ 수량)를 우선하고, 그중 「오래된 수주」를 고른다
                #   (종전: 가장 최근 수주 — 원래 식 max(pool, ...) 는 이 주석으로 남긴다). 회귀: 배정 바뀐 품목 4개(전부 0106) · 초과 배정 19→17
                _fit = [o for o in pool if _left(o) >= r['qty']]
                pool = _fit or pool
                latest = min(pool, key=lambda o: sdt[cand.index[cand['so_no'].astype(str) == o][0]])
                # 2026-09-29: 잔량 남은 오더가 1건뿐이면 사실상 확정 → 「자동 확정」, 둘 이상이면 「모호」(사람 확인)
                # 2026-09-30: 잔량 남은 후보가 0건인데 「모호」로 찍히던 버그 수정 → 「후보 모두 완료」 (배정 결과는 그대로)
                _kind = '자동 확정' if len(live) == 1 else ('후보 모두 완료' if not live else '모호')
                _issue(r, _kind, c, f'같은 끝 4자리 오더 {len(orders)}건: ' + ', '.join(sorted(orders)) + f' → {latest} 로 배정')
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
                    _contrib.setdefault(idx, []).append((r['date'], r['equip'], take, str(d.at[idx, 'so_no'])[-4:], r['note']))
    # 2026-09-30: 초과 배정 경고 (한경준님 확정) — 작업일지 배정량 > 수주량인 품목 행.
    #   「남는 수량은 마지막 후보에 얹는다」 규칙 때문에 오더·품목을 잘못 골라도 조용히 들어가던 것을 사람이 보게 한다.
    #   배정 결과는 바꾸지 않는다(표시만). 예: 2609180106 라핑코너 6MM 수주 1 ← 가공 11 (0106 오배정 의심)
    for idx, cl in _contrib.items():
        sq = float(d.at[idx, 'so_q'])
        if worked[idx] > sq + 1e-9:
            st['overflow'] = st.get('overflow', 0) + 1
            _p = parse_item(d.at[idx, 'itm_nm']) or {}
            _rows = ', '.join(f"{c[0]:%m-%d} {c[1]} {c[2]:g}개" for c in sorted(cl)[:6]) + (' …' if len(cl) > 6 else '')
            st['issues'].append(dict(date=max(c[0] for c in cl), equip='/'.join(sorted({c[1] for c in cl})),
                                     shape=_p.get('shape', ''), dia=_p.get('dia'), qty=int(worked[idx]),
                                     code=str(d.at[idx, 'so_no'])[-4:], note=' / '.join(sorted({str(c[4]) for c in cl}))[:30],
                                     kind='초과 배정',
                                     why=f"{d.at[idx, 'so_no']} 「{str(d.at[idx, 'itm_nm'])[:28]}」 수주 {sq:g} < 작업일지 배정 {worked[idx]:g} "
                                         f"(+{worked[idx] - sq:g}) — 들어온 줄: {_rows} → 번호·형상·날수 확인"))
    return worked, equip, st


def build_queue(df, holds=None, today=None, near_days=3, worklog=None, holidays=None, fg_cap=None):
    """상세 DataFrame → 장비별 정렬 목록 dict. 순수 함수(ERP 호출 없음) — 테스트 가능."""
    import pandas as pd
    holds = holds or {}
    today = today or date.today()
    dn = today + timedelta(days=near_days)
    hol = load_holidays() if holidays is None else set(holidays)

    d = df.copy()
    d['so_q'] = pd.to_numeric(d['so_qty'], errors='coerce').fillna(0)
    d['out_q'] = pd.to_numeric(d.get('out_qty'), errors='coerce').fillna(0) if 'out_qty' in d else 0
    d['so_no'] = d['so_no'].astype(str)
    wl_stats, wl_equip = None, {}
    if worklog is not None:
        d['worked'], wl_equip, wl_stats = apply_worklog(d, worklog, holds)   # 2026-09-30: 보류 오더는 리드타임 상한 예외
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
            # 2026-09-29: 달력일 → 영업일. 원래 식 f'지연 {(today - dl).days}일' 은 이 주석으로 남긴다
            _bd = biz_days_late(dl, today, hol)
            bucket, bkey, tag = 0, (0, 0), (f'지연 {_bd}일' if _bd else '지연(휴무 중)')
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
            fg_hint=fg_hint_for(p, fg_cap) if mach == GX7 else None,
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
                         setups=setups, edge=sum(1 for x in lst if x['edge']),
                         fg_ok=sum(1 for x in lst if (x.get('fg_hint') or {}).get('grade') == 'ok'),
                         fg_ok_qty=sum(x['rest'] for x in lst if (x.get('fg_hint') or {}).get('grade') == 'ok'),
                         fg_cond=sum(1 for x in lst if (x.get('fg_hint') or {}).get('grade') == 'cond'))
    out['etc'] = dict(n=len(items[ETC]), qty=sum(x['rest'] for x in items[ETC]),
                      names=sorted({x['itm'].split('/')[0] for x in items[ETC]}))
    out['excluded'] = dict(hold=int(ex_hold['so_no'].nunique()), minor=int(ex_minor['so_no'].nunique()))
    # 가공 완료(작업일지) 로 목록에서 빠진 품목 — 출하 전
    ground = d[(d['ship_rest'] > 0) & (d['rest'] <= 0) & ~d['so_no'].isin(holds)]
    out['worklog'] = dict(stats=wl_stats, ground_items=int(len(ground)), ground_qty=int(ground['ship_rest'].sum()),
                          tail_items=int(d['tail'].sum()))
    return out


def pd_to_date(sr):
    import pandas as pd
    return pd.to_datetime(sr, errors='coerce', utc=True).dt.tz_convert('Asia/Seoul').dt.date


# ── ERP 조회 스냅샷 (2026-09-30 신설, 한경준님 확정) ─────────────────────────────
#   목적: Cowork(리눅스 VM)는 ERP 주소가 허용 목록에서 막혀(403 blocked-by-allowlist) 직접 조회할 수 없다.
#         자동 실행(08:00·16:00 등)이 이미 받아 온 조회 결과를 파일로 남겨, 분석은 그 파일로 한다.
#   범위: 이 함수가 이미 하는 조회만 — 재연마 수주 품목 상세(chk_detail=1)·수주 머리(chk_detail=0). ERP 추가 호출 없음.
#   보관: 최신 1벌 덮어쓰기(날짜별 보관·자동 삭제 없음) · 거래처명 포함 · 위치 erp/snapshot/ (.gitignore 등재)
#   단가·금액: trico_client 기본 차단 + 저장 직전 is_price_col 로 한 번 더 뺀다(이중).
#   실패해도 목록 생성은 계속한다.
SNAPSHOT_DIR = None


def save_snapshot(name, df, fr, log=print):
    import os, json
    import pandas as pd
    try:
        from trico_client import is_price_col
        base = SNAPSHOT_DIR or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'snapshot')
        os.makedirs(base, exist_ok=True)
        blocked = [c for c in df.columns if is_price_col(str(c))]
        out = df.drop(columns=blocked, errors='ignore')
        path = os.path.join(base, f'{name}_latest.csv')
        tmp = path + '.tmp'
        out.to_csv(tmp, index=False, encoding='utf-8-sig')
        os.replace(tmp, path)
        mp = os.path.join(base, 'snapshot_meta.json')
        try:
            meta = json.load(open(mp, encoding='utf-8'))
        except Exception:
            meta = {}
        meta[name] = dict(saved_kst=pd.Timestamp.now(tz='Asia/Seoul').strftime('%Y-%m-%d %H:%M:%S'),
                          fr_dt=fr, to_dt='(오늘까지)', rows=int(len(out)), cols=[str(c) for c in out.columns],
                          price_cols_dropped_here=blocked)
        with open(mp + '.tmp', 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=1)
        os.replace(mp + '.tmp', mp)
        log(f'  → ERP 스냅샷 저장: erp/snapshot/{name}_latest.csv ({len(out)}행)'
            + (f' · 가격 열 추가 차단 {blocked}' if blocked else ''))
    except Exception as e:
        log(f'  ⚠️ ERP 스냅샷 저장 실패(목록 생성은 계속): {type(e).__name__}: {str(e)[:80]}')


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
    save_snapshot('jae_detail', df, fr, log)   # 2026-09-30 — 원본 그대로(납기 치환 전)
    # 2026-09-29: 납기는 수주 머리(chk_detail=0) 값을 쓴다 — 「오늘 할 일」과 같은 기준
    #   근거: erp/probe_dlv_mismatch.py 실행(2026-09-29 10:29 KST) — 수주 276건 중 9건이 머리≠품목 납기였고,
    #   9건 모두 품목 납기 = 수주일(오더번호 앞 6자리)이었다. 품목 줄 납기가 수주일 기본값으로 남은 것으로 보인다 [추정값].
    #   머리 조회가 실패하면 품목 납기로 계속한다(목록 생성은 멈추지 않는다).
    try:
        h = TricoClient().수주(fr_dt=fr)
        save_snapshot('jae_head', h, fr, log)   # 2026-09-30
        hd = h.drop_duplicates('so_no').assign(so_no=lambda x: x['so_no'].astype(str)).set_index('so_no')['dlv_dt']
        df = df.copy()
        df['so_no'] = df['so_no'].astype(str)
        old = df['dlv_dt'].copy()
        df['dlv_dt'] = df['so_no'].map(hd).fillna(df['dlv_dt'])
        _o = pd_to_date(old); _n = pd_to_date(df['dlv_dt'])
        log(f'  → 납기 = 수주 머리 기준 (품목 납기와 달라 바꾼 행 {int((_o != _n).sum())}개)')
    except Exception as e:
        log(f'  ⚠️ 수주 머리 납기 조회 실패 — 품목 납기로 진행: {type(e).__name__}: {str(e)[:80]}')
    wl, cap = None, None
    try:
        from datetime import datetime as _dt
        _fr = _dt.strptime(fr, '%Y-%m-%d').date()
        # 2026-09-29: 전년 1월부터 읽어 FG 실적표를 만들고, 가공분 차감에는 조회 기간(fr 이후)만 쓴다
        wl_all = load_worklog(min(_fr, date(date.today().year - 1, 1, 1)))
        wl = [r for r in wl_all if r['date'] >= _fr]
        try:
            cap = build_fg_capability(wl_all)
            log(f"  → FG 실적표: Ø8 초과 조합 {len(cap)}개 (🟢 {sum(1 for v in cap.values() if v['grade'] == 'ok')} · 🟡 {sum(1 for v in cap.values() if v['grade'] == 'cond')})")
        except Exception as e:
            log(f'  ⚠️ FG 실적표 생성 실패 — 표시 없이 진행: {type(e).__name__}: {e}')
    except Exception as e:
        log(f'  ⚠️ 장비별 투입 목록 — 작업일지 읽기 실패, 가공분 차감 없이 진행: {type(e).__name__}: {e}')
    try:
        q = build_queue(df, holds, worklog=wl, fg_cap=cap)
        q['since'] = fr
        try:
            n1, n2, n3 = write_unmatched_report(((q.get('worklog') or {}).get('stats') or {}).get('issues', []))
            log(f'  → 작업일지 확인 필요: 최근 14일 {n1}줄 · 그 이전 {n2}줄 (참고 {n3}줄) → erp/worklog_unmatched.txt')
        except Exception as e:
            log(f'  ⚠️ 작업일지 확인 목록 저장 실패(목록 생성은 계속): {type(e).__name__}: {e}')
        return q
    except Exception as e:
        log(f'  ⚠️ 장비별 투입 목록 집계 실패: {type(e).__name__}: {e}')
        return None


# ── 작업일지 확인 필요 목록 (2026-09-29 신설) ──────────────────────────────────
#   오더와 못 맞춘 작업일지 줄 = 목록에서 수량이 안 빠지는 줄. 현장에서 특이사항을 고치면 다음 실행에 반영된다.
#   파일은 매 실행마다 덮어쓴다(최신 1개). 거래처명·단가는 없지만 사내 기록이라 .gitignore 등재.
UNMATCHED_PATH = None


def write_unmatched_report(issues, path=None, recent_days=14, today=None):
    import os
    from datetime import datetime
    path = path or UNMATCHED_PATH or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worklog_unmatched.txt')
    today = today or date.today()
    order = {'번호 없음': 0, '매칭 실패': 1, '초과 배정': 2, '모호': 3, '후보 모두 완료': 4, '자동 확정': 5, '상한 확정': 6, '재가공': 7}
    iss = sorted(issues, key=lambda x: (-x['date'].toordinal(), order.get(x['kind'], 9), x['equip']))
    ACT = ('번호 없음', '매칭 실패', '초과 배정', '모호', '후보 모두 완료')          # 사람이 볼 것 (2026-09-30: 초과 배정·후보 모두 완료 추가)
    act = [x for x in iss if x['kind'] in ACT]
    info = [x for x in iss if x['kind'] not in ACT]   # 자동 확정·재가공 — 참고
    recent = [x for x in act if (today - x['date']).days <= recent_days]
    older = [x for x in act if (today - x['date']).days > recent_days]
    cnt = lambda L, k: sum(1 for x in L if x['kind'] == k)
    def fmt(x):
        dia = f"Ø{x['dia']:g}" if x['dia'] is not None else 'Ø?'
        code = x['code'] or '(없음)'
        return (f"{x['date']} | {x['equip']:<3} | {str(x['shape'])[:8]:<8} {dia:<6} {x['qty']:>3}개 | "
                f"{x['kind']} | 번호 {code} | 특이사항 「{str(x['note'])[:30]}」 | {x['why']}")
    try:
        from zoneinfo import ZoneInfo
        _now = datetime.now(ZoneInfo('Asia/Seoul'))
    except Exception:
        _now = datetime.now()
    L = [f"작업일지 확인 필요 목록 — 생성 {_now:%Y-%m-%d %H:%M} KST",
         "이 줄들은 ERP 오더와 못 맞춰서 「장비별 투입 목록」에서 수량이 빠지지 않는다.",
         "고치는 법: 월간생산일지 해당 행 특이사항에 오더번호 끝 4자리를 적거나 오타를 바로잡는다 → 다음 자동 실행에 반영",
         "※ 「모호」 = 끝 4자리가 같은 오더가 여럿이고 둘 이상에 잔량이 남아 있음 → 이 줄 수량을 다 받을 수 있는 오더 중 가장 오래된 오더로 배정했다(2026-10-01~, 잔량은 작업일 기준). 틀렸으면 현장에서 확인한 오더를 메모해 둔다 (⚠️ 특이사항에 10자리 전체를 적으면 지금은 인식하지 못해 「번호 없음」이 된다 — 2026-09-30 확인)",
         "※ 「자동 확정」(잔량 남은 오더가 1건뿐)·「재가공」(사내 재작업)은 확인할 필요 없음 — 맨 아래 참고 절에만 둔다",
         "※ 「초과 배정」(2026-09-30~) = 한 품목 행에 작업일지 수량이 수주량보다 많이 들어갔다 → 다른 오더·품목 몫이 잘못 붙었을 가능성. 줄의 번호·형상·날수를 확인한다",
         "※ 「후보 모두 완료」(2026-09-30~) = 끝 4자리가 같은 후보가 여럿인데 전부 잔량 0 → 가장 오래된 오더로 배정했다(2026-10-01~). 해당 형상 품목이 없으면 번호 오기 의심",
         f"※ 「상한 확정」(2026-09-30~) = 같은 끝 4자리 후보 중 리드타임 {LEAD_CAP_DAYS}일 초과 후보를 빼서 1건으로 확정(실측 최대 23일) — 참고 절",
         "",
         f"■ 최근 {recent_days}일 — {len(recent)}줄 (번호 없음 {cnt(recent, '번호 없음')} · 매칭 실패 {cnt(recent, '매칭 실패')} · 초과 배정 {cnt(recent, '초과 배정')} · 모호 {cnt(recent, '모호')} · 후보 모두 완료 {cnt(recent, '후보 모두 완료')})"]
    L += [fmt(x) for x in recent] or ['(없음)']
    L += ["", f"■ 그 이전 — {len(older)}줄 (번호 없음 {cnt(older, '번호 없음')} · 매칭 실패 {cnt(older, '매칭 실패')} · 초과 배정 {cnt(older, '초과 배정')} · 모호 {cnt(older, '모호')} · 후보 모두 완료 {cnt(older, '후보 모두 완료')}) — 대부분 이미 출하돼 영향 적음"]
    L += [fmt(x) for x in older] or ['(없음)']
    L += ["", f"■ 참고 — 확인 불필요 {len(info)}줄 (자동 확정 {cnt(info, '자동 확정')} · 상한 확정 {cnt(info, '상한 확정')} · 재가공 {cnt(info, '재가공')})"]
    L += [fmt(x) for x in info] or ['(없음)']
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    return len(recent), len(older), len(info)


# ── GX7 품목의 FG 실적 표시 (2026-09-29 신설, 한경준님 확정) ──────────────────────
#   목적: GX7 로더 사용 금지 중 GX7 대기(449개)가 FG(320개)보다 많다 → FG 에서 깎아 본 실적이 있는 GX7 품목을 표시
#   근거: 2025~2026 작업일지 실측 [실측 검증]. 「FG 로 옮겨라」가 아니라 「FG 실적이 있다」는 참고 표시 — 투입은 현장 판단
#   키: (형상 shape_key, 날수, 직경). 작업일지 형상에 라핑·HSS·NC 가 들어간 줄은 제외(배정 규칙상 원래 GX7 계열)
#   판정: FG 실적 ≥ FG_MIN_QTY 개 이고 FG/GX7 평균 가공시간 비 ≤ 1.5 → ok(🟢) / ≤ 2.0 → cond(🟡) / 그 외 표시 없음
#   2026-09-29 시험 집계: 🟢 평4Ø10(286개·1.44) 코너4Ø10(96·1.19) 코너4Ø12(50·1.31) 코너2Ø10(22·1.03) · 🟡 평4Ø12(26·1.73)
#   🔴 볼2Ø10·Ø12 는 FG 가공시간 2.2배라 표시 안 됨
FG_MIN_QTY = 20
FG_RATIO_OK, FG_RATIO_COND = 1.5, 2.0


def build_fg_capability(wl):
    agg = {}
    for r in wl:
        raw = str(r.get('shape') or '').lower()
        if '라핑' in raw or 'hss' in raw or 'nc' in raw:
            continue
        if not r.get('skey') or r.get('blade') is None or r.get('dia') is None or r['dia'] <= 8 or r['qty'] <= 0:
            continue
        a = agg.setdefault((r['skey'], r['blade'], r['dia']),
                           {'FG': [0, 0.0, 0, set()], 'GX7': [0, 0.0, 0, set()]})
        e = a.get(r['equip'])
        if e is None:
            continue
        e[0] += r['qty']
        e[3].add(r['date'])
        if r.get('ct', 0) > 1:
            e[1] += r['ct'] * r['qty']
            e[2] += r['qty']
    cap = {}
    for k, a in agg.items():
        fg, gx = a['FG'], a['GX7']
        if fg[0] <= 0:
            continue
        cf = fg[1] / fg[2] if fg[2] else None
        cg = gx[1] / gx[2] if gx[2] else None
        ratio = (cf / cg) if (cf and cg) else None
        if fg[0] >= FG_MIN_QTY and ratio is not None and ratio <= FG_RATIO_OK:
            grade = 'ok'
        elif fg[0] >= FG_MIN_QTY and ratio is not None and ratio <= FG_RATIO_COND:
            grade = 'cond'
        else:
            grade = None
        cap[k] = dict(grade=grade, fg_qty=fg[0], fg_days=len(fg[3]), ratio=ratio,
                      ct_fg=round(cf) if cf else None, ct_gx=round(cg) if cg else None)
    return cap


def fg_hint_for(p, cap):
    """GX7 배정 품목 p(parse_item 결과)의 FG 실적 판정. 직경 규칙(Ø8 초과)으로만 GX7 에 간 품목에만 붙인다."""
    if not cap or not p:
        return None
    if p['shape'] == '드릴' or p['mat'] == 'HSS' or '라핑' in p['shape'] or p['dia'] <= 8:
        return None
    v = cap.get((shape_key(p['shape']), p['blade'], p['dia']))
    if not v or not v['grade']:
        return None
    return v
