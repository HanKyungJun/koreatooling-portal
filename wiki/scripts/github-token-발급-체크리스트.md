---
type: runbook
category: "인증·배포 — GitHub fine-grained PAT 발급·교체 절차"
tags: [GitHub, PAT, 토큰, 인증, 403, generate.py, 배포, 보안]
sources:
  - "[INT-TOKEN-403-2026]"
updated: 2026-08-28
status: "검증됨"
---

# GitHub 토큰 발급·교체 체크리스트

> 🔴 **이 문서가 없어서 같은 403 오류가 세 번 반복됐습니다** — 2026-07-07 · 2026-07-08 · **2026-08-28**.
> 2026-07-08 결정문이 *"향후 fine-grained PAT 재발급 시 체크리스트화할 필요"* 라고 적었으나 작성되지 않았고,
> 51일 뒤 동일 증상이 재발했습니다. 토큰을 바꿀 때는 **반드시 이 문서를 열고** 진행하세요.

## 0. 이 토큰이 쓰이는 곳

```
.env (GITHUB_TOKEN)  →  generate.py 726행이 매 실행마다
                        https://{TOKEN}@github.com/{USER}/{REPO}.git 로 remote URL 조립 → push
```

- **토큰의 정본은 `.env`** 입니다. `git remote set-url` 로 URL만 고쳐도 `generate.py` 가 다시 덮어씁니다.
- `.env` 는 저장소 루트(`C:\Users\TOOLKOREA\Desktop\cnc-wiki\.env`), **UTF-8(BOM 없음)·LF**, `GITHUB_TOKEN` 은 16행.
- 점으로 시작해 탐색기에서 **숨김** 처리됩니다 (`보기 → 표시 → 숨긴 항목`).
- `.gitignore:64` 로 추적 제외돼 있습니다. ⚠️ 2026-06-10 에 한 번 커밋된 이력이 있으므로 **절대 추적시키지 마세요.**

---

## 0-1. 현재 사용 중인 토큰 (2026-08-28 기준)

| 항목 | 값 |
|---|---|
| 이름 | **`cnc-wiki-2026-08`** |
| 발급일 | 2026-08-28 |
| **만료일** | 🔴 **2026-11-26 (목)** |
| 권한 | Metadata `Read-only` + **Contents `Read and write`** |
| 대상 저장소 | `koreatooling-portal` |

> 🔴 **만료되면 17:00 자동화가 조용히 멈춥니다.** `generate.py` 는 push 가 실패해도 로컬 파일은 정상 생성하므로
> **며칠 지나서야 "포털이 왜 안 바뀌지?" 하고 알아채게 됩니다.** 만료 1주일 전(**2026-11-19경**)에 갱신하세요.
>
> ⚠️ 무기한 토큰(이전 `ToolKorea`)을 90일로 바꾼 것은 옳은 선택이지만, 그 대가로 **갱신을 기억해야 하는 의무**가 생겼습니다.
> 갱신 시 이 문서 §1 부터 다시 따라가고, **이 표의 값도 함께 갱신**하세요.

---

## 1. 새 토큰 발급 — 3단계를 **모두** 해야 합니다

**https://github.com/settings/personal-access-tokens** → `Generate new token`

> ⚠️ **핵심 원칙: `Repository access`(저장소 선택)와 `Permissions`(권한 종류·수준)는 완전히 별개 설정입니다.**
> 저장소만 고르고 권한을 안 주면 **읽기는 되고 push만 403** 으로 거부됩니다. 이게 3회 반복된 원인입니다.

| # | 항목 | 설정값 | 놓치기 쉬운 이유 |
|---|---|---|---|
| ① | **Token name** | `cnc-wiki-YYYY-MM` | — |
| ② | **Expiration** | **90 days** 권장 | 기본이 무기한인 경우가 있고, GitHub이 ⚠️ 경고를 띄웁니다 |
| ③ | **Repository access** | **Only select repositories** → `koreatooling-portal` | 🔴 **`Public repositories` 를 고르면 읽기 전용**입니다 — 저장소가 Public이라 맞아 보이지만 push가 안 됩니다 |
| ④ | **Permissions → Repository permissions → `Contents`** | **`Read and write`** | 🔴 **가장 자주 틀리는 곳.** 아래 §1-1 참조 |
| ⑤ | **Update / Generate token** 버튼 | 반드시 클릭 | 안 누르면 반영 안 됩니다 |

`Metadata: Read-only` 는 자동으로 붙습니다. **그 외 권한은 필요 없습니다.**

### 1-1. 🔴 `Contents` 를 찾는 법 — 함정 2개

**함정 A — 목록이 알파벳순이라 스크롤을 내리면 지나칩니다.**
`Add permissions` 드롭다운은 A→Z 순입니다. `Contents` 는 **C** 라서 위쪽에 있는데,
스크롤을 내리다 보면 **`Repository security advisories`**(R) 같은 다른 항목을 고르기 쉽습니다.
**→ 드롭다운 상단 검색창에 `Contents` 를 입력하세요.** (2026-08-28 실제 오류: `Repository security advisories` 를 체크함)

**함정 B — 체크만 하면 기본이 `Read-only` 입니다.**
`Contents` 를 체크해 목록에 추가한 뒤, **그 항목 옆의 `Access` 드롭다운을 `Read and write` 로 바꿔야** 합니다.
체크만 하고 넘어가면 여전히 403 입니다. (2026-07-08 실제 오류)

**최종 상태가 이래야 합니다:**

```
Repositories 1 (또는 2)
├─ Metadata    Required    Read-only
└─ Contents               Read and write   ← 이게 없으면 push 불가
```

---

## 2. `.env` 교체 — 인코딩 주의

⚠️ **`Add-Content` · `Out-File` · 메모장 금지.** Windows PowerShell 5.1 의 기본 인코딩이 **CP949** 라
한글 주석이 깨지고, git·python 이 파일을 못 읽게 됩니다. (2026-08-28 `.gitignore` 에서 실제 발생)

**방법 A — PowerShell (.NET 명시, 토큰이 히스토리에 안 남음)**

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
$t = Read-Host "새 토큰 붙여넣기"
$p = "$PWD\.env"
$c = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)
$c = [Regex]::Replace($c, '(?m)^GITHUB_TOKEN=.*$', "GITHUB_TOKEN=$t")
[IO.File]::WriteAllText($p, $c, (New-Object Text.UTF8Encoding $false))
```

**방법 B — 에디터**: VS Code(`code .env`) 또는 Notepad++ 로 16행 값만 교체하고 **UTF-8 저장**.

> 💡 **토큰 권한만 고치는 경우에는 `.env` 를 건드릴 필요가 없습니다.** 기존 토큰을 편집하면 값은 그대로입니다.

---

## 3. 검증 — 부작용 없는 순서

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki

# ① 쓰기 권한 확인 (실제로 아무것도 올라가지 않음)
git push --dry-run origin main
#   성공 예: b0ad167..76a2afc  main -> main
#   실패 예: remote: Permission to ... denied  →  §1-1 로 돌아가 Contents 확인

# ② 실제 push
git push

# ③ 자동화 전체 경로 확인
python generate.py
#   [git] push: ...s (code=0)  +  ✅ 업로드 완료  가 나와야 정상
```

### ⚠️ 진단 시 하지 말 것 — `GET /repos/{owner}/{repo}` 의 `permissions` 는 믿을 수 없습니다

이 API가 돌려주는 `pull/push/admin` 은 **토큰의 권한이 아니라 계정의 저장소 역할**입니다.
저장소 주인이면 토큰에 쓰기 권한이 없어도 **`push=True`** 로 나옵니다.
2026-08-28 에 이 값을 근거로 "권한 정상"이라 오판할 뻔했습니다.

**단, 이 호출로 얻을 수 있는 정보는 있습니다:**

| 결과 | 의미 |
|---|---|
| HTTP 401 | 토큰 자체가 무효 (붙여넣기 실수·삭제됨) |
| HTTP 404 | `Repository access` 에 이 저장소가 없음 |
| HTTP 200 인데 `git push` 는 403 | **읽기만 됨 → `Contents` 권한 문제 확정** |

**쓰기 권한의 진짜 판정 도구는 `git push --dry-run` 입니다.**

---

## 4. 마무리

- [ ] 새 토큰으로 `git push --dry-run` 성공 확인
- [ ] `python generate.py` 로 자동화 경로 확인
- [ ] **그다음에** 옛 토큰 `Delete` (순서를 바꾸면 17:00 자동화가 실패합니다)
- [ ] Classic 탭(`Tokens (classic)`)에도 불필요한 토큰이 없는지 확인
- [ ] 만료일을 캘린더에 등록 (90일 뒤 갱신 필요)

---

## 5. 과거 사고 이력

| 날짜 | 증상 | 근본 원인 |
|---|---|---|
| 2026-06-10 | `.env` 가 커밋됨 (`GITHUB_TOKEN=ghp_…`) | `.gitignore` 미설정. 같은 날 추적 제거했으나 **blob 은 히스토리에 잔존**. 해당 classic 토큰은 이후 삭제 확인(2026-08-28) |
| 2026-07-07 | 16:00 자동화 17분 멈춤 후 실패 | git-credential-manager 가 비대화형 세션에서 프롬프트 시도 → `GIT_TERMINAL_PROMPT=0`·`GCM_INTERACTIVE=never` 추가로 해결. 같은 날 run.log 에 **토큰 평문 노출** 발견 → 마스킹 함수 추가(`generate.py` 688~693행) |
| 2026-07-08 | push 403 | fine-grained PAT 의 **Contents 가 Read-only** — 저장소만 선택하고 권한 미설정 |
| **2026-08-28** | push 403 (**재발**) | 권한 목록에서 `Contents` 대신 **`Repository security advisories`** 를 체크. 체크리스트가 없어 동일 함정 반복 |

> ✅ **2026-08-28 종결** — `Contents: Read and write` 설정 후 `git push --dry-run` 성공(`b0ad167..76a2afc main -> main`) → 실제 push 완료. 옛 `ToolKorea` 토큰(무기한) 삭제 확인. **본 체크리스트를 이때 신설**했으므로, 다음 갱신부터는 §1-1 의 함정 2개를 먼저 확인하면 재발하지 않습니다.

## 관련 페이지

- [[scripts/generate]] — 이 토큰을 사용하는 배포 스크립트
- [[_handoff/tasks]] — 미해결 과제
