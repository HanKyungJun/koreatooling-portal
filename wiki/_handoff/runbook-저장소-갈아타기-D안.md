---
type: reference
tags: [저장소, git, 공개노출, 포털, 실행절차, D안]
updated: 2026-09-01
---

# 저장소 갈아타기 실행 절차 (D안)

> `raw/`·`wiki/_private/` 의 **과거 커밋 공개 노출**을 처리하기 위한 실행 절차서입니다.
> 결정 근거는 [[_handoff/decisions|decisions.md]] **2026-08-31** 항목을 먼저 읽으세요.
> ⚠️ **모든 git 명령은 PowerShell에서 실행합니다.** Cowork(리눅스 마운트) 쪽 판독은 CRLF로 오염되고 `.git/index.lock` 을 남깁니다(decisions.md 2026-08-28 (2)·2026-08-28).

---

## 0. 요약

| 항목 | 내용 |
|---|---|
| 목적 | 과거 커밋에 남은 거래처 단가·사내 원본을 **비공개로 격리**하고, 포털은 새 공개 저장소로 이전 |
| 실행 시점 | **2026-09 초 평일 오전** (16:00 배치 전) |
| 예상 소요 | 30분~1시간 (①백업 클론 제외 — 별도 소요) |
| 코드 수정 | **0줄** (저장소 이름을 유지하는 경우) |
| 되돌리기 | 가능 — 원본이 archive 저장소 + 백업 클론 + `.git-archive-backup` 3중으로 남음 |
| **실행 결과** | **✅ 2026-09-01 완료** — 새 저장소 `eaf8e6f` · 481파일 / 53 MB(옛 940.1 MB, −94%) · 검증 4건 통과. 상세는 decisions.md **2026-09-01 (2)** |

### 결과 상태

```
koreatooling-portal-archive   (Private)  ← 406커밋 전체 이력 · raw · _private
koreatooling-portal           (Public)   ← 현재 파일 532개 · 커밋 1개 · Pages 서빙
```

포털 주소 `https://HanKyungJun.github.io/koreatooling-portal/` **불변**.

---

---

## 0-A. 🔴 선결 조치 — `.claude/worktrees/` 정리 (2026-09-01 신설)

> **이 절차를 건너뛰면 ⑤단계에서 `raw/` 사본 1.39 GB가 새 공개 저장소에 딸려 들어갈 수 있습니다.**

### 문제

`.claude/worktrees/` (4개 · **1.4 GB / 2,313 파일**, 그중 **`raw/` 사본 1,654 파일 / 1.39 GB**)가
**`.gitignore` 가 아니라 `.git/info/exclude` 로만** 제외돼 있습니다 [신뢰도: 실측 검증 — 2026-09-01].

```
.git/info/exclude:7:  .claude/worktrees/
.gitignore         :  (해당 규칙 없음)
```

⑤단계는 `.git` 을 rename하고 `git init` 하는데, **`git init` 은 `.git/info/exclude` 를 새로 만든다** —
즉 **이 제외 규칙이 소멸**한다. 그 상태의 `git add -A` 는:

- 각 worktree에 `.git` **파일(gitlink)** 이 있어 git이 embedded repository로 취급 → 엉뚱한 gitlink 4개 유입 또는 경고
- 그 gitlink가 가리키는 `.git/worktrees/...` 는 rename으로 **이미 사라진 상태** → 동작 불확실
- 하필 그 안에 **`raw/` 사본 1.39 GB** 가 있다 → **D안의 목적과 정면으로 어긋난다**

### 조치 (PowerShell)

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki

git status                 # 미커밋 변경 없어야 함
git worktree list

git worktree remove --force .claude/worktrees/gallant-cohen-5aead9
git worktree remove --force .claude/worktrees/hardcore-hermann-b67cf1
git worktree remove --force .claude/worktrees/interesting-bell-80d5fb
git worktree remove --force .claude/worktrees/jolly-bohr-6d6ceb
git worktree prune

Get-ChildItem .claude\worktrees -ErrorAction SilentlyContinue
#   남아 있으면: Remove-Item .claude\worktrees -Recurse -Force

# 제외 규칙을 .gitignore 로 이관 (git init 후에도 살아남도록)
Add-Content -Path .gitignore -Value "`n# Claude Code worktree 잔재 (2026-09-01, .git/info/exclude 에서 이관)`n.claude/worktrees/" -Encoding UTF8

git status --short
git add .gitignore
git commit -m "gitignore: .claude/worktrees 이관 (D안 git init 대비)"
git push
```

⚠️ `Add-Content` 기본 인코딩은 **CP949** 다 — 한글 주석이 깨지므로 `-Encoding UTF8` 필수(2026-08-28 사고 기록).

### 부수 효과

- **디스크 약 1.4 GB 확보** — 실행 시점 여유 15 GB / 94% 사용이었다. 백업 미러를 뜨기 전에 비우는 편이 안전하다.
- 런북 §6-2(worktree 사본 정리)와 tasks.md P3 항목이 **함께 종결**된다.

### ★ 일반화 — `git init` 으로 이력을 갈아끼울 때의 점검 항목

`.git/` 안에만 있는 설정은 **전부 소멸**한다. ⑤단계 전에 확인할 것:

| 항목 | 확인 명령 | 소멸 여부 |
|---|---|---|
| `.git/info/exclude` | `cat .git/info/exclude` | **소멸** — `.gitignore` 로 이관 필요 |
| `git config` (로컬) | `git config --local --list` | **소멸** — user.name/email은 `generate.py` 가 매번 재설정하므로 무해 |
| hooks | `ls .git/hooks/*` (`.sample` 제외) | **소멸** |
| worktree 등록 | `git worktree list` | **소멸** — 먼저 제거할 것 |

## 1. 실행 전 준비

### 1-1. 백업 (⚠️ 이것 없이는 진행하지 않습니다)

```powershell
cd C:\Users\TOOLKOREA\Desktop
git clone --mirror https://github.com/HanKyungJun/koreatooling-portal.git koreatooling-portal-backup.git
```

- 원격 실제 크기 미확인이라 소요 시간은 **예측 불가** — 여유를 두고 시작하세요.
- 완료 후 크기 확인: `(Get-ChildItem koreatooling-portal-backup.git -Recurse | Measure-Object Length -Sum).Sum / 1GB`
- 이 백업은 **롤백의 최후 수단**입니다. 절차가 전부 끝나고 1~2주 정상 동작을 확인한 뒤 정리하세요.

### 1-2. 사전 점검

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
git status                                   # 미커밋 변경 없어야 함
git log --oneline origin/main..HEAD          # 미푸시 0건이어야 함
git log --oneline -1                         # 마지막 커밋 SHA 기록해 둘 것
```

미푸시 커밋이 있으면 **먼저 push**하고 시작합니다.

### 1-3. 자동화 정지

```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "*CNC*" } | Select-Object TaskName, State
Get-ScheduledTask | Where-Object { $_.TaskName -like "*CNC*" } | Disable-ScheduledTask
```

⚠️ 교체 도중 16:00/17:00 배치가 돌면 **옛 저장소에 push**되어 상태가 꼬입니다.

🔴 **`Disable-ScheduledTask` 는 관리자 권한이 필요합니다** — 일반 창에서는 *"액세스가 거부되었습니다"* (HRESULT 0x80070005). 시작 메뉴 → PowerShell **우클릭 → 관리자 권한으로 실행** (2026-09-01 실측).

**✅ 2026-09-01 실측 — cnc-wiki 관련 예약 작업 6개** (런북 §5 「전체 목록 확인 필요」 해소):

| 작업명 | 트리거 | 동작 | git push | 정지 |
|---|---|---|---|---|
| `CNC_Daily_Report` | 주간 16:00 | `daily_and_upload.bat` | **함** | **필수** |
| `CNC_Daily_Report_OnBoot` | 부팅 시 | 당일 보고서 없으면 위 bat | **함** | **필수** |
| `cnc-wiki Drive 동기화` | 매일 16:30 | `scripts/sync_to_gdrive.py` | 안 함 | 필수(`*CNC*` 필터에 걸림) |
| `ANCA_Scraper_Daily` | 매일 13:00 | `scripts/anca-monitor/run_scraper.ps1` | **안 함** | 불필요 |
| `DailyDlvAlert` | 매일 09:00 | `erp/daily_dlv_alert.py` | **안 함** | 불필요 |
| `DailyZeroPriceAlert` | 매일 09:00 | `erp/zero_price_alert.py` | **안 함** | 불필요 |

⚠️ **`*CNC*` 필터는 뒤 3개를 놓친다.** 이들은 cnc-wiki 폴더에 파일을 쓰지만 **git 명령을 전혀 호출하지 않으므로**(4개 스크립트 전수 grep: `git`·`push`·`generate.py`·`remote set-url`·`subprocess`·`os.system` **매칭 0건**, 2026-09-01 실측) 교체 중 돌아도 무해하다 — 최악의 경우 `git add -A` 이후 파일이 바뀌는 정도이며 나중에 커밋하면 된다. **정지 대상은 push하는 작업뿐이다.**

넓게 조회하려면:

```powershell
Get-ScheduledTask | Where-Object { $_.Actions.Execute -like "*cnc-wiki*" -or $_.Actions.Arguments -like "*cnc-wiki*" } |
  Select-Object TaskName, State
```

---

## 2. 실행 절차

### ① 기존 저장소 Pages 끄기

GitHub 웹 → `koreatooling-portal` → **Settings → Pages → Source: None**

> 새 저장소에서 켜기 전에 꺼야 충돌이 없습니다.

### ② 기존 저장소 이름 변경

**Settings → General → Repository name** → `koreatooling-portal-archive` → Rename

### ③ archive 저장소 Private 전환

**Settings → General → Danger Zone → Change repository visibility → Make private**

**확인:** 로그아웃(또는 시크릿 창)에서 `https://github.com/HanKyungJun/koreatooling-portal-archive` 가 **404**여야 합니다.

### ④ 새 공개 저장소 생성

GitHub → New repository
- 이름: **`koreatooling-portal`** (원래 이름)
- **Public**
- README·.gitignore·license **전부 체크 해제** (빈 저장소로)

> 🔴 **여기가 확인 필요 지점입니다.** 이름이 거부되면(rename 리다이렉트가 점유) **중단하고 재판단**하세요.
> 대안: 다른 이름으로 생성 → `.env` 에 `GITHUB_REPO=<새이름>` 추가 → 위키 내 포털 URL 인용 4건 정정
> (`wiki/_handoff/decisions-archive/2026-08.md`, `wiki/_handoff/worklog-archive/2026-06.md`, 그리고 추적되지 않는 `run.log`·`generate.log`)

### ⑤ 로컬 `.git` 갈아끼우기

파일은 그대로 두고 **이력만** 새로 시작합니다. `.gitignore` 가 이미 있으므로 `raw/`·`wiki/_private/`·`.env` 는 자동 제외됩니다.

> 🔴 **2026-09-01 개정 — 백업은 반드시 작업 트리 「밖」으로 옮긴다.**
> 옛 절차는 `Rename-Item .git .git-archive-backup` 으로 **작업 트리 안에** 남기라고 했는데, 그 순간 그것은 `.git` 이 아닌 **평범한 폴더**가 되어 `git add -A` 가 loose object 7,918개(1.35 GB)를 **전부 스테이징**한다. 2026-09-01 실행에서 **8,598 파일이 스테이징됐고 커밋 직전에 잡혔다.** 그 object 안에는 **`raw/`·`wiki/_private/` 과거 blob이 그대로** 있어, 커밋됐다면 **D안의 목적이 정반대로 무너졌다.**

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki

# 5-1. 기존 .git 을 작업 트리 「밖」으로 보존 (삭제 아님)
Move-Item .git ..\cnc-wiki-git-archive-backup
Test-Path ..\cnc-wiki-git-archive-backup    # True
Test-Path .\.git                            # False

# 5-2. 새 이력 시작
git init
git branch -M main

# 5-3. 커밋 신원 (새 .git 이라 로컬 config 가 비어 있음)
git config user.name  "HanKyungJun"
git config user.email "hzn2001@toolkorea.co.kr"
git config core.quotepath false

git add -A
```

**🔴 커밋 전 3단 검증 — 순서를 지킬 것**

```powershell
# ⓑ 먼저 개수. 패턴 검사보다 이게 먼저다.
(git status --short | Measure-Object -Line).Lines
#   → 480 내외. 2,000 을 넘으면 즉시 중단 (백업·worktree 유입)

# ⓐ 유입 검사 — .env.example 외에는 아무것도 나오지 않아야 정상
git status --short | Select-String -Pattern "raw/|_private|archive-backup|\.git/|worktrees|__pycache__"

# ⓒ 최상위 폴더 분포 — 낯선 항목이 있는지 눈으로
git status --short | ForEach-Object { ($_ -split '\s+')[1] -split '/' | Select-Object -First 1 } |
  Group-Object | Sort-Object Count -Descending | Select-Object -First 15 Count, Name

# ⓓ 옛 저장소와 파일 목록 대조 — 무엇이 빠지는지 전수 확인
git -C ..\koreatooling-portal-backup.git config core.quotepath false
git -C ..\koreatooling-portal-backup.git ls-tree -r --name-only main | Sort-Object | Set-Content -Encoding UTF8 $env:TEMP\old.txt
git ls-files | Sort-Object | Set-Content -Encoding UTF8 $env:TEMP\new.txt
Compare-Object (Get-Content $env:TEMP\old.txt -Encoding UTF8) (Get-Content $env:TEMP\new.txt -Encoding UTF8)
#   '<=' = 빠진 것(빌드산출물·캐시면 정상, 포털 서빙 파일이면 중단)
#   '=>' = 새로 들어온 것(0건이어야 정상)
```

⚠️ **개수를 먼저 보는 이유**: 2026-09-01 실행에서 ⓐ 패턴에 `.git-archive-backup` 이 빠져 있어 **검사가 통과처럼 보였다.** 유입을 실제로 잡아낸 것은 **8,598이라는 숫자**였다.

📌 **2026-09-01 실측 참고값** — 옛 저장소 추적 534 → 새 저장소 **481**. 차이 53건은 `git init` 으로 `.gitignore` 가 **기존 추적 파일에도 처음 적용**된 결과이며, 전부 빌드 산출물·캐시·`_to_delete`·개인 로컬 설정이었다. **포털 서빙 파일과 위키 콘텐츠는 하나도 빠지지 않았다.**

```powershell
git commit -m "init: 포털 저장소 재구성 (D안) - 이력은 koreatooling-portal-archive 참조"
```

### ⑥ 새 저장소로 push

```powershell
git remote add origin https://github.com/HanKyungJun/koreatooling-portal.git
git push -u origin main
```

> 인증은 기존 PAT를 그대로 사용합니다. `generate.py` 가 실행 시마다 `remote set-url` 로 토큰 URL을 다시 넣으므로, 여기서는 수동 인증으로 충분합니다.

### ⑥-1. 🔴 fine-grained PAT 의 저장소 범위 갱신 (2026-09-01 신설 — 필수)

> **이름이 같아도 새 저장소는 「다른 저장소」다.** fine-grained PAT는 **저장소 ID 단위**로 권한을 주므로, 새로 만든 `koreatooling-portal` 에는 **권한이 따라오지 않는다.** 토큰은 여전히 옛 저장소(현 archive)만 가리킨다.

**증상** (2026-09-01 실측):

```
[git] commit: 5.9s (code=0)
[git] push: 0.8s (code=128)
❌ 푸시 실패: remote: Permission to HanKyungJun/koreatooling-portal.git denied to HanKyungJun.
fatal: ... The requested URL returned error: 403
```

**⚠️ 수동 push가 되는 것에 속지 말 것.** ⑥의 수동 `git push` 는 **Windows 자격 증명 관리자**를 타서 성공한다. 실패하는 것은 **`generate.py` 가 `remote set-url` 로 박아 넣는 토큰 URL 경로뿐**이다. 그래서 ⑥이 성공해도 ⑧에서 처음 드러난다. 게다가 `generate.py` 가 origin을 토큰 URL로 바꿔놓으므로 **그 뒤의 수동 push까지 403이 된다.**

**조치**: GitHub → Settings → Developer settings → **Personal access tokens → Fine-grained tokens** → 해당 토큰 →
**Repository access** 에 **`koreatooling-portal` 추가** → **Contents: Read and write** 확인 → Update.
✅ **토큰 값은 그대로이므로 `.env` 수정 불필요.** archive는 push할 일이 없으니 목록에서 빼도 된다.

**복구(응급)**: 토큰 범위를 고치기 전이라면 아래로 자격 증명 관리자 경로를 되살려 수동 push할 수 있다.

```powershell
git remote set-url origin https://github.com/HanKyungJun/koreatooling-portal.git
git push
```

⚠️ 단 `generate.py` 는 실행마다 토큰 URL로 되돌리므로 **응급 조치일 뿐**이다. 16:00 배치 전에 토큰 범위를 반드시 고칠 것.

💡 **파생 논점** — 자격 증명 관리자 경로는 저장소가 바뀌어도 통했고 토큰 URL 경로만 막혔다. `generate.py` 의 토큰 재기입을 걷어내고 credential helper에 맡기면 **평문 상주(tasks.md P3)와 이 범위 문제가 동시에 사라진다.**

### ⑦ 새 저장소 Pages 켜기

**Settings → Pages → Source: Deploy from a branch → `main` / `/ (root)`** → Save

- 루트에 `.nojekyll` 이 있으므로 Jekyll 미사용으로 그대로 서빙됩니다.
- 반영까지 1~2분 걸립니다.

### ⑧ 자동화 재개 + 시험 실행

```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "*CNC*" } | Enable-ScheduledTask

cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
python generate.py
```

`wiki/reports/daily/generate.log` 에서 확인:
- `git add` 실패 **0건**
- `commit code=0` 또는 정상적인 「변경 없음」
- `push code=0`
- ⚠️ `✅ 업로드 완료` 만 보고 판단하지 말 것 — **커밋 code와 함께** 확인합니다(decisions.md 2026-08-28).

### ⑨ 잔재 object 정리 (2026-09-01 신설)

⑤에서 스테이징을 한 번이라도 취소했다면 그때 해시된 object가 **도달 불가 상태로 남는다**(2026-09-01: unreachable loose **8,590개**).

```powershell
git prune --expire=now
git count-objects -vH
```

📌 2026-09-01 실측 결과: loose **0** · garbage **0** · in-pack 527 · **53.17 MiB**. 작업 전 로컬 `.git` 이 1.35 GB였으므로 사실상 전량 정리됐다.

---

## 3. 실행 후 검증 체크리스트

| # | 확인 항목 | 방법 | 기대값 |
|---|---|---|---|
| 1 | 포털 정상 | `https://HanKyungJun.github.io/koreatooling-portal/` | **200** · 「코리아툴링 생산팀 포털」 |
| 2 | `_private` 차단 | `.../wiki/_private/소재-단가-이력.md` | **404** |
| 3 | `raw` 차단 | `.../raw/CNC 정보/...` | **404** |
| 4 | archive 비공개 | 시크릿 창에서 `github.com/HanKyungJun/koreatooling-portal-archive` | **404** |
| 5 | 새 저장소 내용 | `git ls-files \| Measure-Object -Line` | **532 내외**, `raw/`·`_private` **0건** |
| 6 | 자동화 | 다음 16:00 배치 후 `run.log`·`generate.log` | 오류 0건 · `push code=0` |
| 7 | 대시보드 갱신 | 포털 상단 갱신 시각 | 당일로 갱신됨 |

검증용 PowerShell:

```powershell
$base = "https://HanKyungJun.github.io/koreatooling-portal"
foreach ($p in @("/", "/wiki/_private/%EC%86%8C%EC%9E%AC-%EB%8B%A8%EA%B0%80-%EC%9D%B4%EB%A0%A5.md")) {
  try   { $r = Invoke-WebRequest "$base$p" -UseBasicParsing; "$p -> $($r.StatusCode)" }
  catch { "$p -> $($_.Exception.Response.StatusCode.value__)" }
}
```

---

## 4. 롤백

| 중단 시점 | 되돌리는 법 |
|---|---|
| ①~④ 사이 | archive 저장소를 원래 이름으로 rename → Public 전환 → Pages 재설정 |
| ⑤ 이후 | `Remove-Item .git -Recurse -Force` → `Move-Item ..\cnc-wiki-git-archive-backup .git` → 위와 동일 |
| 최악의 경우 | `koreatooling-portal-backup.git` (mirror)에서 재클론 후 push |

⚠️ **⑤에서 `.git` 을 삭제하지 말고 rename** 하는 이유가 이것입니다. 정상 동작 확인 전까지 `.git-archive-backup` 을 지우지 마세요.

---

## 5. 알려진 미확인 사항

| 항목 | 상태 |
|---|---|
| 저장소 이름 재사용 가능 여부(④) | **확인 필요** — rename 리다이렉트 해제 동작 미실측 |
| 원격 저장소 실제 크기 | **✅ 2026-09-01 확정 — 940.1 MB** (API 조회 성공). 로컬 `.git` 1.35 GB보다 작은 것은 로컬이 loose object 상태이기 때문 [실측 검증] |
| Task Scheduler 관련 작업 전체 목록 | **✅ 2026-09-01 확정 — 6개**(정지 필요 3 / 무해 3). §1-3 표 참조. `Disable-ScheduledTask` 는 **관리자 권한 필요** |
| 노출 기간 중 실제 열람 여부 | **확인 불가** — 접근 로그 없음. 추정하지 않는다 |
| `.git/info/exclude` 소멸 문제 | **✅ 2026-09-01 해소** — §0-A로 선결 처리 |

---

## 6. 함께 정리할 것 (이번 작업과 별개, 같은 날 처리 권장)

1. **`git gc --prune=now`** — `.git` loose object 7,918개 / 1.35 GiB, `tmp_obj_*` garbage 52건 잔존 (2026-08-31 실측). ⑤에서 `.git` 을 새로 만들면 자동 해소되나, `.git-archive-backup` 정리 전 참고.
2. ~~**`.claude/worktrees/` 옛 `generate.py` 사본 3건**~~ → **§0-A로 승격·선결 처리**(실측 결과 **4건 · 1.4 GB**, 그중 `raw/` 사본 1.39 GB). 원래 표기 3건은 실측 4건으로 정정. 옛 `generate.py` 사본 3건 — `hardcore-hermann-b67cf1` · `interesting-bell-80d5fb` · `jolly-bohr-6d6ceb`. 저장소 이름이 하드코딩 기본값으로 들어 있어 혼동 소지.
3. **PAT 평문 상주** — `origin` URL에 fine-grained PAT가 평문으로 박혀 있음(`generate.py:726` 이 매 실행 재기입). 커밋되지는 않으나 credential helper 방식 전환 검토. → tasks.md 별도 항목.

---

작성: 2026-08-31 (Cowork) / 근거: decisions.md 2026-08-31
개정: **2026-09-01** — ⑤단계 전면 개정(백업을 작업 트리 밖으로 · 커밋 전 3단 검증), §1-3 실측 반영(예약 작업 6개 표·관리자 권한), §5 미확인 2건 해소(원격 940.1 MB · 작업 목록), §0-A 선결 조치 신설(`.git/info/exclude` 소멸 함정), §5·§6 갱신
