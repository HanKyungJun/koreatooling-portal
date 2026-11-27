# 2026년 1~10월 재연마 수주 · 출하 · 생산 집계 (2026-11-27) — ../report_order_decline/data.json + 출하 납품처별 표 + KPI 생산값
import json, os, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.abspath(os.path.join(H, '..', '..'))
D = json.load(open(os.path.join(H, '..', 'report_order_decline', 'data.json'), encoding='utf-8'))
# 생산: wiki/comparisons/출하현황-KPI-트렌드-2022-2026.md §5-1 (1~9월 엑셀 작업일지, 10월 ERP 작업실적)
PROD = {'2025': [1202, 876, 1091, 1471, 933, 947, 1411, 1131, 1134, 1096], '2026': [1280, 1048, 1501, 1632, 1333, 1501, 1533, 1105, 1053, 1326]}
def ship(y):
    d = pd.read_excel(os.path.join(BASE, 'wiki', 'comparisons', f'출하현황_납품처별_월별분석_{y}.xlsx'), sheet_name='요약', header=1)
    d = d[d['납품처명'].astype(str).str.startswith('거래처')]
    return d.set_index('납품처명')[[f'{i}월' for i in range(1, 11)]].fillna(0).astype(float).sum(1)
a, b = ship(2025), ship(2026); idx = a.index.union(b.index); a = a.reindex(idx, fill_value=0); b = b.reindex(idx, fill_value=0)
top = b.sort_values(ascending=False).head(10)
out = {'PROD': PROD, 'TOP': [[k, int(a[k]), int(b[k])] for k in top.index], 'top10share': [round(top.sum() / b.sum() * 100, 1)],
       'cust': [int((a > 0).sum()), int((b > 0).sum())]}
json.dump(out, open(os.path.join(H, 'data2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(out, sum(PROD['2025']), sum(PROD['2026']))
