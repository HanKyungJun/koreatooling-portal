---
type: tool
category: "공구 카탈로그 — 외부 공급사"
manufacturer: "COGO TOOL"
catalog_file: "raw/Catalog/COGO.pdf"
catalog_pages: 448
total_products: "15,481 tools / 225 items"
catalog_volume: "Vol.10 (2026)"
tags: [카탈로그, COGO, 엔드밀, 드릴, 인덱스]
sources:
  - "raw/Catalog/COGO.pdf (사내 보유 PDF)"
  - "raw/Catalog/COGO.cache.json (pdf_search.py 추출 텍스트 캐시)"
  - "[CAT-COGO-AISUM]"
updated: 2026-07-10
status: "네비게이션 인덱스 — 시리즈 코드·페이지·용도 매핑"
---

# COGO TOOL 카탈로그 인덱스

> **목적**: 448p PDF 카탈로그를 빠르게 탐색하기 위한 네비게이션 인덱스.
>
> **카탈로그 위치**: `raw/Catalog/COGO.pdf` (67 MB)
> **추출 캐시**: `raw/Catalog/COGO.cache.json` (1.1 MB) — `scripts/pdf_search.py`로 키워드 검색 즉시 가능
>
> ⚠️ COGO PDF 일부 페이지는 텍스트 추출 시 `(cid:NNN)` 패턴 발생 (글꼴 임베드 차이). 영문 본문·표는 정상 추출, 한글 일부 깨질 수 있음. 직접 PDF 열어 확인 권장.

---

## 1. 카탈로그 개요

- **공급사**: COGO TOOL
- **공급 라인업**: **15,481 tools in 225 items** (카탈로그 p.2 명시)
- **카탈로그 볼륨**: Vol.10 (2026년판)
- **주력 제품군**: Carbide Endmill / Drill, High Speed Series Tools
- **자료 형식**: 한·일·영 3개 국어 병기
- **코팅 표기**: 영문 직접 표기 (AlCrN, TiSiN, DLC 등) — JJ와 대비

---

## 2. 시리즈 코드별 인덱스

> COGO는 제품 시리즈를 코드 prefix (HARD, SPEED, DRILL 등)로 구분. 페이지 헤더에 코드가 큼지막하게 표시됨.

### 2.1 주요 시리즈 (10p 이상)

| 시리즈 코드 | 페이지 범위 | 페이지 수 | 용도 |
|---|---|---|---|
| **HARD** | 102-154 | 47p | 고경도용 엔드밀 (HRC 60+) |
| **SPEED** | 155-218 | 46p | 고속가공용 엔드밀 |
| **MILL** (Thread Mill) | 408-443 | 36p | 쓰레드밀 (나사 가공) |
| **DRILL** | 43-76 | 33p | 초경 드릴 |
| **ABS** | 323-346 | 20p | ABS 수지 가공용 |
| **SUS** | 252-275 | 15p | 스테인리스 가공용 |
| **MULTI** | 277-296 | 14p | 다목적 |
| **TAPER** | 348-358 | 10p | 테이퍼 공구 |

### 2.2 보조 시리즈 (3~10p)

| 시리즈 코드 | 페이지 범위 | 페이지 수 | 용도 |
|---|---|---|---|
| **CBN** | 92-100 | 8p | CBN 엔드밀 (고경도 한계 영역) |
| **BLUE** | 383-393 | 7p | Blue 코팅 시리즈 |
| **3AHE** | 300, 307-310 | 5p | (개별 제품 시리즈) |
| **CMTC** | 9, 372-375 | 5p | (개별 제품 시리즈) |
| **2AHE** | 303-306 | 4p | (개별 제품 시리즈) |
| **2GML** | 43-44 등 | — | Carbide Micro Drill 0.1~1mm |
| **2GDD** | 5 등 | — | High-speed Drill (HRC 28 이하 / S45C / SCM / 주강·주철) |
| **2HOB, 2LCR, 4NSM, JCRO, MIDAS** | 산재 | 3p | 특수 목적 |

### 2.3 카테고리별 분포 (검색 매칭)

| 카테고리 | 페이지 수 |
|---|---|
| End Mill (엔드밀) | 160p (11, 77-188, 195, 202-370 등) |
| Drill (드릴) | 16p (43, 50-59, 66-76 등) |
| Thread Mill | 17p (381, 408-442) |
| Tap (탭) | 14p (112-118, 348-365) |
| Chamfer (면취) | 18p (255-281, 287-296) |
| Insert (인서트) | 3p (444-447) |
| Burr (버) | 2p (240, 333) |

---

## 3. 피삭재별 페이지 분포 (검색 결과)

| 피삭재 | COGO 적용 페이지 수 | 주 시리즈 |
|---|---|---|
| 스테인리스 (SUS) | 85p | SUS, MULTI |
| 알루미늄 (Aluminum) | 64p | ABS 일부, SPEED |
| 경화강 (Hardened Steel, HRC > 50) | 62p | HARD, CBN |
| 동 (Copper) | 40p | — |
| 티타늄 (Titanium) | 28p | SUS, MULTI |
| 복합재 (Composite) | 13p | (CFRP·GFRP) |
| 흑연 (Graphite) | 9p | — |

---

## 4. 코팅 검색 결과 (영문 표기)

> COGO는 영문 코팅 명칭을 직접 사용 — wiki [[공구-코팅]] 색상 식별 가이드와 직접 매칭 가능.

| 코팅 | COGO 적용 페이지 수 | 비고 |
|---|---|---|
| AlCrN | 23p (216-222 등) | 고온·건식 (위키 §3.4) |
| TiSiN | 23p (102-107 등) | 나노복합 초경도 (위키 §3.5) |
| Coating (일반) | 8p (43-47 등) | 종합 안내 |
| HRC 표기 | 142p | 적용 경도 범위 명기 |

---

## 5. 소재·용도별 제품군 빠른 참조 (★★☆ — 2차 요약자료, 원문 대조 권장)

> 출처: `[CAT-COGO-AISUM]` — 2026 COGO 카탈로그를 기반으로 작성된 AI 상담용 요약자료(사내 "생성형 AI 시스템설계와 RAG" 강의 실습 산출물). ⚠️ 카탈로그 원문이 아니므로 세부 SKU·수치는 §2 시리즈 인덱스 또는 `[CAT-COGO]` 원문 대조 후 사용.

### 5-1. 전체 제품군 (18종)

THREAD · G-SERIES · BLUE · GENERAL · TAPER · ABS · ALUMINUM · MULTI · SUS · G-TAC · COMPOSITE · GRAPHITE · COPPER · SPEED · HARD · CBN · DENTAL · DRILL

> §2 페이지 인덱스에 아직 없는 시리즈(ALUMINUM, GENERAL, G-SERIES, G-TAC, COMPOSITE, GRAPHITE, COPPER, DENTAL, THREAD)는 페이지 범위 미확인 — 확인 필요.

### 5-2. 소재·상황별 1차 제품군 매칭표

| 가공 소재 / 상황 | 우선 확인 제품군 | 카탈로그상 근거 요약 | 상담·발주 전 추가 확인 |
|---|---|---|---|
| 일반강, S45C, SCM, 주강, 주철 | GENERAL, DRILL, **2GDD Drill** | 2GDD Drill: HRC28 이하, S45C/SCM/주강/주철용 고정밀 드릴, 치핑·돌발파손 방지, 칩 배출성 향상 | 소재명, 경도, 홀 직경/깊이, 관통 여부 |
| SUS, 스테인리스 | SUS | SUS 계열 포함 | SUS304/316 여부, 경도, 가공방식, 직경, 장비 강성 |
| 알루미늄 | ALUMINUM | ALUMINUM 계열 포함 | 알루미늄 종류, 용착 문제, 칩 배출, 표면조도, 고속가공 여부 |
| 범용/소재 불명확 | GENERAL, MULTI | 범용·다목적 분류 | 정확한 소재·경도·가공방식·공구형태 우선 질문 |
| CFRP, GFRP | COMPOSITE | CFRP/GFRP/glass·carbon fiber 대응. 8~12날 정삭엔드밀(A type=슬로팅용 밑날多, B type=2날 수직·수평용), 6~16날 라우터(황삭) | CFRP/GFRP 여부, 박리 문제, 황삭/정삭, 가공방향 |
| Graphite, 흑연, 강화플라스틱, 탄소섬유 | GRAPHITE, COMPOSITE 일부 | 2·3날 다이아몬드 코팅 엔드밀. graphite/강화플라스틱/탄소섬유/비철·비금속 대응 | 전극가공 여부, 정삭/황삭, 분진·마모 문제 |
| 비철·비금속 소재 | GRAPHITE, COMPOSITE, COPPER | — | 구리/흑연/플라스틱/복합소재 중 구체 소재 확인 |
| 구리, 동합금 | COPPER | COPPER 계열 포함 | 순동/동합금 여부, 용착, 표면조도 |
| 고경도강 HRC52~70 | **HARD** | 파손 저항성 향상 설계, 내마모 특수코팅, 고속·고효율 절삭력 | 정확한 HRC, 정삭/황삭, 장비 강성 |
| 초고경도 (HRC90 미만) | **CBN Endmills** | 카탈로그 표현: "Cutting range < HRC90", 초경 대비 긴 수명·"Tool life 50 hours" 마케팅 표현 | ⚠️ 수명 수치는 카탈로그 마케팅 표현 — 실측 검증 없이 확정값처럼 사용 금지 |
| 진동, 채터링, 떨림 | **M series** | 부등분할날, 불균일 피치, multiple helix, wide chip pocket, TiSiN-R 코팅 | 돌출 길이, 장비 강성, 소재·가공방식 |
| 홈가공, T-slot, slotting | **CMTC T-CUTTER** | 20·24날, 내마모성·내구성 강화, 초미립자 초경합금 | 홈 폭·깊이, 소재, 장비 조건 |
| 나사 가공 | THREAD | THREAD 계열 포함 | 내/외경, 나사 규격, 공차 |
| 테이퍼 가공 | TAPER | TAPER 계열 포함 (§2: 348-358, 10p) | 테이퍼 각도·깊이·공차 |
| 치과용 (Glass Ceramic, Zirconia, PMMA, Titanium-Alloy, Chrome Cobalt) | **DENTAL** | DENTAL CARBIDE ENDMILLS | 산업용과 구분, 치과 CAD/CAM 조건 |

### 5-3. 제품 선정 전 확인 체크리스트 (상담·발주 공통)

1. 소재명 + 경도(HRC) + 열처리 여부 + 난삭재 여부
2. 가공 방식: 드릴링 / 측면·홈·정삭·황삭 / T-slot / 나사 / 테이퍼
3. 공구 형태: 엔드밀 / 드릴 / 라우터 / T-CUTTER / Thread mill / Dental endmill
4. 치수: 공구 직경, 날장, 유효장, 전장, 샹크
5. 장비 조건: 강성, 스핀들 회전수 범위, 냉각 방식, 요구 표면조도·공차
6. 기존 문제: 치핑, 파손, 채터링, 칩 배출 불량, 수명 부족

> ⚠️ 가격·재고·납기·할인율은 이 자료(및 카탈로그)만으로 확정 불가 — 담당자/ERP 확인 필요. CBN "50시간" 등 수명 수치도 카탈로그 마케팅 표현이며 사내 실측 검증값이 아님(§8 사내 실사용 현황과 별도로 구분).

---

## 6. 카탈로그 사용법

### 6.1 텍스트 빠른 검색 (캐시 활용)

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
python scripts/pdf_search.py raw/Catalog/COGO.pdf "HARD"
python scripts/pdf_search.py raw/Catalog/COGO.pdf "AlCrN" --pages 216 218 220
python scripts/pdf_search.py raw/Catalog/COGO.pdf "TiSiN"
```

### 6.2 직접 PDF 열기

```powershell
start raw\Catalog\COGO.pdf
```

위 §2 시리즈 코드의 페이지로 즉시 이동.

### 6.3 위키에서 인용

- 출처 ID `[CAT-COGO]` 사용 ([[sources]] §3 참조), 2차 요약자료 인용 시 `[CAT-COGO-AISUM]`
- 페이지 번호 함께 명기: `[CAT-COGO p.155]` (SPEED 시리즈 시작점)

---

## 7. 관련 페이지

- [[jj-카탈로그]] — JJ TOOLS 카탈로그 인덱스 (자매 카탈로그)
- [[초경]] §8.3 — 사내 운영 등급 (카탈로그에서 매핑 후보)
- [[공구-코팅]] — 코팅 종류별 상세 (COGO는 영문 표기로 직접 매칭 가능)
- [[연삭-조건-목록]] — 형상별 조건
- `scripts/pdf_search.py` — 카탈로그 검색 도구

---

## 8. 사내 실사용 현황 (테스트 결과 요약)

> ⚠️ 아래 데이터는 사내 실측 테스트 기반 — 신뢰도: 사내 경험값.  
> 장비: CHEVALIER QP2040L (MCT)

### 8-1. COGO 알파(GPP) 드릴 — S45C 탄소강 (D5, 2날)

공구: `ONM050-2GPP050` (G-팡팡, L1=32mm, S5)

| 조건 | 결과 |
|------|------|
| N=2,500 rpm (Vc=39.3 m/min), Vf=300 mm/min | 마모 낮음, 치즐에지 형상 유지, 버 발생 눈에 띄게 적음 |
| 제조사 권장: N=2,450 rpm, Vf=360 mm/min | — |

- 종합 순위: **1위 (6종 중 최우수)** — 성능·버·마모 모두 우수.
- 상세: [[드릴-6종-비교-D5]]

### 8-2. COGO 부영(GBS) 드릴 — S45C 탄소강 (D5, 2날)

공구: `2GBS 050` (L1=32mm, S5)

| 조건 | 결과 |
|------|------|
| N=2,500 rpm (Vc=39.3 m/min), Vf=300 mm/min | 치즐에지 파손, 외주 코너 일부 파손. 버 발생은 눈에 띄게 적음 |
| 제조사 권장: N=2,400 rpm, fr=0.10~0.15 mm/rev | — |

- 종합 순위: **4위** — 버 발생은 적으나 마모·파손 형상으로 조건 조정 필요.
- 상세: [[드릴-6종-비교-D5]]

### 8-3. 카탈로그 파일 위치

| 파일 | 위치 |
|------|------|
| COGO.pdf (67 MB) | `raw/Catalog/COGO.pdf` (로컬, 2026-06-08 복원) |
| COGO.cache.json | `raw/Catalog/COGO.cache.json` (로컬) |

---

## 9. 변경 이력

- 2026-07-10 — §5 "소재·용도별 제품군 빠른 참조" 신규 추가 (`[CAT-COGO-AISUM]`, 사내 RAG 강의 실습 산출물 기반 2차 요약자료). 중복 번호(§6) 정리, §6~§8 재번호. (Cowork)
- 2026-06-08 — §6-3 파일 위치 서버→로컬 업데이트 (raw/Catalog/ 복원 완료). (Cowork)
- 2026-06-08 — §6 사내 실사용 현황 추가 (D5 드릴 비교 테스트 결과 집계). 카탈로그 파일 서버 이동 반영. (Cowork)
- 2026-05-12 — 신규 작성. COGO.cache.json 분석 기반 시리즈 코드·페이지·코팅 인덱스. JJ 대비 영문 코팅 표기로 위키 cross-reference 직접 가능. (Cowork)

---

> **확장 후보** (시간 날 때):
> - 자주 사용하는 시리즈(HARD, SPEED, DRILL)의 상세 spec 추출 → 독립 페이지
> - COGO PDF의 깨진 한글 텍스트 처리 — `(cid:NNN)` 패턴 디코딩 또는 OCR 재추출
> - 사내 입출고 데이터와 카탈로그 코드 매핑표
