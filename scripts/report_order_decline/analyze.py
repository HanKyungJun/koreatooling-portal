# 수주 감소 원인 분석 보고(2026-11-27) — 원자료 집계 → data.json (거래처는 익명 코드만 저장)
# 실행: python analyze.py   (cnc-wiki 루트 기준 경로)
import csv, glob, json, os, re, warnings
import pandas as pd
warnings.filterwarnings('ignore')
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
J = lambda *p: os.path.join(BASE, *p)
BIG3 = ['거래처 C', '거래처 O', '거래처 W']

# 익명 코드 대조 (wiki/_private, 실명은 data.json 에 남기지 않음)
def core(n):
    c = re.sub(r'\(주\)|㈜|주식회사|\(유\)|유한회사', '', str(n)); return re.sub(r'\(.*?\)|-.*$', '', c).strip()
M = {}
for r in csv.DictReader(open(J('wiki', '_private', '거래처_익명코드표.csv'), encoding='utf-8-sig')):
    M[r['core'].strip()] = r['code']
    for v in re.split(r'[|;/]', r['variants'] or ''):
        if v.strip(): M[v.strip()] = r['code']; M[core(v)] = r['code']
code = lambda n: M.get(str(n).strip()) or M.get(core(n)) or '미매핑'

# 1) 출하: 납품처별 월별 (익명판)
def ship(y):
    d = pd.read_excel(J('wiki', 'comparisons', f'출하현황_납품처별_월별분석_{y}.xlsx'), sheet_name='요약', header=1)
    d = d[d['납품처명'].astype(str).str.startswith('거래처')]
    m = [f'{i}월' for i in range(1, 13)]
    return d.set_index('납품처명')[m].fillna(0).astype(float)
a, b = ship(2025), ship(2026)
idx = a.index.union(b.index); a = a.reindex(idx, fill_value=0); b = b.reindex(idx, fill_value=0)
ex = ~idx.isin(BIG3)
S = {'2025': {}, '2026': {}}
for y, t in (('2025', a), ('2026', b)):
    S[y] = {'전체': [int(t[f'{i}월'].sum()) for i in range(1, 13)],
            '대형3': [int(t.loc[~ex, f'{i}월'].sum()) for i in range(1, 13)],
            '고객수': [int((t[f'{i}월'] > 0).sum()) for i in range(1, 13)],
            **{c: [int(t.loc[c, f'{i}월']) for i in range(1, 13)] for c in BIG3}}
def period(r):
    c = [f'{i}월' for i in r]
    return {k: [int(a.loc[msk, c].sum().sum()), int(b.loc[msk, c].sum().sum())] for k, msk in (('전체', idx == idx), ('대형3제외', ex))}
S['기간'] = {'1~7월': period(range(1, 8)), '8~10월': period(range(8, 11)), '1~10월': period(range(1, 11))}
S['2025연간'] = int(a.sum().sum()); S['C2025'] = int(a.loc['거래처 C'].sum())

# 2) 수주: 6~9월 월별 export + 10월 ERP 스냅샷(2026-11-10 저장)
rows = []
for f in sorted(glob.glob(J('raw', '수주현황', '재연마 수주현황_*.xlsx'))) + [J('raw', '출하현황', '재연마 수주현황_20260611132814.xlsx')]:
    d = pd.read_excel(f); d = d[d['수주번호'].notna()]; d['mt'] = os.path.getmtime(f); rows.append(d)
o = pd.concat(rows).sort_values('mt').drop_duplicates('수주번호', keep='last')
o['dt'] = pd.to_datetime(o['수주일자'], errors='coerce'); o['code'] = o['납품처명'].map(code); o['q'] = o['수주량']
s = pd.read_csv(J('erp', 'snapshot', 'jae_head_latest.csv')); s['dt'] = pd.to_datetime(s['so_dt'].str[:10]); s['code'] = s['cust_nm'].map(code); s['q'] = s['so_qty']
o = pd.concat([o[o.dt < '2026-10-01'][['dt', 'code', 'q']], s[(s.dt >= '2026-10-01') & (s.dt < '2026-11-01')][['dt', 'code', 'q']]])
assert (o.code == '미매핑').sum() == 0
o['ym'] = o.dt.dt.strftime('%Y-%m')
HOL = ['2026-05-01', '2026-05-05', '2026-05-25', '2026-06-03', '2026-07-17', '2026-08-03', '2026-08-04', '2026-08-17', '2026-09-24', '2026-09-25', '2026-10-05', '2026-10-09']
def bdays(ym):
    p = pd.Period(ym, 'M'); return len([x for x in pd.bdate_range(p.start_time, p.end_time) if x.strftime('%Y-%m-%d') not in HOL])
O = []
for ym in ['2026-06', '2026-07', '2026-08', '2026-09', '2026-10']:
    x = o[o.ym == ym]; oth = x[~x.code.isin(BIG3)]; bd = bdays(ym)
    g = lambda c: int(x.loc[x.code == c, 'q'].sum())
    O.append({'ym': ym, '영업일': bd, '합계': int(x.q.sum()), '건수': len(x), '고객수': int(x.code.nunique()),
              'C': g('거래처 C'), 'O': g('거래처 O'), 'W': g('거래처 W'), '기타': int(oth.q.sum()),
              '기타_대량': int(oth.q[oth.q >= 100].sum()), '기타_대량건': int((oth.q >= 100).sum()), '기타_소량': int(oth.q[oth.q < 100].sum()),
              '기타_일평균': round(oth.q.sum() / bd, 1), '대량건': int((x.q >= 100).sum()), '대량수량': int(x.q[x.q >= 100].sum())})
S['수주'] = O
S['O_last'] = str(o[o.code == '거래처 O'].dt.max().date())
S['W_11월'] = int(s[(s.code == '거래처 W') & (s.dt >= '2026-11-01')].q.sum())

# 3) 품목 지름 구간 (출하 품목 정리.xlsx, 1~7월)
p = pd.read_excel(J('raw', '출하현황', '출하 품목 정리.xlsx'), sheet_name='출하현황')
p['dt'] = pd.to_datetime(p['출하일자'], errors='coerce'); p = p[p.dt.notna() & (p.dt.dt.month <= 7) & p.dt.dt.year.isin([2025, 2026])]
def dia(t):
    m = re.search(r'/(\d+(?:\.\d+)?)\s*mm', str(t), re.I); return float(m.group(1)) if m else None
def band(x):
    if x is None or pd.isna(x): return '미분류'
    return '6 mm 이하' if x <= 6 else ('6 초과 12 mm 이하' if x <= 12 else ('12 초과 20 mm 이하' if x <= 20 else '20 mm 초과'))
p['band'] = p['품목명'].map(dia).map(band)
t = p.pivot_table(index='band', columns=p.dt.dt.year, values='출고', aggfunc='sum').fillna(0)
S['지름'] = {k: [int(t.loc[k, 2025]), int(t.loc[k, 2026])] for k in t.index}
json.dump(S, open(os.path.join(os.path.dirname(__file__), 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(S['기간'], ensure_ascii=False)); print(pd.DataFrame(O).to_string()); print(S['지름'], S['O_last'], S['W_11월'], S['C2025'], S['2025연간'])
