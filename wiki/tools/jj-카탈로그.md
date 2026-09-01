---
type: tool
category: "공구 카탈로그 — 외부 공급사"
manufacturer: "JJ TOOLS (제이제이툴스, 구 장진공구)"
catalog_file: "raw/Catalog/JJ.pdf"
catalog_pages: 524
total_products: "18,619 tools / 278 items"
tags: [카탈로그, JJ, 장진공구, 엔드밀, 드릴, 인덱스]
sources:
  - "raw/Catalog/JJ.pdf (사내 보유 PDF)"
  - "raw/Catalog/JJ.cache.json (pdf_search.py 추출 텍스트 캐시)"
  - "www.jjtools.co.kr (공식)"
updated: 2026-06-08
status: "네비게이션 인덱스 — 시리즈·페이지·용도 매핑"
---

# JJ TOOLS 카탈로그 인덱스

> **목적**: 524p PDF 카탈로그를 빠르게 탐색하기 위한 네비게이션 인덱스.
> "이 공구 카탈로그 어디 있나?" 한경준님 자주 묻는 질문을 1초 안에 답하기 위함.
>
> **카탈로그 위치**: `raw/Catalog/JJ.pdf` (51 MB)
> **추출 캐시**: `raw/Catalog/JJ.cache.json` (1.9 MB) — `scripts/pdf_search.py`로 키워드 검색 즉시 가능

---

## 1. 카탈로그 개요

- **공급사**: JJ TOOLS (제이제이툴스), 구명 장진공구. Made in Korea.
- **공식 사이트**: https://www.jjtools.co.kr
- **공급 라인업**: **18,619 tools in 278 items** (카탈로그 p.5 명시)
- **공구 오차 표준**: 0.1R~1R ±0.003mm / 1R~3R ±0.005mm / 3R 이상 ±0.008mm
- **주력 제품군**: 초경 엔드밀 (Carbide End Mills) 중심, CBN/PCD/Insert도 포함

---

## 2. 시리즈별 인덱스

### 2.1 엔드밀 시리즈 (주력)

| 시리즈 | 페이지 | 용도 | 비고 |
|---|---|---|---|
| **CBN series** | 8-9 | 고경도강 (HRC 60+) | CBN 모재, 일반 초경 한계 영역 |
| **HARD series** | 6-15 | 고경도용 (HRC 50~70) | 경화강·프리하든강 |
| **JJ series** | 6-7 | 고경도용 메인 라인 | 표지 강조 시리즈 |
| **R-TAC** | 12-13, 22-31, 213-219, 474 | 고이송용 (코팅) | R-TAC 자체 코팅, 고속·고이송 |
| **High Speed** | 다수 | 고속가공용 | 산재 |
| **E series** | 7, 26-31, 111, 204 | 강력 절삭 (Heavy Cuts) | 거친 가공 |
| **G series** | 7, 28-33, 170-171, 275-277 | 범용 (General Purpose) | 일반 가공 |
| **V series** | 10-11, 28-29, 169-176, 301 | 고능률 범용 (Various Symmetry) | 다양한 대칭 |

### 2.2 피삭재 전용 엔드밀

| 시리즈 | 페이지 | 피삭재 |
|---|---|---|
| FOR ALUMINUM (NE 등) | 12-13, 21-37, 209-236, 247-253 | 알루미늄 (A6061·A7075 등) |
| FOR GRAPHITE | 17, 179-194, 283-284 | 흑연 (CFRP 인접) |
| FOR COMPOSITE | 15, 25-37, 195-197 | 복합재 (CFRP, GFRP) |
| FOR SUS & TITANIUM | 14-15 외 산재 | SUS·티타늄·인코넬 |
| FOR COPPER | 산재 | 동·황동 |

### 2.3 기타 공구 라인

| 시리즈 | 페이지 | 종류 |
|---|---|---|
| Drills (드릴) | 197, 297-340 외 | 초경 드릴 |
| Thread Mills (쓰레드밀) | 23, 32-37, 260, 331-395 | 나사 가공 |
| Inserts (인서트) | 18-19, 32-35, 278-287 | 교환 가능 인서트 |
| **PCD series** | 34-35, 288-295 | 다이아몬드 (비철·복합재) |
| Burrs (버) | 196-197, 247-251 | 절삭 버 |
| Chamfer (면취) | 32-33, 172-178, 202-204, 247-255, 298 | 면취 공구 |
| Engraving | 337-339 | 조각용 |
| Tap (탭) | 16-17, 24-37, 54-57, 77-78 | 나사 가공 |

---

## 3. 피삭재별 페이지 분포 (검색 결과)

| 피삭재 | JJ 카탈로그 적용 페이지 수 | 주 시리즈 |
|---|---|---|
| 경화강 (Hardened Steel, HRC > 50) | 148p | HARD, CBN, JJ series |
| 알루미늄 (Aluminum) | 119p | NE 등 FOR ALUMINUM, PCD |
| 동 (Copper) | 151p | DLC 코팅, PCD |
| 스테인리스 (SUS) | 99p | FOR SUS & TITANIUM |
| 티타늄 (Titanium) | 43p | FOR SUS & TITANIUM |
| 흑연 (Graphite) | 41p | FOR GRAPHITE |
| 복합재 (Composite) | 29p | FOR COMPOSITE, PCD |

> ⚠️ 페이지 수는 검색 매칭 횟수이며 일부 페이지는 여러 카테고리 중복.

---

## 4. 카탈로그 사용법

### 4.1 텍스트 빠른 검색 (캐시 활용)

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
python scripts/pdf_search.py raw/Catalog/JJ.pdf "D6 4날"
python scripts/pdf_search.py raw/Catalog/JJ.pdf "HRC 65" --pages 25 26 27
```

- 캐시(`JJ.cache.json`) 이미 있으므로 검색은 1초 이내
- 결과로 일치 페이지 번호 + 페이지 내용 출력

### 4.2 직접 PDF 열기

```powershell
start raw\Catalog\JJ.pdf
```

기본 PDF 뷰어에서 열림. 위 §2 시리즈 표의 페이지 번호로 즉시 이동.

### 4.3 위키에서 인용

위키 본문에서 JJ 공구 인용 시:
- 출처 ID `[CAT-JJ]` 사용 ([[sources]] §3 참조)
- 페이지 번호 함께 명기: `[CAT-JJ p.42]`

---

## 5. 관련 페이지

- [[cogo-카탈로그]] — COGO 카탈로그 인덱스 (자매 카탈로그)
- [[초경]] §8.3 — 사내 운영 등급 (카탈로그에서 매핑 후보)
- [[공구-코팅]] — 코팅 종류별 상세 (JJ는 R-TAC 자체 코팅 + 한글 표기)
- [[연삭-조건-목록]] — 형상별 조건 (카탈로그 제품과 매칭)
- `scripts/pdf_search.py` — 카탈로그 검색 도구

---

## 6. 사내 실사용 현황 (테스트 결과 요약)

> ⚠️ 아래 데이터는 사내 실측 테스트 기반 — 신뢰도: 사내 경험값.  
> 장비: CHEVALIER QP2040L (MCT)

### 6-1. JJ 엔드밀 — AL6061 측면가공 (D10 3날)

| 공구 | RPM | Vc | Vf | 결과 | 비고 |
|------|-----|----|----|------|------|
| J.J 3ALE 100 250 070 | 5,500→6,600 rpm | 172.8→207.3 m/min | 1,300→1,430 mm/min | 재연마 후 재사용 가능 | AL 용착(BUE) 흔적, 날 형상 유지 |

- 순위: YG-1에 이어 **2위** (면 거칠기 기준). 스핀들 부하 18% (YG-1 14%).
- 상세: [[AL엔드밀-3종-비교]]

### 6-2. JJ NC드릴 — S45C 탄소강 (D4, 90°)

테스트 공구: J.J SPO(비코팅) `2SPO040090050` / SPOC(코팅) `2SPOC040090050`

| 차수 | 조건 | JJ 결과 |
|------|------|---------|
| NC_3 (비코팅) | Vc=60.3 m/min, N=4,800 | — (가공 홀 수 미기록) |
| NC_4 (코팅 후 재테스트) | 조건 미기록 | 미기록 |

- 종합 순위: WIDIN > SENO > HANDERK > J.J (NC드릴 4종 기준)
- 상세: [[NC드릴-4종-비교-D4]]

### 6-3. JJ 두배 드릴 — S45C 탄소강 (D5, 2날)

| 공구 | 조건 | 결과 | 비고 |
|------|------|------|------|
| J.J 두배 (2DUBES 050 440 S06) | N=2,500 rpm, Vf=300 mm/min | 포인트 파손·심한 마모 (1차) → 대체 투입 후 우수 (병행) | L1=44mm, 타 제품(32mm)과 사양 불일치. 원보고서 "조건 적절하지 않음" 명시 |

- ⚠️ 1차 비교는 조건 불일치로 결론 보류. L1=44mm·S6 홀더 맞는 조건으로 재테스트 필요.
- 상세: [[드릴-6종-비교-D5]]

### 6-4. 카탈로그 파일 위치

| 파일 | 위치 |
|------|------|
| JJ.pdf (51 MB) | `raw/Catalog/JJ.pdf` (로컬, 2026-06-08 복원) |
| JJ.cache.json | `raw/Catalog/JJ.cache.json` (로컬) |

---

## 7. 변경 이력

- 2026-06-08 — §6-4 파일 위치 서버→로컬 업데이트 (raw/Catalog/ 복원 완료). (Cowork)
- 2026-06-08 — §6 사내 실사용 현황 추가 (비교 테스트 결과 집계, 3종). 카탈로그 파일 서버 이동 반영. (Cowork)
- 2026-05-12 — 신규 작성. JJ.cache.json 분석 기반 시리즈·페이지·피삭재 인덱스. 향후 사내 입출고 데이터와 cross-link 보강 가능. (Cowork)

---

> **확장 후보** (시간 날 때):
> - 시리즈별 상세 페이지 (`wiki/tools/jj-NE-series.md` 등) — 사용 빈도 높은 시리즈만
> - 카탈로그 페이지 → 사내 공구 코드 매핑표 (영업·구매 시스템과 연계)
> - 가격대별 정렬 (단가 데이터는 정보 분류 원칙에 따라 별도 관리)
