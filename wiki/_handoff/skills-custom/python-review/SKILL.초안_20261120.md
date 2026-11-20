---
name: python-review
description: review-role 전용 하위 검토표 — review-role 이 .py 검수 때 Skill 도구로 부르는 파이썬 항목표(P1~P9 파이썬 고유 실수 · W1~W8 사내 실행 환경 — 인코딩 · 작업 스케줄러 · exe · 엑셀 · 삭제 · KST · 종료 코드 · PC 경로). 「검토 · 검수 · 점검해 줘」 같은 요청 문구로는 직접 부르지 않는다 — 그런 요청은 review-role 이 먼저 받고 이 스킬을 부른다.
---

# 파이썬 코드 검토표 (python-review)

「검수해 줘」 대상이 `.py` 일 때 review-role §1-A 가 code-review 와 함께 부른다. 경준님이 이 이름을 외울 필요는 없다.
**창구는 review-role 하나다** — 이 스킬은 부품(파이썬 항목표)이라 요청 문구로 직접 불리지 않게 description 에 부르는 말을 넣지 않았다(2026-11-20, 같은 말로 두 스킬이 경쟁하지 않게). 검토 요청에서 이 스킬이 먼저 불렸으면 review-role 을 불러 그 순서(§1-A)대로 진행한다.
code-review 는 정확성 · 성능 · 보안 같은 일반 항목을 본다. 이 스킬은 그 밖의 **파이썬 고유 실수(P)** 와 **사내 PC · 예약 작업 · exe 환경에서만 터지는 것(W)** 을 본다.

## 0. 먼저 — 실행 맥락 확인

같은 코드라도 어떻게 돌아가느냐에 따라 심각도가 달라진다. 지적 전에 아래를 grep 으로 확인하고 결과 첫 줄에 적는다.

| 맥락 | 확인 방법 | 영향 받는 항목 |
|---|---|---|
| 예약 작업으로 도나 | `scripts/*.bat` · `*.vbs` · `setup_scheduler*.ps1` 에서 파일 이름 grep | W2 · W7 이 「상」 후보 |
| exe 로 빌드되나 | `*.spec` 의 Analysis 대상 · `datas` | W3 |
| 손으로 돌리나 | 위 둘 다 없음 | W2 · W7 은 「하」 |
| 어느 Python 으로 도나 | 사내 PC 는 3.14 계열(2026-11-19 새 PC 3.14.10 — 3.15 가 기본 설치돼 되돌림, PC이전_체크리스트) | W1 |
| 감싸는 bat 가 무엇을 해 주나 | 그 bat 의 `set PYTHONUTF8=1` · `>> run.log 2>&1` · `cd /d` · `exit /b` | W1 · P7 · W2 · W7 — bat 가 이미 막고 있으면 심각도를 내린다 |

- device_bash 는 사용자 PC 안의 Linux VM 이다 — Windows 의 Python 버전 · 경로 동작과 다르다. Windows 에서만 확인되는 것은 「확인 필요」.
- **스크립트는 실행하지 않는다**(메일 발송 · ERP 조회 · 파일 삭제가 있을 수 있음). 돌리는 것은 문법 검사(`python -m py_compile`)와 `ruff check`(있으면)까지.

## 1. 심각도 (코드용 — review-role §3 의 상 · 중 · 하에 맞춤)

- **상** — 잘못된 값이 보고서 · ERP · 고객에게 나감, 파일 유실 · 삭제, 실패했는데 성공으로 보임, 비밀값 노출
- **중** — 특정 조건(파이썬 버전 업 · PC 교체 · exe 빌드 · 파일이 열려 있음)에서 깨짐
- **하** — 지금은 동작함. 사용 중단 예고 · 유지보수 · 표기

## 2. 파이썬 고유 항목 (P1~P9)

| # | 확인 | 기본 심각도 | 수정안 |
|---|---|---|---|
| P1 | 예외 삼키기 — `except:` · `except Exception: pass` · 로그 없이 넘김 | 상(예약 작업) / 중 | 잡을 예외를 좁히고, 로그를 남긴 뒤 다시 던지거나 W7 처럼 종료 코드 1 |
| P1-a | 부른 함수 안의 `sys.exit()` 를 `except Exception` 으로 감쌈 — `SystemExit` 는 `BaseException` 이라 안 잡혀 상위 흐름 전체가 멈춤(2026-11-20 generate.py → `daily_dlv_alert.get_gmail_service` 사례) | 중 — 종료 코드 1 이 작업 결과까지 넘어가면(실패로 보임) 중, 중간에서 0 으로 바뀌면 상(W7 과 같은 기준, 11-20 시험 ① 보정) | 공용 함수처럼 `except (Exception, SystemExit)` 로 받거나, 부르는 함수가 `sys.exit` 대신 예외를 던지게 |
| P2 | `with` 없이 파일 · 엑셀 · DB 연결 열기 → 예외 때 안 닫힘 · 파일 잠김 | 중 | `with open(...) as f:` · `with pd.ExcelWriter(...)` |
| P3 | 바뀌는 기본값 — `def f(x=[])` · `x={}` | 중 | `x=None` 후 함수 안에서 `x = []` |
| P4 | 위험 호출 — `eval` · `exec` · 외부 파일 `pickle.load` · `yaml.load`(SafeLoader 없음) · `subprocess(..., shell=True)` 에 입력값 | 상 | `ast.literal_eval` · `json` · `yaml.safe_load` · 인자 목록으로 호출 |
| P5 | 비밀값 하드코딩 — 토큰 · 비밀번호 · API 키 · 메일 계정 | 상 | `.env` · 토큰 파일(git 제외 확인 `git check-ignore`) |
| P6 | `== None` · `type(x) == int` | 하 | `is None` · `isinstance(x, int)` |
| P7 | 예약 작업 스크립트가 `print` 만 씀 → 창이 숨겨지면 기록이 안 남음 | 중(예약 작업) / 하. 감싸는 bat 가 `>> run.log 2>&1` 로 받으면 **해당 없음** | `logging` 으로 파일 기록, 또는 bat 에서 로그 파일로 받기 |
| P8 | `from x import *` · 내장 이름 가리기(`list` · `id` · `type` · `input` · `file`) | 하 | 이름 바꾸기 |
| P9 | 긴 함수(약 80줄 넘음) · 4단 넘는 중첩 · 뜻 없는 숫자(열 번호 · 9 시간 등) — 사내 경험값 기준 | 하 | 함수 나누기 · 이름 있는 상수 |

- P4 · P5 는 code-review 보안 항목과 겹친다. 같은 줄을 두 번 지적하지 않고 한 번만 적는다(구분 `코드`).

## 3. 사내 실행 환경 항목 (W1~W8)

| # | 확인 | 심각도 | 수정안 · 근거 |
|---|---|---|---|
| W1 인코딩 | `open()` · `read_text()` · `write_text()` · `subprocess(text=True)` 에 `encoding=` 없음 | 한글을 읽고 쓰면 **중** / 영문만(토큰 JSON · 시트 ID)이면 **하** / 감싸는 bat 에 `set PYTHONUTF8=1` 이 있으면 이미 3.15 와 같은 UTF-8 모드라 **하**(단 같은 스크립트를 손으로 돌리면 다름 — 2026-11-20 실측: `PYTHONUTF8` 있는 bat 3개, 없는 bat 7개) | 항상 `encoding="utf-8"` 명시. Python 3.15(2026-10-09 출시)부터 기본이 로케일(cp949) → UTF-8 로 바뀜 [PEP 686] — 지금 cp949 로 읽히던 파일이 버전만 올려도 깨진다. 일괄 찾기: `python -X warn_default_encoding 파일.py` [PEP 597] |
| W1-a CSV | pandas `read_csv` 는 버전과 상관없이 UTF-8 이 기본 — ERP · 장비가 cp949 로 내보낸 CSV 는 `encoding="cp949"` 명시. 엑셀로 열 CSV 를 `to_csv` 할 때 `encoding` 없음 | 중 | 엑셀용은 `encoding="utf-8-sig"`(사내 본보기 `scripts/parse_worklog.py`) |
| W2 작업 스케줄러 경로 | 상대 경로(`open("data.csv")` · `Path("wiki/…")`)를 예약 작업에서 씀 | bat 에 `cd /d` 가 있으면 **하**(bat 에 기댐) / 없으면 **상** | 작업 스케줄러는 「시작 위치」가 비어 있으면 `%windir%\system32` 에서 실행한다 [Microsoft Learn, Task Scheduler 용어집 W]. 코드에서 `BASE = Path(__file__).resolve().parent` 기준으로 |
| W3 PyInstaller exe | 단일 파일 exe 에서 `__file__` · 상대 경로 기준으로 저장 · 설정 파일 읽기 | 상 | 단일 파일 exe 는 실행 때 임시 폴더(`sys._MEIPASS`)에 풀리고 종료 때 지워진다 → 저장은 `Path(sys.executable).parent`, 묶은 데이터 읽기는 `sys._MEIPASS`. 사내 본보기 `erp/erp_gui.py` 53~58행 `getattr(sys, "frozen", False)` 분기. **코드를 고치면 exe 재빌드**(`erp/build_exe.bat`)까지가 한 일 — 뷰어(TricoERP.exe)에 반영돼야 끝 |
| W4 엑셀 | `.xls` · `.xlsx` 엔진 미지정 · 열려 있는 파일에 쓰기(PermissionError 처리 없음) · 원본 엑셀 덮어쓰기 | 원본 덮어쓰기 **상** / 나머지 **중** | `engine="xlrd"`(xls) · `"openpyxl"`(xlsx) 명시, PermissionError 때 「엑셀 파일을 닫고 다시」 안내, 결과는 새 파일 |
| W5 삭제 · 이동 | `os.remove` · `Path.unlink` · `shutil.rmtree` · `shutil.move` · 덮어쓰는 `os.replace` 가 확인 · 미리보기 없이 실행 | 상 | 기본은 미리보기, `--apply` 를 줄 때만 실행(사내 본보기 `scripts/slim_tasks.py --apply`). 지우기보다 `_to_delete/` 로 옮기기 |
| W6 시각 (KST) | `datetime.utcnow()` · `utcfromtimestamp()` 를 **그대로** 날짜 · 시각으로 씀 | **상** — 07:30 KST 는 UTC 로 전날 22:30 → 보고서 날짜가 하루 밀림 | `datetime.now(timezone(timedelta(hours=9)))` (추가 설치 없음) |
| W6-a | `utcnow() + timedelta(hours=9)` 처럼 이미 보정한 코드 | **하** — 결과는 맞음 | 3.12 부터 `utcnow()` 사용 중단 예고 → 위 형식으로 바꾸기 권고. `ZoneInfo("Asia/Seoul")` 는 Windows 에서 `tzdata` 패키지가 필요하니 쓰면 requirements 확인 |
| W7 실패 종료 코드 | 예약 작업 스크립트가 예외를 잡고 정상 종료 → 종료 코드 0 → 스케줄러 「마지막 실행 결과 0x0」(성공)으로 보임. 스크립트가 1 을 내도 **감싸는 bat 가 그 단계 결과를 안 넘기면** 같은 문제 | 상(예약 작업) / 로그 · 누락 점검 스킬(daily-report-check 등)로 따로 잡히면 **중** | 실패 때 `sys.exit(1)`. 감싸는 bat 에서 단계마다 `%ERRORLEVEL%` 을 받아 마지막에 `exit /b` 로 넘기는지 확인. R4-1 「조용한 성공」과 같은 문제 |
| W8 PC 고정 경로 | `C:\Users\<이름>\…` 절대 경로 | **하** | 새 코드는 `Path(__file__)` 기준 · `Path.home()`. ⚠️ 지금 `C:\Users\TOOLKOREA` 는 연결 폴더(junction)로 `C:\Users\HAN` 이 열린다(decisions 2026-11-19 (1)) → **파일마다 지적하지 않고 「연결 폴더 없애기 전 고칠 목록」 1건으로 묶는다**(파일 수 · 목록). 연결 폴더를 없애는 계획이 잡히면 중으로 올린다 |

## 4. 순서

1. §0 실행 맥락 확인 → 결과 첫 줄에 「예약 작업 / exe / 수동」 표시.
2. 문법 검사 · ruff(있으면) — 못 돌리면 「확인 필요」.
3. P1~P9 · W1~W8 grep + 해당 줄 읽기. 지적마다 `파일:행` 증거. grep 에만 걸리고 줄을 안 읽은 것은 지적하지 않는다(여러 줄에 걸친 `open(...,\n encoding=…)` 오탐 주의).
4. 오탐 반증 — 걸린 곳이 맥락상 문제가 없으면(예: 영문만 쓰는 토큰 JSON) 심각도를 내리거나 「해당 없음」.
5. review-role §3 표에 합친다 — 「구분」 열은 `Py`(이 스킬) · `코드`(code-review) · `R4` · `G`. 검토 줄 예: `검토(R4 주 · 코드 리뷰 · Py): 통과 n · 확인 필요 m(대표 항목)`

## 5. 하지 않는 것

- 코드를 고치지 않는다 — 지적과 수정안까지. 고치는 것은 경준님 「진행」 뒤(review-role §1-A).
- 스크립트를 실행하지 않는다(§0).
- 웹 프레임워크(Django · FastAPI · Flask) 항목은 없다 — 사내에 없음. 생기면 code-review 로 본다.
- 타입 힌트 · PEP 8 줄 길이 · docstring 은 지적하지 않는다(사내 스크립트 규모에 비해 잡음이 큼).

## 6. 출처 · 보정

- [PEP 686] Make UTF-8 mode default (Python 3.15) · [PEP 597] EncodingWarning · Python 3.15.0 출시 공지(discuss.python.org, 2026-10-09) · pandas `read_csv` 문서 · Microsoft Learn「Task Scheduler — W(working directory)」 — 모두 제조사 · 표준 문서(1 · 2순위).
- 같은 파일을 두 번 검수하면 지적이 달라질 수 있다(11-20 generate.py 2회 — 상 지적이 서로 다름). 중요 파일은 이전 검수 결과(테스트카드 · worklog)를 찾아 합쳐 보고, 「이전 검수에 있었는데 이번에 빠진 것」을 따로 적는다.
- 심각도 · 「80줄」 · 「4단」 기준은 사내 경험값. 첫 실사용 3건 결과로 보정한다(skills-custom/테스트카드 #8).
- 2026-11-20 실제 코드 80개 grep 시험: 상 0 · 지적 대부분 하(W1 영문 JSON 10곳 · W6-a 3곳 · W8 19개 파일) — 기존 코드보다 **새로 짜는 코드를 미리 막는 용도**.
- 2026-11-20 `scripts/daily_report.py`(예약 작업 CNC_Daily_Report) 1개 전체 적용: 지적 1(W7 중 — `daily_and_upload.bat` 가 1단계 종료 코드를 안 받아 작업 결과는 마지막 generate.py 결과만 보임, run.log 에는 남음) · 오탐 반증 3(P1 의도된 파싱 실패 처리 · P7 bat 가 run.log 로 받음 · W1 bat `PYTHONUTF8=1`) → 이 보정을 §0 · P7 · W1 · W7 에 반영.

## 원본 고지 (MIT)

P1~P9 는 everything-claude-code 의 `agents/python-reviewer.md` 를 바탕으로 사내에 맞게 골라 고쳐 썼다. 원본 고지:

Copyright (c) 2026 Affaan Mustafa — MIT License. Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
