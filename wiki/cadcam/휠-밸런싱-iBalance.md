---
type: cadcam
category: "휠 운영 — 진동 제어"
subcategory: "휠 밸런싱"
source_author: "Simon Richardson (ANCA)"
source_publisher: "ANCA Pty Ltd — e-Sharp News, 2022년 9월호"
source_url: "https://machines.anca.com/e-sharp-news/september-2022/a-fine-balancing-act-how-to-correctly-balance-grin?lang=ko-KR"
source_publish_date: "2022-09-08"
tags: [휠밸런싱, iBalance, 진동제어, ANCA, SimonRichardson, 스핀들, 표면조도]
sources:
  - "[VEN-ANCA-RICHARDSON2022] Simon Richardson — 'A fine balancing act: how to correctly balance grinding wheels on an ANCA machine'. ANCA e-Sharp News, 2022-09"
  - "[VEN-NORTON-WINTER-2023] Saint-Gobain Norton Winter Tool Grinding Catalog 2023 — 진동 안정성 관련"
  - "[ACA-INASAKI2001] Inasaki et al. (2001). Grinding chatter — Origin and suppression. CIRP Annals — 채터·진동 학술 근거"
  - "[STD-ISO12413] ISO 12413:2019 — Bonded abrasive products safety"
updated: 2026-05-18
status: "ANCA e-Sharp 2022-09 원문 정리 + 본 위키 정합 주석. 한국어 원문 정상 추출"
---

# 정밀한 밸런싱 잡기 — ANCA iBalance (휠 밸런싱)

> 본 페이지는 **Simon Richardson** (ANCA)이 ANCA *e-Sharp News* 2022년 9월호에 게시한 *"정밀한 밸런싱 잡기: ANCA 기계에서 그라인딩 휠의 균형을 올바르게 맞추는 방법"* 한국어 원문을 정리하고, 본 위키의 정착된 1차 출처와의 정합 주석을 추가한 자료입니다.
>
> 원문: <https://machines.anca.com/e-sharp-news/september-2022/a-fine-balancing-act-how-to-correctly-balance-grin?lang=ko-KR>
>
> 신뢰도: **★★★★☆** (ANCA 1차, 본 위키 사용 ANCA 장비 직접 대응)

---

## 1. 휠 진동 — 그라인딩의 적

정확하게 밸런싱이 잡힌 휠은 우수한 표면 마감이 가능하며 복잡한 형상도 만들어낼 수 있습니다. 이런 이유에서 모든 고품질의 그라인더는 그라인딩 작업의 적이 바로 **진동**이라는 것을 알고 있습니다.

휠이 균형을 잃게 되면 기계의 스핀들 집합 전체에서 진동이 느껴집니다. 심한 경우에는, 휠 불균형이 기계 전체에 걸쳐 느껴질 수 있습니다. 이로 인해:

1. 휠이 과도하게 마모될 수 있음
2. 툴이 부정확하게 제조됨
3. 툴 표면 마감 불량으로 이어짐

> **그라인딩 휠이 진동을 유발하는 경우에는, 견고한 그라인딩 기계를 사용한다고 해도 해결되지 않습니다.**

### 1.1 본 위키 정합 — 본 위키 [[tools/wheels/catalog/index|홍익다이아 카탈로그]] 보유 휠과의 관계

본 위키 보유 휠 5종(Ø125·Ø100 Resin Bond Diamond, 결합도 R)도 모두 ANCA tool grinder에 장착되어 사용. 본 자료의 진동 제어 원리는 직접 적용 가능. 본 위키 [[휠RPM-정책-검증-노트]]의 Vc 18-25 m/s 범위 운영 중에도 휠 불균형이 있으면 동일 Vc에서도 진동 발생 → 표면조도 ↓.

---

## 2. 밸런싱의 3가지 옵션

회전하는 개체의 밸런싱을 맞추는 경우, 단 **세 가지 옵션**만으로 작동합니다:

1. **무게 추가** (add weight)
2. **무게 이동** (move weight)
3. **무게 제거** (remove weight)

이러한 기본 사항은 그라인딩 휠에도 적용되며 **iBalance**는 작업자에게 이상의 옵션들을 제공합니다.

---

## 3. ANCA iBalance — 소프트웨어 기반 밸런싱

iBalance는 ANCA만의 고유한 소프트웨어 제품으로:

- 사용자에게 휠 진동 가능성을 **사전에 경고**
- ANCA 기계 제품군에 **이미 내장된** 기술 사용 (별도 하드웨어 불필요)
- 휠의 균형이 맞지 않는지 여부를 판단
- 일련의 **단계를 통해 작업자를 유도·안내**하여 휠 균형을 맞추도록 함

### 3.1 작동 원리

iBalance는 그라인딩 휠 팩의 **진동량과 불균형 방향**을 감지·측정합니다.

| 단계 | 내용 |
|------|------|
| 1. 감지 | 기계 **서보 드라이브의 센서**를 사용하여 휠 불균형 감지 |
| 2. 측정 | **모터의 전류 변화 모니터링** → 데이터 분석 |
| 3. 결정 | **밸런싱 웨이트가 추가되어야 하는 정확한 위치 결정** + 기계에 표시 |
| 4. 안내 | 사용자 인터페이스가 무게 실을 위치 + 필요한 무게량 표시 |
| 5. 조정 | 작업자가 **휠 너트 끝에 무게 추가** (소프트웨어 어시스턴트 식별 위치) |

> ★ 핵심: 타이어 밸런서와 같은 원리로 휠 너트 끝에 웨이트를 부착.

### 3.2 정합 주석 — 본 위키 [[휠-20도-Ø125-1-1]] 등 보유 휠 운영

본 위키 휠 페이지(5종)에는 현재 밸런싱 변수 미수록. iBalance가 ANCA 장비에 기본 장착되어 있으므로 **사내 ANCA 머신에서 즉시 사용 가능**. 운영 표준화 시 본 자료 §3.1 단계 적용 가능.

---

## 4. iBalance의 4가지 이점

| # | 이점 | 효과 |
|---|------|------|
| 1 | **휠 수명 연장** | 진동으로 인한 과도 마모 감소 |
| 2 | **고가의 오프라인 밸런싱 장비 불필요** | 자본 투자 절감 |
| 3 | **추가 하드웨어 유지 관리 불필요** | 기계 자체만으로 신뢰 가능 |
| 4 | **밸런싱 유지 작업 시간 절약** | 생산성 ↑ |

> "iBalance를 사용하면 ANCA 그라인딩 연삭기에서 완벽한 툴을 생산할 수 있게 되어 더 이상 밸런싱 유지 작업을 수행하는 데 소요되는 낭비를 피할 수 있습니다." — Simon Richardson

---

## 5. 본 위키 정합 종합 평가

### 5.1 본 자료의 본 위키 적용 가치

| 본 자료 권장 | 본 위키 매핑 | 가치 |
|------------|-----------|------|
| iBalance 사용 (ANCA 내장) | 사내 ANCA 머신 즉시 사용 | 🟢 **즉시 적용 가능** |
| 진동 ↔ 표면조도 인과 | [[표면조도-불량]] §2 채터링 메커니즘 | 🟢 보강 |
| 휠 불균형 ↔ 수명 단축 | [[휠RPM-정책-검증-노트]] 안전 운영 | 🟢 보강 |
| 휠 너트 끝 웨이트 추가 | [[휠-20도-Ø125-1-1]] 등 보유 휠 5종 | 🟡 운영 표준 정립 가치 |

### 5.2 본 자료가 다루지 않는 영역

| 본 자료 미수록 | 보완 출처 |
|--------------|---------|
| 정량 진동 한계 (예: 진동 RMS μm/s) | [STD-ISO12413] §6 + [ACA-INASAKI2001] |
| 휠 마모 패턴 진단 | [[표면조도-불량]] + Norton Winter Catalog 2023 case study |
| 채터링 메커니즘 (수학 모델) | [ACA-INASAKI2001] *Grinding chatter — Origin and suppression*, CIRP Annals 50(2), 515-534 |

### 5.3 본 자료의 학술적 위치

본 자료는 ANCA의 자사 소프트웨어(iBalance) 홍보 자료이나, **휠 진동 제어 = 표면 품질의 핵심 원리**라는 산업 공통 인식을 명시. 학술적 근거는:

- **Inasaki, I., Karpuschewski, B., & Lee, H.S. (2001).** Grinding chatter — Origin and suppression. *CIRP Annals*, 50(2), 515-534. — 채터 발생·억제 메커니즘 종합 (이미 sources.md [ACA-INASAKI2001] 등재)
- **ISO 12413:2019** §6 — 휠 균형 안전 기준

---

## 6. 사내 적용 권장

### 6.1 보유 휠 5종 iBalance 적용 순서

1. ANCA 머신 컨트롤 메뉴에서 iBalance 활성화 확인
2. 신규 휠 장착 시 dressing 전 1차 iBalance 실행
3. dressing 후 2차 iBalance 실행 (휠 형상 변화 확인)
4. 본 위키 [[휠-20도-Ø125-1-1]] 등 페이지에 iBalance 측정값 기록 양식 추가 (다음 세션 권장)

### 6.2 [[연삭-테스트-방법]] (Walter Graf 2011) §3 준비 단계와 통합

Walter Graf 2011의 준비 단계 체크리스트에 "휠 형상 변화 확인" 항목이 있으나, **밸런싱은 별도 항목으로 명시되어 있지 않음**. iBalance를 Walter Graf 6단계 워크플로우의 **§3.4 휠 체결·검사** 하위 항목으로 통합 권장:

```
§3.4 휠 체결·검사 (Walter Graf 2011)
  ├─ 플라스틱 망치 검사 (크랙)
  ├─ 토크 렌치 체결 (20 ft·lb / 30 N·m)
  └─ ★ iBalance 실행 (신규 항목, Simon Richardson 2022)
```

---

## 7. 관련 페이지

### ANCA e-Sharp 시리즈
- [[anca-esharp-index|ANCA e-Sharp News 전체 인덱스]]
- [[연삭-테스트-방법]] — Walter Graf 2011 (밸런싱은 §3.4 보강 후보)
- [[MRR-기반-연삭공정-분석]] — Vadim Zaiser 2022-06
- [[연삭유-성능-가이드]] — Steven Lowery + Markus Munde 2022-03
- [[고성능-엔드밀-제작-가이드-part1]] — Thomson Mathew 2022-01
- [[에너지효율-연삭-7가지팁]] — Kaine Mulder 2024-02

### 본 위키 정합 페이지
- [[표면조도-불량]] §2 — 채터링·진동 메커니즘
- [[휠RPM-정책-검증-노트]] — Vc 운영 정책 + 안전 한계
- [[tools/wheels/catalog/index|홍익다이아 카탈로그]] — 보유 휠 사양
- [[휠-20도-Ø125-1-1]], [[휠-45도-Ø125-1-2]], [[휠-5도-Ø125-1-2]], [[휠-컵-Ø100-1-1]], [[휠-컵-Ø100-1-2]] — 보유 휠 5종

---

## 8. 참고 문헌

### 1차 출처 (본 자료)

- **Richardson, S. (2022).** *정밀한 밸런싱 잡기: ANCA 기계에서 그라인딩 휠의 균형을 올바르게 맞추는 방법 (A fine balancing act: how to correctly balance grinding wheels on an ANCA machine)*. ANCA *e-Sharp News*, September 2022. https://machines.anca.com/e-sharp-news/september-2022/a-fine-balancing-act-how-to-correctly-balance-grin
  - Simon Richardson — ANCA 작가/기술 컨트리뷰터

### 학술 (정합 보강)

- **Inasaki, I., Karpuschewski, B., & Lee, H.S. (2001).** Grinding chatter — Origin and suppression. *CIRP Annals*, 50(2), 515-534. — 채터 발생·억제 메커니즘 학술 표준.

### 국제 표준

- **ISO 12413:2019** — *Bonded abrasive products — Safety requirements*. 휠 안전 운영 기준.

---

## 9. 변경 이력

- **2026-05-18** — 신규 작성. Simon Richardson 2022-09 한국어 원문 정리 + 본 위키 정합 주석. iBalance 작동 원리 (서보 드라이브 센서 → 모터 전류 → 웨이트 위치 결정) + 4가지 이점 + Walter Graf 2011 §3.4 보강 후보 명시. 학술 정합: [ACA-INASAKI2001] CIRP Annals 50(2), 515-534. (Cowork)
