# -*- coding: utf-8 -*-
"""ERP 작업실적(NC 공정) 조회 — 일일보고 · 현황판이 엑셀 월간생산일지 대신 읽는다 (2026-10-23 Cowork 신설)

배경: 엑셀 작업일지 입력을 2026-10-23 부터 멈추고 생산 실적은 ERP 하나로 간다(decisions 2026-10-23 (4) · (5) · (6)).
읽기 전용 — FillDataSetEx(조회)만 쓴다. ERP 에 저장하지 않는다. 가격 컬럼은 TricoClient 기본값대로 차단.

조회 순서
  PPC120_g00 (작업지시, 기간 = 작업지시일) → PPC120_g10 (@wo_no, 공정 현황 · 공정별 wo_id)
  → PPC120_g20 (@wo_id BigInt, 작업실적 줄: work_dt · mc_cd · ok_qty · bad_in_qty · pw_tm …)
  - g00 의 기간은 작업지시일이라, 앞선 달에 낸 지시를 이번 달에 가공한 실적이 빠진다 → 지시는 LOOKBACK 일 앞부터 읽고,
    작업실적을 work_dt 로 거른다(probe_pw_detail.py 와 같은 방식).
  - 조회 수를 줄이려고 작업 시작일(wo_fr_dt)이 없거나 작업 완료일(wo_to_dt)이 기간 시작 − MARGIN 일보다 앞선 지시는 건너뛴다.
    full=True 면 거르지 않는다(대조용).
  - g10 의 NC 공정 줄 투입누계(wrk_in_tot)가 0 이면 그 공정은 실적이 없으므로 g20 을 부르지 않는다.
  - prc_cd 20 = NC(FG · GX7 합침, 장비 구분 없음) · 30 = 코팅

실측(2026-10-23, probe_pw_detail): 10-01 ~ 10-23 NC 작업실적 176줄 · 양품 947 · 불량 8 / 엑셀 FG+GX7 합 971
"""
import io, contextlib, os, time
from datetime import date, datetime, timedelta

import pandas as pd

LOOKBACK = 90     # 작업지시를 기간 시작보다 며칠 앞부터 읽을지
MARGIN = 7        # 작업 완료일 거르기 여유(일)
NC = '20'
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, 'snapshot')     # .gitignore 의 erp/snapshot/ — 추적 안 함

_BIGINT_XML = ('<a:SQLArray><a:ParamaterDataTable i:nil="true"/><a:ParamaterDirection>Input</a:ParamaterDirection>'
               '<a:ParamaterName>{name}</a:ParamaterName><a:ParamaterPrecision>0</a:ParamaterPrecision>'
               '<a:ParamaterScale>0</a:ParamaterScale><a:ParamaterSize>0</a:ParamaterSize>'
               '<a:ParamaterValue i:type="b:long" xmlns:b="http://www.w3.org/2001/XMLSchema">{value}</a:ParamaterValue>'
               '<a:Paramatertype>BigInt</a:Paramatertype><a:Paramatertypename/></a:SQLArray>')


def _num(frame, col):
    """열이 없으면 0 (ERP 는 값이 모두 빈 열을 응답에서 뺀다)."""
    if col not in frame.columns:
        return pd.Series(0.0, index=frame.index)
    return pd.to_numeric(frame[col], errors='coerce').fillna(0)


def _day(sr):
    """ERP 날짜(문자열 · +09:00) → date. 빈 값은 NaT."""
    return pd.to_datetime(sr.astype(str).str[:10], errors='coerce').dt.date


def _q(c, ws, params):
    """조회 + 가격 컬럼 차단 경고 출력 숨김(차단 자체는 그대로)."""
    with contextlib.redirect_stdout(io.StringIO()):
        return c.query(ws, params)


# ── g20 작업실적 캐시 (2026-10-27 신설 — decisions 2026-10-27 (7)) ─────────────────────────
# g10 NC 공정 줄의 누계(투입 wrk_in_tot · 양품 ok_in_tot · 불량 bad_in_tot)가 지난번과 같으면 그 공정의 g20 실적 줄도
# 바뀌지 않았다고 보고 저장해 둔 줄을 다시 쓴다 → 새 실적이 들어온 공정만 g20 을 부른다.
# 한계: 누계는 그대로인데 지난 실적의 날짜 · 설비만 고친 경우는 못 잡는다 → CACHE_DAYS 일이 지난 항목은 새로 읽고,
#       full=True 또는 use_cache=False 면 캐시를 안 쓴다.
# ✅ 2026-10-27 13:23 PC 검증(probe_g20_cache.py, 10-01 ~ 10-27): 캐시 없음 ↔ 캐시 재사용 196줄 · 날짜별 양품 1,028 · 불량 8 모두 같음 ·
#    조회 495 → 250회 · 48 → 15 s → 켬(decisions 2026-10-27 (7)). 끄기 = 아래 값을 False 로.
G20_CACHE = True
CACHE_DAYS = 7
G20_CACHE_PATH = os.path.join(CACHE_DIR, 'g20_cache.json')
_G20_KEEP = ('work_dt', 'prc_cd', 'mc_cd', 'ok_qty', 'bad_in_qty', 'pw_tm', 'mng_no', 'pw_no', 'pw_sq', 'fr_tm', 'to_tm', 'mdt')


def _sig(n):
    """g10 NC 공정 줄의 누계 서명 '투입|양품|불량'."""
    def f(k):
        v = pd.to_numeric(n.get(k), errors='coerce')
        return '' if pd.isna(v) else f'{float(v):g}'
    return f"{f('wrk_in_tot')}|{f('ok_in_tot')}|{f('bad_in_tot')}"


def _load_g20_cache(path):
    import json
    try:
        with open(path, encoding='utf-8') as fp:
            d = json.load(fp)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _save_g20_cache(path, cache, log=print):
    import json
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as fp:
            json.dump(cache, fp, ensure_ascii=False, default=str)
        os.replace(tmp, path)
    except Exception as e:
        log(f'  ⚠️ g20 캐시 저장 실패(조회 결과는 그대로): {type(e).__name__}: {e}')


def fetch_nc_results(fr, to, client=None, log=print, full=False, prc=NC, use_cache=None, cache_path=None):
    """작업일 fr ~ to (date 또는 'YYYY-MM-DD') 의 NC 작업실적 줄 DataFrame.

    열: work_dt(date) · wo_no · so_no · itm_cd · itm_nm · jae_coating · jae_angle · prc_cd · mc_cd · ok · bad ·
        pw_tm · mng_no · pw_no · pw_sq · fr_tm · to_tm · mdt
    실패하면 예외를 그대로 올린다(호출하는 쪽에서 처리).
    """
    from trico_client import TricoClient
    fr = fr if isinstance(fr, date) else date.fromisoformat(str(fr))
    to = to if isinstance(to, date) else date.fromisoformat(str(to))
    c = client or TricoClient()
    t0 = time.time()
    if use_cache is None:
        use_cache = G20_CACHE or os.getenv('ERP_G20_CACHE', '') == '1'
    use_cache = bool(use_cache) and not full
    cache_path = cache_path or G20_CACHE_PATH
    cache = _load_g20_cache(cache_path) if use_cache else {}
    now = datetime.now()
    hit = miss = 0
    g00 = c.생산실적(fr_dt=(fr - timedelta(days=LOOKBACK)).isoformat(), to_dt=to.isoformat())
    n_all = len(g00)
    if not n_all:
        log(f'  ⚠️ ERP 작업지시 0행 ({fr} ~ {to})')
        return pd.DataFrame()
    if not full:
        wfr = _day(g00['wo_fr_dt']) if 'wo_fr_dt' in g00 else pd.Series(pd.NaT, index=g00.index)
        wto = _day(g00['wo_to_dt']) if 'wo_to_dt' in g00 else pd.Series(pd.NaT, index=g00.index)
        started = wfr.notna() & (wfr <= to)
        alive = wto.isna() | (wto >= fr - timedelta(days=MARGIN))
        g00 = g00[started & alive]
    g00 = g00.drop_duplicates('wo_no')

    # @wo_id 는 BigInt(long)로 보내야 한다 — 이 함수 안에서만 이 클라이언트의 _param_xml 을 감싼다
    import types
    orig = c._param_xml

    def _px(self, name, value, size=0, type_='NVarChar'):
        if name == '@wo_id' and isinstance(value, int) and not isinstance(value, bool):
            return _BIGINT_XML.format(name=name, value=value)
        return orig(name, value, size, type_)

    c._param_xml = types.MethodType(_px, c)
    rows, calls, fail = [], 1, 0
    try:
        for _, r in g00.iterrows():
            try:
                g10 = _q(c, 'PPC120_g10', {'@wo_no': str(r['wo_no']), '@dn_bc': None, '@capsule_mng_no': None, '@co_cd': '01'})
                calls += 1
            except Exception:
                fail += 1; continue
            if not len(g10) or 'prc_cd' not in g10.columns:
                continue
            for _, n in g10[g10['prc_cd'].astype(str) == prc].iterrows():
                if 'wrk_in_tot' in g10.columns:
                    wi = pd.to_numeric(n.get('wrk_in_tot'), errors='coerce')
                    if pd.isna(wi) or float(wi) <= 0:
                        continue
                wid = pd.to_numeric(n.get('wo_id'), errors='coerce')
                if pd.isna(wid):
                    continue
                ck, sg = str(int(wid)), _sig(n)
                ent = cache.get(ck) if use_cache else None
                fresh = False
                if ent and ent.get('sig') == sg:
                    try:
                        fresh = (now - datetime.fromisoformat(ent.get('at', ''))).days < CACHE_DAYS
                    except Exception:
                        fresh = False
                if fresh:
                    g20 = pd.DataFrame(ent.get('rows') or [])
                    hit += 1
                else:
                    try:
                        g20 = _q(c, 'PPC120_g20', {'@wo_id': int(wid), '@ent_bc': 'PP270100'})
                        calls += 1
                    except Exception:
                        fail += 1; continue
                    if len(g20) and 'prc_cd' in g20.columns:
                        g20 = g20[g20['prc_cd'].astype(str) == prc]
                    if use_cache:
                        keep = [k for k in _G20_KEEP if k in g20.columns]
                        cache[ck] = {'sig': sg, 'at': now.isoformat(timespec='seconds'),
                                     'rows': g20[keep].astype(object).where(g20[keep].notna(), None).to_dict('records') if len(g20) else []}
                        miss += 1
                if not len(g20):
                    continue
                if 'prc_cd' in g20.columns:
                    g20 = g20[g20['prc_cd'].astype(str) == prc]
                g20 = g20.assign(work_dt=_day(g20['work_dt']) if 'work_dt' in g20 else pd.NaT)
                g20 = g20[(g20['work_dt'] >= fr) & (g20['work_dt'] <= to)]
                if not len(g20):
                    continue
                out = pd.DataFrame({
                    'work_dt': g20['work_dt'],
                    'wo_no': str(r['wo_no']), 'so_no': str(r.get('so_no', '')), 'itm_cd': str(r.get('itm_cd', '')),
                    'itm_nm': str(r.get('itm_nm', '')),
                    'jae_coating': r.get('jae_coating'), 'jae_angle': r.get('jae_angle'),
                    'prc_cd': prc,
                    'mc_cd': g20['mc_cd'] if 'mc_cd' in g20 else '',
                    'ok': _num(g20, 'ok_qty'), 'bad': _num(g20, 'bad_in_qty'), 'pw_tm': _num(g20, 'pw_tm'),
                })
                for k in ('mng_no', 'pw_no', 'pw_sq', 'fr_tm', 'to_tm', 'mdt'):
                    out[k] = g20[k] if k in g20 else ''
                rows.append(out)
    finally:
        del c._param_xml
    if use_cache and miss:
        _save_g20_cache(cache_path, cache, log)
    df = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    log(f'  → ERP 작업실적(NC) {fr} ~ {to}: 작업지시 {len(g00)}/{n_all}개{" (전체)" if full else ""} · 조회 {calls}회(실패 {fail}) · '
        f'{len(df)}줄 · 양품 {df["ok"].sum() if len(df) else 0:g} · 불량 {df["bad"].sum() if len(df) else 0:g} · {time.time() - t0:.0f}s'
        + (f' · g20 캐시 재사용 {hit} / 새로 읽음 {miss}' if use_cache else ''))
    if fail:
        log(f'  ⚠️ 조회 실패 {fail}회 — 실적이 일부 빠졌을 수 있음')
    return df


def save_cache(df, fr, to):
    """조회 결과를 erp/snapshot/pw_nc_<fr>_<to>.csv 로 남긴다(현황판 전환 때 재사용 · 대조용). 가격 열 없음."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        p = os.path.join(CACHE_DIR, f'pw_nc_{fr}_{to}.csv')
        df.to_csv(p, index=False, encoding='utf-8-sig')
        return p
    except Exception:
        return None


# ── 표준공수(초/개) 추정 ─────────────────────────────────────────────────────────
# 출처: wiki/measurements/재연마_표준공수DB_2022-2026_통합본_20261023.xlsx 「표준 공수 DB」 시트(엑셀 작업일지 2022-01 ~ 2026-10-23 의 개당 가공시간 중앙값)
# 신뢰도: 사내 경험값 기반 **추정값** — 그날 실제 가공시간이 아니다. ERP 「작업(분)」(pw_tm)은 시작 ~ 종료 경과시간이라 쓰지 않는다.
# 맞추는 순서(기준 표기)
#   ① 일치        : 형상 · 지름 · 날수 · 소재가 같은 줄
#   ② 형상군      : 코너(R 값 모름) 처럼 ERP 품목명이 DB 보다 덜 자세할 때 — 같은 형상군 · 지름 · 날수 · 소재 줄들의 표본수 가중 평균
#   ③ 근사 지름   : 형상군 · 소재 같고 지름 차 0.5 mm 이내(날수 무관) 표본수 가중 평균
#   ④ 형상 평균   : 형상군 · 소재 전체 표본수 가중 평균
#   없음          : 형상을 DB 에서 못 찾음 → 시간 합계에서 빼고 줄 수를 따로 표시
import re as _re
# 2026-10-23: 엑셀 작업일지 마지막 판으로 만든 통합본으로 바꿈(옛 파일 재연마_표준공수DB_2022-2026.xlsx 는 그대로 둠) — decisions 2026-10-23 (9)
STD_DB = os.path.join(os.path.dirname(HERE), 'wiki', 'measurements', '재연마_표준공수DB_2022-2026_통합본_20261023.xlsx')
if not os.path.exists(STD_DB):   # 통합본이 없으면 옛 파일
    STD_DB = os.path.join(os.path.dirname(HERE), 'wiki', 'measurements', '재연마_표준공수DB_2022-2026.xlsx')

# ERP 품목명 형상 → DB 형상군(접두어). 라핑 계열은 DB 에 따로 없어 기본 형상으로 근사하고 기준에 「근사」 를 붙인다.
_SHAPE = {'평': '평', '볼': '볼', '코너': '코너R', '드릴': '드릴', '면취': '면취',
          '라핑코너': '코너R', '라핑평': '평', '라핑볼': '볼'}


def parse_item(nm):
    """'4날/평/10mm/초경/밑날/일반 코팅' → dict(blade, shape, dia, mat). 규격 밖이면 None."""
    p = [x.strip() for x in str(nm or '').split('/')]
    if len(p) < 4:
        return None
    b = _re.match(r'^(\d+)\s*날', p[0]); m = _re.match(r'^([\d.]+)', p[2])
    if not b or not m:
        return None
    mat = 'HSS' if p[3].upper() == 'HSS' else p[3]
    return dict(blade=int(b.group(1)), shape=p[1], dia=float(m.group(1)), mat=mat)


def _group(db_shape):
    s = str(db_shape)
    if s.startswith('코너'):
        return '코너R'
    if s.startswith('평'):
        return '평'
    return s          # 볼 · 드릴 · NC드릴 · 면취


class StdTime:
    def __init__(self, path=STD_DB):
        db = pd.read_excel(path, sheet_name='표준 공수 DB', header=2)
        db = db[pd.to_numeric(db['중앙값'], errors='coerce').notna()].copy()
        db['grp'] = db['형상'].map(_group)
        for k in ('직경', '날수', '중앙값', '표본수'):
            db[k] = pd.to_numeric(db[k], errors='coerce')
        self.db = db

    @staticmethod
    def _wavg(x):
        w = x['표본수'].fillna(1).clip(lower=1)
        return float((x['중앙값'] * w).sum() / w.sum())

    def lookup(self, itm_nm, angle=None):
        """(초/개 또는 None, 기준 문자열). angle = 작업지시 jae_angle(예: 'R1') — 코너의 R 값을 알면 「일치」로 맞춘다."""
        p = parse_item(itm_nm)
        if p is None:
            return None, '없음(품목명 규격 밖)'
        g = _SHAPE.get(p['shape'])
        if g is None:
            return None, f"없음(형상 「{p['shape']}」)"
        approx = ' · 라핑 근사' if p['shape'].startswith('라핑') else ''
        d = self.db[(self.db['grp'] == g) & (self.db['소재'] == p['mat'])]
        if not len(d):
            return None, f"없음({g} · {p['mat']})"
        exact_shape = d['형상'].isin([{'평': '평(스퀘어)'}.get(g, g)]) if g != '코너R' else pd.Series(False, index=d.index)
        if g == '코너R':
            m = _re.match(r'^\s*R\s*([\d.]+)', str(angle or ''), _re.I)
            if m:
                exact_shape = d['형상'] == f"코너R{float(m.group(1)):g}"
        x = d[exact_shape & (d['직경'] == p['dia']) & (d['날수'] == p['blade'])]
        if len(x):
            return float(x['중앙값'].iloc[0]), '일치' + approx
        x = d[(d['직경'] == p['dia']) & (d['날수'] == p['blade'])]
        if len(x):
            return self._wavg(x), '형상군' + approx
        x = d[(d['직경'] - p['dia']).abs() <= 0.5]
        if len(x):
            return self._wavg(x), '근사 지름' + approx
        return self._wavg(d), '형상 평균' + approx
