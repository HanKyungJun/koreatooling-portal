"""재연마 정가 조회 — 사내 창 프로그램 시험판 묶음 만들기 (2026-10-29 Cowork)

실행: python scripts\\build_price_app.py [출력 폴더]
  기본 출력: outputs\\price_app_YYYYMMDD\\
  만드는 것: 정가조회.pyw · price_core.py (프로그램) · price_data.json (정가 데이터, price_lookup.py --export-json)
            정가조회_실행.bat · exe만들기.bat · 정가조회_설정.ini(예시) · 설치안내.md
정가표 · ERP 파일이 바뀌면 다시 실행한다(데이터만 바꾸려면 price_data.json 만 교체해도 됨).
"""
import os, sys, subprocess, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, 'price_app')
KST = datetime.timezone(datetime.timedelta(hours=9))
today = datetime.datetime.now(KST).strftime('%Y%m%d')
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'outputs', f'price_app_{today}')
os.makedirs(out, exist_ok=True)

r = subprocess.run([sys.executable, os.path.join(HERE, 'price_lookup.py'), '--export-json', os.path.join(out, 'price_data.json')],
                   capture_output=True, text=True, encoding='utf-8')
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-500:])
if r.returncode != 0 or not os.path.exists(os.path.join(out, 'price_data.json')):
    sys.exit('price_lookup.py --export-json 실패')
for n in ('정가조회.pyw', 'price_core.py'):
    shutil.copyfile(os.path.join(SRC, n), os.path.join(out, n))

def w(name, text, enc='utf-8'):
    with open(os.path.join(out, name), 'w', encoding=enc, newline='') as f:   # 줄 끝은 문자열에 직접(\r\n)
        f.write(text)

w('정가조회_실행.bat', '@echo off\r\nchcp 65001 >nul\r\ncd /d "%~dp0"\r\nstart "" pythonw "정가조회.pyw"\r\n')
w('exe만들기.bat', '@echo off\r\nchcp 65001 >nul\r\ncd /d "%~dp0"\r\necho 재연마 정가 조회 exe 만들기 (PyInstaller)\r\npip install pyinstaller -q\r\n'
  'pyinstaller --onefile --windowed --name "정가조회" --add-data "price_core.py;." "정가조회.pyw"\r\n'
  'copy /y price_data.json dist\\ >nul\r\nif exist 정가조회_설정.ini copy /y 정가조회_설정.ini dist\\ >nul\r\n'
  'echo.\r\necho 완료: dist\\정가조회.exe  (price_data.json 과 같은 폴더에 두고 실행)\r\npause\r\n')
w('정가조회_설정.ini.예시', '; 이 파일 이름을 정가조회_설정.ini 로 바꾸면 아래 경로의 price_data.json 을 읽는다\r\n'
  '; (사내 공유 폴더에 데이터 하나만 두고 모든 PC 가 같이 쓰기 — 경로는 실제 공유 폴더로 고칠 것)\r\n'
  '[데이터]\r\n경로 = \\\\192.168.0.252\\ToolKorea\\생산팀\\4.AI 자료실\\정가조회\\price_data.json\r\n')
w('설치안내.md', f'''# 재연마 정가 조회 — 사내 창 프로그램 시험판 ({today})

## 실행

- Python 이 깔린 PC: `정가조회_실행.bat` 더블클릭
- exe 로 쓰기: 이 폴더에서 `exe만들기.bat` 실행 → `dist\\정가조회.exe` (price_data.json 과 같은 폴더에 둔다)

## 화면

- 항목 선택(재질 · 형상 · 날 수 · 날경 · 작업 부위 · 코팅) / 문장 입력(예 「10파이 2날 볼 고경도」)
- 결과: 규격 · 정가 · 상태(OK · 확인 필요 · 없음) · 근거. 「결과 복사」 → 메신저 · 메일에 붙여 넣기용 글
- 정가만(할인 적용 전). 할인율 · 거래처 단가 · 사업장 판매가는 데이터에 없다

## 가격이 바뀌면

`python scripts\\build_price_app.py` → 새 `price_data.json` 만 교체(프로그램 재설치 불필요).
여러 PC 가 같이 쓰려면 `정가조회_설정.ini.예시` 를 `정가조회_설정.ini` 로 바꾸고 공유 폴더 경로를 적는다.

## 규칙

- 조회 규칙은 웹 위젯(`price_lookup_core.js`)과 같다 — 2026-10-29 대조 11,616 조합 · 문장 12개 모두 같은 결과
- 드릴은 정가표(26.10) 구간 안만 금액. 표 밖(초경 20 mm 초과 · 밑날 외)은 「확인 필요」 + ERP 등록 정가 참고 표시
''')
print('정가 조회 프로그램 시험판:', out)
for n in sorted(os.listdir(out)):
    print(f'  {n}  {os.path.getsize(os.path.join(out, n)):,} B')
