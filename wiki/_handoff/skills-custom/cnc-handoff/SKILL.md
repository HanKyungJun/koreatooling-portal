---
name: "cnc-handoff"
description: "[핸드오프] 세션 시작 시 위키 현황 요약, 종료 시 worklog 블록 생성. \"세션 시작\", \"핸드오프 읽어줘\", \"어디까지 했어\", \"마무리해줘\" 로 실행합니다."
---

# cnc-wiki 핸드오프 스킬

이 스킬은 cnc-wiki 세션 컨텍스트를 빠르게 복원하고 마무리하는 데 사용합니다.
2026-11-03 개정: 기본은 **가볍게 시작**(CLAUDE.md §0-A). 큰 파일 전체 읽기는 「전체」를 요청할 때만. 종료 블록은 Claude 가 worklog 에 직접 쓴다.
2026-11-03 2차 개정: P0 · P1 판정을 `(P0,` · `(P1,` 로 바꿈(내린 항목 · 양식 줄 제외) · 메모 목록 잘림 확인 추가(CLAUDE.md §15-4).
2026-11-18 개정: 종료 블록에 「검토:」 줄 추가 — AI 역할 검토표 4주 측정 자료(decisions 2026-11-18 (2)).
2026-11-16 개정: 커밋 안내를 `git add -A` → **바꾼 파일만 경로로** add · 실명 검사는 pre-commit 훅이 대신(수동 `--check` 단계 삭제) · 끝에 push 확인 줄.

## 핸드오프 파일 경로

```
C:\Users\TOOLKOREA\Desktop\cnc-wiki\wiki\_handoff\
├── context.md      — 프로젝트 큰 그림·범위·용어 (전체 모드에서만)
├── decisions.md    — 확정 결정 로그 (최신이 맨 위)
├── tasks.md        — 작업 큐 (P0~P3 우선순위)
└── worklog.md      — 세션별 핸드오프 블록 (최신이 맨 위)
```

파일은 device_bash 로 PC 에서 직접 읽습니다(`$HOME/mnt/cnc-wiki/wiki/_handoff`). 클라우드로 올리지 않습니다.

## 모드 판단

- **세션 시작 · 가볍게(기본)**: "읽어줘", "시작", "어디까지", "상태", "handoff", "핸드오프", "요약" 또는 키워드 없음
- **세션 시작 · 전체**: "전체", "현황 전체", "처음부터", "오래 쉬었" 가 들어 있을 때
- **세션 종료**: "종료", "마무리", "끝", "worklog 써줘", "핸드오프 작성", "commit 준비"

---

## 세션 시작 — 가볍게 (기본)

아래 3가지만 읽습니다(합계 3,000자 이하가 기준 — CLAUDE.md §15-4). CLAUDE.md · 프로젝트 메모는 자동으로 들어오므로 따로 읽지 않습니다. 세 가지는 python 한 번으로 같이 읽습니다.

1. `worklog.md` 맨 위 `## ` 블록 1개
2. `tasks.md` 「진행 중」에서 `- [ ]` 로 시작하고 **`(P0,` 또는 `(P1,`** 이 든 **제목 줄만** — 우선순위 바로 뒤 쉼표로 판정한다. `(P1 → P3` 처럼 내린 항목과 `[제목] (P0/P1/P2/P3)` 양식 줄은 빠진다. 「→ 가 든 줄 빼기」 방식은 쓰지 않는다(제목 안에 → 가 있는 진짜 P1 이 빠짐, 2026-11-03 실측)
3. `decisions.md` 맨 위 `## ` 제목 3줄만

추가 확인 1가지: 세션에 들어온 프로젝트 메모 목록(MEMORY.md)에 잘림 표시(`[truncated]`)가 보이면 현황 요약 맨 끝에 「메모 목록이 잘려 있음 — 정리 필요(§15-4)」 한 줄을 붙입니다.

출력(15줄 이내):

```
## cnc-wiki 현황 (YYYY-MM-DD KST)
지난 세션: [worklog 맨 위 블록 — 미완·다음 단계 2~3줄]
P0: [항목 또는 없음]
P1: [제목만, 최대 8개]
최근 결정: ① … ② … ③ …
지금 할 것 제안: [1~2개]
```

특정 항목을 이어서 할 때만 그 항목의 전문 · 관련 decisions 를 추가로 읽습니다. `sources.md` 는 출처 ID 를 찾을 때만 읽습니다.

## 세션 시작 — 전체

순서대로 읽고 위와 같은 형식으로 요약하되 「프로젝트 개요」(context.md 1~2줄)와 P2~P3 요약을 덧붙입니다.

1. `context.md` 2. `decisions.md` 최신 5건 3. `tasks.md` P0·P1 전문 4. `worklog.md` 맨 위 블록

파일을 읽은 후 모순이 보이면 요약 전에 먼저 알립니다. 파일이 없거나 읽기 실패면 「파일 없음 — 직접 확인 필요」로 표시합니다.

---

## 세션 종료

이번 세션에서 한 일을 바탕으로 핸드오프 블록을 **직접** `wiki/_handoff/worklog.md` 맨 위에 추가합니다(붙여넣기용 블록만 주지 않음). 파일은 python read-modify-write 로 UTF-8(BOM 유지) 그대로 씁니다.

블록은 **항목당 1~2줄, 전체 10줄 안팎**(맨 위 블록 1,000자 이하). 긴 경위는 위키 페이지 · tasks 항목에 두고 블록에는 경로만.

```markdown
## YYYY-MM-DD (#N) 핸드오프 — Cowork

- 한 일: …
- 결과/산출물: … (경로)
- 미완·블로커: … 또는 없음
- 다음 단계 제안: …
- 검토: R? 주 · R? — 통과 n · 확인 필요 n · 통과 뒤 지적 n (작은 일만 했으면 「작은 일(G1)」)
- 챗으로 가져갈 질문: … 또는 없음
```

「완료」라고 쓰기 전에 해당 파일을 다시 읽어 실제로 반영됐는지 확인합니다(CLAUDE.md §15-2).

결정 기록은 CLAUDE.md §5-A 기준(조건 · 안전 · 대외 · 돈 · 규칙)에 해당할 때만 decisions.md 맨 위에 직접 추가합니다. 나머지는 worklog 한 줄로 충분합니다.

### 커밋 안내

1. **add 할 파일 목록**을 만든다 — 이번 세션에서 직접 만들거나 고친 파일만. 놓친 것이 없는지 device_bash 읽기 명령으로 대조한다:

   ```bash
   cd $HOME/mnt/cnc-wiki
   git --no-optional-locks -c core.quotepath=false diff --ignore-cr-at-eol --numstat | awk '$1!=0||$2!=0'
   git --no-optional-locks -c core.quotepath=false status --short --untracked-files=all | grep '^??'
   ```

   - 첫 줄은 줄바꿈(CRLF)만 다른 파일을 뺀 실제 변경, 둘째 줄은 새 파일이다. device_bash 의 `git status` `M` 목록은 CRLF 때문에 부풀어 보이므로 근거로 쓰지 않는다.
   - 이번 세션이 바꾸지 않은 파일(다른 세션 · 자동화 · 한경준님 수정)이 보이면 목록에 넣지 않고 「세션 밖 변경 N개 — 이번 커밋에서 뺌」 한 줄로 알린다.
   - `.bak_*` · `outputs/` 는 .gitignore 대상이라 넣지 않는다.

2. 커밋 메시지는 한글이므로 `outputs/commit_msg_YYYYMMDD.txt` 를 python 으로 UTF-8(BOM 없음)으로 만든다.

3. 아래 명령을 안내한다. 경로는 저장소 기준 상대 경로 · 큰따옴표로 감싼다. 명령 상자에는 주석을 넣지 않는다.

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
git add -- "wiki/_handoff/worklog.md" "바꾼/파일/경로.md"
git commit -F outputs\commit_msg_YYYYMMDD.txt
git push
git log --oneline origin/main..HEAD
```

- 마지막 줄 출력이 비어 있으면 push 완료라고 함께 안내한다.
- `git add -A` · `git add .` 는 쓰지 않는다 — 세션 밖 변경 · CRLF 노이즈가 같이 들어간다.
- 거래처 실명 검사는 **pre-commit 훅이 커밋할 때 자동으로** 한다(`.githooks/pre-commit` → `anonymize_public.py --check`, decisions 2026-11-16 (1)). 커밋 전에 따로 돌리라고 안내하지 않는다. 커밋이 막히면 출력에 나온 파일을 고친 뒤 다시 커밋하고, `--no-verify` 로 건너뛰라고 안내하지 않는다.

> ⚠️ Cowork bash(device_bash)에서 git 쓰기(add · commit · push · mv)는 하지 않습니다. `--dry-run` 도 인덱스 락을 남깁니다. 읽기 명령만 `git --no-optional-locks` 로 쓰고, 쓰기는 반드시 한경준님 PowerShell에서 실행합니다.

---

## 주의사항

- `raw/` 폴더는 절대 수정하지 않습니다 (읽기 전용).
- 단가·금액은 위키에 기록하지 않습니다.
- 파일 간 내용이 충돌하면 `decisions.md` 최신 항목이 우선합니다.
- 수치에는 항상 단위를 표기합니다 (RPM, mm/min, m/s, Ra μm 등).
- 시각은 항상 KST. device_bash 의 ls·stat 시각은 UTC 라 +9h.
- 주제가 바뀌면 「여기서 새 세션을 권합니다」라고 한 줄로 알립니다(CLAUDE.md §0-C).