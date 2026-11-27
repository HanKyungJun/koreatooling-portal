# AGENTS.md — cnc-wiki Codex 작업 규약

이 폴더는 cnc-wiki 작업 공간입니다. Codex는 작업을 시작할 때 아래 문서를 먼저 확인하고, 기존 위키/핸드오프 흐름을 존중합니다.

## 작업 시작 전 읽기 (가볍게 시작 — 2026-11-27~)

Codex는 무료 요금제(월 사용량 한도, 매월 26일 초기화 — 2026-11-27 화면 확인)라서 큰 파일 전체를 읽지 않습니다. 역할 분담은 `wiki/_handoff/ai-handoff.md` 「역할 분담」.

**꼭 읽을 것**
1. `wiki/_handoff/ai-handoff-current.md` — 지금 맡은 작업 카드(목적 · 읽을 파일 · 끝 기준 · 결과 위치)
2. 작업 카드의 「읽을 파일」(최대 3개)

**필요할 때만, 부분만**
- `wiki/_handoff/decisions.md` — 맨 위 제목 3줄만. 관련 결정은 제목을 검색해 그 항목만
- `wiki/_handoff/worklog.md` · `tasks.md` · `wiki/index.md` — 전체를 열지 않고 검색(`Select-String` 등)으로 필요한 줄만
- `wiki/_handoff/codex-project-brief.md` — 작업 카드만으로 맥락이 모자랄 때
- `wiki/_handoff/context.md` · `memory.md` · `wiki/overview.md` — 큰 방향이 바뀔 때만

담당이 Codex인 작업 카드가 없으면 작업하지 않고 사용자에게 알립니다.
문서가 서로 다르면 `decisions.md`의 최신 항목을 우선합니다.
~~시작할 때 context · decisions · worklog · memory · index · overview · brief 7개 전체 읽기~~(2026-11-26 — 합계 약 17.6만 자라 무료 한도에 맞지 않음, decisions 2026-11-27 (2))

## 프로젝트 이해

- 목적: CNC/MCT, 공구 연삭, 재연마 작업일지, 출하/KPI 데이터를 모아 사내 지식 위키와 운영 대시보드로 관리합니다.
- 주요 흐름: `raw/` 원본 자료 → `wiki/` 정리 문서와 분석 파일 → `dist/` 정적 웹 화면 → Google Drive/Sheets 연동 및 배포.
- 사용자는 전문 개발자가 아니어도 현장 지식과 데이터를 제공하고, AI가 구조화·자동화·보안 점검을 보조하는 협업 방식을 선호합니다.

## 작업 원칙

- 한국어로 답변합니다.
- 기존 파일명 스타일인 한국어 케밥 케이스와 Markdown 표/체크리스트 형식을 유지합니다.
- 원본 자료는 `raw/`에 보존하고, LLM이 정리한 내용은 `wiki/`에 둡니다.
- 웹 산출물은 `dist/`, 템플릿은 `templates/`, 자동화 코드는 루트 또는 `scripts/`의 기존 패턴을 따릅니다.
- 민감정보가 있는 파일이나 토큰은 출력·공유·커밋 대상으로 취급하지 않습니다.
- 코멘트/피드백/검토 의견은 가능하면 원문을 직접 고치지 말고, 작성자와 날짜가 있는 추가 블록으로 남깁니다.

```markdown
> [작성자: Codex / 날짜: YYYY-MM-DD]
> 질문: ...
> 의견: ...
> 근거: ...
```

## 보안 주의

- 루트에 Google OAuth 관련 `client_secret*.json`, `token*.json`, `sheets_id.json` 파일이 있습니다.
- 코드에 비밀번호, 토큰, API 키가 하드코딩되어 있을 수 있으므로 외부 배포·GitHub 업로드 전 반드시 분리합니다.
- 비밀값은 답변에 그대로 노출하지 않고, 필요하면 `.env` 또는 로컬 설정 파일로 옮기는 방향을 제안합니다.

## 작업 종료 시

작업 기록은 `wiki/_handoff/ai-worklog-codex.md`의 **안내문(`> Codex가 직접 확인하거나…`) 바로 아래**에 새 블록으로 넣습니다(파일 맨 앞 · 제목 위에 넣지 않음). 작업 카드 상태(`ai-handoff-current.md`)도 「마침」 또는 「한도로 멈춤」으로 바꿉니다.

공용 흐름에 남길 만한 변경이면 `wiki/_handoff/worklog.md`의 **첫 `## ` 블록 앞**에 아래 형식으로 짧게(5줄 안팎) 기록합니다. worklog 전체를 읽을 필요는 없습니다.

```markdown
## YYYY-MM-DD 핸드오프 — Codex
- 한 일: ...
- 결과/산출물: ...
- 미완·블로커: ...
- 다음 단계 제안: ...
- 챗으로 가져갈 질문: ...
```
