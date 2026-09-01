---
type: machine
manufacturer: "ANCA Pty Ltd"
model: "FX5 Linear"
series: "FX Linear Range"
category: "Tool Grinder (공구 연삭기)"
status_in_factory: "⬜ 사내 미도입 (비교·도입검토 대상)"
controller: "ANCA ToolRoom (공통 플랫폼)"
automation: "Simple Loader (기본 탑재)"
measurement: "LaserUltra (온머신 자동 측정·보정)"
tags: [ANCA, FX5, FX5Linear, 재연마, 소형연삭기, LaserUltra, SimpleLoader]
sources:
  - "[VEN-ANCA-ESHARP-2025-02-TAKEDA]"
  - "[VEN-ANCA-ESHARP-ARCHIVE]"
updated: 2026-06-02
---

# ANCA FX5 Linear

ANCA FX Linear 시리즈 소형·범용 CNC 공구 연삭기. 초경 엔드밀 재연마 및 소형 공구 제조에 특화. Simple Loader + LaserUltra 조합으로 야간·무인 연속 운전이 가능한 모델.

> **사내 도입 상태**: ⬜ **미도입** — 비교·도입 검토 대상.
> 사내 주력 장비 → [[anca-cnc-tool-grinder]] (FX/MX/GX 시리즈 공통 개요).

---

## 1. 장비 포지셔닝

| 항목 | 내용 |
|------|------|
| 시리즈 | FX Linear Range (소형·범용) |
| 대상 고객 | 소규모 재연마 전문점, 제조 진입 사업자 |
| 주요 응용 | 초경 엔드밀 재연마, 드릴 재연마, 소형 공구 신품 제조 |
| 경쟁 포지션 | MX/GX 시리즈(양산·고강성)보다 진입 장벽 낮음 |

신뢰도: **제조사 기준** [VEN-ANCA-ESHARP-2025-02-TAKEDA]

---

## 2. 주요 사양 및 특징

### 2-1. 핵심 하드웨어

| 항목 | 내용 |
|------|------|
| 축 구성 | Linear 드라이브 — 근거리 정밀 이동 최적화 |
| 이송 속도 | 기존 볼스크루 방식 대비 "획기적으로 빠름" (Takahashi, 2025) |
| 홈 가공 속도 | 기존 대비 압도적 (특히 groove cutting) |
| 가공 정밀도 | 근거리 축 이동 구성 → 반복 정밀도 우수 |

신뢰도: **제조사 기준** [VEN-ANCA-ESHARP-2025-02-TAKEDA]

### 2-2. 자동화 — Simple Loader

| 항목 | 내용 |
|------|------|
| 방식 | 기본 탑재 로봇 로더 |
| 운용 형태 | 야간·휴일 무인 연속 운전 가능 |
| 효과 | Takeda Industries 적용 후 생산량 수배 이상 증가 |

신뢰도: **제조사 기준** [VEN-ANCA-ESHARP-2025-02-TAKEDA]

### 2-3. 계측 — LaserUltra (온머신 자동 보정)

LaserUltra는 ANCA 전 모델 공통 옵션이나, FX5 Linear에서 Simple Loader와 결합 시 무인 운전의 핵심 역할을 함.

| 기능 | 내용 |
|------|------|
| 측정 방식 | 레이저 온머신 측정 (가공 중·가공 후) |
| 자동 보정 | 공구가 공차 이탈 → 자동으로 보정값 적용 |
| 무인 운전 | 야간·휴일 품질 유지 핵심 — 작업자 없이 공차 관리 가능 |
| 효과 | "게임 체인저" — Takahashi 사장 직접 평가 |

⚠️ **사내 적용 주의**: 사내 장비에 LaserUltra가 설치되어 있는지 먼저 확인 필요. 설치 여부·활용 현황 → [[ANCA-사내적용-체크리스트-2026-05]] 참고.

신뢰도: **제조사 기준** [VEN-ANCA-ESHARP-2025-02-TAKEDA]

---

## 3. 소프트웨어

FX5 Linear는 ANCA 공통 ToolRoom 소프트웨어 플랫폼 사용:

| 소프트웨어 | 역할 |
|-----------|------|
| ToolRoom | 공구 설계·시뮬레이션·가공 프로그램 |
| iGrind | 재연마 공정 워크플로우 |
| CIM3D | 가공 시뮬레이션 (충돌 방지) |
| LaserUltra | 온머신 측정·보정 |

소프트웨어 생태계 상세 → [[anca-cnc-tool-grinder]] §소프트웨어 및 자동화 생태계

---

## 4. 도입 사례 — Takeda Industries (일본, 2022)

> 출처: ANCA e-Sharp News, February 2025 [VEN-ANCA-ESHARP-2025-02-TAKEDA]

| 항목 | 내용 |
|------|------|
| 회사 | Takeda Industries (일본) |
| 사업 구성 | 재연마 60% + 제조 40% |
| 월 처리량 | 재연마 약 2,000개 / 성수기 제조 최대 800개 |
| 도입 시기 | 2022년 12월 |
| 도입 배경 | 대량 생산 확장 목적, ANCA 소프트웨어 가능성 확인 후 채택 |
| 오퍼레이터 | 사장 Takahashi (68세) 직접 운용 → 후계 교육 중 |
| 주요 효과 | 생산량 수배 증가, 야간·휴일 무인 운전 달성 |
| 기술 지원 | ANCA Japan 기술 스태프 초기 밀착 지원 |

**TOOLKOREA와의 유사점:**
- 재연마 전문 → 제조 병행 사업 모델 동일
- 소규모 운영 체계에서 ANCA 자동화 도입으로 생산성 비약적 향상
- 재연마·제조 수량 비교 벤치마크로 활용 가능

상세 벤치마크 분석 → [[재연마-벤치마크-takeda-industries]]

---

## 5. FX5 vs 사내 보유 장비 비교

| 항목 | FX5 Linear | 사내 보유 (FX/GX 계열) |
|------|-----------|----------------------|
| 포지셔닝 | 소형·범용 | 확인 필요 |
| Simple Loader | 기본 탑재 | 옵션 여부 확인 필요 |
| LaserUltra | 탑재 (케이스 확인) | [[ANCA-사내적용-체크리스트-2026-05]] |
| 야간 무인 운전 | ✅ 검증됨 | 조건부 가능 (로더·LaserUltra 필요) |

⚠️ 사내 장비의 정확한 모델명·옵션 구성 확인 후 비교표 보완 필요.

---

## 6. 관련 페이지

- [[anca-cnc-tool-grinder]] — ANCA 전체 라인업·사내 운용 개요
- [[재연마-벤치마크-takeda-industries]] — Takeda Industries 재연마 사업 벤치마크
- [[ANCA-사내적용-체크리스트-2026-05]] — 사내 즉시 적용 가능 항목
- [[휠-밸런싱-iBalance]] — iBalance 소프트웨어 (FX5 공통 옵션)
- [[anca-esharp-index]] — e-Sharp News 전체 인덱스
