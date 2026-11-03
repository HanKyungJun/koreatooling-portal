import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import math
plt.rcParams['font.family']='Noto Sans CJK KR'
plt.rcParams['axes.unicode_minus']=False
plt.rcParams['font.size']=11
C1='#1f4e79'; C2='#c55a11'; G='#6b6b6b'; BAND='#dfe9d8'

# Fig 1 — test1 input vs measured
fig,ax=plt.subplots(figsize=(7.2,4.0),dpi=200)
x=[1,2,3,4]; inp=[3.05,2.93,2.860,2.790]
ax.axhspan(2.807,2.881,color=BAND,zorder=0,label='허용 범위 2.807 ~ 2.881 mm')
ax.axhline(2.837,color='#2e7d32',ls='--',lw=1,label='목표 2.837 mm (0.96 × 2.955)')
ax.plot(x,inp,'o--',color=G,lw=1.3,label='입력값 (Final diameter)')
head=[(3.000,3.000),(2.985,2.987),(2.920,2.922),(2.853,2.854)]
tap=[None,(2.988,2.992),(2.928,2.935),(2.858,2.862)]
for i,(a,b) in enumerate(head):
    xi=x[i]-0.06
    ax.vlines(xi,a,b,color=C1,lw=4)
    ax.plot(xi,(a+b)/2,'s',color=C1,ms=5,mfc='white' if i==0 else C1)
for i,t in enumerate(tap):
    if t is None: continue
    xi=x[i]+0.06; ax.vlines(xi,t[0],t[1],color=C2,lw=4); ax.plot(xi,sum(t)/2,'D',color=C2,ms=5)
ax.plot([],[],'s',color=C1,label='측정값 머리 쪽 (범위)'); ax.plot([],[],'D',color=C2,label='측정값 테이퍼 쪽 (범위)')
ax.annotate('1회: 비접촉\n(가공 전 2.990 ~ 3.003)',xy=(0.94,3.0),xytext=(1.08,2.888),fontsize=9,color=G,arrowprops=dict(arrowstyle='-',color=G,lw=0.8))
ax.set_xticks(x); ax.set_xticklabels(['1회','2회','3회','4회'])
ax.set_ylabel('지름 (mm)'); ax.set_ylim(2.76,3.07); ax.set_xlim(0.75,4.5); ax.grid(axis='y',alpha=0.3)
ax.legend(fontsize=8.5,loc='upper right',frameon=False)
for i,(a,b) in enumerate(head[1:],1): ax.text(x[i]-0.1,(a+b)/2,f'{a:.3f}' if a==b else f'{a:.3f}~{b:.3f}',ha='right',va='center',fontsize=7.5,color=C1)
for i,t2 in enumerate(tap):
    if t2: ax.text(x[i]+0.1,sum(t2)/2,f'{t2[0]:.3f}~{t2[1]:.3f}',ha='left',va='center',fontsize=7.5,color=C2)
fig.tight_layout(); fig.savefig('fig1.png'); plt.close()

# Fig 2 — position-wise
fig,axs=plt.subplots(1,2,figsize=(7.2,3.6),dpi=200,sharey=True)
pos=['머리 쪽','중간','테이퍼 쪽']
ax=axs[0]; ax.axhspan(2.807,2.881,color=BAND,zorder=0); ax.axhline(2.837,color='#2e7d32',ls='--',lw=1)
r=[(2.853,2.854),(2.854,2.855),(2.858,2.862)]
for i,(a,b) in enumerate(r):
    ax.vlines(i,a,b,color=C1,lw=5); ax.plot(i,(a+b)/2,'o',color=C1,ms=4)
    ax.text(i,b+0.004,f'{a:.3f}~{b:.3f}' if a!=b else f'{a:.3f}',ha='center',fontsize=8.5)
ax.set_title('(가) 테스트 1, 4회 (D 2.955 mm)',fontsize=10)
ax.text(2.35,2.809,'허용 2.807 ~ 2.881',ha='right',fontsize=8,color='#2e7d32')
ax=axs[1]; ax.axhspan(2.822,2.896,color=BAND,zorder=0); ax.axhline(2.851,color='#2e7d32',ls='--',lw=1)
v=[2.890,2.905,2.907]
ax.plot(range(3),v,'o-',color=C2,lw=1.5)
for i,y in enumerate(v): ax.text(i,y+0.004,f'{y:.3f}',ha='center',fontsize=8.5)
ax.set_title('(나) 테스트 2, 1회 (D 2.970 mm)',fontsize=10)
ax.text(2.35,2.824,'허용 2.822 ~ 2.896',ha='right',fontsize=8,color='#2e7d32')
for ax in axs:
    ax.set_xticks(range(3)); ax.set_xticklabels(pos); ax.set_xlim(-0.4,2.4); ax.grid(axis='y',alpha=0.3)
axs[0].set_ylabel('넥 지름 dn (mm)'); axs[0].set_ylim(2.80,2.925)
fig.tight_layout(); fig.savefig('fig2.png'); plt.close()

# Fig 3 — concept: wheel shape vs neck end (test1)
fig,ax=plt.subplots(figsize=(7.2,3.3),dpi=200)
t=math.tan(math.radians(12))
rD=2.955/2; rn=2.853/2; XS=4.25; XE=19.44; L2=XE-7.0
# tool upper profile
ax.plot([0,XS],[rD,rD],color='k',lw=1.6)
ax.plot([XS,XS],[rD,rn],color='k',lw=1.6)
ax.plot([XS,L2],[rn,rn],color='k',lw=1.6)
ax.plot([L2,XE],[rn,rn+7.0*t],color='k',lw=1.6)
ax.plot([XE,22.5],[rn+7.0*t,rn+7.0*t],color='k',lw=1.0,ls=':')
ax.plot([0,22.5],[0,0],color=G,lw=0.8,ls='-.')
ax.text(22.6,0,'중심선',va='center',fontsize=8,color=G)
# wheel at final position
wx=[L2-2.8,L2,XE,XE,L2-2.8]; wy=[rn,rn,rn+7.0*t,4.6,4.6]
ax.fill(wx,wy,color='#bcd3ea',ec=C1,lw=1.2)
ax.text((L2-2.8+XE)/2,4.0,'휠 (정삭 이송 끝 위치)',ha='center',fontsize=9,color=C1)
# dims
def dim(x1,x2,y,txt):
    ax.annotate('',xy=(x1,y),xytext=(x2,y),arrowprops=dict(arrowstyle='<->',lw=0.8))
    ax.text((x1+x2)/2,y+0.12,txt,ha='center',fontsize=8.5)
dim(L2-2.8,L2,5.0,'원통부 약 2.8')
dim(L2,XE,5.0,'12° 면 약 7.0')
for xv,lab in [(0,'0 (공구 끝)'),(XS,'넥 시작\n약 4.2 ~ 4.3'),(L2,'L2\n약 12.5'),(XE,'X End\n19.44 (입력)')]:
    ax.plot([xv,xv],[-0.15,-0.55],color='k',lw=0.8)
    ax.text(xv,-0.65,lab,ha='center',va='top',fontsize=8.5)
ax.text(2.1,rD+0.15,'머리 Ø D',ha='center',fontsize=8.5)
ax.text((XS+L2)/2,rn-0.35,'넥 dn',ha='center',fontsize=8.5)
ax.text((L2+XE)/2+1.2,rn+3.5*t-0.45,'12° 테이퍼',ha='center',fontsize=8.5)
ax.set_xlim(-0.8,24); ax.set_ylim(-1.9,5.6); ax.axis('off')
fig.tight_layout(); fig.savefig('fig3.png'); plt.close()
print('ok')
