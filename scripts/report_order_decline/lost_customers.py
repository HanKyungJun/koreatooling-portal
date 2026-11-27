# 거래 끊긴 거래처 목록 (2026-11-27). 실명판 xlsx 는 wiki/_private/reports/ 에만 씀 — 이 파일에는 실명 없음
# 실행: python scripts/report_order_decline/lost_customers.py
import csv, glob, os, re, warnings
import numpy as np, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
warnings.filterwarnings('ignore')
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); J = lambda *p: os.path.join(BASE, *p)
OUT = J('wiki', '_private', 'reports', '거래끊긴_거래처_정리_20261127_실명.xlsx')
MAP = list(csv.DictReader(open(J('wiki', '_private', '거래처_익명코드표.csv'), encoding='utf-8-sig')))
NAME = {r['code']: r['core'] for r in MAP}
def core(n):
    c = re.sub(r'\(주\)|㈜|주식회사|\(유\)|유한회사', '', str(n)); return re.sub(r'\(.*?\)|-.*$', '', c).strip()
M2 = {}
for r in MAP:
    M2[r['core'].strip()] = r['code']
    for v in re.split(r'[|;/]', r['variants'] or ''):
        if v.strip(): M2[v.strip()] = r['code']; M2[core(v)] = r['code']
code = lambda n: M2.get(str(n).strip()) or M2.get(core(n)) or '미매핑'
RENAMED = {'거래처 I': '2024. 11.부터 거래처 Q 상호로 거래 계속', '거래처 L': 'ERP에 거래처 M 상호로 처리하라고 되어 있음, 거래 계속'}
CONFIRMED = {'거래처 C': '거래 종료 확인(2026. 9. 3.)'}
PRIORITY = {'거래처 O': 1, '거래처 AK': 2}
NOTE = {'거래처 O': '2025년에도 4~7월 공백 뒤 8월 재개한 적 있음. 이번 공백 6개월', '거래처 AK': '2022년부터 34개월 거의 매달 거래한 단골',
        '거래처 E': '2022~2023년 출하 상위 2곳 안', '거래처 Z': '2022년 546개, 2026. 4. 30개 일시 거래', '거래처 AA': '26개월 거래, 2023년 617개'}

# 출하 2022~2026 납품처별 월별
fr = []
for y in range(2022, 2027):
    d = pd.read_excel(J('wiki', 'comparisons', f'출하현황_납품처별_월별분석_{y}.xlsx'), sheet_name='요약', header=1)
    d = d[d['납품처명'].astype(str).str.startswith('거래처')].set_index('납품처명')[[f'{i}월' for i in range(1, 13)]].fillna(0).astype(float)
    d = d.groupby(level=0).sum(); d.columns = [f'{y}-{i:02d}' for i in range(1, 13)]; fr.append(d)
S = pd.concat(fr, axis=1).fillna(0); S = S[[c for c in S.columns if c <= '2026-10']]
# 수주 2026. 5. ~ 11. 10.
o = []
for f in glob.glob(J('raw', '수주현황', '재연마 수주현황_*.xlsx')) + [J('raw', '출하현황', '재연마 수주현황_20260611132814.xlsx')]:
    d = pd.read_excel(f); d = d[d['수주번호'].notna()]; o.append(pd.DataFrame({'code': d['납품처명'].map(code), 'dt': pd.to_datetime(d['수주일자'], errors='coerce')}))
s = pd.read_csv(J('erp', 'snapshot', 'jae_head_latest.csv')); o.append(pd.DataFrame({'code': s['cust_nm'].map(code), 'dt': pd.to_datetime(s['so_dt'].str[:10])}))
LO = pd.concat(o).dropna().groupby('code')['dt'].max()

rows = []
for c, r in S.iterrows():
    act = r[r > 0]
    if act.empty: continue
    lo = LO.get(c); los = lo.strftime('%Y-%m-%d') if lo is not None and not pd.isna(lo) else ''
    if r[['2026-09', '2026-10']].sum() > 0 or los >= '2026-08-01': continue  # 최근 거래 있음
    yr = {y: int(r[[k for k in r.index if k.startswith(y)]].sum()) for y in ['2022', '2023', '2024', '2025', '2026']}
    last_act = max(act.index.max(), los[:7] if los else '')
    tot = sum(yr.values()); months = len(act)
    if c in RENAMED: grp = '상호 변경'
    elif c in CONFIRMED or c in PRIORITY: grp = '2026년 끊김'
    elif last_act >= '2026-06': grp = '지켜볼 곳'
    elif last_act >= '2026-01': grp = '2026년 끊김'
    elif last_act >= '2025-01': grp = '2025년 끊김'
    else: grp = '2024년 이전 끊김'
    small = tot < 100 and months < 4
    rows.append(dict(분류=grp, 우선=PRIORITY.get(c, ''), 업체=NAME.get(c, c), 코드=c, 첫출하=act.index.min(), 마지막출하=act.index.max(), 마지막수주=los,
                     **{f'{y}년': v for y, v in yr.items()}, 합계=tot, 거래개월=months, 소량=('소량·일회성' if small else ''),
                     비고=re.sub(r'거래처 ([A-Z]{1,2})', lambda m: NAME.get(m.group(0), m.group(0)), CONFIRMED.get(c) or RENAMED.get(c) or NOTE.get(c, ''))))
T = pd.DataFrame(rows)
order = {'2026년 끊김': 0, '지켜볼 곳': 1, '2025년 끊김': 2, '2024년 이전 끊김': 3, '상호 변경': 4}
T['_o'] = T['분류'].map(order); T['_s'] = T['소량'] != ''
T = T.sort_values(['_o', '_s', '합계'], ascending=[True, True, False]).drop(columns=['_o', '_s'])

wb = Workbook(); thin = Side(style='thin', color='C9C7C7'); B = Border(left=thin, right=thin, top=thin, bottom=thin)
HF = PatternFill('solid', fgColor='E4E0F0'); F = Font(name='맑은 고딕', size=10); FB = Font(name='맑은 고딕', size=10, bold=True)
def sheet(ws, df, widths):
    ws.append(list(df.columns))
    for c in ws[1]: c.font = FB; c.fill = HF; c.border = B; c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    for row in df.itertuples(index=False):
        ws.append(list(row))
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = F; c.border = B
            if isinstance(c.value, (int, float)) and not isinstance(c.value, bool): c.number_format = '#,##0'; c.alignment = Alignment(horizontal='right')
    for i, w in enumerate(widths): ws.column_dimensions[chr(65 + i)].width = w
    ws.freeze_panes = 'A2'; ws.auto_filter.ref = ws.dimensions
W1 = [14, 6, 18, 11, 10, 10, 12, 9, 9, 9, 9, 9, 9, 9, 12, 44]
ws = wb.active; ws.title = '주요 업체'
main = T[(T['소량'] == '') & (T['분류'] != '상호 변경')].drop(columns=['소량'])
sheet(ws, main, W1)
sheet(wb.create_sheet('전체 목록'), T, W1 + [44])
sheet(wb.create_sheet('상호 변경'), T[T['분류'] == '상호 변경'].drop(columns=['소량']), W1)
ws = wb.create_sheet('기준과 한계')
for line in ['거래 끊긴 거래처 정리 (2026. 11. 27., 생산팀)', '',
             '기준: 2026. 8. 1. ~ 11. 10. 수주 없음, 2026. 9~10월 출하 없음',
             '분류: 마지막 출하 또는 수주가 있던 해. 2026. 6. 이후 마지막인 곳은 「지켜볼 곳」(공백 3~4개월)',
             f"예외: {NAME['거래처 C']}은 거래 종료 확인, {NAME['거래처 O']}과 {NAME['거래처 AK']}는 거래 주기에 비해 공백이 길어 2026년 끊김으로 둠",
             '소량·일회성: 합계 100개 미만이고 거래 개월 4개월 미만',
             '수량: 출하 수량(개), 연마불가 제외. 단가와 금액은 넣지 않음', '',
             '한계: 2022년 출하는 5월부터. 수주 자료는 2026. 5.부터라 그 전 수주 날짜는 없음',
             '한계: 끊긴 사유는 사내 기록에 없음. 영업 확인 필요',
             '실명판 사내 전용. 원자료: 출하현황 납품처별 월별 집계 2022~2026, 수주현황 내보내기, ERP 저장본 2026. 11. 10.']:
    ws.append([line])
ws.column_dimensions['A'].width = 100
for r in ws.iter_rows():
    for c in r: c.font = FB if c.row == 1 else F
os.makedirs(os.path.dirname(OUT), exist_ok=True); wb.save(OUT)
print('저장', OUT); print(T.groupby('분류').agg(곳=('업체', 'count'), 합계=('합계', 'sum'))); print(main[['분류', '우선', '업체', '마지막출하', '마지막수주', '2025년', '2026년']].to_string(index=False))
