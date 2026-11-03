---
type: script
category: "자동화 스크립트 인덱스"
total_scripts: 17
language: "Python 3.x"
tags: [scripts, 자동화, 인덱스, Python, pandas, openpyxl, Google API, Flask]
sources:
  - "실제 코드: scripts/*.py, run.py, watcher.py, app.py, generate.py, setup_sheets.py"
  - "환경변수: .env / .env.example"
  - "SECURITY_NOTES.md (민감 정보 처리)"
updated: 2026-05-13
status: "초안 — 17개 스크립트 카탈로그. 상세 페이지는 핵심 스크립트만 향후 분리."
---

# Scripts 인덱스 — 자동화 코드 카탈로그

> cnc-wiki 자동화 스크립트 **17개**의 목적·입출력·사용법 요약. 핵심 스크립트(daily_report, generate, pdf_search 등)는 향후 별도 상세 페이지 작성 후보.
>
> 본 페이지의 목적:
> 1. "이 자동화 어떤 스크립트가 담당하지?" 즉시 답
> 2. 환경 재구성·인수인계 시 의존 관계 파악
> 3. 보안·유지보수 우선순위 도출

---

## 1. 실행 환경·의존성 공통

- **언어**: Python 3.x (3.10+ 권장)
- **필수 패키지** (자주 쓰는 것):
  - `pandas`, `openpyxl`, `xlrd` — 엑셀 처리
  - `pdfplumber` — PDF 텍스트 추출
  - `google-api-python-client`, `google-auth-oauthlib` — Google Drive/Sheets
  - `flask` — 웹 서버
  - `watchdog` — 파일 변경 감시
  - `python-dotenv` — 환경변수 로드 (2026-05-11 보안 정리 후)
  - `requests` — HTTP 호출
- **민감 정보**: `client_secret_*.json`, `token*.json`, `.env` → 모두 `.gitignore` 보호 (SECURITY_NOTES.md 참조)
- **루트 디렉터리**: 모든 스크립트는 `C:\Users\TOOLKOREA\Desktop\cnc-wiki\` 기준 상대경로 사용

---

## 2. 카테고리별 스크립트

### 2.1 카탈로그·문서 검색 (1개)

#### `scripts/pdf_search.py` (124줄)
- **목적**: PDF 텍스트 고속 검색. 첫 실행 시 페이지별 텍스트 추출 후 `.cache.json` 저장 → 이후 검색은 수초 이내.
- **입력**: PDF 파일 경로 + 키워드
- **출력**: 일치 페이지 번호 + 페이지 본문 (stdout)
- **사용 예**:
  ```powershell
  python scripts/pdf_search.py raw/Catalog/JJ.pdf "D6 4날"
  python scripts/pdf_search.py raw/Catalog/COGO.pdf "AlCrN" --pages 216 218
  python scripts/pdf_search.py raw/Catalog/JJ.pdf "키워드" --rebuild   # 캐시 재생성
  ```
- **의존성**: pdfplumber, ProcessPoolExecutor (병렬 추출)
- **관련 페이지**: [[jj-카탈로그]], [[cogo-카탈로그]]

---

### 2.2 일일보고 (2개)

#### `scripts/daily_report.py` (399줄)
- **목적**: 재연마 작업일지(`raw/출하현황/재연마 작업일지(YYYY)/재연마_월간생산일지 (M월).xls`)에서 그날 데이터 추출 → 일일보고 xlsx 생성.
- **입력**: 날짜 (선택, 미지정 시 오늘)
- **출력**: `wiki/reports/daily/YYYY-MM-DD_일일보고.xlsx` (오늘 출력물이 이 패턴)
- **사용 예**:
  ```powershell
  python scripts/daily_report.py             # 오늘
  python scripts/daily_report.py 2026-05-12  # 특정일
  ```
- **포맷 특징**: 맑은 고딕 폰트, FAST GRIND 연파랑 / GX7 연초록 / 합계 연노랑 색상 코딩
- **관련**: `app.py` 대시보드와 동일 데이터 소스
- **상세 페이지**: [[scripts/daily-report]] — 함수 설명·트러블슈팅·실행 흐름 포함

#### `scripts/upload_to_sheets.py` (439줄)
- **목적**: `daily_report.py` 생성 일일보고 → Google Sheets 자동 업로드.
- **입력**: 날짜 (선택)
- **출력**: Google Sheets 2개 시트 갱신
  - "오늘의 보고" — 매일 덮어쓰기 (최신만 유지)
  - "월별 누적" — 날짜별 행 추가/갱신
- **사용 예**: `python scripts/upload_to_sheets.py [YYYY-MM-DD]`
- **의존성**: `daily_report.py`의 데이터 추출 함수 재사용 (`from daily_report import ...`)
- **민감**: `token_sheets.json` + `FORM_SHEET_ID` (.env) 필요

---

### 2.3 출하현황·KPI 분석 (4개)

#### `scripts/make_excel.py` (211줄)
- **목적**: 단년도 출하현황 분석 → 납품처별 월별 분석 xlsx 생성.
- **입출력**: `raw/출하현황/` → `wiki/comparisons/출하현황_납품처별_월별분석_YYYY.xlsx`
- **스타일**: 헤더 짙은 파랑(`1F497D`), TOP5 노랑 강조, TOP10 연노랑

#### `scripts/make_excel_history.py` (226줄)
- **목적**: 다년도 출하현황 이력 비교 → 연도별 출하 추이 xlsx.
- **출력**: 다년도 비교 표·차트 xlsx

#### `scripts/make_kpi_excel.py` (448줄)
- **목적**: 단년도 KPI(설비가동률·작업효율·양품률) 종합 분석 → xlsx + 차트.
- **출력**: `wiki/comparisons/YYYY_KPI_설비가동율_작업효율_양품율.xlsx`
- **특징**: BarChart, LineChart 자동 생성. 가정(assumption) 셀 노란 강조.

#### `scripts/make_kpi_multiyear.py` (493줄)
- **목적**: 다년도 KPI 통합 분석.
- **출력**: `wiki/comparisons/KPI_설비가동율_작업효율_양품율_YYYY1-YYYY2.xlsx`

> 위 4개 스크립트의 출력물은 모두 `wiki/comparisons/` 에 저장되며, 한경준님이 직접 분석하시거나 `app.py` 대시보드가 읽음.

---

### 2.4 데이터 추출 (1개)

#### `scripts/make_tool_pages.py` (204줄)
- **목적**: 재연마 작업일지(2022~2026 전체)에서 형상별(볼/평/드릴/스퀘어/면취/코너R/NC) 데이터 수집 → 위키 페이지 생성 후보.
- **활용**: [[연삭-조건-목록]] 및 형상별 7개 페이지([[연삭-조건-볼]] 등) 자동 생성에 사용됐을 가능성.
- **분류 로직** (스크립트 내):
  ```python
  if '볼' in s: return '볼'
  if '드릴' in s: return '드릴'
  if 'nc' in s: return 'NC'
  if any(x in s for x in ['코너', 'r0.', 'r1', ...]): return '코너R'
  ...
  ```

---

### 2.5 Google Drive 동기화 (4개)

#### `scripts/list_gdrive.py` (104줄)
- **목적**: Google Drive의 `cnc-wiki 분석자료` 폴더 내용 리스트.
- **민감**: `token.json` 필요.

#### `scripts/browse_gdrive.py` (105줄)
- **목적**: 특정 폴더 브라우즈. 읽기 전용(`drive.readonly` scope).
- **민감**: `token_readonly.json` 필요.

#### `scripts/upload_to_gdrive.py` (90줄)
- **목적**: 핵심 분석 xlsx 3개를 Drive `cnc-wiki 분석자료` 폴더에 업로드.
- **업로드 대상** (코드 내 하드코딩):
  - `출하현황_납품처별_월별분석_2025.xlsx`
  - `2025_KPI_설비가동율_작업효율_양품율.xlsx`
  - `KPI_설비가동율_작업효율_양품율_2022-2025.xlsx`
- **민감**: `token.json`

#### `scripts/sync_to_gdrive.py` (136줄)
- **목적**: `wiki/` 폴더 전체를 Google Drive `cnc-wiki` 폴더에 동기화. 변경된 파일만 업로드.
- **민감**: `token.json`

> Google Drive 관련 4개 스크립트는 OAuth 파일명이 코드에 하드코딩되어 있음 → SECURITY_NOTES.md "scripts/* 의 OAuth 파일명 분리" 후속 작업 대상 (tasks.md 백로그).

---

### 2.6 웹 서버 / 정적 생성 (4개)

#### `generate.py` (루트, 1138줄)
- **목적**: GitHub Pages 배포용 정적 HTML 생성 (재연마 의뢰 접수, 불량 신고, 진행 문의, 소모품 구매, 직원 대시보드).
- **입력**: `raw/출하현황/`, `wiki/comparisons/*.xlsx`
- **출력**: `dist/` 안에 6개 HTML (index, request, defect, inquiry, supplies, dashboard)
- **사용 예**:
  ```powershell
  python generate.py            # 생성 + GitHub Pages 자동 푸시
  python generate.py --local    # 로컬 파일만 생성 (푸시 안 함)
  ```
- **민감**: `GITHUB_TOKEN` (.env), `STAFF_PASS` (.env)
- **2026-05-11 보안 정리**: 환경변수화 완료. `--local` 모드 외엔 `GITHUB_TOKEN` 필수 체크.
- **상세 페이지**: [[scripts/generate]] — 함수 설명·환경변수·배포 흐름·트러블슈팅 포함

#### `app.py` (루트, 398줄)
- **목적**: Flask 웹 서버. 로컬 대시보드 + Google Drive/Sheets API 프록시.
- **포트**: 5000
- **주요 라우트**:
  - `/` — index.html 또는 templates/index.html
  - `/dashboard` — 대시보드
  - `/api/dashboard-data` — 출하현황 + 일일보고 데이터
  - `/api/form-submissions` — Google Sheets 폼 제출 조회 (`FORM_SHEET_ID` .env)
  - `/api/sync` — `wiki/` → Google Drive 동기화
  - `/api/list`, `/api/browse` — Drive 탐색
- **민감**: `client_secret_*.json`, `token*.json`, `FORM_SHEET_ID`
- **상세 페이지**: [[scripts/app]] — 라우트 상세·Drive 유틸리티·자동화 체인 전체 그림·트러블슈팅 포함

#### `run.py` (루트, 9줄)
- **목적**: `app.py` 실행 + 2초 후 브라우저 자동 오픈 (`http://localhost:5000`).
- **사용 예**: `python run.py`

#### `watcher.py` (루트, 85줄)
- **목적**: `wiki/comparisons/`, `raw/출하현황/` 폴더 변경 감시 → 변경 발생 시 `generate.py --local` 자동 실행.
- **디바운스**: 마지막 이벤트 후 3초 대기 (연속 저장 통합)
- **사용 예**: 백그라운드 실행 (`python watcher.py`)
- **의존성**: `watchdog`

---

### 2.7 초기 설정 (1개)

#### `setup_sheets.py` (루트, 108줄)
- **목적**: Google Sheets API OAuth 토큰 1회 발급. `token_sheets.json` 생성.
- **실행 시점**: 최초 1회 또는 토큰 만료·재발급 시
- **결과**: 이후 `upload_to_sheets.py` 등이 자동으로 토큰 사용

---

## 3. 의존 그래프

```
[raw/출하현황/*.xls]
      │
      ▼
  daily_report.py ──→ wiki/reports/daily/*.xlsx
      │                       │
      │                       └─→ upload_to_sheets.py ─→ Google Sheets
      │
      ▼
  make_excel*.py / make_kpi_excel*.py ──→ wiki/comparisons/*.xlsx
                                                │
                                                ├─→ generate.py ──→ dist/*.html ──→ GitHub Pages
                                                │
                                                └─→ app.py (Flask) ──→ 브라우저 대시보드
                                                                          │
                                                                          ├─ /api/dashboard-data
                                                                          └─ /api/form-submissions (Google Sheets 폼)

[wiki/]
      │
      └─→ sync_to_gdrive.py ──→ Google Drive cnc-wiki/

[watcher.py] (백그라운드) ──→ 변경 감지 ──→ generate.py --local 자동 실행
```

---

## 4. 일상 사용 시나리오

### 4.1 매일 아침 — 일일보고 발행

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
python scripts/daily_report.py
python scripts/upload_to_sheets.py    # Sheets에도 반영
```

### 4.2 월말 — 출하·KPI 재계산

```powershell
python scripts/make_excel.py          # 출하현황 분석
python scripts/make_kpi_excel.py      # KPI 분석
```

### 4.3 외부 배포 (GitHub Pages)

```powershell
python generate.py     # 생성 + 푸시
```

### 4.4 로컬 대시보드

```powershell
python run.py          # Flask 서버 + 브라우저 자동 오픈
```

### 4.5 백그라운드 자동화

```powershell
start python watcher.py    # 폴더 변경 감지 → 자동 generate.py
```

---

## 5. 유지보수·확장 우선순위

| 우선 | 작업 | 근거 |
|---|---|---|
| P1 | scripts/* OAuth 파일명 → .env 분리 | SECURITY_NOTES.md 미완 항목 |
| P2 | 핵심 스크립트 상세 페이지 (`scripts/daily_report.md`, `scripts/generate.md`, `scripts/pdf_search.md`) | 인수인계·문서 표준화 |
| P2 | requirements.txt 생성 (의존성 명시) | 환경 재구성 편의 |
| P3 | sync_to_gdrive 점진 백업 정책 명문화 | 데이터 거버넌스 |
| P3 | Weibull 분석 스크립트 신규 (공구 수명 데이터 누적 후) | [[공구-수명-관리]] §8 |

---

## 6. 관련 페이지

- [[jj-카탈로그]], [[cogo-카탈로그]] — `pdf_search.py` 활용
- [[연삭-조건-목록]], [[연삭-조건-볼]] 등 7개 형상별 페이지 — `make_tool_pages.py` 자동 생성 후보
- [[anca-cnc-tool-grinder]] — 재연마 일지 → `daily_report.py` 입력
- (예정) 각 스크립트 상세 페이지: `daily_report.md`, `generate.md`, `pdf_search.md` 등

---

## 7. 참고 문헌

### 라이브러리 공식 문서
- pandas — https://pandas.pydata.org/docs/
- openpyxl — https://openpyxl.readthedocs.io/
- pdfplumber — https://github.com/jsvine/pdfplumber
- Google API Python Client — https://github.com/googleapis/google-api-python-client
- Flask — https://flask.palletsprojects.com/
- watchdog — https://python-watchdog.readthedocs.io/

### 코드 스타일·관행
- PEP 8 — Python 코드 스타일 가이드
- Wiggins, A. (2017). *The Twelve-Factor App* — 설정·환경변수 분리 원칙 (본 위키 ADR-005)

---

## 8. 변경 이력

- 2026-05-13 — 초안 작성. 17개 스크립트(scripts/ 12개 + root 4개 + setup 1개) 7개 그룹 분류. 의존 그래프·일상 시나리오·유지보수 우선순위 정리. 핵심 스크립트 상세 페이지는 향후 분리. (Cowork)
