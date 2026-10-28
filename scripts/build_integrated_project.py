"""사내 Claude 프로젝트 「사내 공구 문의」(재연마 정가 + 취급 제품) 통합 폴더 만들기.

정가 폴더(export_price_project.py 출력)와 제품 폴더(catalog_export.py 출력)를 받아
지식 파일 8개 + 지시문을 한 폴더로 모은다. 0_자료_안내.md 는 두 안내를 이어 붙인다.
원본 폴더는 건드리지 않는다(복사만).

사용:
  python scripts\\build_integrated_project.py <정가 폴더> <제품 폴더> <출력 폴더>
예:
  python scripts\\build_integrated_project.py outputs\\claude_project_price_20261028_2 outputs\\claude_project_products_20261028 outputs\\claude_project_integrated_20261028
근거: decisions 2026-10-28 (9)
"""
import os, sys, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PRICE_FILES = ('1_정가표_구간표.csv', '2_등록품목_정가.csv', '3_확인필요_품목.csv')
PROD_FILES = ('JJ_1_제품군_요약.csv', 'JJ_2_품번_치수.csv', 'COGO_1_제품군_요약.csv', 'COGO_2_품번_치수.csv')
TEMPLATE = os.path.join(HERE, 'project_templates', '통합_지시문.md')


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if len(sys.argv) != 4:
        print(__doc__); sys.exit(2)
    price, prod, out = sys.argv[1:4]
    if os.path.exists(out) and os.listdir(out):
        print(f'출력 폴더가 이미 있고 비어 있지 않습니다: {out} — 다른 이름을 쓰세요(덮어쓰지 않음)'); sys.exit(1)
    os.makedirs(out, exist_ok=True)
    missing = [os.path.join(price, f) for f in PRICE_FILES + ('0_자료_안내.md',) if not os.path.exists(os.path.join(price, f))]
    missing += [os.path.join(prod, f) for f in PROD_FILES + ('0_자료_안내.md',) if not os.path.exists(os.path.join(prod, f))]
    if not os.path.exists(TEMPLATE):
        missing.append(TEMPLATE)
    if missing:
        print('없는 파일:', *missing, sep='\n  '); sys.exit(1)
    for f in PRICE_FILES:
        shutil.copy2(os.path.join(price, f), os.path.join(out, f))
    for f in PROD_FILES:
        shutil.copy2(os.path.join(prod, f), os.path.join(out, f))
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    a = open(os.path.join(price, '0_자료_안내.md'), encoding='utf-8-sig').read().strip()
    b = open(os.path.join(prod, '0_자료_안내.md'), encoding='utf-8-sig').read().strip()
    shift = lambda t: '\n'.join(('#' + l) if l.startswith('# ') else l for l in t.splitlines())
    head = (f'# 사내 공구 문의 — 자료 안내\n\n'
            f'- 묶은 시각: {now:%Y-%m-%d %H:%M} KST (scripts/build_integrated_project.py)\n'
            f'- 재연마 정가 파일: {", ".join(PRICE_FILES)} — 아래 「재연마 정가 자료 안내」\n'
            f'- 신품 제품 파일: {", ".join(PROD_FILES)} — 아래 「취급 제품 자료 안내」\n'
            f'- 재연마 정가와 신품 카탈로그는 서로 다른 자료입니다. 신품 가격은 없습니다.\n')
    open(os.path.join(out, '0_자료_안내.md'), 'w', encoding='utf-8').write(head + '\n' + shift(a) + '\n\n' + shift(b) + '\n')
    shutil.copy2(TEMPLATE, os.path.join(out, '지시문_프로젝트에_붙여넣기.md'))
    size = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out))
    print(f'{out}: 지식 파일 8개(0 · 1 · 2 · 3 · JJ 2 · COGO 2) + 지시문 · 합계 {size/1e6:.2f} MB')


if __name__ == '__main__':
    main()
