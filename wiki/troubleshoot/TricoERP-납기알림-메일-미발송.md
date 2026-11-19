---
type: troubleshoot
tags: [TricoERP, ERP, 납기알림, 단가0알림, Gmail, PyInstaller, exe, PC이전, 자동화]
sources: []
updated: 2026-11-19
---

# TricoERP 뷰어 — 납기 알림 메일 미발송 (새 PC 이전 때 발견)

> 🔴 토큰 · 암호 · 메일 주소는 이 문서에 기록하지 않는다(CLAUDE.md §4).

**대상**: `erp/dist/TricoERP.exe` 설정 탭 「3. 납기 알림 수동 실행」 · 「4. 단가 0 출하 전표 알림 수동 실행」
**발견**: 2026-11-19 새 PC(desktop-dqdpa0j, 사용자 HAN) 이전 직후
**결론**: 새 PC 문제가 아니라 **뷰어(exe) 버튼 코드에 원래부터 있던 결함 4개**였다. 옛 PC 에서도 이 버튼으로는 메일이 나가지 않았을 것으로 본다(추정값 — 옛 PC 에서 시험한 기록 없음). ERP 조회와 Gmail 인증은 처음부터 정상이었다.

---

## 1. 먼저 알아 둘 것 — 새 PC 에서 피들러는 다시 안 해도 된다 (실측 검증)

- `trico_client.py` 는 로그인 세션 · 쿠키 · PC별 토큰 없이, 요청마다 사용자 정보(매크로)를 코드에 고정된 값으로 함께 보낸다. PC가 바뀌어도 서버 쪽에서 달라지는 게 없다.
- 접속 주소는 `erp.toolkorea.co.kr:8101` 하나, **사무실 LAN 에서만** 동작한다.
- 피들러는 **새 화면(조회)을 추가할 때만** 필요하다. 그때 새 PC 에 피들러를 설치하고, 사용설명서의 피들러 경로(`C:\Users\TOOLKOREA\...`)를 HAN 으로 바꿔 읽는다.
- 확인: 설정 탭 [연결 테스트] → 「연결됨 (47건 조회)」 (2026-11-19)

## 2. 오류가 나온 순서와 원인 (모두 실측 검증 — 2026-11-19)

하나를 고치면 그 뒤 단계에서 다음 오류가 드러나는 구조였다. 같은 증상을 다시 보면 **로그의 마지막 줄**로 몇 번째 원인인지 찾는다.

| 순서 | 로그 마지막 줄 | 원인 | 조치 |
|---|---|---|---|
| ① | `FileNotFoundError: ...\erp\dist\daily_dlv_alert.py` | exe 는 알림 스크립트를 exe 안에 묶어 두는데(`--add-data`), 버튼 코드는 exe 옆 `dist` 폴더에서 찾았다. 묶인 파일은 실행 때 임시 폴더(`%TEMP%\_MEI…`, `sys._MEIPASS`)에 풀린다 | `_alert_script()` 추가 — exe 로 실행하면 `sys._MEIPASS` 에서 찾는다. 알림 엑셀은 임시 폴더가 아니라 `dist\outputs\` 에 저장하도록 지정 |
| ② | (①을 고쳐야 드러남) 메일 부품 import 실패 | exe 를 만들 때 PyInstaller 가 `erp_gui.py` 가 직접 import 하는 것만 넣는다. 알림 스크립트가 쓰는 `googleapiclient` · `email.mime` 은 빠져 있었다(옛 빌드 목록 `build/TricoERP/PYZ-00.toc` 에서 확인) | `build_exe.bat` · `TricoERP.spec` 에 `--hidden-import` 6개 + `--collect-data googleapiclient`(Gmail 정적 discovery 문서) + `zero_price_alert.py` 추가 |
| ③ | `NameError: name '__file__' is not defined` | 스크립트를 `types.ModuleType()` 으로 불러와 `__file__` 이 없었다. 알림 스크립트 30번째 줄 `Path(__file__)` 에서 멈춤 | `importlib.util.module_from_spec(spec)` 으로 불러온다 |
| ④ | `AttributeError: 'int' object has no attribute 'empty'` | 버튼 코드가 `send_email(out_path, urgent)` 로 불렀는데 스크립트의 함수는 `send_email(긴급건수, 수주표)` 이다. 수주에 D-3 표시(`flag_urgent`)를 붙이는 단계도 빠져 있었다 — **뷰어가 스크립트와 따로 놀았다** | `daily_dlv_alert.py` 의 `__main__` 순서와 똑같이 맞춤: 조회 → `flag_urgent` → `build_excel` → `send_email(urgent, df_so)` |
| — | 스케줄러 줄이 「3」으로 보임 | `Get-ScheduledTask` 상태를 JSON 으로 받으면 숫자가 나온다. **3 = Ready(등록됨 · 대기)** 로 정상 | 숫자 → 글자 표시(0 Unknown · 1 Disabled · 2 Queued · 3 Ready · 4 Running) |

- 결과: 2026-11-19 15:44 「[납기 알림] 2026-11-19 — D-3 이내 37건」 실제 수신 확인 (실측 검증)
- Gmail 토큰은 옛 PC 에서 가져온 `dist\token_gmail.json` 이 「만료」로 보였으나 첫 발송 때 자동 갱신됨(15:27) — **재인증 불필요**였다 (실측 검증)

## 3. exe 다시 만들기 (새 PC)

1. TricoERP 창을 **닫는다** — 켜 둔 채로 빌드하면 exe 를 덮어쓰지 못한다.
2. `erp\build_exe.bat` 더블클릭 → 끝에 「Done: dist\TricoERP.exe」.
   - 실패하면 「[FAILED]」가 나오고 멈춘다(2026-11-19 추가 — 전에는 실패해도 「Done」이 찍혔다).
   - 처음 줄의 `'5001'` · `'Trico'` 은(는) … 오류는 한글 출력 때문이라 무시한다.
3. 새 exe 인지 확인: 설정 탭 스케줄러 줄이 **「Ready」** 로 보이면 새 판.

⚠️ 새 PC 는 `pyinstaller` 명령이 PATH 에 없다(「'pyinstaller'은(는) 내부 또는 외부 명령… 아닙니다」). 그래서 배치 파일은 `python -m PyInstaller` 로 부른다. 빌드에 쓰는 Python 은 3.14(`%LOCALAPPDATA%\Python\pythoncore-3.14-64`).

## 4. 다시 생기지 않게 — 뷰어에 버튼을 붙일 때 점검

1. **스크립트를 직접 실행했을 때의 순서**(`if __name__ == "__main__":`)와 버튼 코드 순서가 같은가 — 함수 이름 · 인자 순서까지
2. 버튼이 부르는 스크립트가 exe 에 묶이는가(`--add-data`) · 그 스크립트가 쓰는 라이브러리가 exe 에 들어가는가(`--hidden-import`)
3. 빌드 후 `build/TricoERP/PYZ-00.toc` 에 필요한 모듈 이름이 있는지 grep
4. 버튼을 **끝까지(메일 발송까지)** 한 번 눌러 본다 — 「연결됨」만 보고 끝내지 않는다

## 5. 남은 것 (2026-11-19 기준)

- 「지금 단가 0 알림 실행」 — 같은 방식으로 고쳤고 모의 시험은 통과했지만 **실물 발송은 아직 안 해 봄** (확인 필요)
- 납기 메일 **제목 건수(37)** 는 수주 + 생산실적 + 출하의 D-3 합계, **본문 표(6줄)** 는 수주만 — 기준이 달라 헷갈릴 수 있음. 맞출지 미정
- 일일보고 예약(`CNC_Daily_Report` 등)은 새 PC 에 Ready 로 등록돼 있음. `scripts/setup_scheduler.ps1` 의 경로를 사용자명과 상관없게 바꿈(`$BaseDir = Split-Path -Parent $PSScriptRoot`) — 새 PC 에는 `C:\Users\TOOLKOREA` → `C:\Users\HAN` 정션도 있음(decisions 2026-11-19 (1))

## 6. 바뀐 파일 (원본은 모두 `.bak_20261119`)

- `erp/erp_gui.py` — `_alert_script()` · `_TASK_STATE` · `module_from_spec` · 납기 알림 순서 · 완료 줄 출력
- `erp/build_exe.bat` · `erp/TricoERP.spec` — 묶을 파일 · 숨은 import · `python -m PyInstaller` · 실패 시 멈춤
- `scripts/setup_scheduler.ps1` — `$BaseDir`

---

## 7. 관련 페이지

- [[사내-공유폴더-SMB-자격증명]] — 같은 자동화 쪽 진단 가이드(예약 작업 S4U · 로그 판정)
- `erp/dist/사용설명서.txt` — 뷰어 사용법 · 새 화면 추가(피들러 캡처) 절차
- `wiki/_handoff/worklog.md` — 2026-11-19 (#4)
