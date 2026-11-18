import csv, collections, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fp='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
fm.fontManager.addfont(fp)
plt.rcParams['font.family']=fm.FontProperties(fname=fp).get_name()
plt.rcParams['axes.unicode_minus']=False
INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'; SURF='white'
r=[x for x in csv.DictReader(open('/home/claude/trend/items.csv')) if x['기간']=='안']
def base(ax):
    for s in ['top','right','left']: ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(GRID); ax.tick_params(colors=INK2, length=0)
# Fig1 분류 x 상태
cats=[('A','A 감시 · 보정'),('B','B 프로그래밍(CAM · 자동 프로그램)'),('C','C 상담 에이전트'),('D','D 자율 장비 · 셀')]
stat=[('판매 중','#0d366b'),('개발','#1c5cab'),('시연','#3987e5'),('컨셉','#86b6ef')]
cnt=collections.Counter((x['분류'],x['상태']) for x in r)
fig,ax=plt.subplots(figsize=(6.3,2.6),dpi=300)
for i,(c,lab) in enumerate(cats[::-1]):
    left=0
    for s,col in stat:
        n=cnt[(c,s)]
        if n:
            ax.barh(i,n,left=left,color=col,height=0.62,edgecolor=SURF,linewidth=1.2)
            ax.text(left+n/2,i,str(n),ha='center',va='center',fontsize=8,color='white' if s!='컨셉' else INK)
            left+=n
    ax.text(left+0.3,i,f'계 {left}',va='center',fontsize=8,color=INK2)
ax.set_yticks(range(4)); ax.set_yticklabels([l for _,l in cats[::-1]],fontsize=8.5,color=INK)
ax.set_xlim(0,16.5); ax.set_xticks([0,5,10,15]); ax.tick_params(axis='x',labelsize=7.5)
ax.xaxis.grid(True,color=GRID,linewidth=0.6); ax.set_axisbelow(True); base(ax)
h=[plt.Rectangle((0,0),1,1,color=c) for _,c in stat]
ax.legend(h,[s for s,_ in stat],ncol=4,loc='lower left',bbox_to_anchor=(0,1.0),frameon=False,fontsize=8,handlelength=1,columnspacing=1.2)
ax.set_xlabel('건수(37건, 2025-11 ~ 2026-11 발표)',fontsize=7.5,color=INK2)
fig.tight_layout(); fig.savefig('/home/claude/trend/fig/fig1_class_status.png',facecolor=SURF); plt.close()
# Fig2 지역
regs=['일본','유럽','한국','대만','미국','중국']
rc=collections.Counter(x['지역'] for x in r)
fig,ax=plt.subplots(figsize=(6.3,2.3),dpi=300)
vals=[rc[g] for g in regs]
ax.bar(range(6),vals,color='#2a78d6',width=0.55,edgecolor=SURF,linewidth=1.2)
for i,v in enumerate(vals):
    ax.text(i,v+0.3,str(v) if v else '0',ha='center',va='bottom',fontsize=8,color=INK if v else INK2)
ax.set_xticks(range(6)); ax.set_xticklabels(regs,fontsize=8.5,color=INK)
ax.set_ylim(0,15.5); ax.set_yticks([0,5,10,15]); ax.tick_params(axis='y',labelsize=7.5)
ax.yaxis.grid(True,color=GRID,linewidth=0.6); ax.set_axisbelow(True); base(ax)
ax.set_ylabel('건수',fontsize=7.5,color=INK2)
fig.tight_layout(); fig.savefig('/home/claude/trend/fig/fig2_region.png',facecolor=SURF); plt.close()
# Fig3 발표월
months=['2025-11','2025-12']+[f'2026-{m:02d}' for m in range(1,12)]
mc=collections.Counter(x['발표월'] for x in r)
ev={'2026-03':'TMTS','2026-04':'SIMTOS\n하노버','2026-05':'GrindingHub','2026-09':'IMTS · AMB','2026-10':'JIMTOF','2026-11':'로보월드'}
fig,ax=plt.subplots(figsize=(6.3,2.5),dpi=300)
vals=[mc[m] for m in months]
ax.bar(range(len(months)),vals,color='#2a78d6',width=0.6,edgecolor=SURF,linewidth=1.2)
for i,(m,v) in enumerate(zip(months,vals)):
    if v: ax.text(i,v+0.25,str(v),ha='center',va='bottom',fontsize=8,color=INK)
    if m in ev: ax.text(i,v+1.3,ev[m],ha='center',va='bottom',fontsize=6.5,color=INK2,linespacing=1.0)
ax.set_xticks(range(len(months))); ax.set_xticklabels([m[2:4]+'.'+m[5:] for m in months],fontsize=7,color=INK)
ax.set_ylim(0,14.5); ax.set_yticks([0,5,10]); ax.tick_params(axis='y',labelsize=7.5)
ax.yaxis.grid(True,color=GRID,linewidth=0.6); ax.set_axisbelow(True); base(ax)
ax.set_ylabel('건수',fontsize=7.5,color=INK2); ax.set_xlabel('발표 연 · 월',fontsize=7.5,color=INK2)
fig.tight_layout(); fig.savefig('/home/claude/trend/fig/fig3_month.png',facecolor=SURF); plt.close()
# Fig4 확인 수 x 구분
fig,ax=plt.subplots(figsize=(6.3,2.0),dpi=300)
k=collections.Counter((x['확인수'],x['구분']) for x in r)
ks=['1','2','3','4']
for j,(g,col) in enumerate([('제조사','#0d366b'),('추정','#86b6ef')]):
    pass
bottom=[0]*4
for g,col,tc in [('제조사','#1c5cab','white'),('추정','#86b6ef',INK)]:
    v=[k[(q,g)] for q in ks]
    ax.bar(range(4),v,bottom=bottom,color=col,width=0.55,edgecolor=SURF,linewidth=1.2,label=g+(' (원문 확인)' if g=='제조사' else ' (기사 경유)'))
    for i,(b,n) in enumerate(zip(bottom,v)):
        if n: ax.text(i,b+n/2,str(n),ha='center',va='center',fontsize=8,color=tc)
    bottom=[a+b for a,b in zip(bottom,v)]
ax.set_xticks(range(4)); ax.set_xticklabels(['1곳','2곳','3곳','4곳'],fontsize=8.5,color=INK)
ax.set_ylim(0,24); ax.set_yticks([0,10,20]); ax.tick_params(axis='y',labelsize=7.5)
ax.yaxis.grid(True,color=GRID,linewidth=0.6); ax.set_axisbelow(True); base(ax)
ax.set_xlabel('확인 수(서로 다른 발행처)',fontsize=7.5,color=INK2); ax.set_ylabel('건수',fontsize=7.5,color=INK2)
ax.legend(frameon=False,fontsize=8,loc='upper right')
fig.tight_layout(); fig.savefig('/home/claude/trend/fig/fig4_confirm.png',facecolor=SURF); plt.close()
print('ok')
