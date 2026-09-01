---
type: cadcam
category: "엔드밀 설계·연삭"
subcategory: "고성능 엔드밀 제작 — Part 1 형상 설계"
source_author: "Thomson Mathew (ANCA Software Product Manager)"
source_publisher: "ANCA Pty Ltd — e-Sharp News, 2022년 1월호"
source_url: "https://machines.anca.com/e-sharp-news/january-2022/how-to-grind-a-high-performance-endmill-part-1"
source_publish_date: "2022-01-13"
source_series: "5-part instructional series — Part 1 of 5"
tags: [엔드밀, endmill, 고성능, helix, variableHelix, chatter, ANCA, ToolRoom, RN34, ThomsonMathew]
sources:
  - "[VEN-ANCA-MATHEW2022] Thomson Mathew — 'Your technical guide to grinding a high performance endmill (part one)'. ANCA e-Sharp News, 2022-01"
  - "[ACA-ENGIN2001] Engin & Altintas (2001). Mechanics and dynamics of general milling cutters. Int. J. MTM, 41(15), 2195-2212 — 엔드밀 강성 학술"
  - "[ACA-SMITH2008-CTT] Smith, G.T. (2008). Cutting Tool Technology. Springer. Ch.5 엔드밀"
  - "[ACA-INASAKI2001] Inasaki et al. (2001). Grinding chatter — CIRP Annals 50(2)"
  - "[ACA-STEPHENSON2016] Stephenson & Agapiou (2016). Metal Cutting Theory and Practice"
updated: 2026-05-18
status: "ANCA e-Sharp 2022-01 영문 원문 정리 + 본 위키 정합 주석. Part 1 of 5 시리즈, Part 2~5는 미정착"
---

# 고성능 엔드밀 제작 가이드 Part 1 — 형상 설계·파라미터 검증

> 본 페이지는 **Thomson Mathew** (ANCA Software Product Manager)가 ANCA *e-Sharp News* 2022년 1월호에 게시한 *"Your technical guide to grinding a high performance endmill (part one)"* 영문 원문을 정리하고, 본 위키의 정착된 1차 출처와의 정합 주석을 추가한 자료입니다.
>
> 원문: <https://machines.anca.com/e-sharp-news/january-2022/how-to-grind-a-high-performance-endmill-part-1>
>
> 신뢰도: **★★★★☆** (Tier 1.5 — ANCA Software Product Manager, 절삭공구 산업 25년 경력, 다수 ANCA 소프트웨어 아키텍트)
>
> **시리즈**: 본 자료는 **5부 시리즈의 Part 1**. Part 2~5는 본 위키 미정착 (다음 세션 후속 작업).
> **Part 1 주제**: 형상 설계(Geometry Design)와 파라미터 검증.

---

## 1. 엔드밀 성능에 영향을 미치는 4대 요인 ★★★

모든 엔드밀은 **설계**로부터 시작하며, 잘 설계된 형상이 고성능 엔드밀을 만듭니다.

| # | 요인 | 영향 |
|---|------|------|
| 1 | **카바이드 소재의 등급·품질** | 경도 (매트릭스 내 카바이드 등급에 의존. **작은 입자 = 더 단단한 공구**) |
| 2 | **절삭공구 형상 설계** | **본 자료 핵심** — 형상이 차지하는 비중 압도적 |
| 3 | **정밀 제조 공정 / 품질 관리** | 일관된 결과 보장 |
| 4 | **코팅 종류** | 수명·절삭 성능 향상 |

> ★ 핵심 인용: **"But geometry has an outsized role"** — 형상의 역할이 비대.

### 1.1 본 위키 정합 — 4대 요인 ↔ 본 위키 페이지

| 본 자료 요인 | 본 위키 매핑 |
|------------|-----------|
| 카바이드 등급 | [[초경]] §3 (ISO 513 P/M/K/N/S/H 분류, Co 함량, 입자 크기) |
| 형상 설계 | [[공구-코어-직경]] (dc/D 코어 비율 17개 형상 표준값) |
| 정밀 제조·품질 관리 | [[재연마-프로그램-워크플로우]] (CAD→CAM→시뮬→머신→검증 7단계) |
| 코팅 | [[공구-코팅]] (TiN/TiCN/TiAlN/AlTiN/AlCrN/DLC/PCD 등) |

→ 본 자료의 4대 요인이 **본 위키의 4개 핵심 페이지**로 정확히 매핑.

---

## 2. 형상 설계의 주요 요소

엔드밀 설계의 주요 인자들:

1. **Variable helix + Index flute** 결합 형상 설계
2. **Core geometry** 설계 (= [[공구-코어-직경]] dc/D)
3. **OD clearance 각도** — eccentric vs facet relief 설계
4. **End face 설계** — wiper flats + pad grinding 또는 end dubbing

> ⚠️ "Endmill set" 단위 = 사용자가 한 번에 가공하는 엔드밀의 묶음.

### 2.1 본 위키 정합 — Core Geometry

본 자료의 "Core geometry design"은 [[공구-코어-직경]] (2026-05-14 신규)와 직접 대응:
- dc/D 코어 비율 17개 형상 권장값
- 사내 가공 데이터 (181004garam dc/D=0.667 등 실측 사례)

---

## 3. "Weird" Endmills — 채터링 회피의 진화 ★★★

업계 발전은 엔드밀이 점점 **"이상한(weird)" 모양**으로 변화하는 과정을 봐왔습니다. 공구 제작자들이 **높은 재료 제거율(MRR)을 추구하면서 채터링 회피**를 시도했기 때문입니다.

### 3.1 채터링이란?

**Regenerative chatter** = 공구와 공작물 사이의 **하모닉(harmonics)이 다른 주파수**일 때 발생.

| 현상 | 결과 |
|------|------|
| 두 자가 진동 객체가 서로 충돌 | 표면 마감 ↓ |
| | 치수 정확도 ↓ |
| | 공구·기계 수명 ↓ |
| | 생산성·수익성 ↓ |

> 출처 (학술): [ACA-INASAKI2001] Inasaki, I., Karpuschewski, B., & Lee, H.S. (2001). Grinding chatter — Origin and suppression. *CIRP Annals*, 50(2), 515-534.

---

## 4. Helix 각도 — Low vs High ★★★

### 4.1 High Helix (> 35°)

| 항목 | High Helix |
|------|-----------|
| 강도·이송속도·칩 배출률 | **빠름** — 인기 |
| 단단한 소재 적용 | ✅ 우수 (Low Helix 대비) |
| **채터링** | ❌ **더 발생하기 쉬움** (Low Helix 대비) |
| 절삭력 방향 | **수직 성분 ↑** (수평 성분 ↓) — 공구 변형 ↓ |
| 축방향 rake | **양각 ↑** → 절삭력 ↓ → 이송속도 ↑ 가능 |
| 코어 두께 | **두꺼움** (헬릭스 형상으로 인해) — 공구 강성 ↑ |
| 적용 소재 | 단단한 합금 (and 알루미늄 같은 연한 재료에도 사용) |
| 단점 | **채터링 ↑** + 소재에 강하게 파고듦 |

### 4.2 Low Helix (15° 부근)

| 항목 | Low Helix |
|------|----------|
| 채터링 | ✅ 덜 발생 |
| 연한 소재 | ✅ 우수 |
| 이송속도·MRR | **낮음** (단점) |

### 4.3 본 위키 정합 — Helix 각도 ↔ 보유 휠 5종

본 위키 [[휠-20도-Ø125-1-1]] 등 5종 휠은 **공구의 helix 각도가 아닌 휠 자체의 V 각도**:
- 휠 V 각도 (5°, 20°, 45°) ≠ 엔드밀 helix 각도 (15°~60°)
- 그러나 휠의 V 각도와 helix gash 가공 사이에 **간접 관계** 존재:
  - V 5° 휠 ([[휠-5도-Ø125-1-2]]): Low helix gash 가공
  - V 45° 휠 ([[휠-45도-Ø125-1-2]]): 깊은 gash 가공

> 자세한 관계는 [[홍익다이아-Flute-Gash-휠]] §1V1, §3V1 (V 5°~45° 9단계) 참조.

### 4.4 본 위키 [[공구-코어-직경]]와의 정합

본 자료: "High helix → 코어 두께 ↑ → 강성 ↑"

[[공구-코어-직경]] (2026-05-14)의 dc/D 권장값:
- 스퀘어 엔드밀: dc/D 0.55
- 볼 엔드밀: dc/D 0.50
- High helix tools는 코어가 자연 두꺼워지므로 dc/D 권장값과 일관

---

## 5. Variable Helix Endmills — 최첨단 기술 ★★★

> "Variable helix end mills with variable index are considered **state of the art** these days."

### 5.1 정의

- 헬릭스를 **flute 길이를 따라 또는 flute-to-flute로 변동**
- 목적: **채터링 억제**

### 5.2 작동 메커니즘

```
채터링 = 공명 효과 (Resonance effect)
       ↓
공명 깨뜨림 (Break up resonance)
       ↓
Flute가 공작물에 부딪히는 패턴을 다양화
       ↓
채터링 ↓
```

> ★ 핵심: 공명을 깨뜨리는 모든 행위가 채터링 감소에 기여.

### 5.3 ANCA ToolRoom RN34 — 공구 밸런싱

본 자료 시점: ANCA의 **ToolRoom RN34 릴리스의 공구 밸런싱 기능**이 채터링 대응의 완벽한 솔루션으로 제시됨.

> ⚠️ 시대성: 본 자료 시점(2022-01) 이후 ToolRoom RN35 출시(2025-03, Feedrate Optimisation). 본 자료의 "RN34"는 이전 버전.

---

## 6. 본 위키 정합 종합 평가

### 6.1 본 자료의 본 위키 적용 가치

| 본 자료 권장 | 본 위키 매핑 | 가치 |
|------------|-----------|------|
| 4대 성능 요인 | [[초경]] / [[공구-코어-직경]] / [[재연마-프로그램-워크플로우]] / [[공구-코팅]] | 🟢 **체계적 매핑** — 본 위키 정착 확인 |
| High helix → 코어 두께 ↑ → 강성 ↑ | [[공구-코어-직경]] dc/D 권장값 | 🟢 강성 메커니즘 보강 |
| Variable helix + index → 채터링 ↓ | [[표면조도-불량]] §2 채터링 메커니즘 | 🟢 채터링 대응 신기술 추가 |
| Weird endmills + 카오스 공명 깨뜨림 | (본 위키 미수록) | 🟡 신규 정보 — 향후 채터링 트러블슈팅 페이지 작성 시 인용 |
| ToolRoom RN34 공구 밸런싱 | (본 위키 미수록) | 🟡 ANCA 운영 노하우 |

### 6.2 시리즈 Part 2~5 — 미정착

본 자료는 5부 시리즈 중 Part 1. 나머지 4부:

| Part | 추정 주제 (본 자료 §1 4대 요인 기반) |
|------|------------------------------|
| Part 1 (본 페이지) | **형상 설계·파라미터 검증** ✅ 정착 |
| Part 2 | (추정) 카바이드 등급 선택 |
| Part 3 | (추정) 정밀 제조·품질 관리 |
| Part 4 | (추정) 코팅 |
| Part 5 | (추정) 종합·사례 |

> ⚠️ Part 2~5의 정확한 URL은 [[anca-esharp-index|ANCA e-Sharp News 전체 인덱스]] 추출 시 archive에서 자동 발견되지 않음. 직접 URL 또는 ANCA 사이트 검색 필요. **다음 세션 후속 작업**.

### 6.3 시대성

- 2022-01 자료 — ANCA ToolRoom RN34 시점
- 본 자료 시점 이후:
  - RN35 출시 (2025-03)
  - CIM3D V9 출시 (2025-02)
  - 본 자료의 "공구 밸런싱"은 [[휠-밸런싱-iBalance]] (Simon Richardson 2022-09)와 다른 개념 (공구 자체 vs 휠 자체)

### 6.4 학술적 위치

본 자료는 ANCA의 자사 소프트웨어(ToolRoom) 홍보 측면이 있으나, **형상 설계·채터링 메커니즘 자체는 학술 표준**:

| 본 자료 개념 | 학술 출처 |
|------------|---------|
| 엔드밀 강성 모델 | [ACA-ENGIN2001] Engin & Altintas (2001) — *Int. J. MTM* 41(15), 2195-2212 |
| 채터링 발생·억제 | [ACA-INASAKI2001] Inasaki et al. (2001) — *CIRP Annals* 50(2), 515-534 |
| 엔드밀 형상·코어·코팅 | [ACA-SMITH2008-CTT] Smith (2008) Ch.5 |
| 절삭 이론 종합 | [ACA-STEPHENSON2016] Stephenson & Agapiou (2016) |

---

## 7. 사내 적용 권장

### 7.1 보유 휠 5종 ↔ 엔드밀 helix 매칭

| 본 위키 휠 | 권장 helix 가공 |
|----------|--------------|
| [[휠-5도-Ø125-1-2]] (V 5°) | Low helix endmill (15°~20°) |
| [[휠-20도-Ø125-1-1]] (V 20°) | Mid helix endmill (25°~30°) |
| [[휠-45도-Ø125-1-2]] (V 45°) | High helix endmill (35°+) gash |
| [[휠-컵-Ø100-1-1]], [[휠-컵-Ø100-1-2]] | End face / clearance |

→ 추정 매칭, 실제는 사내 공정에 따라 검증 필요.

### 7.2 사내 변종 R&D ↔ Variable Helix 개념

[[공구사양-실험-이력]] (2026-05-14)의 14개 변종 그룹은 **Variable Helix·Variable Index 개념의 실험적 적용**으로 해석 가능. Box, Hunter & Hunter (2005) DoE 프레임과 결합 시 사내 R&D 체계화 기반.

---

## 8. 관련 페이지

### ANCA e-Sharp 시리즈
- [[anca-esharp-index|ANCA e-Sharp News 전체 인덱스]]
- [[연삭-테스트-방법]] — Walter Graf 2011 (6단계 방법론)
- [[휠-밸런싱-iBalance]] — Simon Richardson 2022-09
- [[MRR-기반-연삭공정-분석]] — Vadim Zaiser 2022-06
- [[연삭유-성능-가이드]] — Steven Lowery + Markus Munde 2022-03
- [[에너지효율-연삭-7가지팁]] — Kaine Mulder 2024-02

### 본 위키 정합 페이지 — 4대 요인 매핑
- [[초경]] — 카바이드 등급·품질 (ISO 513)
- [[공구-코어-직경]] — Core geometry (dc/D)
- [[재연마-프로그램-워크플로우]] — 정밀 제조·품질 관리
- [[공구-코팅]] — 코팅 종류

### 본 위키 정합 페이지 — Helix·채터링
- [[표면조도-불량]] §2 — 채터링 메커니즘
- [[공구사양-실험-이력]] — 사내 변종 R&D (Variable Helix 응용)
- [[홍익다이아-Flute-Gash-휠]] — 휠 V 각도와 helix gash

---

## 9. 참고 문헌

### 1차 출처 (본 자료)

- **Mathew, T. (2022).** *Your technical guide to grinding a high performance endmill (part one) — Geometry Design and Parameter Verification*. ANCA *e-Sharp News*, January 2022. https://machines.anca.com/e-sharp-news/january-2022/how-to-grind-a-high-performance-endmill-part-1
  - Thomson Mathew — ANCA Software Product Manager (절삭공구 산업 25년 경력)
  - 시리즈 1/5

### 학술 (정합 보강)

- **Engin, S. & Altintas, Y. (2001).** Mechanics and dynamics of general milling cutters. *International Journal of Machine Tools and Manufacture*, 41(15), 2195-2212. — 엔드밀 강성·동역학.
- **Inasaki, I., Karpuschewski, B., & Lee, H.S. (2001).** Grinding chatter — Origin and suppression. *CIRP Annals*, 50(2), 515-534. — 채터 발생·억제.
- **Smith, G.T. (2008).** *Cutting Tool Technology: Industrial Handbook*. Springer. Ch.5 엔드밀 — 형상·코어·코팅·수명.
- **Stephenson, D.A. & Agapiou, J.S. (2016).** *Metal Cutting Theory and Practice* (3rd ed.). CRC Press.
- **Tlusty, J., Smith, S., & Zamudio, C. (1979).** New NC routines for quality in milling. *CIRP Annals*, 29(1), 295-300. — 볼노즈 엔드밀 코어·강성 균형.

### 본 자료 인용 외부 출처

- CNCCookBook — *Solid Carbide End Mill Coatings Grades Geometries*. https://www.cnccookbook.com/solid-carbide-end-mill-coatings-grades-geometries/
- Modern Machine Shop — *Reducing chatter with weird endmills in CNC machining*. https://www.mmsonline.com/articles/reducing-chatter-with-weird-endmills-in-cnc-machining
- CNCCookBook — *Chatter in machining*. https://www.cnccookbook.com/chatter-in-machining-milling-lathe-vibration/

---

## 10. 변경 이력

- **2026-05-18** — 신규 작성. Thomson Mathew 2022-01 영문 원문 정리 + 본 위키 정합 주석. 4대 성능 요인 (카바이드·형상·제조품질·코팅) + 본 위키 4개 페이지 매핑 + High vs Low helix + Variable helix index (채터링 회피) + ToolRoom RN34. Part 2~5 미정착 (다음 세션 후속). 학술: Engin & Altintas 2001 / Inasaki 2001 / Smith 2008 인용. (Cowork)
