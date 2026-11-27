# Codex 작업 기록

> Codex가 직접 확인하거나 수행한 작업만 기록합니다. 최신 기록을 위에 추가합니다.

## 2026-11-27 — Codex 작업 기록 위치 정리
- 수주 감소 Claude 인계 메모를 제목·안내문 아래로 이동했다(본문 변경 없이 1회 유지).
- 대기 카드 `codex-worklog-order-fix-2026-11-27`을 마침으로 갱신했다.

## 2026-11-26 — 수주 감소 원인 Claude 인계 메모
- 인계 ID: `shipment-order-decline-cause-2026-11-26`.
- 기존 분석에서 확인한 8월 수주 -972개 분해를 요약: C 거래 종료 약 -230개/월(사유 미확인), O 발주 공백 약 -190개(사유 미확인), 기타 약 -550개(주기·물량 변동, 미확인). 7월에는 6월 늦은 수주 출하가 몰린 시점 효과가 있음.
- Claude 조사 자료: `wiki/_handoff/수주감소_원인조사_Claude인계_20261126.md`. 현재 인계 `ai-handoff-current.md`를 이 작업으로 지정.
- 제한: 원본/외부 자료를 더 조회하거나 수정하지 않았으며, 거래처 익명 코드를 유지했다. 확인되지 않은 시장·가격·경쟁사 요인은 원인으로 단정하지 않도록 명시했다.

## 2026-11-26 — 엑셀 대조 및 제조사 자료 조사

- 엑셀: `wiki/reports/daily/2026-11-26_일일보고.xlsx`를 `read_only=True, data_only=True`로 열어 읽기 전용 확인. 2개 시트, 수식 0개, 07:55 생성된 ERP 속보 스냅샷.
- 계산: 9개 오늘 생산과 55.8개 전일 기준 평균 간 감소율 83.9%는 표기와 일치. 월 누적 1,013은 전일까지 1,004+오늘 9로 맞음.
- 확인 결과: 전일 NC 양품 58개와 불량 1개를 합산한 총수량 59개로, 세부 행과 주석은 서로 일치한다. 월평균 55.8개는 기존 18 작업일 기준의 총수량 평균이며 오늘 수량 대비 83.9% 감소 계산도 맞다. 월 누적 1,013개는 전일까지 1,004개에 오늘 9개를 더한 값.
- 외부 조사: TYROLIT 공식 2024 정밀 연삭 카탈로그 p.17은 초경합금/산업 세라믹용 다이아몬드 휠 권장 절삭속도 15~25 m/s를 제시한다. `wiki/tools/anca-tom-파일-분석.md`에서 18~25를 사내 권장처럼 보이던 문구를 사내 데이터 분포로 고치고, 제조사 범위와 적용 한계를 출처와 함께 덧붙였다.
- 한계: 보고서는 07:55 ERP 속보 스냅샷이라 최종 확정값은 ERP에서 확인해야 한다. 카탈로그는 일반 권고이며 개별 휠·기계·공정 조건 확인을 대체하지 않는다. Claude는 주간 사용량 한도 소진으로 비교 검토 미실행.

## 2026-11-26 — 코드·자동화 점검

- `scripts/update_overview.py --dry-run`: 정상 종료, 카테고리 합계 174. Windows Python 실행기는 `C:\Users\HAN\AppData\Local\Python\bin\python.exe`; 기본 WindowsApps 별칭은 실행 오류. `-X utf8` 사용 시 출력도 정상 표시.
- Python AST 문법 확인: `scripts/update_overview.py`, `scripts/daily_report.py`, `generate.py` 3개 통과. `generate.py`의 JavaScript 정규식 문자열에 있던 Python `SyntaxWarning` 원인을 수정한 뒤 경고를 오류로 승격해 재확인 통과.
- JS 문법 확인: `dist/portal.js`, `netlify_to_sheets.gs` 통과.
- 보안 정리: Git 추적 중인 `netlify_to_sheets.gs`에서 스프레드시트 식별자·알림 주소의 하드코딩을 제거하고 `FORM_SHEET_ID`, `FORM_NOTIFY_EMAIL` Script Properties로 이동. 소스에서 기존 값 검색 0건.
- 미완: 수정된 GAS는 아직 배포하지 않음. Apps Script 프로젝트 속성 2개 설정 후 새 버전 배포가 필요하며, 첨부 저장 실주소 재시험은 기존 핸드오프 항목으로 남음.
- 실행하지 않은 작업: 실제 일일 배치·Drive/GitHub 업로드·고객 폼 제출은 외부 변경이 수반되어 실행하지 않음.

## 2026-11-26 — 프로젝트 맥락 파일 정리 및 overview 정정 완료

- 한 일: 기존 `context.md`·`memory.md`·`decisions.md`·`tasks.md`·`worklog.md`를 바탕으로 민감정보를 제외한 Codex 프로젝트 요약을 만들고, 루트 `AGENTS.md`에서 참조하도록 연결했다.
- overview 수정: 통계 기준일을 갱신하고, 집계 범위를 명시했다. D8 확정 경험값, D5 HWP 이관 완료, 기존 통계 자동화 스크립트의 완료 사실을 반영하고, 오래된 작업 목록을 정리했다.
- 자동화 개선: `scripts/update_overview.py`가 통계 섹션 기준일도 갱신하도록 보완했다.
- 변경 파일: `AGENTS.md`, `wiki/_handoff/codex-project-brief.md`, `wiki/overview.md`, `scripts/update_overview.py`, `_handoff/README.md`, `ai-handoff.md`, `ai-handoff-current.md`, `ai-worklog-codex.md`, `worklog.md`.
- 확인: 집계 로직을 PowerShell로 재현한 카테고리 합계 174 유지. Python/py 실행기는 이 환경에서 WindowsApps 오류가 있어 스크립트 실행은 불가. 자동 테스트는 실행하지 않음(요청 없음).
- 상태: Codex 맥락은 저장소 파일에 고정. 계정의 Codex Memories 설정은 직접 변경하지 않음.

## 2026-11-26 — 인계 전환 및 overview 현황 대조 (Codex 단독)

- 인계 전환: 사용자가 Claude의 주간 토큰 소진을 알려 Codex 단독으로 시험을 이어가도록 `ai-handoff-current.md`와 `ai-handoff.md`를 갱신했다.
- 확인 범위: `wiki/overview.md`, `scripts/update_overview.py`, D8 조건 상세, D5 비교 페이지, `tasks.md`, `tasks-archive.md`.
- 통계: `python scripts/update_overview.py --dry-run`과 `py -3 ...`는 WindowsApps 실행 오류로 실행되지 않았다. 집계 로직을 PowerShell로 재현한 결과 스크립트가 세는 13개 카테고리 합계는 **174**로 overview 값과 일치했다. 따라서 숫자 자체가 틀렸다고 보지는 않는다.
- 발견한 불일치:
  1. `overview.md` 「페이지 통계」 제목은 2026-05-27 기준으로 남아 있지만 frontmatter/마지막 갱신은 2026-11-26이다. `update_overview.py`는 통계표와 성장 추이만 갱신하므로 제목의 기준일과 본문 수동 갱신 항목은 자동 갱신되지 않는다.
  2. overview는 D8 조건을 검증 중으로 표기하지만 `wiki/tools/연삭-조건-D8-4날-코너R-GASH.md`는 2026-06-05에 2,800~3,200 RPM을 사내 경험값으로 확정했다고 명시한다. 재측정 권고와 조건 미확정은 구분해야 한다.
  3. overview는 D5 HWP 실측 이관을 미완으로 제시하지만 `wiki/comparisons/드릴-6종-비교-D5.md` §5·§5-B는 2026-05-27 이관 완료로 체크했고, tasks-archive에도 완료 기록이 있다.
  4. overview는 `scripts/update_overview.py`를 미작성 후보로 표기하지만 파일이 존재하고, `tasks-archive.md`는 2026-05-29 완료로 기록한다.
- 제한/미완: 사용자가 요청한 시험 범위대로 원본 overview는 수정하지 않았다. Python dry-run은 실행 환경 문제로 검증하지 못했다.
- 다음 제안: overview의 날짜·D8·D5·스크립트 항목을 정정하고, 자동 갱신 스크립트가 관리하는 범위와 수동 갱신이 필요한 본문을 나눠 표시한다.
- 시험 상태: Codex 검토 완료, 수정 대기.

## 2026-11-26 — Claude ↔ Codex 인계 시험 시작

- 목적: Claude와 Codex의 작업 기록을 분리하고, 공용 인계 파일로 서로 이어 읽는 흐름을 시험한다.
- 추가 파일: `ai-handoff.md`, `ai-handoff-current.md`, `ai-worklog-codex.md`, `ai-worklog-claude.md`.
- 규칙: 각 AI는 자기 기록에만 추가하고 상대 기록은 수정하지 않는다. 현재 담당자와 범위는 `ai-handoff-current.md`를 기준으로 한다.
- 시험 작업: Claude에게 `wiki/overview.md`를 실제 저장소와 대조해 검토 요청. 운영 문서는 수정하지 않고 Claude 작업 기록에 근거와 제안만 적도록 범위를 제한했다.
- 확인: 기존 `wiki/_handoff/README.md`, `context.md`, `decisions.md`, `worklog.md`, `memory.md`, `tasks.md`, `wiki/index.md`, `wiki/overview.md`를 읽었다. 현재 Git 상태에는 미커밋 변경이 없었다.
- 다음 단계: 사용자가 Claude에 현재 인계 파일을 전달한다. Claude 기록이 추가되면 Codex가 실제 파일과 대조해 시험을 마무리한다.
- 상태: Claude 작업 대기.

