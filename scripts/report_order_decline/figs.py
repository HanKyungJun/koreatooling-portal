# 그림 2장 — data.json 에서 그림. 실행: python figs.py
import json, os, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
H = os.path.dirname(os.path.abspath(__file__))
fp = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
fm.fontManager.addfont(fp); plt.rcParams['font.family'] = fm.FontProperties(fname=fp).get_name(); plt.rcParams['axes.unicode_minus'] = False
D = json.load(open(os.path.join(H, 'data.json'), encoding='utf-8'))
INK, INK2, GRID, DARK, MID, LIGHT = '#231F20', '#58595B', '#E4E3DF', '#3B3561', '#8C86B4', '#D3CFE6'
def base(ax):
    for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(GRID); ax.tick_params(colors=INK2, length=0, labelsize=8)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)

# 그림 1. 월별 출하 2025 vs 2026 (1~10월), 대형 3곳과 나머지로 나눔
m = list(range(10)); w = 0.38
fig, ax = plt.subplots(figsize=(6.4, 2.9), dpi=300)
for k, (y, x0) in enumerate((('2025', -w / 2), ('2026', w / 2))):
    tot = D[y]['전체'][:10]; big = D[y]['대형3'][:10]; rest = [t - g for t, g in zip(tot, big)]
    ax.bar([i + x0 for i in m], rest, w, color=MID if y == '2026' else LIGHT, edgecolor='white', linewidth=0.6, label=f'{y}년 나머지 거래처')
    ax.bar([i + x0 for i in m], big, w, bottom=rest, color=DARK if y == '2026' else INK2, edgecolor='white', linewidth=0.6, label=f'{y}년 거래처 C, O, W')
ax.set_xticks(m); ax.set_xticklabels([f'{i + 1}월' for i in m]); ax.set_ylabel('출하 (개)', fontsize=8, color=INK2)
base(ax); ax.legend(fontsize=7, frameon=False, ncol=2, loc='upper left', bbox_to_anchor=(0, 1.2))
fig.tight_layout(); fig.savefig(os.path.join(H, 'fig', 'fig1.png')); plt.close(fig)

# 그림 2. 2026년 6~10월 수주, 거래처 C · W · 나머지
O = D['수주']; lab = [f"{int(r['ym'][5:])}월\n영업일 {r['영업일']}일" for r in O]
fig, ax = plt.subplots(figsize=(6.4, 2.8), dpi=300)
rest = [r['기타'] for r in O]; wv = [r['W'] for r in O]; cv = [r['C'] for r in O]
ax.bar(range(5), rest, 0.55, color=MID, edgecolor='white', label='나머지 거래처')
ax.bar(range(5), wv, 0.55, bottom=rest, color=LIGHT, edgecolor='white', label='거래처 W')
ax.bar(range(5), cv, 0.55, bottom=[a + b for a, b in zip(rest, wv)], color=DARK, edgecolor='white', label='거래처 C')
for i, r in enumerate(O):
    ax.text(i, r['합계'] + 40, f"{r['합계']:,}", ha='center', fontsize=7.5, color=INK)
ax.set_xticks(range(5)); ax.set_xticklabels(lab); ax.set_ylabel('수주 (개)', fontsize=8, color=INK2); ax.set_ylim(0, 2600)
base(ax); ax.legend(fontsize=7, frameon=False, ncol=3, loc='upper right')
fig.tight_layout(); fig.savefig(os.path.join(H, 'fig', 'fig2.png')); plt.close(fig)
print('ok')
