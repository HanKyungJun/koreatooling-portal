"""재연마 예상 정가 위젯 — 시험판 묶음 만들기 (2026-10-29 Cowork)

실행: python scripts\\build_price_widget.py [출력 폴더]
  기본 출력: outputs\\price_widget_YYYYMMDD\\
  만드는 것: price-data.js · price-lookup.js (price_lookup.py --export-web 결과, 정가만)
            price-widget.js (화면) · demo.html (붙인 예) · 미리보기_단일파일.html (파일 하나로 열리는 미리보기) · 설치안내.md
정가표 · ERP 파일이 바뀌면 다시 실행한다. 원본 정가표는 읽기만 한다.
"""
import os, sys, subprocess, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KST = datetime.timezone(datetime.timedelta(hours=9))
today = datetime.datetime.now(KST).strftime('%Y%m%d')
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'outputs', f'price_widget_{today}')
os.makedirs(out, exist_ok=True)

# ① 데이터 · 조회 로직 — 정가표에서 못 찾은 블록이 있어도 시험판은 만든다(--force). 그 규격은 화면에 「담당자 확인」
r = subprocess.run([sys.executable, os.path.join(HERE, 'price_lookup.py'), '--export-web', out, '--force'], capture_output=True, text=True, encoding='utf-8')
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-500:])
if r.returncode != 0:
    sys.exit('price_lookup.py --export-web 실패')
shutil.copyfile(os.path.join(HERE, 'price_widget', 'price-widget.js'), os.path.join(out, 'price-widget.js'))

DEMO_HEAD = '''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>재연마 예상 정가 위젯 (시험판)</title>
<style>body{margin:0;background:#f6f7f9;font-family:"Malgun Gothic","맑은 고딕",system-ui,sans-serif;color:#1d2330}
.page{max-width:760px;margin:0 auto;padding:24px 16px 48px}.page h1{font-size:22px;margin:0 0 6px}.page p{color:#5d6675;font-size:14px;margin:0 0 16px}</style>
</head><body><div class="page">
<h1>견적 문의 (예시 페이지)</h1>
<p>아래 상자가 위젯입니다. 실제 견적 폼 · 쇼핑몰 상세 페이지에는 아래 3줄 + div 한 개만 붙이면 됩니다(설치안내.md).</p>
<div id="kt-price-widget" data-inquiry-url="estimate.html"></div>
</div>
'''
with open(os.path.join(out, 'demo.html'), 'w', encoding='utf-8') as f:
    f.write(DEMO_HEAD + '<script src="price-data.js"></script>\n<script src="price-lookup.js"></script>\n<script src="price-widget.js"></script>\n</body></html>\n')

def inline(name):
    return open(os.path.join(out, name), encoding='utf-8').read().replace('</script', '<\\/script')
with open(os.path.join(out, '미리보기_단일파일.html'), 'w', encoding='utf-8') as f:
    f.write(DEMO_HEAD + ''.join(f'<script>\n{inline(n)}\n</script>\n' for n in ('price-data.js', 'price-lookup.js', 'price-widget.js')) + '</body></html>\n')

GUIDE = f'''# 재연마 예상 정가 위젯 — 시험판 ({today})

## 붙이는 법

웹폼 · 쇼핑몰 페이지에 아래를 넣는다. 파일 3개(`price-data.js` · `price-lookup.js` · `price-widget.js`)는 같은 폴더에 올린다.

```html
<div id="kt-price-widget" data-inquiry-url="estimate.html"></div>
<script src="price-data.js"></script>
<script src="price-lookup.js"></script>
<script src="price-widget.js"></script>
```

- `data-inquiry-url`: 「이 규격으로 견적 문의」 버튼이 갈 주소. 비우면 버튼이 안 나온다. 주소 뒤에 `?spec=규격` 이 붙는다(받는 폼에서 읽어 채우는 것은 아직 안 함)
- 한 페이지에 여러 개: `<div data-kt-price-widget></div>`

## 보여 주는 것 · 안 보여 주는 것

- 정가만(정가표 기준, 할인 적용 전). 할인율 · 거래처 단가 · 사업장 정보는 데이터에 없다
- 정가표에 없는 규격 · 정가표와 ERP 등록 정가가 다른 규격 · 사업장 파일끼리 다른 규격 → 금액 대신 「담당자 확인」
- 입력 방식 두 가지: 항목 선택(재질 · 형상 · 날 수 · 날경 · 작업 부위 · 코팅) / 문장 입력(예 「10파이 2날 볼 고경도」)

## 다시 만들기

정가표 · ERP 내려받기가 바뀌면: `python scripts\\build_price_widget.py`

## 공개 전 확인 (미결)

- 안내 문구 · 공개 범위 대표님 확인(decisions 2026-10-27 (8))
- 정가표에서 못 찾는 블록(HSS 리머 · 초경 라핑 평 밑골수리 고경도)은 「담당자 확인」으로 나온다
- 초경 드릴 20 mm 초과 · 밑날 외 드릴 · HSS 드릴 고경도(보류)는 ERP 등록 정가 또는 「담당자 확인」
- `price-data.js` 는 누구나 내려받을 수 있다 — 정가 외 값을 넣지 않는다
'''
open(os.path.join(out, '설치안내.md'), 'w', encoding='utf-8').write(GUIDE)
print('위젯 시험판:', out)
for n in sorted(os.listdir(out)):
    print(f'  {n}  {os.path.getsize(os.path.join(out, n)):,} B')
