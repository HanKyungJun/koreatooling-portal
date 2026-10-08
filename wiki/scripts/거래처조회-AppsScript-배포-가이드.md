---
type: runbook
category: "배포 — 거래처 발주·재고 조회(워크숍 범위 ③) Apps Script 웹 앱"
tags: [AppsScript, GAS, 구글시트, 배포, 거래처조회, B2B, 워크숍, 보안]
sources:
  - "[VEN-GOOGLE-APPSSCRIPT-WEBAPP]"
updated: 2026-10-08
status: "검증됨(사내) — 배포·업로드·현황판 조회 확인 2026-10-08 · 거래처 공개 전"
---

# 거래처 조회 Apps Script 배포 가이드

> 거래처가 접속 코드로 자기 발주·진행 현황을 보는 화면(워크숍 범위 ③)을 **처음 배포하고, 이후 운영(거래처 추가·코드 수정·토큰 교체)** 하는 절차.
> 결정 근거: decisions.md **2026-10-08 (2)·(3)** · 설계: [[projects/워크숍-업무자동화-B2B사이트-2026-10]] §③

## 개요

```
경준님 PC (07:50 · 16:00 정규 실행)
  ERP 수주 → erp/snapshot/jae_detail_latest.csv
        │  python erp/customer_portal_export.py --upload
        │  (허용 열만 · .env 의 CUSTOMER_PORTAL_CUSTS 거래처만 · 업로드 토큰)
        ▼
Apps Script 웹 앱 「코리아툴링 거래처조회」  ←── scripts/customer_portal_gas.gs
        │  비공개 구글 시트: codes · data · meta · access_log
        ▲
        │  POST {action:'view', code}
고객 브라우저 — 조회 화면 order-status.html (접속 코드 입력 → 그 거래처 행만)
```

| 구성 요소 | 위치 | 비밀값 보관 |
|---|---|---|
| 내보내기 스크립트 | `erp/customer_portal_export.py` | `.env` (URL · 업로드 토큰 · 허용 거래처) |
| Apps Script 코드 | `scripts/customer_portal_gas.gs` (저장소 사본) → 콘솔에 붙여넣기 | 스크립트 속성 (`SHEET_ID` · `UPLOAD_TOKEN`) |
| 데이터 시트 | 구글 드라이브 (공유하지 않음) | 접속 코드는 `codes` 탭에만 |
| 조회 화면 | `scripts/customer_portal/order-status.html` (시범 중) → 확정 후 `dist/` | 없음 — 화면에 데이터 없음 |

🔴 **이 저장소는 Public 이다.** 시트 ID · 업로드 토큰 · 접속 코드를 코드·위키·커밋 메시지에 적지 않는다.

---

## 1. 처음 배포 (한 번만)

### 준비

- 구글 계정: **hzn2001@toolkorea.co.kr** 로 로그인된 브라우저 (다른 계정이 기본이면 그 계정에 만들어진다)
- 업로드 토큰: PowerShell 에서 생성 → 메모해 둔다

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 1-1. 데이터 시트 만들기

1. [sheets.new](https://sheets.new) → 이름 예: `거래처조회_데이터`
2. **공유하지 않는다** (Apps Script 가 「나」 권한으로 읽고 쓴다)
3. 주소창 `https://docs.google.com/spreadsheets/d/【여기】/edit` 의 【여기】 = **시트 ID** → 복사
4. 탭은 만들지 않아도 된다 — 첫 업로드 때 `data`·`meta`·`codes` 가, 첫 조회 때 `access_log` 가 자동 생성된다

### 1-2. Apps Script 프로젝트 만들기

1. [script.new](https://script.new) → 왼쪽 위 「제목 없는 프로젝트」 → **`코리아툴링 거래처조회`**
2. 기본 코드(`function myFunction…`)를 **전부 지우고** `scripts/customer_portal_gas.gs` 내용을 통째로 붙여넣기 → 저장(Ctrl+S)
3. ⚠️ 기존 「코리아툴링 공개폼」·「절삭조건 계산」 프로젝트에 붙여넣지 않는다 — 이름과 용도가 엇갈린 전례가 있다(project memory 「Apps Script 프로젝트 정체」)

### 1-3. 스크립트 속성 등록

왼쪽 ⚙️ **프로젝트 설정** → 맨 아래 **스크립트 속성 추가**

| 속성 | 값 |
|---|---|
| `SHEET_ID` | 1-1 에서 복사한 시트 ID |
| `UPLOAD_TOKEN` | 준비 단계에서 만든 토큰 |

🔴 둘 중 하나라도 없으면 업로드·조회가 모두 `not_configured` 로 거부된다(닫힌 기본값 — 현장기록 v2 와 다름).

### 1-4. 웹 앱으로 배포

1. 오른쪽 위 **배포 → 새 배포** → 톱니 → 유형 **웹 앱**
2. 설명: `v1 2026-10-08`
3. **다음 사용자로 실행: 나** (hzn2001@toolkorea.co.kr)
4. **액세스 권한: 모든 사용자** — 고객이 구글 로그인 없이 접속 코드로 조회하므로 필요
5. 배포 → 권한 승인 창: 계정 선택 → 「고급」 → 「(안전하지 않음)으로 이동」 → 허용 (본인이 만든 스크립트라 뜨는 경고)
6. **웹 앱 URL** (`https://script.google.com/macros/s/…/exec`) 복사
7. 확인: 브라우저로 URL 을 열면 `{"status":"ok","service":"customer-portal","note":"POST only"}` 가 보여야 한다 — 주소만 열어서는 데이터가 나오지 않는 게 정상

### 1-5. `.env` 등록 (경준님 PC)

`C:\Users\TOOLKOREA\Desktop\cnc-wiki\.env` 를 **VS Code** 로 열어 아래 3줄 추가(형식은 `.env.example` 참고).

```
CUSTOMER_PORTAL_GAS_URL=<1-4 의 웹 앱 URL>
CUSTOMER_PORTAL_UPLOAD_TOKEN=<스크립트 속성 UPLOAD_TOKEN 과 같은 값>
CUSTOMER_PORTAL_CUSTS=<시범 거래처 코드, 쉼표 구분>
```

⚠️ PowerShell `Add-Content`·메모장으로 고치지 않는다 — CP949 로 저장돼 한글 주석이 깨진다(2026-08-28 사고).

### 1-6. 첫 업로드

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
python erp\customer_portal_export.py
python erp\customer_portal_export.py --upload
```

- 첫 줄(드라이런): `업로드 허용 N곳 [...]` 에 시범 거래처가 보이는지
- 둘째 줄: `✅ 업로드 완료: 거래처 N곳 · M행` → 시트에 `data`·`meta`·`codes` 탭이 생긴다

### 1-7. 접속 코드 발급

```powershell
python erp\customer_portal_export.py --new-code
```

나온 12자 코드를 시트 **`codes` 탭**에 한 줄로 입력:

| 거래처코드 | 거래처명 | 접속코드 | 사용(Y/N) | 메모 |
|---|---|---|---|---|
| (ERP 거래처 코드) | (거래처명) | (12자 코드) | `Y` | 발급일 · 전달 담당 |

- 거래처코드는 `CUSTOMER_PORTAL_CUSTS` 에 넣은 값과 같아야 한다
- 코드는 대소문자 구분 없음. 0/O · 1/I/L 처럼 헷갈리는 글자는 쓰지 않는다

### 1-7b. 사내 검토 (2026-10-08 추가 — 거래처 공개 전 단계)

조회 화면은 처음에 **사내 현황판 직원 전용 구역**에만 올라간다(`generate.py` 의 `INTERNAL_ONLY` — GitHub Pages 로 안 나감). 원본은 `scripts/customer_portal/order-status.html`.

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
python erp\customer_portal_export.py --ping
python generate.py --local
python erp\customer_portal_export.py --codes-tsv
```

1. `--ping` → `✅ 웹 앱 정상` 이어야 한다
2. `generate.py --local` → 로그에 `→ 거래처 조회 업로드: N곳 · M행` · 현황판 폴더에 `order-status.html` 생성
3. `--codes-tsv` 출력(거래처마다 한 줄, 탭 구분)을 **한 번만** 실행해 시트 `codes` 탭 **A2** 에 붙여넣기 — 실행할 때마다 새 코드가 나온다
4. 현황판 `index.html` → 🔒 직원 전용 → 📦 「거래처 조회 (사내 검토)」 → 코드 입력

### 1-8. 조회 시험 → 공개

1. 조회 화면 `order-status.html` 의 `GAS_URL` 을 실제 URL 로 교체 (Cowork 가 함)
2. 화면에서 1-7 코드로 조회 → 그 거래처 행만 나오는지 · 틀린 코드는 「접속 코드가 맞지 않습니다」인지
3. 시트 `access_log` 에 `ok` / `denied` 가 기록되는지 (코드 원문은 남지 않는 게 정상)
4. 확인 후 `dist/` 로 옮기고 포털 메인 카드 추가 · 정규 실행에 업로드 연결 (Cowork)

---

## 2. 운영

### 2-1. 거래처 추가

1. `.env` 의 `CUSTOMER_PORTAL_CUSTS` 에 거래처 코드 추가 (예: `105703,103445`)
2. `python erp\customer_portal_export.py --upload`
3. `--new-code` 로 코드 발급 → `codes` 탭에 한 줄 추가 (`Y`)

### 2-2. 거래처 중지 · 코드 교체

- 중지: `codes` 탭의 `사용(Y/N)` 을 `N` → 즉시 조회 불가 (재배포 불필요)
- 교체(코드 유출 의심): `--new-code` 로 새 코드 → 같은 줄의 접속코드만 바꿈 → 거래처에 새 코드 전달
- 데이터에서도 빼려면 `.env` 의 `CUSTOMER_PORTAL_CUSTS` 에서 지우고 다시 `--upload` (업로드는 `data` 탭을 통째로 교체한다)

### 2-3. Apps Script 코드를 고쳤을 때

1. 저장소의 `scripts/customer_portal_gas.gs` 를 먼저 고친다 (사본이 정본과 어긋나지 않게)
2. 콘솔에 붙여넣고 저장
3. **배포 → 배포 관리 → ✏️ 편집 → 버전: 새 버전 → 배포** — 🟢 **URL 이 그대로**라 `.env`·조회 화면을 안 고쳐도 된다
4. ⚠️ 「새 배포」를 누르면 **URL 이 바뀐다** → `.env` 와 조회 화면을 모두 고쳐야 하고, 옛 배포는 「보관처리」해야 옛 URL 이 죽는다

### 2-4. 업로드 토큰 교체

1. 새 토큰 생성(1. 준비의 명령)
2. 스크립트 속성 `UPLOAD_TOKEN` 값 교체 → 저장 (재배포 불필요)
3. `.env` 의 `CUSTOMER_PORTAL_UPLOAD_TOKEN` 같은 값으로 교체
4. `--upload` 1회로 확인

---

## 3. 문제 해결

| 증상 · 응답 | 원인 | 조치 |
|---|---|---|
| 업로드 `not_configured` | 스크립트 속성 `SHEET_ID`·`UPLOAD_TOKEN` 미등록 | 1-3 |
| 업로드 결과가 `ok` 인데 행 수가 `None` (2026-10-08 실제 발생) | 업로드가 doPost 가 아니라 **doGet** 에 닿음 — 「조용한 성공」. 같은 시각 `--ping` 은 doPost 에 닿아 `not_configured` | 수정: `rows` 없는 `ok` 는 실패로 판정 · 리다이렉트를 직접 따라가며 경로 출력(`경로: POST 302 → GET …`). 재발하면 그 경로 줄을 확인. 🔄 **2026-10-08 추가 관찰**: 스크립트 속성 저장 직후 첫 업로드가 doGet 응답 → `--probe` 로 본문 크기(1~218 KB) 원인 아님 확인 → **같은 명령 재실행은 성공(293행)**. 원인 미확정 [추정값 — 속성 반영 지연 등]. 대응: doGet 응답이면 5초 뒤 1회 재시도 |
| PowerShell `Invoke-RestMethod -Method Post` 결과가 `POST only` | POST 가 리다이렉트 과정에서 GET 으로 처리됨 — PowerShell 쪽 동작 [실측 2026-10-08] | 확인은 `python erp\customer_portal_export.py --ping` 으로(실제 업로드와 같은 경로) |
| 업로드 `forbidden` | `.env` 토큰 ≠ 스크립트 속성 토큰 | 2-4 의 2·3 을 같은 값으로 |
| 업로드 「응답이 JSON 이 아님」 | URL 오타 · 배포 액세스 권한이 「모든 사용자」가 아님 · 권한 승인 안 됨 | 1-4 다시 확인 |
| 업로드 `error` + 메시지 | 시트 ID 오류 · 시트 삭제 | 시트 ID 재확인 |
| 「CUSTOMER_PORTAL_CUSTS 가 비어 있어」 | 허용 거래처 미등록(닫힌 기본값) | 1-5 |
| 조회 「접속 코드가 맞지 않습니다」 | 코드 오타 · `사용`이 `N` · 거래처코드가 `data` 에 없음 | `codes` 탭 · `CUSTOMER_PORTAL_CUSTS` 확인 |
| 조회 「잠시 후 다시 시도」(`busy`) | 10분 안에 틀린 코드 30회 초과 → 10분간 조회 중지 | 10분 대기. 반복되면 `access_log` 의 `denied` 급증 확인 |
| 조회 결과가 어제 값 | PC 정규 실행 · 업로드가 안 돌았음 | 화면 「기준 시각」 · 시트 `meta` · `generate.log` 확인 |

## 4. 보안 원칙

- 화면으로 나가는 열은 `customer_portal_export.py` 의 `ALLOWED` 목록뿐 — 직원명·사내 메모·배송지·단가는 나가지 않는다. 스냅샷에 새 열이 생겨도 목록에 없으면 나가지 않는다
- 데이터는 공개 저장소(GitHub Pages)에 올리지 않는다 — 암호화해도 git 이력에 영구히 남는다
- 접속 코드는 조회 기록에 원문을 남기지 않는다 · 틀린 코드와 사용 중지 코드를 화면에서 구분하지 않는다
- 웹 앱 URL 은 공개돼도 된다 — 업로드는 토큰, 조회는 접속 코드로 막는다

## 변경 이력

| 날짜 | 내용 | 적용 |
|---|---|---|
| 2026-10-08 | 신규 작성 (v1 코드 기준) | 🔄 첫 배포 전 |
| 2026-10-08 | 사내 조회 성공(현황판 file:// 포함) · 화면 폭 1280 px · 기준 시각 표기 수정 · 저장소 `.gs` 에 `meta` 텍스트 저장(⬜ 콘솔 새 버전 배포 필요) | ✅ 사내 검토 |
| 2026-10-08 | 웹 앱 배포(GET 확인) · 1-7b 사내 검토 단계 · `--ping`·`--codes-tsv` · PowerShell POST 함정 추가 | 🔄 사내 검토 |

## 관련 페이지

- [[projects/워크숍-업무자동화-B2B사이트-2026-10]] — §③ 설계 · 시제품 검증 결과
- [[scripts/github-token-발급-체크리스트]] — 토큰을 `.env` 에 넣는 같은 유형의 절차
- [[generate|generate.py 상세]] — 정규 실행(07:50 · 16:00) · 포털 배포
