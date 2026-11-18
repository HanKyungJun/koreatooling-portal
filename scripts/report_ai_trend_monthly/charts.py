"""월간 보고 누적 그래프 — python3 charts.py items_master.csv YYYY-MM 출력폴더
최근 12개월(보고 월 포함) 발표만 센다. 색: dataviz 순서형 파랑 4단(검증 통과), 단일 계열 #2a78d6"""
import csv, sys, os, collections, glob, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
master, month, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
cands = glob.glob('/usr/share/fonts/**/NotoSansCJK-Regular.ttc', recursive=True) + glob.glob('/usr/share/fonts/**/*Nanum*Gothic*.ttf', recursive=True) + glob.glob('/usr/share/fonts/**/malgun*.ttf', recursive=True)
if cands:
    fm.fontManager.addfont(cands[0]); plt.rcParams['font.family'] = fm.FontProperties(fname=cands[0]).get_name()
plt.rcParams['axes.unicode_minus'] = False
INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e4e3df', 'white'
ym = lambda s: int(s[:4]) * 12 + int(s[5:7]) - 1
end = ym(month)
rows = [r for r in csv.DictReader(open(master, encoding='utf-8-sig')) if len(r['발표월']) == 7 and end - 12 < ym(r['발표월']) <= end]
def base(ax):
    for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(GRID); ax.tick_params(colors=INK2, length=0)
cats = [('A', 'A 감시 · 보정'), ('B', 'B 프로그래밍(CAM · 자동 프로그램)'), ('C', 'C 상담 에이전트'), ('D', 'D 자율 장비 · 셀')]
stat = [('판매 중', '#0d366b'), ('개발', '#1c5cab'), ('시연', '#3987e5'), ('컨셉', '#86b6ef')]
cnt = collections.Counter((r['분류'], r['상태']) for r in rows)
mx = max([sum(cnt[(c, s)] for s, _ in stat) for c, _ in cats] + [1])
fig, ax = plt.subplots(figsize=(6.3, 2.6), dpi=300)
for i, (c, lab) in enumerate(cats[::-1]):
    left = 0
    for s, col in stat:
        n = cnt[(c, s)]
        if n:
            ax.barh(i, n, left=left, color=col, height=0.62, edgecolor=SURF, linewidth=1.2)
            ax.text(left + n / 2, i, str(n), ha='center', va='center', fontsize=8, color='white' if s != '컨셉' else INK)
            left += n
    ax.text(left + mx * 0.02, i, f'계 {left}', va='center', fontsize=8, color=INK2)
ax.set_yticks(range(4)); ax.set_yticklabels([l for _, l in cats[::-1]], fontsize=8.5, color=INK)
ax.set_xlim(0, mx * 1.18); ax.xaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True); base(ax); ax.tick_params(axis='x', labelsize=7.5)
h = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c in stat]
ax.legend(h, [s for s, _ in stat], ncol=4, loc='lower left', bbox_to_anchor=(0, 1.0), frameon=False, fontsize=8, handlelength=1, columnspacing=1.2)
ax.set_xlabel(f'건수(최근 12개월 {len(rows)}건)', fontsize=7.5, color=INK2)
fig.tight_layout(); fig.savefig(os.path.join(out, 'fig1_class_status.png'), facecolor=SURF); plt.close()
months = []
for k in range(end - 11, end + 1): months.append(f'{k // 12}-{k % 12 + 1:02d}')
mc = collections.Counter(r['발표월'] for r in rows); vals = [mc[m] for m in months]
fig, ax = plt.subplots(figsize=(6.3, 2.4), dpi=300)
ax.bar(range(12), vals, color='#2a78d6', width=0.6, edgecolor=SURF, linewidth=1.2)
for i, v in enumerate(vals):
    if v: ax.text(i, v + max(vals + [1]) * 0.03, str(v), ha='center', va='bottom', fontsize=8, color=INK)
ax.set_xticks(range(12)); ax.set_xticklabels([m[2:4] + '.' + m[5:] for m in months], fontsize=7, color=INK)
ax.set_ylim(0, max(vals + [1]) * 1.25); ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True); base(ax); ax.tick_params(axis='y', labelsize=7.5)
ax.set_ylabel('건수', fontsize=7.5, color=INK2); ax.set_xlabel('발표 연 · 월', fontsize=7.5, color=INK2)
fig.tight_layout(); fig.savefig(os.path.join(out, 'fig3_month.png'), facecolor=SURF); plt.close()
print('charts ok', len(rows))
