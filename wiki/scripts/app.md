---
type: script
language: python
filename: "app.py"
path: "app.py"
category: "Flask 웹 서버·Google Drive/Sheets API 프록시"
tags: [app, Flask, Google_Drive, Google_Sheets, 대시보드, API, 동기화]
sources:
  - "[SYS-KLEPPMANN]"
updated: 2026-05-26
status: "검증됨"
---

# app.py — Flask 로컬 대시보드·Drive API 프록시 서버

> **목적**: 로컬 Flask 웹 서버 역할. 두 가지 기능을 담당합니다.  
> (1) `dist/` 정적 HTML 파일 서빙 (generate.py가 빌드한 포털)  
> (2) Google Drive·Sheets API 프록시 — 대시보드에 실시간 데이터 공급 및 wiki/ 폴더 Drive 동기화
>
> **신뢰도**: 실측 검증 (서버 운영 중, `app.py` 코드 직접 분석 — 398줄)

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| **스크립트 경로** | `app.py` (repo 루트) |
| **언어·버전** | Python 3.x, Flask |
| **포트** | 5000 (`http://localhost:5000`) |
| **의존성** | `flask`, `google-auth`, `google-api-python-client`, `openpyxl`, `python-dotenv` (선택) |
| **정적 파일** | `dist/` 폴더 (generate.py 빌드 결과물) |
| **API 연동** | Google Drive API v3, Google Sheets API v4 |
| **설정** | `.env` 파일 또는 시스템 환경변수 |

---

## 2. 실행 방법

### 2.1 직접 실행

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
python app.py
```

서버 시작 후 브라우저에서 `http://localhost:5000` 접속.

### 2.2 run.py 경유 실행 (브라우저 자동 오픈)

```powershell
python run.py
```

`app.py` 실행 + 2초 후 브라우저 자동 오픈. 일상 사용 권장.

### 2.3 환경변수 설정 (`.env` 파일)

```env
FORM_SHEET_ID=1AbCdEfGhIjK...   # Google Sheets 폼 수신 시트 ID (필수)
```

> `FORM_SHEET_ID`가 없으면 서버는 정상 시작되지만 `/api/form-submissions` 엔드포인트가 동작하지 않습니다.  
> 시작 시 `⚠️ 경고: FORM_SHEET_ID 환경변수가 없습니다.` 메시지가 출력됩니다.

---

## 3. 라우트 목록

| 메서드 | 경로 | 역할 | 인증 필요 |
|--------|------|------|-----------|
| `GET` | `/` | index.html 서빙 (`dist/`) | 없음 |
| `GET` | `/dashboard` | dashboard.html 서빙 (`dist/`) | 없음 |
| `GET/POST` | `/<path>` | dist/ 내 임의 파일 서빙 (POST는 로컬 테스트용, 무응답) | 없음 |
| `GET` | `/api/dashboard-data` | Drive에서 출하현황·일일보고 다운로드 → JSON | Drive OAuth (RW) |
| `GET` | `/api/form-submissions` | Sheets에서 폼 4탭 조회 → JSON | Sheets OAuth |
| `POST` | `/api/sync` | `wiki/` → Google Drive 동기화 | Drive OAuth (RW) |
| `GET` | `/api/list` | Drive `cnc-wiki` 폴더 전체 목록 | Drive OAuth (RW) |
| `POST` | `/api/browse` | Drive 특정 폴더명 탐색 | Drive OAuth (RO) |

---

## 4. 핵심 함수 설명

### 4.1 인증

#### `get_service(token_file, scopes) → Google Drive Service`

OAuth 2.0 인증을 수행하고 Google Drive API 서비스 객체를 반환합니다.

```
1. token_file 존재 → Credentials 로드
2. 만료 + refresh_token 있음 → 자동 갱신 후 token_file 저장
3. drive v3 service 반환
```

사용되는 토큰 파일 3종:

| 파일 | 스코프 | 용도 |
|------|--------|------|
| `token.json` | `drive.file` (RW) | 동기화·업로드·Drive 데이터 조회 |
| `token_readonly.json` | `drive.readonly` (RO) | browse API (읽기 전용) |
| `token_sheets.json` | `spreadsheets` + `drive.file` | 폼 시트 데이터 읽기 |

> ⚠️ 토큰 파일이 없으면 처음 API 호출 시 오류가 발생합니다. Google OAuth 초기 인증 플로우(브라우저 열기)가 필요합니다. `SECURITY_NOTES.md` 참조.

### 4.2 API 엔드포인트 상세

#### `GET /api/dashboard-data`

`dashboard.html`의 Chart.js 차트와 KPI 카드에 데이터를 공급합니다.

```
Drive(token.json) 연결
  └─ cnc-wiki/comparisons/ 폴더 탐색
       └─ 출하현황_납품처별_월별분석_2025.xlsx 찾기
            └─ download_bytes() → parse_shipping()
  └─ cnc-wiki/reports/daily/ 폴더 탐색
       └─ 가장 최근 "*일일보고*" 파일 찾기
            └─ download_bytes() → parse_daily()
  → JSON 반환: { ok, shipping, daily, daily_file, fetched_at }
```

**`parse_shipping(buf)` 반환 구조:**

```python
{
    'months': ['1월', ..., '12월'],
    'customers': [
        {'name': '거래처명', 'monthly': [int × 12], 'total': int},
        ...   # total 기준 내림차순 정렬
    ]
}
```

- `wiki['요약']` 시트, 3행부터 읽기 (`row[1]` = 거래처명, `row[2~13]` = 월별 수량)

**`parse_daily(buf)` 반환 구조:**

```python
{
    'title': str, 'meta': str,
    'fast':  {'qty_actual': int, 'qty_target': int, 'qty_avg': int, 'time_actual': int},
    'gx7':   {'qty_actual': int, 'qty_target': int, 'qty_avg': int, 'time_actual': int},
    'total': {'qty_actual': int, 'qty_target': int, 'time_actual': int},
    'cumulative': int, 'cumulative_info': str
}
```

- `wiki/reports/daily/` 최신 일일보고 xlsx의 `ws.worksheets[0]` (일일 요약 시트) 파싱
- 행·열 매핑: `rows[3][2]` = FG 오늘 수량, `rows[5][2]` = GX7 오늘 수량, `rows[10][2]` = 월누적

#### `GET /api/form-submissions`

`dashboard.html`의 "접수현황" 탭에 폼 데이터를 공급합니다. 30초마다 자동 갱신.

```
Sheets(token_sheets.json) 연결
  └─ FORM_SHEET_ID 시트 4탭 순회
       └─ '재연마의뢰'!A1:Z500, '불량신고'!A1:Z500,
          '진행문의'!A1:Z500, '소모품요청'!A1:Z500
  → JSON 반환: { ok, data: { 탭명: {headers, rows(역순)} }, fetched_at }
```

> 폼 데이터는 `rows`가 **역순(최신이 위)** 으로 반환됩니다.

#### `POST /api/sync`

`wiki/` 폴더 전체를 Google Drive `cnc-wiki` 폴더에 업로드·동기화합니다.

```
로컬 mtime vs Drive modifiedTime 비교
  → 로컬이 더 새것이면: 업로드 (신규 create 또는 기존 update)
  → Drive가 더 새것이면: 건너뜀
`~$` 접두 파일(Office 잠금 파일) 자동 건너뜀
→ JSON 반환: { ok, output: "업로드 N개 / 건너뜀 M개" }
```

> ⚠️ `wiki/_private/` 같은 민감 폴더가 있다면 동기화 범위에서 제외하는 로직을 직접 추가해야 합니다 (현재 `wiki/` 전체 동기화).

#### `GET /api/list`

Drive `cnc-wiki` 폴더의 전체 파일 트리를 텍스트로 반환합니다.

#### `POST /api/browse`

```json
{ "folder": "폴더명" }
```

Drive 전체에서 해당 이름의 폴더를 찾아 파일 목록을 반환합니다. 동명 폴더가 여러 개이면 모두 표시.

### 4.3 Drive 탐색 유틸리티

| 함수 | 역할 |
|------|------|
| `_drive_root_id(service)` | Drive에서 `cnc-wiki` 루트 폴더 ID 조회 |
| `navigate_folder(service, path_parts)` | `['comparisons']` 등 경로 배열로 폴더 재귀 탐색 → folder_id |
| `find_file(service, folder_id, name)` | 폴더 내 특정 파일명 검색 → file dict |
| `find_latest_file(service, folder_id, contains='')` | 가장 최근 수정된 파일 검색 (`modifiedTime desc`) |
| `download_bytes(service, file_id)` | Drive 파일 → `BytesIO` 객체 다운로드 |
| `get_or_create_folder(service, name, parent_id)` | 폴더 없으면 생성 후 ID 반환 |
| `get_drive_files(service, folder_id)` | 폴더 내 파일 dict (`{파일명: file_dict}`) 반환 |

---

## 5. 설정 상수

| 상수 | 값 | 용도 |
|------|-----|------|
| `CREDS_FILE` | `client_secret_...json` (긴 파일명) | OAuth 클라이언트 시크릿 |
| `TOKEN_RW` | `token.json` | Drive RW 토큰 |
| `TOKEN_RO` | `token_readonly.json` | Drive RO 토큰 |
| `TOKEN_SHEETS` | `token_sheets.json` | Sheets 토큰 |
| `LOCAL_ROOT` | `wiki` | 동기화 대상 로컬 폴더 |
| `DRIVE_SYNC_ROOT` | `cnc-wiki` | Drive 대상 폴더명 |
| `DRIVE_LIST_ROOT` | `cnc-wiki 분석자료` | 브라우즈 기본 폴더명 (미사용) |
| `DIST_DIR` | `dist/` (절대경로) | 정적 HTML 서빙 폴더 |
| `FORM_TABS` | `['재연마의뢰', '불량신고', '진행문의', '소모품요청']` | Sheets 탭 이름 목록 |

---

## 6. 실행 흐름 (전체 아키텍처)

```
브라우저 http://localhost:5000
        │
        ├─ GET /                → dist/index.html    (generate.py 빌드 결과)
        ├─ GET /dashboard       → dist/dashboard.html
        ├─ GET /<any>           → dist/<any>
        │
        ├─ GET /api/dashboard-data
        │       └─ Google Drive (token.json)
        │               ├─ 출하현황 xlsx → parse_shipping() → Chart.js 데이터
        │               └─ 최신 일일보고 xlsx → parse_daily() → KPI 카드 데이터
        │
        ├─ GET /api/form-submissions (30초 자동 갱신)
        │       └─ Google Sheets (token_sheets.json)
        │               └─ FORM_SHEET_ID 4탭 → 접수현황 테이블
        │
        ├─ POST /api/sync
        │       └─ Google Drive (token.json)
        │               └─ wiki/ 폴더 전체 업로드 (mtime 비교)
        │
        └─ GET /api/list | POST /api/browse
                └─ Google Drive 폴더 탐색 → 텍스트 출력
```

---

## 7. 보안 주의사항

> decisions.md (2026-05-11) 및 SECURITY_NOTES.md에 기록된 내용.

| 파일/설정 | 취급 주의 이유 | 현재 상태 |
|-----------|---------------|----------|
| `client_secret_*.json` | Google OAuth 앱 시크릿 | `.gitignore` 보호 ✅ |
| `token*.json` (3개) | 개인 Google 계정 접근 토큰 | `.gitignore` 보호 ✅ |
| `FORM_SHEET_ID` | Sheets 접근 키 | `.env` 분리 ✅ |
| `STAFF_PASS` | generate.py 화면 보호 비번 (app.py 미사용) | `.env` 분리 ✅ |

> ⚠️ `/api/sync` 엔드포인트는 인증 없이 `wiki/` 전체를 Drive에 업로드합니다.  
> 로컬 네트워크 외부에 노출되지 않도록 주의하세요 (`host='0.0.0.0'`).

---

## 8. 트러블슈팅

### 8.1 FORM_SHEET_ID 없음

```
⚠️ 경고: FORM_SHEET_ID 환경변수가 없습니다.
```

`.env` 파일에 `FORM_SHEET_ID=...` 추가 후 재시작.

### 8.2 `/api/dashboard-data` 오류 — Drive 폴더 없음

```json
{"ok": false, "error": "Drive에서 comparisons 폴더를 찾을 수 없습니다."}
```

`/api/sync` 먼저 실행해 `wiki/` 폴더를 Drive에 업로드하면 해결됩니다.

### 8.3 토큰 만료·무효

```
google.auth.exceptions.RefreshError: ...
```

해당 `token*.json` 파일을 삭제하고 처음 API 호출 시 OAuth 브라우저 인증을 다시 완료합니다.

### 8.4 포트 충돌

```
OSError: [WinError 10048] ... port 5000
```

다른 Flask 인스턴스가 실행 중입니다. `app.py` 내 `port=5000`을 다른 포트로 변경하거나 기존 프로세스를 종료합니다.

### 8.5 openpyxl / flask 없음

```powershell
pip install flask google-auth google-api-python-client openpyxl python-dotenv --break-system-packages
```

---

## 9. 의존성 목록

| 패키지 | 역할 | 설치 여부 확인 |
|--------|------|---------------|
| `flask` | 웹 서버·라우팅 | `python -c "import flask"` |
| `google-auth` | OAuth 2.0 인증 | `python -c "import google.auth"` |
| `google-api-python-client` | Drive·Sheets API 클라이언트 | `python -c "from googleapiclient.discovery import build"` |
| `openpyxl` | xlsx 파싱 (대시보드 데이터) | `python -c "import openpyxl"` |
| `python-dotenv` | `.env` 파일 로드 | 없어도 동작 (시스템 환경변수 사용) |
| `mimetypes`, `io`, `os`, `datetime` | 유틸리티 | 표준 라이브러리 |

**일괄 설치:**
```powershell
pip install flask google-auth google-api-python-client openpyxl python-dotenv --break-system-packages
```

---

## 10. 자동화 체인 전체 그림

```
[raw/출하현황/*.xls]  ←─ 원본 소스
        │
        ▼
scripts/daily_report.py   ← 수동 실행 (또는 daily_and_upload.bat)
        │  wiki/reports/daily/YYYY-MM-DD_일일보고.xlsx 생성
        │
        ▼ (subprocess 자동 호출)
generate.py (루트)
        │  dist/*.html 재빌드 + GitHub Pages 업로드
        │
        ▼ (수동 또는 /api/sync)
app.py → /api/sync
        │  wiki/ → Google Drive 동기화
        │
        ▼
브라우저 http://localhost:5000/dashboard
        │
        ├─ /api/dashboard-data  → Drive에서 최신 xlsx 다운로드 → Chart.js
        └─ /api/form-submissions → Sheets 폼 데이터 조회 → 접수현황 테이블
```

---

## 11. 연동 스크립트 및 서비스

| 항목 | 관계 | 설명 |
|------|------|------|
| `scripts/daily_report.py` | 선행 실행 | 일일보고 xlsx 생성 → /api/dashboard-data 입력 |
| `generate.py` | 선행 실행 | dist/ HTML 재빌드 → 서빙 대상 |
| `run.py` | 실행 래퍼 | app.py 실행 + 브라우저 자동 오픈 |
| `watcher.py` | 병렬 실행 | wiki/ 변경 감지 → generate.py 자동 트리거 |
| Google Apps Script | 폼 수신 | 폼 → Sheets에 저장 (app.py가 읽음) |

---

## 12. 관련 페이지

- [[scripts/daily-report]] — daily_report.py (일일보고 xlsx 생성 → /api/dashboard-data 입력)
- [[scripts/generate]] — generate.py (dist/ HTML 빌드 → app.py가 서빙)
- [[scripts/index]] — 전체 스크립트 카탈로그

---

## 13. 변경 이력

| 날짜 | 변경 내용 | 사유 | 비고 |
|------|----------|------|------|
| 2026-05-11 | `FORM_SHEET_ID` .env 분리, `client_secret_*.json`·`token*.json` git 추적 제외 | 보안 정리 (decisions.md 2026-05-11) | |
| 2026-05-26 | 위키 페이지 초안 작성 | app.py 코드 직접 분석 후 자동화 체인 문서화 완성 | Cowork |
