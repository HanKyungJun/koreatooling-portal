---
type: report
tags: [ISO, 표준, 공구연삭, 참조, ANCA, ResinBond, 초경]
sources:
  - "[STD-ISO12413]"
updated: 2026-05-14
---

# ISO 표준 참조집 — 공구연삭 (ANCA × Resin Bond Diamond × WC)

작성: TOOL KOREA / 한경준 (사내 기술자료)
분류: 사내 참조 카탈로그 (1차 표준 메타데이터 인덱스)
대상 공정: ANCA CNC tool grinder × Resin bond diamond #320~#400 × 초경(WC-Co) 엔드밀 가공
연결 자료: `한글_그라인딩_통합계산기_v4.xlsx`(현재) / `_v5.xlsx`(예정)

---

## 1. 머리말 — 본 문서의 성격과 한계

### 1-1. 본 문서가 담는 것

각 ISO 표준의 **메타데이터(번호·제목·연도·스코프 요약·우리 적용·공식 링크)**를 정리한 사내 참조 인덱스. 본문 텍스트가 아닌 **카탈로그**다.

### 1-2. 본 문서가 담지 않는 것

ISO 표준 본문(Full text)은 ISO와 회원 표준 기관의 저작물이므로 본 문서에 복사·재배포하지 않는다. 본문은 KSA(한국표준협회) 또는 ISO Store에서 정식 구매 후 별도 보안 폴더에 보관한다.

### 1-3. 스코프 요약(Scope Summary) 표기 원칙

각 표준의 스코프 요약은 ISO 본문을 직접 인용한 것이 아니라 **우리 표현으로 paraphrase한 안내문**이다. 정확한 적용 범위·조항은 반드시 정식 표준 본문을 확인할 것.

### 1-4. 적용 등급 (Tier) 정의

| Tier | 의미 | 보유 권장도 |
|---|---|---|
| **Tier 1** | 우리 공정에서 직접 적용·인용되는 표준 | 사내 보유 필수 |
| **Tier 2** | 간접 적용·교차 참조용 표준 | 사내 보유 권장 |
| **Tier 3** | 관련 분야 / 향후 확장 시 필요 | 카탈로그만 보유 |

---

## 2. 분야별 ISO 표준 정리

### 2-1. 기준 온도 / 측정 환경

#### ISO 1:2016 — Standard reference temperature for the specification of geometrical and dimensional properties

- **Tier**: 1
- **연도**: 2016 (현재 최신)
- **스코프 요약**: 기하·치수 사양에서 사용하는 표준 기준 온도를 **20 °C**로 규정. 모든 도면 치수·측정값은 20 °C 기준으로 보정해 비교한다는 국제 합의 기준.
- **우리 적용**: 09 시트 §6 권장 쿨런트 온도 영역 anchor (“정밀 측정실 환경 20 °C”의 직접 출처)
- **공식 링크**: https://www.iso.org/standard/67630.html
- **보유 상태**: 미보유 (KSA 또는 ISO Store에서 구매 가능)

---

### 2-2. 머신 공구 시험 (ISO 230 시리즈)

#### ISO 230-1:2012 — Test code for machine tools — Part 1: Geometric accuracy of machines operating under no-load or quasi-static conditions

- **Tier**: 2
- **연도**: 2012 (현재 최신)
- **스코프 요약**: 무부하·준정적 조건에서 공작기계의 기하 정확도를 시험하는 방법을 규정. 직선도·평면도·축 직각도 등의 기본 정확도 측정 절차.
- **우리 적용**: ANCA tool grinder 정확도 검증 (간접) — 형상 오차 원인 분석 시 머신 기하 오차 확인
- **공식 링크**: https://www.iso.org/standard/46449.html
- **보유 상태**: 미보유

#### ISO 230-2:2014 — Test code for machine tools — Part 2: Determination of accuracy and repeatability of positioning of numerically controlled axes

- **Tier**: 2
- **연도**: 2014 (현재 최신)
- **스코프 요약**: NC 축의 위치결정 정확도와 반복도를 직접 측정·평가하는 방법.
- **우리 적용**: ANCA NC 축 위치 정밀도 검증 (간접) — Drill X Distance 같은 미세 보정값 검증의 근거
- **공식 링크**: https://www.iso.org/standard/55295.html
- **보유 상태**: 미보유

#### ISO 230-3:2020 — Test code for machine tools — Part 3: Determination of thermal effects

- **Tier**: 1
- **연도**: 2020 (현재 최신)
- **스코프 요약**: 공작기계의 열적 영향(환경 변화·내부 발열·축 회전열)에 의한 변위를 측정·평가하는 시험 방법을 규정.
- **우리 적용**: 09 시트 § 전체 — 쿨런트 온도 변동에 따른 열변형 평가의 1차 표준 출처
- **공식 링크**: https://www.iso.org/standard/73291.html
- **보유 상태**: 미보유 (Tier 1 — 보유 필요)

#### ISO 230-7:2015 — Test code for machine tools — Part 7: Geometric accuracy of axes of rotation

- **Tier**: 2
- **연도**: 2015 (현재 최신)
- **스코프 요약**: 공작기계 회전축(스핀들 등)의 기하 정확도(런아웃·기울어짐 등) 시험 방법.
- **우리 적용**: ANCA 휠 스핀들 정확도 검증 (간접) — 휠 런아웃이 형상 정밀도에 미치는 영향 분석
- **공식 링크**: https://www.iso.org/standard/56624.html
- **보유 상태**: 미보유

---

### 2-3. 머신 공구 안전

#### ISO 16089:2015 — Machine tools — Safety — Stationary grinding machines

- **Tier**: 1
- **연도**: 2015 (현재 최신)
- **스코프 요약**: 정치형 연삭기(고정식 그라인딩 머신)의 안전 요구사항. 가드, 인터록, 비상 정지, 휠 폭주 시 안전 등을 규정.
- **우리 적용**: ANCA 머신 안전 점검 / 사내 안전 교육의 근거
- **공식 링크**: https://www.iso.org/standard/55504.html
- **보유 상태**: 미보유 (Tier 1 — 보유 필요)
- **참고**: 대응 한국 표준 KS B ISO 16089 존재 여부 확인 권장

---

### 2-4. 연삭숫돌 (Bonded Abrasive) 일반

#### ISO 525:2020 — Bonded abrasive products — Shape types, designation and marking

- **Tier**: 1
- **연도**: 2020 (현재 최신, 2013 → 2020 5판으로 갱신)
- **스코프 요약**: 본드 연삭숫돌의 형상 종류·식별 코드·마킹 방식을 규정. 휠 형상 코드(Type 1, 6A2, 11V9 등)와 표기 규칙.
- **우리 적용**: “5도 휠 1-2”, “20도 휠 1-1”, “컵 휠 1-2” 같은 사내 식별 코드의 표준 매핑 (간접)
- **공식 링크**: https://www.iso.org/standard/78476.html
- **보유 상태**: 미보유 (Tier 1 — 보유 필요)
- **갱신 주의**: 2020년 개정으로 제목·구조가 “General requirements” → “Shape types, designation and marking”으로 변경됨. 구판(2013) 자료 참조 시 주의.

#### ISO 603 시리즈 — Bonded abrasive products — Dimensions

- **Tier**: 3
- **연도**: 파트별로 상이 (파트 별 발행 연도 확인 필요)
- **스코프 요약**: 본드 연삭숫돌 각 형상별 표준 치수. ISO 525와 함께 활용.
- **우리 적용**: 향후 휠 신규 도입 시 치수 확인 (참고용)
- **공식 링크**: ISO 검색에서 “ISO 603”
- **보유 상태**: 미보유 / 카탈로그만

---

### 2-5. 연삭숫돌 안전

#### ISO 12413:2019 — Bonded abrasive products — Safety requirements

- **Tier**: 1
- **연도**: 2019 (현재 최신)
- **스코프 요약**: 본드 연삭숫돌의 안전 요구사항. 정격 최대 원주속도(Vmax) 표시·시험·강도 규정.
- **우리 적용**: 휠 정격 Vmax 확인의 근거. 09 시트 §6 운영 영역 상한 검토 시 직접 인용
- **공식 링크**: https://www.iso.org/standard/72906.html
- **보유 상태**: 미보유 (Tier 1 — 보유 필요)
- **국내 매칭**: KS B 5023 (연삭숫돌 안전성)이 유사 영역 다룸

---

### 2-6. 연삭숫돌 균형 / 허용 편차

#### ISO 6103:2014 — Bonded abrasive products — Permissible unbalances of grinding wheels as delivered — Static testing

- **Tier**: 1
- **연도**: 2014 (현재 최신)
- **스코프 요약**: 출하 상태 연삭숫돌의 허용 정적 불균형 한계와 시험 방법.
- **우리 적용**: 휠 입고 검사 / 밸런싱 기준 (간접) — 휠 런아웃 / 진동이 형상 오차에 미치는 영향
- **공식 링크**: https://www.iso.org/standard/61991.html
- **보유 상태**: 미보유 (Tier 1 — 보유 권장)

#### ISO 13942:2000 — Bonded abrasive products — Limit deviations and run-out tolerances

- **Tier**: 3
- **연도**: 2000 (확인 필요 — 갱신판 존재 여부 KSA 통해 재확인 권장)
- **스코프 요약**: 본드 연삭숫돌의 치수 한계편차·런아웃 허용공차.
- **우리 적용**: 휠 입고 검사 시 치수 정확도 기준 (참고)
- **공식 링크**: ISO 검색
- **보유 상태**: 미보유 / 카탈로그만

---

### 2-7. 초연마 (Diamond / CBN)

#### ISO 6104:2005 — Superabrasive products — Rotating grinding tools with diamond or cubic boron nitride — General survey, designation and multilingual nomenclature

- **Tier**: 1
- **연도**: 2005 (현재 최신, 1979 → 2005)
- **스코프 요약**: 다이아몬드·CBN 회전 연삭공구의 일반 분류·식별 코드·다국어 명칭. 우리가 쓰는 resin bond diamond 휠 식별 표준.
- **우리 적용**: 휠 spec 표기 표준화 (간접) — “Resin bond / Diamond / D126 / 100 concentration” 같은 코드 매핑
- **공식 링크**: https://www.iso.org/standard/36553.html
- **보유 상태**: 미보유 (Tier 1 — 보유 필요)

#### ISO 6106:2013 — Abrasive products — Checking the grit size of superabrasives

- **Tier**: 3
- **연도**: 2013 (확인 필요)
- **스코프 요약**: 초연마 그릿 크기(#320, #400 등) 검사 방법.
- **우리 적용**: 휠 그릿 검증 (참고용)
- **공식 링크**: ISO 검색
- **보유 상태**: 미보유 / 카탈로그만

---

### 2-8. 표면조도 (Surface Texture)

#### ISO 4287:1997 — Geometrical Product Specifications (GPS) — Surface texture: Profile method — Terms, definitions and surface texture parameters

- **Tier**: 1
- **연도**: 1997 (개정판 ISO 21920 시리즈로 대체 진행 중 — 갱신 동향 확인 권장)
- **스코프 요약**: 표면조도 프로파일 방식의 용어·정의·파라미터(Ra, Rz, Rq 등) 표준 정의.
- **우리 적용**: 03 시트 절삭강도/Ra 계산기 — Ra 정의의 1차 표준 출처
- **공식 링크**: https://www.iso.org/standard/10132.html
- **보유 상태**: 미보유 (Tier 1 — 보유 필요)
- **갱신 동향**: ISO 21920-2:2021 시리즈가 일부 영역 대체 중. 향후 검토.

#### ISO 4288:1996 — Geometrical Product Specifications (GPS) — Surface texture: Profile method — Rules and procedures for the assessment of surface texture

- **Tier**: 2
- **연도**: 1996 (ISO 21920 시리즈로 대체 진행 중)
- **스코프 요약**: 표면조도 측정 시 cutoff 길이 선택, 평가 길이, 측정 절차 규칙.
- **우리 적용**: 표면조도 측정 표준 절차 (간접)
- **공식 링크**: https://www.iso.org/standard/10134.html
- **보유 상태**: 미보유

---

### 2-9. 공차 / 검사

#### ISO 286-1:2010 — Geometrical product specifications (GPS) — ISO code system for tolerances on linear sizes — Part 1: Basis of tolerances, deviations and fits

- **Tier**: 2
- **연도**: 2010 (현재 최신)
- **스코프 요약**: 선형 치수의 ISO 공차 코드 시스템(H7, h6 등). 도면 공차 표기와 fit/tolerance 관계 규정.
- **우리 적용**: 도면 공차 해석 표준 (간접)
- **공식 링크**: https://www.iso.org/standard/45975.html
- **보유 상태**: 미보유

#### ISO 14253-1:2017 — Geometrical product specifications (GPS) — Inspection by measurement of workpieces and measuring equipment — Part 1: Decision rules for verifying conformity or nonconformity with specifications

- **Tier**: 2
- **연도**: 2017 (현재 최신)
- **스코프 요약**: 측정 결과의 적합·부적합 판정 규칙. 측정 불확도를 어떻게 판정에 반영할지 규정.
- **우리 적용**: 09 시트 §5 정밀도 판정의 절차적 근거 (간접)
- **공식 링크**: https://www.iso.org/standard/70137.html
- **보유 상태**: 미보유

---

### 2-10. 금속가공 윤활제

#### ISO 6743-7 — Lubricants, industrial oils and related products (Class L) — Classification — Part 7: Family M (metalworking)

- **Tier**: 3
- **연도**: 발행 연도 확인 필요
- **스코프 요약**: 금속가공용 윤활제(쿨런트 포함) 분류 체계. Family M 코드.
- **우리 적용**: 쿨런트 spec 표기 표준화 (참고용)
- **공식 링크**: ISO 검색
- **보유 상태**: 미보유 / 카탈로그만

---

### 2-11. 품질 시스템

#### ISO 9001:2015 — Quality management systems — Requirements

- **Tier**: 2
- **연도**: 2015 (현재 최신)
- **스코프 요약**: 조직의 품질경영시스템 요구사항. 문서 관리, 추적성, 변경 관리 등.
- **우리 적용**: 본 카탈로그·계산기 문서의 변경 이력 관리 근거 (간접)
- **공식 링크**: https://www.iso.org/standard/62085.html
- **보유 상태**: 회사 인증 보유 여부에 따라 다름

---

## 3. 우리 워크북 — ISO 표준 cross-reference 요약

| 워크북 위치 | 직접 anchor된 ISO 표준 |
|---|---|
| 09 시트 §6 권장 온도 (20 °C) | ISO 1:2016 |
| 09 시트 § 전체 (열변형) | ISO 230-3:2020 |
| 09 시트 §5 정밀도 판정 | ISO 14253-1:2017 |
| 휠 식별 (5도/20도/컵 휠) | ISO 525:2020, ISO 6104:2005 |
| 휠 정격 Vmax | ISO 12413:2019 |
| 머신 안전 일반 | ISO 16089:2015 |
| 휠 균형 / 입고 검사 | ISO 6103:2014 |
| Ra 정의 (03 시트) | ISO 4287:1997 |
| 도면 공차 해석 | ISO 286-1:2010 |
| 변경 이력 관리 | ISO 9001:2015 |

---

## 4. 구매 / 접근 경로

### 4-1. 한국 채널 (권장 — 한국어 매칭본 확인 가능)

- **한국표준협회(KSA) e-Standard**: https://www.ksa.or.kr/
  - ISO 표준 단권 구매 가능 (영문 원본)
  - 일부는 KS 표준으로 한국어 채택본 존재 (예: KS B ISO 16089)
  - 가격: 통상 5만~30만 원대 (페이지 수에 비례)
- **국가표준 종합정보센터 e-나라표준인증**: https://standard.go.kr/
  - KS 표준 무료 열람 가능 (다운로드 일부 제한)
  - ISO와 매칭된 KS 번호 확인용

### 4-2. 직접 ISO Store

- **ISO Store**: https://www.iso.org/store.html
  - 영문 원본, USD 단위
  - PDF 다운로드 또는 종이 인쇄본
  - 멀티 라이센스 / 사이트 라이센스 옵션 있음

### 4-3. 사내 활용 시 라이센스 주의

- 단권 구매: 통상 1인 1라이센스 (사내 공유 시 추가 라이센스 필요)
- 멀티 라이센스: 사용자 수에 따라 산정
- 인쇄 / 사본 / 디지털 배포 제약 확인 필수

---

## 5. 갱신 추적 가이드

ISO 표준은 통상 5~10년 주기로 개정된다. 본 카탈로그의 각 항목은 **최소 연 1회 KSA 또는 ISO 검색에서 갱신 여부를 확인**할 것.

특히 다음 표준은 갱신·대체 동향이 활발하다:

- **ISO 4287 / 4288 → ISO 21920 시리즈로 대체 진행 중** (2021~) — 표면조도
- **ISO 525**: 2013 → 2020에서 제목·구조 변경 사례 — 향후 추가 개정 가능성
- **ISO 230 시리즈**: 자주 amendment 추가 (-2:2014/Amd 1 등)

확인 시 보는 지표:
1. ISO 공식 페이지의 “Status”가 “Published” 인지 “Withdrawn” 인지
2. “Latest version” 표시 연도
3. “Replaces” / “Replaced by” 항목

---

## 6. 사내 보유 상태 추적 표 (별도 관리)

본 표는 사내에서 구매한 표준 PDF의 보유 상태를 추적한다. 본 카탈로그 갱신 시 함께 업데이트.

| ISO 번호 | 보유 상태 | 보유 위치 | 구매일 | 라이센스 | 비고 |
|---|---|---|---|---|---|
| ISO 1:2016 | 미보유 | — | — | — | Tier 1 |
| ISO 230-3:2020 | 미보유 | — | — | — | Tier 1 |
| ISO 525:2020 | 미보유 | — | — | — | Tier 1 |
| ISO 6104:2005 | 미보유 | — | — | — | Tier 1 |
| ISO 12413:2019 | 미보유 | — | — | — | Tier 1 |
| ISO 16089:2015 | 미보유 | — | — | — | Tier 1 |
| ISO 6103:2014 | 미보유 | — | — | — | Tier 1 |
| ISO 4287:1997 | 미보유 | — | — | — | Tier 1 |
| (이하 Tier 2~3 생략) | | | | | |

---

## 7. 권장 우선 구매 순서 (예산 단계별)

**1차 (Tier 1, 8건) — 사내 운영 1차 표준**
ISO 1, ISO 230-3, ISO 525, ISO 6104, ISO 12413, ISO 16089, ISO 6103, ISO 4287

**2차 (Tier 2 선별, 4건) — 운영 정밀화**
ISO 230-1, ISO 230-2, ISO 14253-1, ISO 286-1

**3차 (필요 시, 7건) — 확장 / 보조**
ISO 230-7, ISO 4288, ISO 9001, ISO 13942, ISO 6106, ISO 603 시리즈, ISO 6743-7

---

## 8. 변경 이력 (본 카탈로그)

| 버전 | 일자 | 내용 |
|---|---|---|
| v1.0 | 2026-05 | 초판 — Tier 1 (8건) + Tier 2 (7건) + Tier 3 (4건) 19건 정리. v4 워크북과 cross-reference. |

---

## 9. 관련 사내 자료

- `한글_그라인딩_통합계산기_v4.xlsx` — 본 카탈로그가 anchor하는 계산기
- `한글_그라인딩_통합계산기_v5.xlsx` (예정) — ISO 매핑 시트 추가본
- `Brinksmeier_2006_검증_백업.md` — 학술 인용 검증 백업
- `Pre_Machining_Analysis_Report.docx` — 가공 전 분석 보고서 (관련 표준 참조)
- `grinding_academic_reference.docx` — 학술 근거 문서

---

## 10. 면책 사항

본 카탈로그의 스코프 요약은 우리 사내 사용을 돕기 위한 안내문이며 ISO 표준 본문을 대체할 수 없다. 정식 적용·증거·계약·인증 목적으로는 반드시 정식 표준 본문을 구매·확인할 것. 본 카탈로그의 정확성은 작성 시점 기준이며 ISO 갱신에 따라 변경될 수 있다.
