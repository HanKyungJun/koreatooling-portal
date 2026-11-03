---
type: script
language: python
filename: "daily_report.py"
path: "scripts/daily_report.py"
category: "일일보고 자동화"
tags: [daily_report, 자동화, Excel, pandas, openpyxl, 일일보고, 재연마]
sources:
  - "[SYS-KLEPPMANN]"
updated: 2026-05-26
status: "검증됨"
---

# daily_report.py — 재연마 일일보고 Excel 자동화 스크립트

> **목적**: 재연마 작업일지(.xls)를 읽어 일일보고 Excel(.xlsx)을 자동 생성합니다.  
> 동일 날짜·동일 입력 파일에서 항상 동일한 보고서가 출력되도록 설계되어 있습니다.
>
> **신뢰도**: 실측 검증 (스크립트 운영 중, `scripts/daily_report.py` 코드 직접 분석)

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| **스크립트 경로** | `scripts/daily_report.py` |
| **언어·버전** | Python 3.x (3.8 이상 권장) |
| **의존성** | `pandas`, `openpyxl`, `argparse`, `subprocess` (표준 라이브러리 포함) |
| **입력** | `raw/출하현황/재연마 작업일지({year})/재연마_월간생산일지 ({month}월).xls` |
| **출력** | `wiki/reports/daily/YYYY-MM-DD_일일보고.xlsx` |
| **연동** | 실행 후 `scripts/generate.py` 자동 호출 (subprocess) |

---

## 2. 실행 방법

### 2.1 기본 실행

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
python scripts/daily_report.py
```

날짜 미지정 시 **오늘 날짜**를 자동 사용합니다.

### 2.2 날짜 지정 실행

```powershell
python scripts/daily_report.py 2026-05-15
```

과거 날짜로 보고서를 재생성할 때 사용합니다.

### 2.3 BAT 파일 실행 (자동화)

| BAT 파일 | 동작 |
|----------|------|
| `scripts/run_daily_report.bat` | daily_report.py 실행 → `upload_to_sheets.py` (Google Sheets 업로드) 순차 실행 |
| `scripts/daily_and_upload.bat` | daily_report.py 실행 → generate.py 실행, 모두 `run.log`에 기록 |

> **참고**: BAT 파일은 Windows 환경에서 더블클릭 또는 PowerShell에서 실행합니다.

---

## 3. 입출력 구조

### 3.1 입력 파일 경로 구조

```
raw/
└── 출하현황/
    └── 재연마 작업일지(2026)/
        └── 재연마_월간생산일지 (5월).xls   ← 5월 예시
```

연도·월은 지정 날짜(또는 오늘 날짜)에서 자동 추출됩니다.

#### 입력 파일 내 시트 구조

**시트 0 — 월간합계표** (`read_summary()` 가 읽는 시트)

| pandas 행 범위 | 열 인덱스 | 데이터 |
|---|---|---|
| 행 2~32 (1~31일) | 0 | 일(day) |
| | 1, 2, 3 | FG 수량·금액·시간(초) |
| | 7, 8, 9 | GX7 수량·금액·시간(초) |
| | 13, 14, 15 | 합계 수량·금액·시간(초) |

**시트 {day} — 일별 작업 상세** (`read_detail()` 가 읽는 시트, 예: 시트명 `"26"`)

| 행 범위 | 구분 | 열 인덱스 |
|---|---|---|
| 행 2~16 (슬롯 1~15) | FAST GRIND | [0]=순서, [1]=형상, [2]=날수, [3]=날경, [4]=상크경, [5]=코팅, [6]=특이사항, [8]=완료, [10]=수량, [12]=금액, [13]=시간합계(초) |
| 행 21~35 (슬롯 1~15) | GX7 | 동일 열 구성 |

> ⚠️ **월간합계(시트 0)와 일별 상세(시트 {day})는 다른 시트입니다.** 수량이 0 이하인 행은 자동으로 건너뜁니다.

### 3.2 출력 파일 구조

```
wiki/
└── reports/
    └── daily/
        └── 2026-05-26_일일보고.xlsx
```

#### Sheet 1 — "일일 요약"

| 항목 | 내용 |
|------|------|
| FG 수량·시간 | FAST GRIND 기계 당일 완료 건수·작업 시간 |
| GX 수량·시간 | GX7 기계 당일 완료 건수·작업 시간 |
| 합계 수량·시간 | FG + GX7 합산 |
| 전일대비 | ▲ (증가) / ▼ (감소) 표시 |
| 월평균 대비 | 당월 작업일 평균 대비 |
| 월누적 합계 | 당월 1일~당일 누적 |

**셀 색상 코드:**

| 상수 | 색상 | 의미 | HEX |
|------|------|------|-----|
| `CFGBG` | 연파랑 | FAST GRIND (FG) 행 배경 | `D6E4F7` |
| `CGXBG` | 연초록 | GX7 행 배경 | `E2EFDA` |
| `CTOTBG` | 연노랑 | 합계 행 배경 | `FFF2CC` |
| `CBHDR` | 진파랑 | 헤더·타이틀 배경 | `1F497D` |
| `CUPBG` | 연초록 | 전일대비 증가 | `D5F5E3` |
| `CDNBG` | 연빨강 | 전일대비 감소 | `FADBD8` |

#### Sheet 2 — "작업 상세"

각 기계별 당일 작업 목록:

| 컬럼 | 의미 |
|------|------|
| 순서 | 작업 순번 |
| 형상 | 공구 형상 (스퀘어, 볼, 드릴 등) |
| 날수 F | 날 수 (Flute count) |
| 날경 Ø | 날부 직경 (mm) |
| 샹크경 Ø | 샹크 직경 (mm) |
| 코팅 | 코팅 종류 (TiAlN, DLC 등) |
| 특이사항 | 메모 |
| 완료 | 완료 여부 |
| 수량 | 완료 수량 (개) |
| 시간합계 | 소요 시간 |

---

## 4. 핵심 함수 설명

### 4.1 `find_xls(year, month) → Path`

지정 연도·월에 해당하는 .xls 작업일지 파일 경로를 반환합니다.

```
입력: year=2026, month=5
출력: raw/출하현황/재연마 작업일지(2026)/재연마_월간생산일지 (5월).xls
```

파일이 없으면 `FileNotFoundError`를 발생시킵니다.

### 4.2 `read_summary(path) → DataFrame`

월간 생산일지의 일별 요약 데이터를 읽어 DataFrame으로 반환합니다.

- Sheet 0의 행 2~32 (최대 31일) 파싱
- FG 수량/시간, GX7 수량/시간, 합계 컬럼 포함
- 빈 행은 자동 제외

### 4.3 `read_detail(path, day) → dict`

지정 날(day)의 기계별 작업 상세 목록을 반환합니다.

```python
return {
    "fg": [{'순서': int, '형상': str, '날수(F)': int, '날경(Ø)': any,
            '상크경(Ø)': any, '코팅': str, '특이사항': str, '완료여부': str,
            '수량': int, '시간합계': int, '금액': int}, ...],
    "gx": [...]   # 동일 구조
}
```

- **시트명 = 일(day)을 문자열로 변환** (예: 26일 → 시트 `"26"`)
- 시트가 없으면 `{'fg': [], 'gx': []}` 반환 (오류 아님)
- FG: 시트 {day} 행 2~16 (슬롯 1~15)
- GX7: 시트 {day} 행 21~35 (슬롯 1~15)

### 4.4 `find_prev(summary, today_day) → row`

요약 DataFrame에서 오늘 이전 마지막 **작업일** 행을 찾아 반환합니다.  
전일 데이터가 없으면 `None` 반환 (전일대비 항목이 "—"으로 표시).

### 4.5 `calc_avg(summary, today_day) → dict`

오늘 이전 모든 작업일의 FG·GX7·합계 **평균값**을 계산합니다.  
월 초 (작업일 없음)에는 평균 계산 불가 → `None` 반환.

### 4.6 `make_report(target: date) → Path`

보고서 전체 생성 메인 함수. 위 함수들을 조합하여 xlsx 파일을 생성합니다.

```
target 날짜 → find_xls → read_summary → read_detail
             → find_prev → calc_avg
             → openpyxl로 xlsx 작성
             → wiki/reports/daily/YYYY-MM-DD_일일보고.xlsx 저장
```

### 4.7 `sec_to_hms(sec) → str`

초(seconds)를 `"H:MM:SS"` 형식 문자열로 변환합니다.

```python
sec_to_hms(3661) → "1:01:01"
```

### 4.8 `_int(v) → int`

None·빈 문자열·NaN을 0으로 안전하게 변환합니다. Excel에서 빈 셀을 읽을 때 발생하는 변환 오류를 방지합니다.

---

## 5. 경로 상수 (Path Constants)

```python
BASE = repo 루트 (cnc-wiki/)
RAW  = raw/출하현황/
OUT  = wiki/reports/daily/
```

스크립트 실행 위치와 무관하게 repo 루트 기준으로 동작합니다.

---

## 6. 실행 흐름 (전체)

```
python daily_report.py [날짜]
        │
        ├─ argparse: 날짜 파싱 (없으면 today)
        │
        ├─ find_xls(year, month)
        │   └─ 파일 없음 → FileNotFoundError
        │
        ├─ read_summary(path)
        │   └─ DataFrame: 일별 FG/GX/합계
        │
        ├─ read_detail(path, day)
        │   └─ {fg: [...], gx: [...]}
        │
        ├─ find_prev + calc_avg
        │   └─ 전일 데이터, 월평균
        │
        ├─ make_report()
        │   ├─ Sheet1 "일일 요약" 작성 (색상 적용)
        │   └─ Sheet2 "작업 상세" 작성
        │
        ├─ xlsx 저장 → wiki/reports/daily/YYYY-MM-DD_일일보고.xlsx
        │
        └─ subprocess: python scripts/generate.py 자동 호출
```

---

## 7. 트러블슈팅

### 7.1 FileNotFoundError — 작업일지 파일 없음

```
FileNotFoundError: raw/출하현황/재연마 작업일지(2026)/재연마_월간생산일지 (5월).xls
```

**원인**: 해당 월 작업일지가 아직 생성되지 않았거나 파일명이 다름  
**확인**: `raw/출하현황/` 폴더에서 파일명 정확히 확인 (공백·괄호 포함)  
**해결**: 파일명을 스크립트 기대 형식에 맞추거나, `find_xls()` 내 파일명 패턴 수정

### 7.2 ValueError — 해당일 데이터 없음

```
ValueError: 지정일(26)에 해당하는 데이터가 없습니다.
```

**원인**: 해당 날짜가 휴일이거나 작업일지에 데이터가 미입력  
**확인**: 작업일지(.xls)에서 해당 날짜 행 데이터 입력 여부 확인

### 7.3 openpyxl ImportError

```
ModuleNotFoundError: No module named 'openpyxl'
```

**해결**: `pip install openpyxl pandas --break-system-packages`

### 7.4 generate.py 연동 실패 (subprocess)

daily_report.py 자체는 정상 완료되었으나 generate.py 호출 실패  
→ generate.py 단독 실행으로 문제 분리 후 확인:  
`python scripts/generate.py`

### 7.5 출력 파일 경로 오류

스크립트를 `cnc-wiki/` 루트가 아닌 다른 폴더에서 실행하면 경로 오류 발생 가능  
→ 반드시 `cd C:\Users\TOOLKOREA\Desktop\cnc-wiki` 후 실행

---

## 8. 의존성 목록

| 패키지 | 역할 | 설치 여부 확인 |
|--------|------|---------------|
| `pandas` | .xls 파일 파싱, DataFrame 처리 | `python -c "import pandas"` |
| `openpyxl` | .xlsx 파일 생성·스타일 적용 | `python -c "import openpyxl"` |
| `argparse` | 명령줄 인수 파싱 (날짜) | 표준 라이브러리 (설치 불필요) |
| `subprocess` | generate.py 자동 호출 | 표준 라이브러리 (설치 불필요) |
| `datetime` | 날짜 처리 | 표준 라이브러리 (설치 불필요) |
| `pathlib` | 경로 처리 | 표준 라이브러리 (설치 불필요) |

**일괄 설치**:

```powershell
pip install pandas openpyxl --break-system-packages
```

---

## 9. 연동 스크립트

| 스크립트 | 관계 | 설명 |
|----------|------|------|
| `scripts/generate.py` | 후속 자동 호출 | 정적 웹 화면(`dist/`) 재빌드 |
| `scripts/upload_to_sheets.py` | `run_daily_report.bat` 경유 | 출력 xlsx → Google Sheets 업로드 |
| `scripts/run_daily_report.bat` | 실행 래퍼 | daily_report.py + upload_to_sheets.py |
| `scripts/daily_and_upload.bat` | 실행 래퍼 | daily_report.py + generate.py, 로그 기록 |

---

## 10. 관련 페이지

- [[scripts/index]] — 전체 스크립트 카탈로그 (17개)
- `wiki/reports/daily/` — 일일보고 출력 폴더 (Obsidian에서 폴더로 접근)
- [[materials/알루미늄]], [[materials/sus304]] — 보고서에 포함되는 피삭재 참조
- [[gcode/g81-드릴사이클]], [[gcode/g84-탭핑사이클]] — 작업 상세에 기록되는 가공 종류

---

## 11. 변경 이력

| 날짜 | 변경 내용 | 사유 | 비고 |
|------|----------|------|------|
| 2026-05-26 | 위키 페이지 초안 작성 | `scripts/daily_report.py` 코드 직접 분석 후 문서화 | Cowork |
| 2026-05-26 | 시트 구조 오류 수정 — 일별 상세가 시트 0이 아닌 시트 {day}임을 명확화, 열 인덱스 표 추가, 색상 상수 보완 | 코드 재분석으로 오류 발견 수정 | Cowork |
