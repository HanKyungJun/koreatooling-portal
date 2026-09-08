# -*- coding: utf-8 -*-
"""3차: 대외비 키워드 플래그 파일에 '실제 금액값'이 있는지 판정.
키워드 존재 != 노출. 금액 형태 수치가 함께 있어야 노출로 본다."""
import os, re, sys, zipfile

REPO = os.environ.get('CNC_WIKI_ROOT') or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
# 사용법: python3 confidential_triage.py "wiki/reports/x.docx" ...
#   경로는 저장소 루트 기준 상대경로로 전달한다.
#   판정: 🔴 키워드+금액값 동반 / 🟡 금액형 수치만(수량 오탐 가능) / 🟢 키워드만
TARGETS = sys.argv[1:]
KW = re.compile(r'단가|금액|견적|정가|매출|원가|청구|입금')
# 금액 형태: 1,234,567 / 3,500원 / 1.2억 / 350만원 / 백만원 단위 표기
MONEY = re.compile(r'\d{1,3}(?:,\d{3}){1,}\s*(?:원|만원|천원)?|\d+\s*(?:억|천만|백만|만)\s*원|\d{4,}\s*원')

def text_of(path):
    out = []
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            if not re.search(r'\.xml$', info.filename, re.I):
                continue
            if info.file_size > 12 * 1024 * 1024:
                continue
            try:
                x = z.read(info).decode('utf-8', 'replace')
            except Exception:
                continue
            x = re.sub(r'<[^>]+>', ' ', x)
            out.append(x)
    return re.sub(r'\s+', ' ', ' '.join(out))

for rel in TARGETS:
    full = os.path.join(REPO, rel)
    if not os.path.exists(full):
        print('?? 없음:', rel); continue
    t = text_of(full)
    money = MONEY.findall(t)
    ctx = []
    for m in KW.finditer(t):
        seg = t[max(0, m.start() - 60):m.start() + 70]
        if MONEY.search(seg):
            ctx.append(seg.strip())
    verdict = '🔴 금액값 동반' if ctx else ('🟡 금액형 수치만 존재' if money else '🟢 키워드만 (금액값 없음)')
    print('=' * 78)
    print('%s  %s' % (verdict, rel))
    print('  금액형 수치 %d개 / 키워드+금액 동반 문맥 %d건' % (len(money), len(ctx)))
    for c in ctx[:4]:
        print('   ▸ %s' % c[:190])
