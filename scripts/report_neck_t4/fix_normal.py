"""docx-js 출력에 기본 문단 스타일(Normal, w:default=1)이 없으면 넣는다 — doc_style_check.py 가 스타일을 읽을 수 있게."""
import sys, zipfile, shutil, re
f = sys.argv[1]
z = zipfile.ZipFile(f); files = {n: z.read(n) for n in z.namelist()}; infos = z.infolist(); z.close()
s = files["word/styles.xml"].decode("utf-8")
if not re.search(r'<w:style [^>]*w:type="paragraph"[^>]*w:default="1"', s):
    normal = ('<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
              '<w:rPr><w:rFonts w:ascii="맑은 고딕" w:eastAsia="맑은 고딕" w:hAnsi="맑은 고딕"/><w:sz w:val="30"/></w:rPr></w:style>')
    s = s.replace("</w:latentStyles>", "</w:latentStyles>" + normal, 1) if "</w:latentStyles>" in s else s.replace("</w:docDefaults>", "</w:docDefaults>" + normal, 1)
    files["word/styles.xml"] = s.encode("utf-8")
    tmp = f + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for i in infos: zo.writestr(i, files[i.filename])
    shutil.move(tmp, f); print("Normal 추가")
else:
    print("Normal 있음")
