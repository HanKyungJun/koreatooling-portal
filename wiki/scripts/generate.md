---
type: script
language: python
filename: "generate.py"
path: "generate.py"
category: "정적 사이트 생성·배포"
tags: [generate, 자동화, 정적사이트, GitHub_Pages, 포털, 현황판, Chart.js, openpyxl, xlrd]
sources:
  - "[SYS-KLEPPMANN]"
updated: 2026-05-26
status: "검증됨"
---

# generate.py — 생산팀 포털 정적 사이트 생성·배포 스크립트

> **목적**: 출하현황 Excel과 월간생산일지를 읽어 생산팀 포털 HTML 6페이지를 빌드하고  
> `dist/` 폴더에 저장 후 GitHub Pages 저장소로 자동 배포합니다.
>
> **신뢰도**: 실측 검증 (스크립트 운영 중, `generate.py` 코드 직접 분석 — 1,153줄)

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| **스크립트 경로** | `generate.py` (repo 루트) |
| **언어·버전** | Python 3.x (3.8 이상 권장) |
| **의존성** | `openpyxl`, `xlrd`, `requests`, `python-dotenv` (선택) |
| **입력 1** | `wiki/comparisons/출하현황_납품처별_월별분석_{year}.xlsx` (2022~2026) |
| **입력 2** | `raw/출하현황/재연마 작업일지({year})/재연마_월간생산일지 ({month}월).xls` |
| **출력** | `dist/` 폴더 HTML 6개 파일 |
| **배포** | GitHub Pages (`GITHUB_USER/GITHUB_REPO`) |
| **설정** | `.env` 파일 또는 시스템 환경변수 |

---

## 2. 실행 방법

### 2.1 일반 실행 (GitHub Pages 배포 포함)

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
python generate.py
```

`GITHUB_TOKEN` 환경변수가 필요합니다. `.env` 파일 또는 시스템 환경변수로 설정하세요.

### 2.2 로컬 전용 실행 (GitHub 업로드 없이)

```powershell
python generate.py --local
```

`GITHUB_TOKEN` 없이도 실행 가능. `dist/` 폴더에 HTML만 생성됩니다.

### 2.3 환경변수 설정 (`.env` 파일)

`.env.example`을 복사해 `.env`를 만들고 값을 입력합니다:

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
GITHUB_USER=HanKyungJun
GITHUB_REPO=koreatooling-portal
STAFF_PASS=1234
SHOW_STAFF=True
```

> ⚠️ **주의**: `.env` 파일은 `.gitignore`로 보호됩니다. git에 커밋하지 마세요. (SECURITY_NOTES.md 참조)

---

## 3. 입출력 구조

### 3.1 입력 파일

| 파일 | 경로 | 읽기 방식 |
|------|------|----------|
| 출하현황 xlsx (연도별) | `wiki/comparisons/출하현황_납품처별_월별분석_{year}.xlsx` | openpyxl |
| 월간생산일지 | `raw/출하현황/재연마 작업일지({year})/재연마_월간생산일지 ({month}월).xls` | xlrd |

- 출하현황 파일이 없는 연도는 건너뜁니다 (오류 아님)
- 월간생산일지가 없으면 KPI 카드를 "데이터 없음"으로 표시합니다

### 3.2 출력 파일 (`dist/` 폴더)

| 파일 | 내용 | 접근 |
|------|------|------|
| `index.html` | 생산팀 포털 메인 메뉴 | 공개 |
| `request.html` | 재연마 의뢰 접수 폼 | 공개 |
| `defect.html` | 공구 불량 신고 폼 | 공개 |
| `inquiry.html` | 작업 진행 문의 폼 | 공개 |
| `supplies.html` | 소모품 구매 요청 폼 | 직원 전용 (비밀번호) |
| `dashboard.html` | 재연마 현황판 | 직원 전용 (비밀번호) |

---

## 4. 환경변수 상세

| 변수 | 기본값 | 용도 | 필수 여부 |
|------|--------|------|----------|
| `GITHUB_TOKEN` | — | GitHub Pages push 인증 | `--local` 아닐 때 필수 |
| `GITHUB_USER` | `HanKyungJun` | GitHub 사용자명 | 선택 |
| `GITHUB_REPO` | `koreatooling-portal` | GitHub 저장소명 | 선택 |
| `STAFF_PASS` | `1234` | 직원 전용 페이지 화면 보호 비밀번호 | 선택 |
| `SHOW_STAFF` | `True` | 직원 전용 섹션 표시 여부 | 선택 |

> **보안 참고**: `STAFF_PASS`는 화면 UI 보호용(sessionStorage 기반)이며 실제 인증·권한 시스템이 아닙니다. 민감 정보 접근 제어 용도로는 사용하지 마세요. (SECURITY_NOTES.md 참조)

---

## 5. 핵심 함수 설명

### 5.1 데이터 파싱 함수

#### `parse_shipping(filepath) → dict`

출하현황 Excel 파일을 읽어 납품처별 월별 출하 데이터를 반환합니다.

```python
# 반환 구조
{
    'months': ['1월', '2월', ..., '12월'],
    'customers': [
        {'name': '거래처명', 'monthly': [0, 0, ..., 0], 'total': 0},
        ...
    ]  # total 기준 내림차순 정렬
}
```

- `wiki/comparisons/` 시트 '요약', 3행부터 데이터 읽기
- 거래처 합계 기준 내림차순 정렬 후 반환

#### `parse_worklog() → (dict | None, str | None)`

오늘 날짜 기준 월간생산일지를 읽어 당일·월누적 데이터를 반환합니다.

```python
# 반환 구조 (첫 번째 반환값)
{
    'date': 'YYYY-MM-DD',
    'fast': {'qty': int, 'time_sec': int},
    'gx7':  {'qty': int, 'time_sec': int},
    'total': {'qty': int, 'time_sec': int},
    'cumulative': {
        'fast': int, 'gx7': int,
        'total': int, 'work_days': int
    }
}
# 두 번째 반환값: 파일명 문자열 (로그용)
# 파일 없으면: (None, None)
```

- xlrd로 .xls 읽기 (행 2~nrows)
- 컬럼 배치: [0]=일, [1]=FG수량, [3]=FG시간, [7]=GX수량, [9]=GX시간

### 5.2 HTML 빌더 함수

#### `build_portal_html() → str`

메인 포털 페이지(`index.html`) HTML을 생성합니다.

- 고객 서비스 3개 메뉴: 재연마 의뢰 접수 / 공구 불량 신고 / 작업 진행 문의
- `SHOW_STAFF=True`일 때 직원 전용 섹션 추가 (비밀번호 모달 포함)
- 직원 전용: 재연마 현황판(`dashboard.html`), 소모품 구매 요청(`supplies.html`)

#### `build_request_html() → str`

재연마 의뢰 접수 폼 페이지(`request.html`) HTML을 생성합니다.

- 필드: 회사명·담당자·연락처·이메일·공구종류·재질·규격/수량(행 추가 가능)·특이사항·파일첨부
- 파일 첨부: 드래그앤드롭, Base64 인코딩 → hidden input, 최대 5MB
- 규격 행 동적 추가/제거 (JavaScript)

#### `build_defect_html() → str`

공구 불량 신고 폼 페이지(`defect.html`) HTML을 생성합니다.

- 필드: 회사명·담당자·연락처·발생일자·공구명/규격(행 추가)·불량증상(체크박스)·피삭재/환경·상세내용
- 불량 증상 체크박스: 치핑 / 파손 / 치수불량 / 코팅불량 / 수명단축 / 기타

#### `build_inquiry_html() → str`

작업 진행 문의 폼 페이지(`inquiry.html`) HTML을 생성합니다.

- 필드: 회사명·담당자·연락처·참고일자·문의내용

#### `build_supplies_html() → str`

소모품 구매 요청 폼 페이지(`supplies.html`) HTML을 생성합니다.

- **직원 전용**: `protected=True` → 페이지 로드 시 비밀번호 오버레이 표시
- 필드: 요청자·부서·품목명·규격/사양·수량·희망납기·용도/사유·긴급요청 체크박스

#### `build_dashboard_html(shippings, daily, worklog_date, generated_at) → str`

재연마 현황판 페이지(`dashboard.html`) HTML을 생성합니다.

- **직원 전용**: 비밀번호 오버레이
- **KPI 카드 4개**: FAST GRIND 오늘수량/시간, GX7 오늘수량/시간, 합계, 월누계
- **Chart.js 스택 바차트**: 연도별 탭 전환 (2022~2026), 납품처별 월간 출하량
  - 상위 10개사 개별 표시, 나머지 "기타 N개사" 합산
  - 연간 합계·납품처 수 표시, 상세 테이블 (행 클릭·하이라이트)
- **접수현황 테이블**: Flask `/api/form-submissions` 호출 (30초 자동 갱신)
  - 재연마의뢰 / 불량신고 / 진행문의 / 소모품요청 탭 구성
  - **주의**: Flask 서버가 실행 중이어야 데이터 표시됩니다 (정적 배포 시 "서버 연결 필요" 표시)

### 5.3 공통 컴포넌트

| 상수/함수 | 역할 |
|-----------|------|
| `_FORM_CSS` | 모든 폼 페이지 공통 CSS (Segoe UI, 카드 레이아웃, 모바일 대응) |
| `_AUTH_HTML` | 비밀번호 오버레이 HTML (직원 전용 페이지) |
| `_auth_script(password)` | 비밀번호 확인 JavaScript (sessionStorage 기반) |
| `_AJAX_JS` | 폼 → Google Apps Script URL로 iframe 제출 후 성공 화면 전환 |
| `_form_page(...)` | 폼 페이지 공통 템플릿 (헤더·카드·성공박스·푸터) |
| `APPS_SCRIPT_URL` | Google Apps Script exec URL (폼 데이터 수신 엔드포인트) |

### 5.4 배포 함수

#### `upload_to_github() → str | None`

`dist/` 폴더를 GitHub 저장소에 commit·push합니다.

```
1. git config (user.email, user.name)
2. git remote set-url origin (GITHUB_TOKEN 포함 URL)
3. git add .
4. git commit -m "update: YYYY-MM-DD HH:MM"
   → 변경 없으면 스킵 (nothing to commit)
5. git push origin main
6. 성공 시 GitHub Pages URL 반환
```

---

## 6. 실행 흐름 (전체)

```
python generate.py [--local]
        │
        ├─ .env 로드 (python-dotenv)
        ├─ 환경변수 체크 (GITHUB_TOKEN, --local 아닐 때)
        │
        ├─ 1) 출하현황 파싱
        │   └─ YEARS=[2026..2022] 순회 → parse_shipping() × 최대 5회
        │       파일 없는 연도는 건너뜀
        │
        ├─ 2) 월간생산일지 파싱
        │   └─ parse_worklog() → 오늘 날짜 기준
        │       파일 없으면 daily=None (KPI "데이터 없음")
        │
        ├─ 3) HTML 6페이지 생성
        │   ├─ build_portal_html()  → dist/index.html
        │   ├─ build_request_html() → dist/request.html
        │   ├─ build_defect_html()  → dist/defect.html
        │   ├─ build_inquiry_html() → dist/inquiry.html
        │   ├─ build_supplies_html()→ dist/supplies.html
        │   └─ build_dashboard_html()→ dist/dashboard.html
        │
        └─ 4) 배포
            ├─ --local: 건너뜀 (dist/ 파일만 생성)
            └─ 일반:  upload_to_github() → GitHub Pages
```

---

## 7. 경로 상수

| 상수 | 값 (repo 루트 기준) | 용도 |
|------|--------------------|----|
| `BASE_DIR` | repo 루트 | 절대경로 기준점 |
| `COMP_DIR` | `wiki/comparisons/` | 출하현황 xlsx 위치 |
| `WORKLOG_DIR` | `raw/출하현황/` | 월간생산일지 위치 |
| `DIST_DIR` | `dist/` | HTML 출력 폴더 |
| `YEARS` | `[2026, 2025, 2024, 2023, 2022]` | 출하현황 조회 연도 |

---

## 8. 대시보드 — Flask 연동 구조

`dashboard.html`의 "접수현황" 탭은 별도 Flask 서버(`app.py`)가 필요합니다:

```
브라우저 → fetch('/api/form-submissions')
                │
                └─ Flask app.py 실행 중이어야 응답
                   (정적 파일만으로는 API 없음)
```

- GitHub Pages 배포 버전: 접수현황 탭에서 "서버 연결 필요" 표시 (정상 동작)
- 로컬 대시보드 사용: `python app.py` 실행 후 `http://localhost:PORT/dashboard.html` 접속

---

## 9. 트러블슈팅

### 9.1 GITHUB_TOKEN 없이 실행 시

```
⚠️ GITHUB_TOKEN 환경변수가 필요합니다.
```

**해결**: `.env` 파일 생성 후 토큰 입력, 또는 `--local` 플래그 추가

### 9.2 출하현황 Excel 파일 없음

```
→ 2026: 파일 없음 (건너뜀)
```

오류가 아닙니다. 해당 연도 탭이 대시보드에 표시되지 않습니다.  
`wiki/comparisons/출하현황_납품처별_월별분석_2026.xlsx` 파일 경로 확인.

### 9.3 월간생산일지 없음

```
→ 파일 없음
```

오류가 아닙니다. KPI 카드에 "생산일지 데이터 없음"이 표시됩니다.  
`raw/출하현황/` 폴더에서 파일명 패턴 확인 (공백·괄호 포함):  
`재연마 작업일지(2026)/재연마_월간생산일지 (5월).xls`

### 9.4 GitHub push 실패

```
❌ 푸시 실패: remote: Invalid username or password.
```

**해결**: `GITHUB_TOKEN` 만료 여부 확인 → GitHub Settings에서 새 토큰 발급 → `.env` 갱신

### 9.5 openpyxl / xlrd ImportError

```
ModuleNotFoundError: No module named 'openpyxl'
```

**해결**:
```powershell
pip install openpyxl xlrd requests python-dotenv --break-system-packages
```

### 9.6 dist/ 폴더 생성 안 됨

`dist/` 폴더는 실행 시 자동 생성됩니다 (`os.makedirs(DIST_DIR, exist_ok=True)`).  
폴더 생성 권한 문제라면 수동으로 생성 후 재실행.

---

## 10. 의존성 목록

| 패키지 | 역할 | 설치 여부 확인 |
|--------|------|---------------|
| `openpyxl` | 출하현황 .xlsx 파싱 | `python -c "import openpyxl"` |
| `xlrd` | 월간생산일지 .xls 파싱 | `python -c "import xlrd"` |
| `requests` | (현재 import만, 직접 사용 없음) | `python -c "import requests"` |
| `python-dotenv` | `.env` 파일 로드 | 없어도 동작 (시스템 환경변수 사용) |
| `subprocess` | git 명령 실행 | 표준 라이브러리 |
| `argparse` | `--local` 플래그 처리 | 표준 라이브러리 |
| `json`, `hashlib`, `os`, `datetime` | 유틸리티 | 표준 라이브러리 |

**일괄 설치**:
```powershell
pip install openpyxl xlrd requests python-dotenv --break-system-packages
```

---

## 11. 연동 스크립트 및 서비스

| 항목 | 관계 | 설명 |
|------|------|------|
| `scripts/daily_report.py` | 선행 실행 | daily_report.py가 완료 후 generate.py 자동 호출 |
| `scripts/daily_and_upload.bat` | 실행 래퍼 | daily_report.py → generate.py 순차 실행, 로그 기록 |
| `app.py` | 로컬 Flask 서버 | 대시보드 접수현황 API 제공 (`/api/form-submissions`) |
| Google Apps Script | 폼 수신 엔드포인트 | 폼 데이터 → Google Sheets 저장 |
| GitHub Pages | 배포 대상 | `dist/` → `GITHUB_USER.github.io/GITHUB_REPO/` |

---

## 12. 보안 주의사항

> 이 내용은 SECURITY_NOTES.md와 decisions.md (2026-05-11)에 기록되어 있습니다.

- `GITHUB_TOKEN`: `.env`에만 보관, git에 커밋 금지
- `STAFF_PASS`: 화면 UI 보호용, sessionStorage 기반 — 실제 인증 시스템 아님
- `APPS_SCRIPT_URL`: Google Apps Script exec URL — 민감도 낮음 (폼 수신만)
- 민감 데이터(단가·금액)는 generate.py 출력물에 포함하지 않음

---

## 13. 관련 페이지

- [[scripts/daily-report]] — daily_report.py (generate.py 선행 스크립트)
- [[scripts/index]] — 전체 스크립트 카탈로그 (17개)
- [[출하현황-2022-2024-비교]] — 입력 xlsx 파일 위치 (comparisons/ 폴더)
- [[machines/anca-cnc-tool-grinder]] — 대시보드에 반영되는 장비 데이터

---

## 14. 변경 이력

| 날짜 | 변경 내용 | 사유 | 비고 |
|------|----------|------|------|
| 2026-05-11 | 하드코딩 토큰·비밀번호 → 환경변수 분리 | 보안 정리 (SECURITY_NOTES.md) | decisions.md 기록 |
| 2026-05-26 | 위키 페이지 초안 작성 | `generate.py` 코드 직접 분석 후 문서화 | Cowork |
