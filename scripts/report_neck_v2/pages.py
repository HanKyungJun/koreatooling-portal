import subprocess,json,re,sys
pdf=sys.argv[1]
n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
pg={}; heads={}
for i in range(3,n+1):
    t=subprocess.run(['pdftotext','-f',str(i),'-l',str(i),'-layout',pdf,'-'],capture_output=True,text=True).stdout
    for m in re.finditer(r'^\s*(표 \d+|그림 \d+)\.',t,re.M):
        pg.setdefault(m.group(1),i)
    for h in ['1. 서론','2. 시험 방법','3. 시험 결과','가. 테스트 1','나. 테스트 2','다. 넥 형상','4. 고찰','5. 결론','참고 문헌','부록']:
        if re.search(r'^\s*'+re.escape(h),t,re.M): heads.setdefault(h,i)
print(n,heads); pg.update(heads); json.dump(pg,open('pg.json','w'),ensure_ascii=False); print(pg)
