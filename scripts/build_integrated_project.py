"""사내 Claude 프로젝트 「사내 공구 문의」(재연마 정가 + 취급 제품) 통합 폴더 만들기.

정가 폴더(export_price_project.py 출력)와 제품 폴더 1개 이상(catalog_export.py 출력)을 받아
지식 파일 + 지시문을 한 폴더로 모은다. 제품 폴더 안의 `{메이커}_1_제품군_요약.csv` ·
`{메이커}_2_품번_치수.csv` 짝을 메이커마다 찾아 넣는다(메이커 이름이 겹치면 거부).
0_자료_안내.md 는 정가 안내 + 제품 폴더 안내들을 이어 붙인다. 원본 폴더는 건드리지 않는다(복사만).

사용:
  python scripts\\build_integrated_project.py <정가 폴더> <출력 폴더> <제품 폴더> [<제품 폴더> ...]
예:
  python scripts\\build_integrated_project.py outputs\\claude_project_price_20261028_2 outputs\\claude_project_integrated_YYYYMMDD outputs\\claude_project_products_20261028
근거: decisions 2026-10-28 (9) · (10) 제품군 확장
"""
import os, sys, re, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PRICE_FILES = ('1_정가표_구간표.csv', '2_등록품목_정가.csv', '3_확인필요_품목.csv')
TEMPLATE = os.path.join(HERE, 'project_templates', '통합_지시문.md')


def maker_pairs(folder):
    """제품 폴더에서 {메이커}_1_제품군_요약.csv · {메이커}_2_품번_치수.csv 짝을 찾는다."""
    out = []
    for f in sorted(os.listdir(folder)):
        m = re.match(r'^(.+)_1_제품군_요약\.csv$', f)
        if m and os.path.exists(os.path.join(folder, m.group(1) + '_2_품번_치수.csv')):
            out.append(m.group(1))
    return out


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    price, out, prods = sys.argv[1], sys.argv[2], sys.argv[3:]
    if os.path.exists(out) and os.listdir(out):
        print(f'출력 폴더가 이미 있고 비어 있지 않습니다: {out} — 다른 이름을 쓰세요(덮어쓰지 않음)'); sys.exit(1)
    missing = [os.path.join(price, f) for f in PRICE_FILES + ('0_자료_안내.md',) if not os.path.exists(os.path.join(price, f))]
    makers = {}
    for d in prods:
        if not os.path.exists(os.path.join(d, '0_자료_안내.md')):
            missing.append(os.path.join(d, '0_자료_안내.md'))
            continue
        ms = maker_pairs(d)
        if not ms:
            missing.append(d + ' (메이커 _1 · _2 짝 없음)')
        for mk in ms:
            if mk in makers:
                print(f'메이커 {mk} 가 두 폴더에 있습니다: {makers[mk]} · {d}'); sys.exit(1)
            makers[mk] = d
    if not os.path.exists(TEMPLATE):
        missing.append(TEMPLATE)
    if missing:
        print('없는 파일:', *missing, sep='\n  '); sys.exit(1)
    os.makedirs(out, exist_ok=True)
    for f in PRICE_FILES:
        shutil.copy2(os.path.join(price, f), os.path.join(out, f))
    prod_files = []
    for mk, d in makers.items():
        for f in (mk + '_1_제품군_요약.csv', mk + '_2_품번_치수.csv'):
            shutil.copy2(os.path.join(d, f), os.path.join(out, f)); prod_files.append(f)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    shift = lambda t: '\n'.join(('#' + l) if l.startswith('# ') else l for l in t.splitlines())
    rd = lambda p: open(p, encoding='utf-8-sig').read().strip()
    head = (f'# 사내 공구 문의 — 자료 안내\n\n'
            f'- 묶은 시각: {now:%Y-%m-%d %H:%M} KST (scripts/build_integrated_project.py)\n'
            f'- 재연마 정가 파일: {", ".join(PRICE_FILES)} — 아래 「재연마 정가 자료 안내」\n'
            f'- 취급 메이커({len(makers)}): {" · ".join(makers)} — 파일 {", ".join(prod_files)} — 아래 제품 자료 안내\n'
            f'- 재연마 정가와 신품 카탈로그는 서로 다른 자료입니다. 신품 가격은 없습니다.\n')
    body = [shift(rd(os.path.join(price, '0_자료_안내.md')))]
    for d in dict.fromkeys(makers.values()):
        body.append(shift(rd(os.path.join(d, '0_자료_안내.md'))))
    open(os.path.join(out, '0_자료_안내.md'), 'w', encoding='utf-8').write(head + '\n' + '\n\n'.join(body) + '\n')
    shutil.copy2(TEMPLATE, os.path.join(out, '지시문_프로젝트에_붙여넣기.md'))
    n = len(PRICE_FILES) + len(prod_files) + 1
    size = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out))
    print(f'{out}: 지식 파일 {n}개(메이커 {", ".join(makers)}) + 지시문 · 합계 {size/1e6:.2f} MB')


if __name__ == '__main__':
    main()
