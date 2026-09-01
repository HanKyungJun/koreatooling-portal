# 핸드오프 시스템 (cnc-wiki)

챗(claude.ai), Cowork, Claude Code 세 환경 사이의 컨텍스트 단절을 메우기 위한 공유 노트 폴더입니다.

## 파일 역할

| 파일 | 역할 | 주로 누가 갱신하나 |
|------|------|--------------------|
| `context.md` | 프로젝트 큰 그림 (정의·배경·범위·용어). 자주 안 바뀜. | 사용자 (챗이 갱신 제안 가능) |
| `decisions.md` | 누적 의사결정. **최신이 맨 위.** | 챗에서 결정 → 사용자가 붙여넣음 / Code·Cowork도 발견 사항 추가 |
| `worklog.md` | 실제 실행 기록 + 핸드오프 블록. **최신이 맨 위.** | Cowork·Code가 매 세션마다 |
| `memory.md` | 사용자 선호·협업 방식·장기 주의사항. 반복적으로 기억할 내용만 기록 | 챗·Code·Cowork |
| `chat-project-instructions.md` | claude.ai 챗 프로젝트에 붙여넣을 커스텀 인스트럭션 | 사용자 (1회 셋업) |
| `sources.md` | 외부 출처(ISO 표준·논문·매뉴얼·카탈로그) 마스터 인덱스. 위키 본문에서 ID로 참조. | 챗·Cowork·Codex가 새 출처 인용 시 즉시 등록 |
| `tasks.md` | 작업 큐 (P0~P3 우선순위 + 체크박스). "할 일"은 여기, "한 일"은 worklog. | 챗·Cowork·Codex 모두 |

루트의 `CLAUDE.md`는 Claude Code와 Cowork가 자동으로 읽는 규약 파일입니다 (이 폴더 밖, 위키 루트에 위치).

## 워크플로우

```
[챗에서 토론·설계]
       │ "Cowork에 넘길 핸드오프 정리해줘"
       ▼
[챗이 decisions 블록 + 실행 작업 목록 출력]
       │ 사용자가 decisions 블록을 _handoff/decisions.md 맨 위에 붙여넣음
       ▼
[Cowork/Code에서 실행]
       │ 종료 시 worklog.md 맨 위에 핸드오프 블록 추가
       ▼
[챗으로 돌아갈 때 worklog 핸드오프 블록을 챗에 첨부]
       ▼
[챗에서 다음 토론 시작]
       │ ...
```

## 첫 사용 시 할 일 (체크리스트)

- [ ] `context.md` 채우기 — 한 줄 정의, 배경, 범위, 핵심 용어
- [ ] `decisions.md`에 "현재까지의 핵심 결정" 몇 개 정리 (회사 표준, 작업 원칙 등)
- [ ] claude.ai에서 `cnc-wiki` 프로젝트 만들고 `chat-project-instructions.md`의 점선 사이 텍스트를 Custom Instructions에 붙여넣기
- [ ] 그 프로젝트 Knowledge에 `context.md`, `decisions.md` 업로드
- [ ] Cowork에서 이 폴더를 시작 폴더로 자주 사용 (이번처럼 폴더 선택)
- [ ] Claude Code 사용 시 이 폴더에서 실행 — 루트 `CLAUDE.md`가 자동 적용됨

## Git 운용 (2026-05-08 추가)

`cnc-wiki/`는 로컬 git 저장소입니다 (외부 push 없음, 로컬에만 보존). 모든 변경 이력이 commit으로 추적됩니다. 자세한 결정 배경은 decisions.md의 2026-05-08 항목 참조.

### 핵심 규칙

- **편집은 어디서든**: Cowork(Edit/Write 도구), Code(IDE), Chat(사용자 복붙) 모두 가능
- **commit은 항상 PowerShell**: Cowork bash는 Windows 마운트 폴더에서 git 운용 불가 (실측 확인됨)
- **commit 트리거**: 세션 종료 / decisions 추가 / sources 추가 / 위키 본문 변경 / "정리하고 가자" 싶은 시점

### 표준 commit (PowerShell 복붙용)

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
git add .
git commit -m "[작업 요약을 여기에]"
```

`[작업 요약]` 부분은 매 세션 종료 시 Claude/Codex가 미리 작성해서 제공.

**좋은 commit 메시지 예시**:
- `"sources에 ISO 3685 추가 + sus304.md 가공조건 갱신"`
- `"decisions: 절삭조건 인용 형식 표준화 (ADR-006)"`
- `"재연마 일지 2026 데이터로 KPI 페이지 갱신"`

### 자주 쓰는 git 명령 (PowerShell)

```powershell
git status                              # 어떤 변경이 commit 안 됐는지
git log --oneline -10                   # 최근 10개 commit
git diff wiki/_handoff/decisions.md     # 특정 파일 변경 내역
git log -p wiki/_handoff/decisions.md   # 특정 파일 전체 이력
git checkout wiki/_handoff/STATE.md     # 직전 commit 상태로 복원
```

### 트러블슈팅

| 증상 | 해결 |
|---|---|
| Cowork bash에서 `git` 명령 안 먹힘 | 정상. PowerShell에서 실행. |
| decisions.md 항목을 실수로 삭제 | `git log -p wiki/_handoff/decisions.md`로 commit 찾고 `git checkout [해시] -- 파일경로` |
| `.git/` 크기가 커짐 | `git gc --aggressive --prune=now` |
| 잘못된 파일을 commit함 | `git reset HEAD~1`로 마지막 commit 취소 (단, 변경 자체는 유지) |

## 자주 하는 실수

- 챗에서 결정해놓고 `decisions.md`에 안 옮김 → 다음 Cowork 세션에서 같은 토론 반복
- `worklog.md`에 핸드오프 블록 안 남기고 종료 → 챗으로 돌아갈 때 컨텍스트 끊김
- `context.md`를 너무 자주 손댐 → 큰 그림이 흔들림. 큰 변경은 `decisions.md`에 누적된 후 분기적으로만 반영

## 관계 정리: `log.md` vs `worklog.md`

- 루트의 `log.md`: 위키 자체의 변경 로그 (어떤 페이지를 추가/수정했는지)
- `_handoff/worklog.md`: 챗·Cowork·Code 사이의 작업 핸드오프용 (왜 했고 다음에 뭘 할지)

둘은 목적이 달라 분리해서 운영합니다.

## 코멘트/피드백 작성 원칙

기존 내용을 바로 수정하면 Claude, Codex, 사용자 의견이 섞여 출처를 알기 어려워집니다.
검토 의견이나 질문은 되도록 원문 아래에 다음 형식으로 추가합니다.

```markdown
> [작성자: Codex / 날짜: YYYY-MM-DD]
> 질문: ...
> 의견: ...
> 근거: ...
```
