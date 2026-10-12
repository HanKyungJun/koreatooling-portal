import re,sys
APPLY='--apply' in sys.argv
P='tasks.md'; A='tasks-archive.md'
s=open(P,encoding='utf-8-sig').read()
lines=s.split('\n')
# locate items
items=[]; i=0
while i<len(lines):
    l=lines[i]
    if re.match(r'^- \[[ x]\] ',l):
        j=i+1
        while j<len(lines) and not re.match(r'^- \[[ x]\] ',lines[j]) and not lines[j].startswith('## ') and not (lines[j].strip()=='' and j+1<len(lines) and (re.match(r'^- \[[ x]\] ',lines[j+1]) or lines[j+1].startswith('## '))):
            j+=1
        items.append((i,j)); i=j
    else: i+=1
def size(a,b): return sum(len(x.encode())+1 for x in lines[a:b])
targets=[(a,b) for a,b in items if size(a,b)>=5*1024]
def active(l):
    t=l.strip()
    if t.startswith('- 담당') or t.startswith('- 관련'): return True
    if re.search(r'⏸|🅿️',t) and not t.startswith('- ~~'): return True
    # unstruck ⬜: remove ~~...~~ spans then look for ⬜
    u=re.sub(r'~~.*?~~','',t)
    return '⬜' in u
out=[]; arc=[]; last=0; report=[]
def title(h):
    t=re.sub(r'^- \[[ x]\] ','',h); t=re.sub(r'\*\*','',t)
    return re.split(r' \(P\d',t)[0].strip()[:80]
for a,b in targets:
    body=lines[a+1:b]
    keep=[l for l in body if active(l)]
    t=title(lines[a])
    link=f"  - 📦 **상세 이력 {len(body)}줄 · {size(a,b)/1024:.1f} KB → [[tasks-archive]] 「{t} — 이력 (2026-10-12 이관)」** — 아래는 열린 ⬜·보류·담당·관련 줄만 남긴 것(원문 그대로)"
    out+=lines[last:a]+[lines[a],link]+keep
    arc+=['',f'### {t} — 이력 (2026-10-12 이관)','',f'> `tasks.md` 에서 옮긴 원문 그대로({len(body)+1}줄). 활성 항목은 tasks.md 에 요약으로 남아 있다.','']+lines[a:b]
    last=b
    report.append((size(a,b)/1024, sum(len(x.encode())+1 for x in [lines[a],link]+keep)/1024, len(keep), t))
out+=lines[last:]
new='\n'.join(out)
for r in report: print('%5.1f → %4.1f KB  keep %2d  %s'%r)
print('tasks.md %.1f → %.1f KB'%(len(s.encode())/1024,len(new.encode())/1024))
if APPLY:
    a=open(A,encoding='utf-8-sig').read()
    a=a.rstrip('\n')+'\n\n## 활성 항목 상세 이력 (2026-10-12 이관)\n\n> tasks.md 2단계 압축 — 5 KB 이상 활성 항목의 전체 원문. 지운 것 없음(decisions 2026-10-12 (6)).\n'+'\n'.join(arc)+'\n'
    open(A,'w',encoding='utf-8-sig',newline='').write(a)
    open(P,'w',encoding='utf-8-sig',newline='').write(new)
    print('APPLIED')
