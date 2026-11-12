# 차트 상한 계열(3·4번째)을 점선 · 표식 없음으로 후처리
import zipfile,sys,re,shutil
src=sys.argv[1]; tmp=src+'.tmp'
zin=zipfile.ZipFile(src); zout=zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    data=zin.read(it.filename)
    if re.match(r'ppt/charts/chart\d+\.xml',it.filename):
        x=data.decode('utf-8')
        sers=re.split(r'(?=<c:ser>)',x)
        out=[sers[0]]
        for i,s in enumerate(sers[1:]):
            idx=re.search(r'<c:idx val="(\d+)"/>',s).group(1)
            if idx in ('2','3'):
                s=re.sub(r'(<a:ln[^>]*>)(.*?)(</a:ln>)',lambda m:m.group(1)+re.sub(r'<a:prstDash[^>]*/>','',m.group(2))+'<a:prstDash val="dash"/>'+m.group(3),s,count=1,flags=re.S)
                s=re.sub(r'<c:marker>.*?</c:marker>','<c:marker><c:symbol val="none"/></c:marker>',s,count=1,flags=re.S)
            out.append(s)
        data=''.join(out).encode('utf-8')
    zout.writestr(it,data)
zout.close(); shutil.move(tmp,src); print('dash ok')
