"""오늘(또는 지정일) 재연마 NC 생산량 확인 — ERP 작업실적(PPC120) 읽기 전용.

사용:
  python scripts\\today_output.py                (오늘, KST · 상세)
  python scripts\\today_output.py 2026-10-27     (지정일 · 상세)
  python scripts\\today_output.py --short        (요약만 · 2026-11-02 이전 형식)
  python scripts\\today_output.py --full         (저장본 안 쓰고 이번 달 전체를 ERP 에서 — 느림)
  python scripts\\today_output.py 2026-10-30 --csv erp\\snapshot\\pw_nc_2026-10-01_2026-10-30.csv
                                                 (ERP 대신 저장본으로 보기 — 시험·대조용)
- 속보값: ERP 에 실적을 입력한 만큼만 나온다(작업 중인 날은 낮게 나옴).
- 결과 파일을 쓰지 않는다(조회 속도용 g20 캐시만 erp_worklog 가 갱신). 일일보고서와 같은 함수(erp/erp_worklog.fetch_nc_results)를 쓴다.
- 창 프로그램: scripts/today_output_gui.py (생산량보기.bat) 가 compute() 를 같이 쓴다.
- 월평균 = 이번 달 1일 ~ 전날 중 실적이 있는 날의 평균.
- 추정 가공시간 = 표준공수 DB(erp_worklog.StdTime, 중앙값 초/개) × 개수. 신뢰도: 추정값(참고용).
- ERP 의 to_tm 은 대부분 20:00 고정이라 작업 종료 시각으로 쓰지 않는다. 시각 = fr_tm(실적 시작 입력).
- 2026-11-02 상세 출력 추가(이전본: today_output.py.bak_20261102).
- 2026-11-02 빠른 조회: 일일보고 저장본 + 그 뒤 날짜만 ERP(load 설명 참고) · 표준공수 DB 한 번만 읽기.
"""
import sys, datetime, argparse, unicodedata
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / 'erp'))
import erp_worklog as ew

KST = datetime.timezone(datetime.timedelta(hours=9))
LINE = '=' * 100      # 상자 그림 문자(─ ▇ …)는 한글 윈도 콘솔에서 2칸으로 보일 수 있어 ASCII 만 쓴다


# ── 한글 폭 맞춤 (콘솔에서 한글은 2칸) ──
def _w(s):
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in str(s))


def L(s, n):
    s = str(s)
    if _w(s) > n:
        out = ''
        for c in s:
            if _w(out + c) > n - 1:
                break
            out += c
        s = out + '~'
    return s + ' ' * max(0, n - _w(s))


def R(s, n):
    s = str(s)
    return ' ' * max(0, n - _w(s)) + s


def _day(x):
    return x if isinstance(x, datetime.date) else datetime.date.fromisoformat(str(x)[:10])


def _hm(minutes):
    m = int(round(minutes))
    return f'{m // 60}시간 {m % 60:02d}분' if m >= 60 else f'{m}분'


def _coat(row):
    c = row['jae_coating']
    nm = str(row['itm_nm'])
    if pd.isna(c) or str(c).strip() == '':
        c = '비코팅' if '비코팅' in nm else '미지정'
    if '고경도' in nm:
        c = f'{c}+고경도'
    return str(c)


def _dia_band(dia):
    if dia is None:
        return '규격 밖'
    for hi, lab in ((3, '~3'), (6, '3~6'), (10, '6~10'), (16, '10~16')):
        if dia <= hi:
            return lab
    return '16~'


SNAP_DIR = BASE / 'erp' / 'snapshot'


def _norm(df):
    df = df.copy()
    for c in ('ok', 'bad'):
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    df['work_dt'] = df['work_dt'].map(_day)
    for c in ('wo_no', 'so_no'):
        if c in df:
            df[c] = df[c].astype(str)
    return df


def _read_csv(p):
    try:
        return _norm(pd.read_csv(p, encoding='utf-8-sig'))
    except pd.errors.EmptyDataError:          # 실적 0줄 날 저장본은 빈 파일
        return pd.DataFrame()


def latest_snapshot(d):
    """이번 달 일일보고 저장본 중 가장 늦은 것 (끝날, 경로, 저장 시각 KST) — 없으면 None.
    일일보고(16:00)가 erp/snapshot/pw_nc_<1일>_<당일>.csv 로 남긴다. 끝날 당일분은 저장 시각까지만 들어 있다."""
    fr, best = d.replace(day=1), None
    for p in SNAP_DIR.glob(f'pw_nc_{fr}_*.csv'):
        try:
            to = datetime.date.fromisoformat(p.stem.rsplit('_', 1)[1])
        except ValueError:
            continue
        m = p.stat().st_mtime
        if best is None or (to, m) > (best[0], best[3]):
            best = (to, p, datetime.datetime.fromtimestamp(m, KST), m)
    return best[:3] if best else None


def load(d, csv=None, full=False, info=None):
    """이번 달 1일 ~ d 실적 줄. info(dict)에 출처 설명('src')을 채운다.

    빠른 조회(기본): 일일보고 저장본(끝날 T)이 있으면
      - T > d  → 저장본만 쓴다(ERP 조회 없음 · d 는 이미 지난 날)
      - T <= d → T 전날까지는 저장본, T ~ d 만 ERP 에서 읽는다(살아 있는 작업지시만 → 조회 수가 크게 준다)
      저장본 이후 지난 날짜에 늦게 입력된 실적은 빠질 수 있다 → full=True(전체 다시 읽기)로 이번 달 전체를 ERP 에서.
    """
    info = {} if info is None else info
    fr = d.replace(day=1)
    if csv:
        df = _read_csv(csv)
        info['src'] = f'저장본 {Path(csv).name}'
        return df[(df['work_dt'] >= fr) & (df['work_dt'] <= d)].copy() if len(df) else df
    snap = None if full else latest_snapshot(d)
    if snap:
        to, p, at = snap
        base = _read_csv(p)
        if to > d:
            info['src'] = f'일일보고 저장본({at:%m-%d %H:%M})'
            return base[base['work_dt'] <= d].copy() if len(base) else base
        if len(base):
            base = base[base['work_dt'] < to]
        new = ew.fetch_nc_results(to, d, use_cache=True, log=lambda *a: None)
        new = _norm(new) if len(new) else new
        info['src'] = (f'{to.month}/{to.day} 전까지 저장본({at:%m-%d %H:%M}) + ' if to > fr else '') + \
                      f'{to.month}/{to.day}' + ('' if to == d else f'~{d.month}/{d.day}') + ' ERP'
        parts = [x for x in (base, new) if len(x)]
        return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    info['src'] = 'ERP 이번 달 전체'
    df = ew.fetch_nc_results(fr, d, use_cache=True, log=lambda *a: None)
    return _norm(df) if len(df) else df


def short_view(d, df, t):
    """2026-11-02 이전 출력(요약)."""
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


def group_table(title, t, key, order=None):
    g = t.groupby(key).agg(rows=('qty', 'size'), ok=('ok', 'sum'), bad=('bad', 'sum'), qty=('qty', 'sum'),
                           est=('est_min', 'sum'))
    if order:
        g = g.reindex([k for k in order if k in g.index])
    else:
        g = g.sort_values('qty', ascending=False)
    tot = g['qty'].sum()
    print(f'\n{title}')
    print('  ' + L('구분', 18) + R('줄', 5) + R('양품', 7) + R('불량', 6) + R('합계', 7) + R('비율', 8) + R('추정 시간', 13))
    for k, r in g.iterrows():
        print('  ' + L(k, 18) + R(int(r['rows']), 5) + R(f"{int(r['ok']):,}", 7) + R(int(r['bad']), 6)
              + R(f"{int(r['qty']):,}", 7) + R(f"{r['qty'] / tot * 100:.0f} %", 8) + R(_hm(r['est']) if r['est'] else '-', 13))


_STD, _MEMO = None, {}


def std_time():
    """표준공수 DB 는 한 번만 읽는다(엑셀 읽기가 가장 느림)."""
    global _STD
    if _STD is None:
        _STD = ew.StdTime()
    return _STD


def _lookup(st, nm, angle):
    k = (str(nm), None if pd.isna(angle) else str(angle))
    if k not in _MEMO:
        _MEMO[k] = st.lookup(nm, angle)
    return _MEMO[k]


def compute(d, df, t):
    """상세 계산(콘솔 · 창 프로그램 공용). t 에 열을 덧붙이고 요약 dict 를 돌려준다."""
    r = {'std_err': None}
    try:
        st = std_time()
        res = [_lookup(st, n, a) for n, a in zip(t['itm_nm'], t['jae_angle'])]
        t['sec'] = [x[0] for x in res]
        t['basis'] = [x[1] for x in res]
    except Exception as e:                                   # DB 파일 없음 등 — 추정만 빼고 진행
        r['std_err'] = f'{type(e).__name__}: {e}'
        t['sec'] = None
        t['basis'] = '-'
    t['sec'] = pd.to_numeric(t['sec'], errors='coerce')
    t['est_min'] = [(s * q / 60) if pd.notna(s) else 0 for s, q in zip(t['sec'], t['qty'])]
    parts = t['itm_nm'].astype(str).str.split('/')
    t['item'] = parts.map(lambda p: '/'.join(x.strip() for x in p[:4]))
    t['shape'] = parts.map(lambda p: '/'.join(p[:2]) if len(p) > 1 else p[0])
    t['coat'] = t.apply(_coat, axis=1)
    t['dia'] = t['itm_nm'].map(lambda n: (ew.parse_item(n) or {}).get('dia'))
    t['band'] = t['dia'].map(_dia_band)
    t['tm'] = t['fr_tm'].astype(str).str[:5]
    t['hour'] = t['tm'].str[:2]
    t['mdt_s'] = t['mdt'].astype(str)
    t['late'] = t['mdt_s'].str[:10] != str(d)
    t['angle'] = t['jae_angle'].map(lambda x: '' if pd.isna(x) else str(x))

    r['ok'], r['bad'], r['qty'] = int(t['ok'].sum()), int(t['bad'].sum()), int(t['qty'].sum())
    r['rate'] = r['bad'] / r['qty'] * 100 if r['qty'] else 0
    r['wo'], r['so'], r['rows'], r['items'] = t['wo_no'].nunique(), t['so_no'].nunique(), len(t), t['itm_cd'].nunique()
    r['est_tot'] = float(t['est_min'].sum())
    r['no_std'] = int(t['sec'].isna().sum())
    prev = df[df['day'] < d].groupby('day')['qty'].sum()
    prev = prev[prev > 0]
    r['prev_days'] = len(prev)
    r['avg'] = float(prev.mean()) if len(prev) else None
    r['prev_day'] = prev.index[-1] if len(prev) else None
    r['prev_qty'] = int(prev.iloc[-1]) if len(prev) else None
    m = df[df['day'] <= d]
    r['m_ok'], r['m_bad'] = int(m['ok'].sum()), int(m['bad'].sum())
    r['m_days'] = int(m.groupby('day')['qty'].sum().gt(0).sum())
    r['last_input'] = t['mdt_s'].max()[:16].replace('T', ' ')
    r['groups'] = {
        'shape': _group(t, 'shape'),
        'band': _group(t, 'band', order=['~3', '3~6', '6~10', '10~16', '16~', '규격 밖']),
        'coat': _group(t, 'coat'),
        'hour': _group(t, 'hour', order=sorted(t['hour'].unique())),
    }
    return r


def _group(t, key, order=None):
    g = t.groupby(key).agg(rows=('qty', 'size'), ok=('ok', 'sum'), bad=('bad', 'sum'), qty=('qty', 'sum'),
                           est=('est_min', 'sum'))
    g = g.reindex([k for k in order if k in g.index]) if order else g.sort_values('qty', ascending=False)
    g['pct'] = g['qty'] / max(1, g['qty'].sum()) * 100
    return g


def group_table(title, g):
    print(f'\n{title}')
    print('  ' + L('구분', 18) + R('줄', 5) + R('양품', 7) + R('불량', 6) + R('합계', 7) + R('비율', 8) + R('추정 시간', 13))
    for k, r in g.iterrows():
        print('  ' + L(k, 18) + R(int(r['rows']), 5) + R(f"{int(r['ok']):,}", 7) + R(int(r['bad']), 6)
              + R(f"{int(r['qty']):,}", 7) + R(f"{r['pct']:.0f} %", 8) + R(_hm(r['est']) if r['est'] else '-', 13))


def detail_view(d, df, t):
    r = compute(d, df, t)
    if r['std_err']:
        print(f"  (표준공수 DB 읽기 실패 — 추정 시간 생략: {r['std_err']})")

    # 1. 요약
    print('\n1. 요약')
    print(f"  양품 {r['ok']:,} 개 · 불량 {r['bad']:,} 개 · 합계 {r['qty']:,} 개 · 불량률 {r['rate']:.1f} %")
    print(f"  작업지시 {r['wo']} 건 · 수주 {r['so']} 건 · 실적 {r['rows']} 줄 · 품목 {r['items']} 종")
    if r['est_tot']:
        print(f"  추정 가공시간 합 {_hm(r['est_tot'])} (표준공수 DB 중앙값 × 개수 · 추정값"
              + (f" · 표준 없음 {r['no_std']} 줄 제외)" if r['no_std'] else ')'))
    if r['avg']:
        print(f"  {d.month}월 평균(이전 작업일 {r['prev_days']}일) {r['avg']:,.0f} 개 → 이날은 평균의 {r['qty'] / r['avg'] * 100:.0f} %"
              f" · 전 작업일 {r['prev_day']} {r['prev_qty']:,} 개")
    print(f"  {d.month}월 누계({d.month}/1~{d.day}, 작업일 {r['m_days']}일) 양품 {r['m_ok']:,} 개 · 불량 {r['m_bad']:,} 개"
          f" · 불량률 {r['m_bad'] / max(1, r['m_ok'] + r['m_bad']) * 100:.1f} %")
    print(f"  마지막 실적 입력: {r['last_input']}")

    # 2. 실적 목록
    print('\n2. 실적 목록 (설비별 · 시각 순, 시각 = 실적 시작 입력, * = 다음 날 이후 입력)')
    hdr = ('  ' + R('No', 3) + ' ' + L('시각', 7) + L('관리번호', 12) + L('품목(날/형상/지름/소재)', 24) + L('코팅', 11)
           + L('각도', 6) + R('양품', 5) + R('불량', 5) + R('초/개', 7) + R('추정', 7) + '  ' + L('표준 기준', 14))
    n = 0
    for mc, g in t.sort_values(['mc_cd', 'tm', 'mdt_s']).groupby('mc_cd', sort=True):
        print(f'  [설비 {mc}]')
        print(hdr)
        print('  ' + '-' * 98)
        for _, x in g.iterrows():
            n += 1
            sec = f"{x['sec']:.0f}" if pd.notna(x['sec']) else '-'
            est = f"{x['est_min']:.0f}분" if x['est_min'] else '-'
            print('  ' + R(n, 3) + ' ' + L(x['tm'] + ('*' if x['late'] else ''), 7) + L(x['mng_no'], 12) + L(x['item'], 24)
                  + L(x['coat'], 11) + L(x['angle'], 6) + R(int(x['ok']), 5) + R(int(x['bad']) or '', 5) + R(sec, 7) + R(est, 7)
                  + '  ' + L(str(x['basis']).replace(' · 라핑 근사', '(라핑근사)'), 14))
        print('  ' + '-' * 98)
        print(f'  소계 {len(g)} 줄 · 양품 {int(g["ok"].sum()):,} · 불량 {int(g["bad"].sum())} · 합계 {int(g["qty"].sum()):,} 개'
              + (f' · 추정 {_hm(g["est_min"].sum())}' if g['est_min'].sum() else ''))

    # 3~6. 나눠 보기
    group_table('3. 형상별 (날수/형상)', r['groups']['shape'])
    group_table('4. 공구 지름별 (mm)', r['groups']['band'])
    group_table('5. 코팅별', r['groups']['coat'])
    print('\n6. 시간대별 실적 입력 (fr_tm 기준 · # 1칸 = 2 개)')
    for h, g in r['groups']['hour'].iterrows():
        q = int(g['qty'])
        print(f"  {h}시  {int(g['rows']):>2} 줄 {q:>4} 개  " + '#' * min(40, (q + 1) // 2) + ('+' if q > 80 else ''))

    # 7. 불량
    b = t[t['bad'] > 0]
    print(f'\n7. 불량 상세 ({len(b)} 줄)')
    if not len(b):
        print('  불량 입력 없음')
    for _, x in b.iterrows():
        print(f"  {x['tm']} {x['mng_no']}  {x['item']}  {x['coat']}  양품 {int(x['ok'])} / 불량 {int(x['bad'])}"
              f"  (작업지시 {x['wo_no']})")

    # 8. 표준공수 없는 품목
    xs = t[t['sec'].isna()]
    if len(xs):
        print(f'\n8. 표준공수 없음 ({len(xs)} 줄 · 추정 시간에서 빠짐)')
        for _, x in xs.iterrows():
            print(f"  {x['mng_no']}  {x['itm_nm']}  → {x['basis']}")
    print('\n' + LINE)
    print('  속보값: ERP 입력분만 집계. 추정 시간은 참고값(표준공수 DB 중앙값 · 추정값) — 실측 대체 아님.')


def prepare(df, d):
    """조회 결과에 qty · day 를 붙이고 (df, 그날 줄 t) 를 돌려준다."""
    df = df.copy()
    df['qty'] = df['ok'] + df['bad']
    df['day'] = df['work_dt'].map(_day)
    return df, df[df['day'] == d].copy()


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('date', nargs='?', help='YYYY-MM-DD (없으면 오늘 KST)')
    ap.add_argument('--short', action='store_true', help='요약만')
    ap.add_argument('--csv', help='ERP 대신 저장본 CSV 로 보기(시험용)')
    ap.add_argument('--full', action='store_true', help='저장본 안 쓰고 이번 달 전체를 ERP 에서')
    a = ap.parse_args()
    d = datetime.date.fromisoformat(a.date) if a.date else datetime.datetime.now(KST).date()
    info = {}
    df = load(d, a.csv, full=a.full, info=info)
    now = datetime.datetime.now(KST)
    src = info.get('src', 'ERP')
    print(f'재연마 NC 생산량 — {d} (조회 {now:%Y-%m-%d %H:%M} KST · {src} · 속보값)')
    print(LINE)
    if not len(df):
        print('  이번 달 실적 없음'); return
    df, t = prepare(df, d)
    if not len(t):
        print('  이날 입력된 실적 없음'); return
    if a.short:
        short_view(d, df, t)
    else:
        detail_view(d, df, t)


if __name__ == '__main__':
    main()
