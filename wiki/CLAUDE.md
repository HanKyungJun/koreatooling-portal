# CLAUDE.md — cnc-wiki 작업 규약

이 폴더는 cnc-wiki 작업 공간입니다.
챗(claude.ai), Cowork, Claude Code 어디서 작업하든 아래 규약을 반드시 따릅니다.

## 작업 시작 전 (반드시 읽기)

1. `_handoff/context.md` — 프로젝트 배경·범위·용어 (큰 그림)
2. `_handoff/decisions.md` — 누적된 의사결정 (최신이 맨 위)
3. `_handoff/worklog.md` — 직전 세션의 상태·미완 사항

이 세 파일이 서로 모순되면 **decisions.md의 최신 항목이 우선**합니다.

## 작업 중

- 새로운 결정이 생기면 즉시 `_handoff/decisions.md` 맨 위에 추가
- 코드·파일 변경, 실행 결과, 발견한 이슈는 `_handoff/worklog.md`에 기록
- 위키 본문(`tools/`, `machines/`, `materials/`, `reports/` 등)은 평소처럼 작업

## 작업 종료 시 (필수)

`_handoff/worklog.md` 맨 위에 다음 형식의 **핸드오프 블록**을 추가합니다.

````
## YYYY-MM-DD 핸드오프 — [Cowork|Code|챗]
- 한 일: ...
- 결과/산출물: ... (파일 경로 포함)
- 미완·블로커: ...
- 다음 단계 제안: ...
- 챗으로 가져갈 질문: ...
````

이 블록은 그대로 복사해서 챗(claude.ai)에 붙여넣어 다음 라운드의 토론을 시작하는 용도입니다.

## 챗에서 돌아왔을 때

챗에서 정리해준 결정 블록은 `_handoff/decisions.md` 맨 위에 그대로 붙여넣은 뒤 작업을 시작합니다.

## 폴더 규칙 (이 wiki 전용)

- `_handoff/` — 이 핸드오프 시스템 전용. 위키 컨텐츠와 절대 섞지 않음.
- `reports/`, `tools/`, `machines/`, `materials/`, `cadcam/`, `gcode/`, `comparisons/`, `troubleshoot/`, `projects/`, `scripts/` — 기존 위키 카테고리. 변경 없음.
- `log.md` — 기존 위키 변경 로그. `_handoff/worklog.md`와 별개로 유지.
- `index.md`, `overview.md` — 위키 진입점. 그대로 유지.

## 보고 스타일

- 한국어 응답
- 위키 페이지 작성 시 위키 기존 스타일(파일명 한국어 케밥, 표·체크리스트 활용) 유지
- 핸드오프 블록만은 위 형식을 정확히 따름 (자동 파싱 가능하도록)
