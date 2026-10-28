# -*- coding: utf-8 -*-
r"""카탈로그 PDF → 쪽별 글자 위치(JSON)    2026-10-28 Cowork 신설 (취급 제품 Claude 프로젝트용)
사용: python scripts\catalog\catalog_dump.py raw\Catalog\JJ.pdf outputs\_cat_jj 0 600
이미 만든 쪽은 건너뛴다(중간에 멈춰도 다시 실행하면 이어서). 쪽당 약 1 초. pdfplumber 필요.
"""
import pdfplumber, json, sys, os, time
pdf_path, outdir, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
os.makedirs(outdir, exist_ok=True)
t=time.time()
with pdfplumber.open(pdf_path) as pdf:
    n=len(pdf.pages)
    for i in range(a, min(b, n)):
        fp=os.path.join(outdir, f'{i:04d}.json')
        if os.path.exists(fp): continue
        pg=pdf.pages[i]
        ws=[(w['text'], round(w['x0'],1), round(w['x1'],1), round(w['top'],1), round(w['bottom'],1)) for w in pg.extract_words()]
        json.dump({'w':ws,'W':pg.width,'H':pg.height}, open(fp,'w',encoding='utf-8'), ensure_ascii=False)
print('done', a, b, time.time()-t)
