---
type: cadcam
category: "연삭 공정 최적화"
subcategory: "MRR (Material Removal Rate) 분석"
source_author: "Vadim Zaiser (ANCA)"
source_publisher: "ANCA Pty Ltd — e-Sharp News, 2022년 6월호"
source_url: "https://machines.anca.com/e-sharp-news/june-2022/grinding-process-analysis-based-on-mrr"
source_publish_date: "2022-06-14"
tags: [MRR, Q, Q-prime, 연삭공정, CIMulator3D, CIM3D, ANCA, adaptive grinding, 드레싱주기, VadimZaiser]
sources:
  - "[VEN-ANCA-ZAISER2022] Vadim Zaiser — 'Grinding Process Analysis based on Material Removal Rate'. ANCA e-Sharp News, 2022-06"
  - "[VEN-ANCA-GRAF2011] Walter Graf — Q'w 공식 ([[연삭-테스트-방법]] §4.6)"
  - "[ACA-MALKINGUO2008] Malkin & Guo (2008). Grinding Technology, Ch.5 — MRR 정의"
  - "[ACA-MARINESCU2016] Marinescu et al. (2016). Handbook of Machining with Grinding Wheels, Ch.4"
  - "[VEN-NORTON-WINTER-2023] Saint-Gobain Norton Winter Tool Grinding Catalog 2023 — Qmax 권장값"
updated: 2026-05-18
status: "ANCA e-Sharp 2022-06 원문 정리 + 본 위키 정합 주석. 영문 본문 (한국어 페이지 미생성 자료)"
---

# MRR 기반 연삭 공정 분석 — CIMulator3D 활용

> 본 페이지는 **Vadim Zaiser** (ANCA)가 ANCA *e-Sharp News* 2022년 6월호에 게시한 *"Grinding Process Analysis based on Material Removal Rate"* 영문 원문을 정리하고, 본 위키의 정착된 1차 출처([[연삭-테스트-방법]] Q'w 공식, [[휠RPM-정책-검증-노트]] Vc 정책)와의 정합 주석을 추가한 자료입니다.
>
> 원문: <https://machines.anca.com/e-sharp-news/june-2022/grinding-process-analysis-based-on-mrr>
>
> 신뢰도: **★★★★☆** (ANCA 1차, ANCA 소프트웨어 [[연삭-테스트-방법]] Q'w 공식과 직접 통합)
>
> 부제: *Explore various ways of using the material removal rate Q to optimize the tool grinding process by improving cycle time and reducing the wheel wear*

---

## 1. MRR이란? — Q 정의

**MRR**(Material Removal Rate, 단위 시간당 재료 제거율)는 일반적으로 **Q**로 표기됩니다. 모든 절삭 가공 공정의 핵심 파라미터.

- 높은 MRR = 더 효율적인 운영 + 사이클 타임 감소
- 정의: **단위 시간당 제거된 재료 부피** (mm³/s)

### 1.1 수식

$$
Q = \frac{dV_r}{dt}
$$

- $V_r$ = 제거된 재료 부피 (mm³)
- $t$ = 시간 (s)
- 단위: **mm³/s**

> 복잡한 절삭 공구는 기하학적으로 매우 복잡 — 절삭당 부피 추정은 수학적으로 도전적이며 실무에서 직접 계산은 거의 불가능. 그래서 MRR을 통한 연삭 공정 최적화 기회가 종종 활용되지 못함.

### 1.2 본 위키 정합 — [[연삭-테스트-방법]] Walter Graf의 Q'w와의 관계 ★★★

본 자료의 **Q**는 절대 부피 제거율 (mm³/s).
[[연삭-테스트-방법]] Walter Graf 2011의 **Q'w**(Q-prime)는 단위 휠 폭당 제거율 (mm³/(mm·s)):

$$
Q'_w = \frac{Q}{b} = \frac{V_w \times A_e}{60}
$$

- $b$ = 휠 접촉 폭 (mm)
- $V_w$ = 공작물 이송속도 (mm/min)
- $A_e$ = 연삭 깊이 (mm)

→ **본 자료는 Q (절대값) 중심, Walter Graf는 Q'w (단위 폭당) 중심. 본 자료 §6의 specific volumetric removal rate Q'와 동일 개념.**

---

## 2. CIMulator3D의 MRR 타임라인 ★★★

ANCA의 최신 **CIMulator3D** (CIM3D) 시뮬레이션 엔진은 재료를 **점진적으로 연삭**하여, 이전 이동 시점의 잔여 공작물 부피에서 빼는 방식으로 MRR을 계산합니다.

### 2.1 작동 원리

| 단계 | 내용 |
|------|------|
| 1 | 시뮬레이션 중 매 이동 시점에서 잔여 공작물 부피 계산 |
| 2 | 이전 시점 부피 − 현재 시점 부피 = 제거된 부피 |
| 3 | 제거된 부피 / 이동 시간 = MRR |
| 4 | **MRR을 타임라인 차트로 표시** (전체 연삭 공정 동안의 MRR 시계열) |
| 5 | 타임라인 커서 드래그 시 해당 시점의 MRR이 우측 컨트롤 패널에 표시 |

> ★ 핵심: 복잡한 공구 기하학에서 손계산이 불가능했던 MRR이 **CIM3D 시뮬레이션으로 자동 계산** 가능해짐.

---

## 3. MRR 활용 4가지 — 생산 효율 개선

### 3.1 휠 수명·연삭 효율 개선 ★★★

연삭 휠은 **제조사 권장 MRR 범위**에서 최고 성능 발휘:

| 영역 | 효과 |
|------|------|
| **MRR > Qmax** | 휠 급속 마모 (rapid wheel breakdown) |
| **MRR < Qmin** | 휠 로딩 + 둔화 (wheel loading + dull) |
| **Qmin ≤ MRR ≤ Qmax** | ★ **자생작용**(legendary self-sharpening state) 달성 — 휠이 최적 작동 |

> ⚠️ "전설적인 자생작용 상태(legendary self-sharpening)"라는 표현은 **휠이 사용 중 자체 dressing을 수행**하는 이상적 상태를 의미. 이를 위해 MRR을 Qmin~Qmax 범위로 유지.

### 3.2 본 위키 정합 — 보유 휠 Qmax/Qmin

본 위키 [[tools/wheels/catalog/index|홍익다이아 카탈로그]]에는 보유 휠(HID Resin Bond Diamond)의 Qmax·Qmin 미수록. [[연삭-테스트-방법]] §4.6 Walter Graf 권장값:

| 응용 | Q'w 권장 (mm³/(mm·s)) |
|------|---------------------|
| 초경 엔드밀 플루팅 | **6 ~ 12** ★ |
| 열처리강 크립피드 | 5 ~ 10 |
| 항공 니켈합금 | 10 ~ 20 |
| 공구강 탭 플루팅 | 10 ~ 20 |

본 자료의 Qmax/Qmin과 Walter Graf의 Q'w 권장값이 **사실상 동일 개념**. 사내 HID 보유 휠에 적용 시:
- 초경 엔드밀 플루팅: **Q'w 6-12 mm³/(mm·s)** 범위 유지 권장
- Qmax 초과: 휠 급속 마모
- Qmin 미만: 휠 로딩 + 둔화

### 3.3 깊은 절삭 작업의 패스 분할

깊은 절삭 작업(예: heavy fluting)의 경우 **MRR에 따라 패스 수 분할**:

```
이상적 패스 분할:
  연삭 이동의 MRR이 제조사 권장 범위 내
  ├─ Qmax 초과 작업 → 휠 과부하 (overstress)
  └─ Qmin 미만 작업 → 휠 둔화 (dull)
```

### 3.4 드레싱 주기 결정 ★★★

ANCA의 **iGrind + Dresser** 소프트웨어 통합:
- Fluting 공정에 **내장 드레싱 패널** 포함
- 사전 프로그래밍: 일정 공구 수 또는 패스 수 후 sticking·dressing 자동 실행

#### 드레싱 주기 결정 — 데이터 기반

```
스핀들 파워 (실시간) ─┐
                    ├──> 비교: 두 그래프가 상관해야 함
시뮬레이션 MRR ──────┘    (같은 재료 제거에 같은 에너지 필요)
```

| 관찰 | 의미 | 조치 |
|------|------|------|
| 스핀들 파워가 동일 MRR에서 시간 경과 따라 증가 | **휠 마모** (resharpening 필요) | 자동 sticking 스케줄링 |
| 편차 발생 전 | 정상 | 모니터링만 |
| 편차 발생 후 | 휠 성능 저하 | 즉시 dressing |

> 핵심: **편차 발생 전 자동 sticking으로 사이클 타임 절약 + 휠 보호**.

### 3.5 연삭 이송속도 조정

시뮬레이션에서 사용자는 **MRR 변화를 쉽게 식별** 가능:

| MRR 그래프 패턴 | 의미 | 조치 |
|---------------|------|------|
| 0에서 값으로 점프 | 휠이 가공물에 곧 접촉 | **점프 전 이송속도 증가** → 사이클 타임 ↓ |
| 갑작스러운 sharp shoot | 예상치 못한 휠 과부하 | 실제 가공 시 휠 손상 → **시뮬레이션에서 미리 검출** |
| 빠른 이송속도가 실수로 접근 중 사용 | 휠 충돌 위험 | MRR 차트에서 overshoot 즉시 식별 → 시뮬레이션에서 해결 |

### 3.6 Adaptive Grinding 최적화 ★★

**Adaptive grinding**은 **목표 스핀들 부하**에 따라 이송속도를 조정. 사이클 타임 감소에 유용.

⚠️ **함정**: MRR을 고려하지 않은 adaptive grinding은 휠 제조사 권장 Qmax를 초과할 가능성 → 휠 급속 마모.

> **권장**: 이송속도를 MRR 기반으로 조정 → 휠 보호 + 공정 안정성 유지

---

## 4. Specific Volumetric Removal Rate (Q')

다른 유용한 그래프: **specific volumetric removal rate Q'** — 휠 접촉 폭 단위당 공작물 재료 제거율.

$$
Q' = \frac{Q}{b_{contact}}
$$

CIMulator3D 엔진은 각 시점의 **전체 휠 접촉 폭** 사용하여 Q' 계산.

### 4.1 휠 단면 색상 매핑

Specific volumetric removal rate + 휠 단면 색상 매핑 결합 시:
- **휠의 어느 영역이 가장 부하를 받는지 식별** 가능
- → 해당 영역에 **더 자주 드레싱·sticking 필요**

> ★ 핵심: 휠 표면이 균일하게 마모되지 않음. 부분적으로 집중 부하 받는 영역을 시각화하여 부분 드레싱 가능.

### 4.2 본 위키 정합 — Walter Graf Q'w와 정확히 동일 개념

본 자료의 **Q'** = [[연삭-테스트-방법]] Walter Graf 2011의 **Q'w**.

| 표기 | 출처 | 정의 |
|------|------|------|
| **Q'** | Zaiser 2022 (본 자료) | $Q'/b_{contact}$ |
| **Q'w** | Walter Graf 2011 | $(V_w \times A_e)/60$ |
| 단위 | mm³/(mm·s) | mm³/(mm·s) |

→ **표기만 다를 뿐 동일 변수**. 본 위키는 Walter Graf 표기 Q'w 통일.

---

## 5. 본 위키 정합 종합 평가

### 5.1 본 자료의 본 위키 적용 가치

| 본 자료 권장 | 본 위키 매핑 | 가치 |
|------------|-----------|------|
| MRR 타임라인 차트 (CIM3D) | [[연삭-테스트-방법]] §4.6 Q'w 권장값 적용 | 🟢 **상호 보완** — Walter Graf의 정적 권장값 + Zaiser의 동적 시뮬레이션 |
| 자생작용 (Qmin~Qmax) | [[tools/wheels/catalog/index|홍익다이아 카탈로그]] 보유 휠 운영 | 🟢 Qmax 범위 사내 정립 가치 |
| 드레싱 주기 결정 (스핀들 파워 모니터링) | [[휠-20도-Ø125-1-1]] 등 보유 휠 5종 | 🟢 데이터 기반 dressing 사내 정립 가치 |
| Adaptive grinding ↔ MRR 한계 | [[휠RPM-정책-검증-노트]] 안전 운영 | 🟡 ANCA 옵션 사용 시 주의 |
| Q' = 휠 부분 부하 시각화 | [[홍익다이아-형상-분류]] 12종 형상 | 🟡 형상별 부하 패턴 분석 가능 |

### 5.2 본 자료의 시대성

- 2022년 자료 — CIMulator3D는 본 자료 시점 이후 계속 업데이트됨 (CIM3D V9는 2025-02 자료에 등장)
- **MRR/Q 개념 자체는 시대 무관** (Malkin & Guo 2008, Marinescu 2016 학술 표준 일관)
- 자생작용(self-sharpening) 메커니즘은 Malkin & Guo 2008 Ch.5와 학술적으로 일치

### 5.3 학술적 위치

본 자료의 핵심 개념(MRR, self-sharpening, Qmax/Qmin)은 모두 학술 핸드북에 정착된 표준:

| 본 자료 개념 | 학술 출처 |
|------------|---------|
| MRR / Q 정의 | Malkin & Guo (2008) Ch.5 / Marinescu et al. (2016) Ch.4 |
| Self-sharpening | Malkin & Guo Ch.4 §4.3 / Rowe (2014) Ch.5 |
| Q'w (단위 폭당) | Walter Graf (Winterthur 2011) — [[연삭-테스트-방법]] |
| Qmax/Qmin 권장값 | Walter Graf 2011 §4.6 (초경 엔드밀 6-12 mm³/(mm·s)) |

---

## 6. 사내 적용 권장

### 6.1 보유 휠 5종 MRR 기준 운영

```
1. 신규 공구 시뮬레이션 (CIM3D)
   └─ MRR 타임라인 차트 확인
       ├─ Qmax(예: 12 mm³/(mm·s)) 초과 시점 있는가?
       │   └─ 있으면: 이송속도 감소 또는 패스 분할
       └─ Qmin(예: 6 mm³/(mm·s)) 미만 시점 있는가?
           └─ 있으면: 이송속도 증가 또는 패스 통합

2. 실가공 시 스핀들 파워 vs 시뮬 MRR 비교
   └─ 시간 경과 따른 편차 발생
       └─ 휠 dressing 신호 (sticking 자동 스케줄링)

3. 모든 결과를 본 위키 `휠-{형상}-Ø{직경}-{스택}` 페이지의 §4 사용 이력에 기록
```

### 6.2 [[연삭-테스트-방법]] (Walter Graf 2011) 6단계와의 통합

```
Walter Graf 6단계               | Zaiser 2022 보강
1. 목적                          |
2. 준비                          | Q'w 권장값 (사내 보유 휠 Qmin/Qmax 정의)
3. 테스트                        | CIM3D 시뮬레이션 → MRR 타임라인 확인
4. 평가                          | 스핀들 파워 vs 시뮬 MRR 비교 (드레싱 신호)
5. 기록                          | MRR 차트 캡처 + 휠 페이지 §4에 추가
6. 정보 공유                     |
```

본 자료는 Walter Graf 2011의 **평가·기록 단계를 정량적으로 강화**.

---

## 7. 관련 페이지

### ANCA e-Sharp 시리즈
- [[anca-esharp-index|ANCA e-Sharp News 전체 인덱스]]
- [[연삭-테스트-방법]] — Walter Graf 2011, Q'w 공식 1차 출처
- [[휠-밸런싱-iBalance]] — Simon Richardson 2022-09
- [[연삭유-성능-가이드]] — Steven Lowery + Markus Munde 2022-03
- [[고성능-엔드밀-제작-가이드-part1]] — Thomson Mathew 2022-01
- [[에너지효율-연삭-7가지팁]] — Kaine Mulder 2024-02

### 본 위키 정합 페이지
- [[tools/wheels/catalog/index|홍익다이아 카탈로그]] — Qmin/Qmax 미수록 (다음 세션 보강 권장)
- [[홍익다이아-형상-분류]] — 12종 형상별 접촉 폭 b 정보
- [[휠RPM-정책-검증-노트]] — Vc 정책 (MRR와 독립 변수, 상호 보완)
- [[휠-20도-Ø125-1-1]], [[휠-45도-Ø125-1-2]], [[휠-5도-Ø125-1-2]], [[휠-컵-Ø100-1-1]], [[휠-컵-Ø100-1-2]] — 보유 휠 5종

---

## 8. 참고 문헌

### 1차 출처 (본 자료)

- **Zaiser, V. (2022).** *Grinding Process Analysis based on Material Removal Rate*. ANCA *e-Sharp News*, June 2022. https://machines.anca.com/e-sharp-news/june-2022/grinding-process-analysis-based-on-mrr
  - Vadim Zaiser — ANCA Author/Contributor

### 학술 (정합 보강)

- **Malkin, S. & Guo, C. (2008).** *Grinding Technology: Theory and Applications of Machining with Abrasives* (2nd ed.). Industrial Press. — Ch.4 §4.3 Self-sharpening, Ch.5 MRR.
- **Marinescu, I.D., Hitchiner, M., Uhlmann, E., Rowe, W.B., & Inasaki, I. (2016).** *Handbook of Machining with Grinding Wheels* (2nd ed.). CRC Press. — Ch.4 휠 원주속도·MRR 관계.
- **Rowe, W.B. (2014).** *Principles of Modern Grinding Technology* (2nd ed.). Elsevier. — Ch.5 burn·thermal·MRR 한계.
- **Graf, W. (2011).** *효과적인 연삭 테스트 구성 방법*. ANCA e-Sharp News, December 2011. — [[연삭-테스트-방법]], Q'w 공식 1차.

### 산업 자료 (상호 검증)

- Saint-Gobain Norton Winter — *Tool Grinding Catalog 2023* — case study별 ap·feedrate·Vc → Q'w 산출 가능.

---

## 9. 변경 이력

- **2026-05-18** — 신규 작성. Vadim Zaiser 2022-06 영문 원문 정리 + 본 위키 정합 주석. MRR(Q) vs Q'(specific) 정의 + Q'w (Walter Graf)와의 통일 + CIM3D 타임라인 활용 4가지(자생작용 / 패스 분할 / 드레싱 주기 / adaptive grinding) + 사내 보유 휠 적용 권장 + Walter Graf 6단계와의 통합 워크플로우. (Cowork)
