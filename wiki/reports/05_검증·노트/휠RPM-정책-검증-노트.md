---
type: report
category: "검증 노트 — 운영 정책"
subject: "Resin Bond Diamond 휠 권장 원주속도(Vc) 정책 검증"
tags: [검증, RPM, 원주속도, Vc, 레진본드, 다이아몬드, NortonWinter, ISO12413]
sources:
  - "휠RPM_권장도표_v3_정밀화.xlsx (사용자 작성, 2026-05-15)"
  - "Saint-Gobain Norton Winter Tool Grinding Catalog 2023 (162p)"
  - "Marinescu et al. 2016 / Malkin & Guo 2008 / Rowe 2014"
  - "ISO 12413:2019 / ISO 16089:2015"
verification_date: 2026-05-18
conclusion: "위키 정책(Vc 18-25 m/s) 학술적으로 정확. v3 시트(Vc 25-35 m/s, Sweet 30)는 일반 연삭값을 협소 응용에 잘못 적용 — 약 36% 과대."
updated: 2026-08-28
---

# 휠 RPM 권장 정책 검증 노트

본 노트는 **2026-05-18 기준** Resin Bond Diamond 휠로 초경(WC-Co) 공구를 ANCA tool grinder에서 가공할 때의 권장 원주속도(Vc) 정책을 1차 출처에 근거하여 재검증한 결과입니다.

> ⚠️ **결론**: 위키 [[index|휠 카탈로그]]의 "Vc 18-25 m/s, 상한 25 m/s" 정책이 **학술·산업 1차 출처와 일치**. 사용자 작성 `휠RPM_권장도표_v3_정밀화.xlsx`의 "Vc 25-35 m/s, Sweet Spot 30 m/s" 정책은 textbook의 일반 연삭값을 협소 응용(tool grinding)에 잘못 적용한 것으로 판정.

---

## 1. 검증 배경

### 발견된 정책 충돌

| 항목 | 위키 [[index]] (2026-04-21) | v3 시트 (2026-05-15) | 차이 |
|------|------------------------|-------------------|------|
| 권장 구간 | **18 ~ 25 m/s** | **25 ~ 35 m/s** | 상한 +10 |
| Sweet Spot | (명시 없음 / 18-25 전반) | **30 m/s** ★ | — |
| 레진 상한 | **25 m/s** (절대 금지선) | **40 m/s** (주의 후 금지) | +15 m/s |
| Ø125 최대 권장 RPM | **3,820 rpm** (Vc=25) | **5,348 rpm** (Vc=35) | +40% |
| 4,000 rpm (Ø125) 판정 | ⚠️ 초과 | Sweet Spot 직전 (안전) | **정반대** |

이는 동일 보유 휠을 두고 정반대 운영 정책을 제시하는 상황이므로 1차 출처 검증이 필수.

---

## 2. 1차 출처 — Saint-Gobain Norton Winter Tool Grinding Catalog 2023

세계 1위 연삭재 제조사인 Saint-Gobain의 자회사 **Norton Winter** *"Precision Technology Tool Grinding"* 카탈로그(162p)에서 실제 생산 환경의 case study 데이터를 확보했습니다.

> 📄 출처: [Norton Winter Tool Grinding Catalog 2023](https://media.saint-gobain.com/Abrasives/Norton/Sweden/2023/NORTON-WINTER-TOOL-GRINDING/) (p.18~34, p.39~43 case studies)

### 2.1 초경(WC-Co) + Resin Bond Diamond 실측 case study

| # | 휠 | 기계 | 가공 | **Vc (실측)** | 카탈로그 페이지 |
|---|----|------|------|---------|--------------|
| 1 | D54 Q-Flute EVO | Walter Helitronic Vision | TC 엔드밀 Ø12mm Flute | **18 m/s** | p.18 |
| 2 | D54 Q-Flute EVO | Walter Helitronic + ANCA FX | TC 엔드밀 Ø4~16mm | **18 m/s** | p.18 |
| 3 | D54 Q-Flute PRIME | Rollomatic Grindsmart 629XW | TC 엔드밀 Ø10mm | **18 m/s** (폴리싱 20) | p.18 |
| 4 | D54 Q-Flute EVO | Walter Helitronic | TC 드릴 Ø10mm | **18 m/s** | p.22 |
| 5 | D64 V-Pro 4073 | **ANCA TX7+** | TC 드릴 Ø9mm Gashing | **18 m/s** | p.30 |
| 6 | D64 V-PRIME 5406 | **ANCA MX7 Linear** | TC 엔드밀 Ø12mm Gashing | **22 m/s** | p.30 |
| 7 | D64 V-PRIME 5406 | **ANCA MX7 Linear** | TC 엔드밀 Ø12mm Clearance | **22 → 18 m/s** | p.34 |
| 8 | D64 V-Pro 4073 | SAACKE | TC 드릴 Ø11mm Clearance | **17 m/s** | p.34 |
| 9 | D46 μicro+ 6065 (특수 소공구용) | Kirner K360 | TC 버 Ø6mm | **35 m/s** | p.25 |
| 10 | D15B μicro+ 6055 (특수 소공구용) | Rollomatic 620XS | TC 드릴 Ø0.8mm | **25 m/s** | p.26 |

🔴 **2026-08-28 정정** — ~~**ANCA 장비 한정 (#5, #6, #7)**: Vc = **17~22 m/s**~~ 는 **출처를 잘못 좁힌 서술**입니다. 그 3건의 실제 값은 **#5 = 18 · #6 = 22 · #7 = 22→18** 이며 **17은 포함되지 않습니다** — 17 m/s는 **#8 SAACKE**(ANCA 장비 아님)입니다.

**정정** — **ANCA 한정 = 18 ~ 22 m/s** · **8건 전체 = 17 ~ 22 m/s (최빈 18, 6건/8건)**. 위키 정책과의 일치 결론 자체는 유효합니다. [신뢰도: **실측 검증** — 위 표 재판독]

⚠️ 아울러 본 노트 §7이 *"권장 Vc **18 ~ 22 m/s**"* 라는 **범위**로 적은 것이, [[tools/wheels/index]]로 옮겨지며 *"레진 **하한** 18 m/s — 권장 최소"* 라는 **규범**으로 강화됐습니다. **8건 중 최소값은 17 m/s이므로 18을 하한으로 둘 근거는 없습니다** → 해당 페이지 2026-08-28 정정 참조.

### 2.2 HSS + Resin Bond CBN 실측 case study

| # | 휠 | 기계 | 가공 | **Vc (실측)** | 카탈로그 페이지 |
|---|----|------|------|---------|--------------|
| 11 | B107 V-Pro 4073 | Schneeberger Norma | HSS 엔드밀 Ø35mm | **35 m/s** | p.43 |
| 12 | B107 V-Pro 4073 | Walter Helitronic | HSS 엔드밀 Ø24mm Clearance | **40 m/s** | p.35 |

> HSS는 CBN 휠 사용 시 Vc 35-40 m/s가 표준 — 초경과 다른 영역.

---

## 3. 학술 출처 — 인용 맥락 재검토

v3 시트가 인용한 학술 출처(Marinescu 2016 / Malkin 2008 / Rowe 2014)는 **틀린 인용이 아니나 사용 맥락이 다릅니다**.

### 3.1 학술 출처의 30 m/s "Sweet Spot" 적용 범위

| 출처 | 30 m/s 권장의 맥락 | 본 위키 시나리오 일치 여부 |
|------|---------------|----------------------|
| Marinescu et al. (2016) *Handbook of Machining with Grinding Wheels*, 2nd ed., CRC Press, ch.4 | **일반 연삭 (general grinding)** — 평면연삭·원통연삭·산화알루미늄 휠 포함 | ❌ 협소 응용 다름 |
| Malkin & Guo (2008) *Grinding Technology*, 2nd ed., Industrial Press, ch.3 | 일반 연삭 + 속도-MRR 관계 | ❌ 동일 |
| Rowe (2014) *Principles of Modern Grinding Technology*, 2nd ed., Elsevier, ch.6 | CBN·다이아몬드 일반 속도 범위 | ⚠️ 부분 일치 (CBN 영역에서는 30+ m/s) |
| Klocke (2009) *Manufacturing Processes 2: Grinding, Honing, Lapping*, Springer | 일반 연삭 파라미터 체계 | ❌ 동일 |

### 3.2 결정적 출처 — Norton Winter (제조사 1차)

Saint-Gobain Norton Winter는 **세계 1위 tool grinding wheel 제조사** (Saint-Gobain은 세계 1위 abrasive 제조사). 본 카탈로그는:

- 초경 공구 가공 **case study 10건+** (구체적 휠 모델·기계·Vc 명시)
- ANCA·Walter·Rollomatic·Schneeberger·SAACKE·Kirner·Saacke 다중 기계 환경
- **D54/D64 (Ø125/Ø150 typical, 보유 휠과 동일 등급) 실측값**

→ 학술 textbook의 일반론보다 **본 위키 시나리오에 직접 부합**.

### 3.3 v3의 학술 인용 문제 — 사용 맥락 미스매치

```
v3 출처:
  Marinescu 2016 ch.4 → "Sweet Spot Vc=30 m/s"
                          ↓
                          (일반 연삭 권장값)
                          ↓
                   ❌ 잘못된 적용
                          ↓
  본 시나리오: 초경 + Resin Bond Diamond + ANCA tool grinder
                          ↓
                          (Norton Winter 실측 Vc = 17~22 m/s)
```

**결론**: v3의 30 m/s는 학술적으로 잘못 인용된 것은 아니나, **응용 시나리오 매칭이 부정확**.

---

## 4. ISO 표준 — 안전 한계

### ISO 12413:2019 — *Bonded abrasive products: Safety requirements*

- §6.6: 모든 결합 연삭 제품의 **측면에 Vmax 표시 의무화**
- Resin Bond 일반 Vmax 정격: 휠 직경·강도에 따라 30~60 m/s (제품별)
- 실제 운영 Vc는 Vmax의 70-80% 이하 권장

### ISO 16089:2015 — *Machine tools: Safety: Stationary grinding machines*

- 연삭기 안전 RPM 한계 규정
- 휠 손상·진동에 의한 사고 방지

> ⚠️ Vmax는 **휠 손상 한계 (절대 금지선)**이며, **권장 운영 Vc (Sweet Spot)**와 다른 개념. Vmax 35-45 m/s 휠이라도 실제 운영은 18-22 m/s가 정상 — Norton Winter 데이터로 확인.

---

## 5. 최종 판정 — 정책별 평가

### 5.1 위키 [[index|휠 카탈로그]] (Vc 18-25 m/s, 상한 25)

| 평가 항목 | 판정 |
|----------|------|
| 본 시나리오(TC + Resin Diamond + ANCA) 적합성 | ✅ **정확** |
| Norton Winter 실측과의 일치 | ✅ ANCA case 17-22 m/s 모두 18-25 범위 내 |
| 학술 근거 보강 필요 | ⚠️ 기존에 출처가 "대화 정리 (2026-04-21)"였음. Norton Winter 인용 추가로 강화 |
| 보수성 | ✅ 적절 (안전 마진 확보) |

### 5.2 v3 시트 (Vc 25-35 m/s, Sweet Spot 30, 한계 40)

| 평가 항목 | 판정 |
|----------|------|
| 본 시나리오(TC + Resin Diamond + ANCA) 적합성 | ❌ **과대** |
| Norton Winter 실측과의 일치 | ❌ Sweet Spot 30이 실측(22) 대비 36% 높음 |
| 수식 정확도 | ✅ 100% (수학 자체는 완벽) |
| 인용 자체 | ⚠️ 정확하나 응용 시나리오 미스매치 |
| 일반 연삭(평면·원통)에는 사용 가능 | ✅ — 단, 본 위키 적용 영역 아님 |

### 5.3 비교 차트

```
Vc (m/s) :   15  17  18  19  20  21  22  23  24  25  26 ... 30 ... 35 ... 40
                  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ←── Norton Winter ANCA 실측 (17-22 m/s)
                     ────────────── ←── 위키 정책 (18-25 m/s) ──→
                                          ────────────── ←── v3 정책 (25-35 m/s) ──→
                                                       ★ v3 Sweet (30)
                                                                  ★ v3 한계 (40)
```

---

## 6. 권장 운영 정책 (검증 후 확정)

| 시나리오 | 권장 Vc | 근거 |
|---------|--------|------|
| **초경(WC-Co) + Resin Bond Diamond + ANCA / Walter / Rollomatic** | **18 ~ 22 m/s** | Norton Winter 2023 case studies 8건 |
| TC + 소공구 특화 Resin (Norton μicro+ 등) | 25 ~ 35 m/s | Norton Winter μicro+ case studies |
| **HSS + Resin Bond CBN** | **35 ~ 40 m/s** | Norton Winter V-Pro CBN case studies |
| 세라믹·SiC + Resin Diamond | 15 ~ 25 m/s | Marinescu 2016 ch.11 |
| **절대 한계 (Vmax)** | 휠 측면 라벨 확인 (ISO 12413:2019 의무) | 일반 Resin: 30-45 m/s; 휠별 상이 |

### 본 위키 보유 휠(Ø125·Ø100, R등급, C125, #400)에 대한 권장 RPM

| 직경 | Vc 18 (~~하한~~ **최빈값**) | **Vc 22 (Sweet)** | Vc 25 (사내 상한) |
|------|--------|--------|--------|
| **Ø125** | 2,750 rpm | **3,361 rpm** | 3,820 rpm |
| **Ø100** | 3,438 rpm | **4,202 rpm** | 4,775 rpm |
| Ø75 | 4,584 rpm | **5,603 rpm** | 6,366 rpm |
| Ø150 | 2,292 rpm | **2,801 rpm** | 3,183 rpm |

> 💡 **장비 최대 6,000 rpm**으로는 Ø125 휠로 ANCA 표준 Vc 22 m/s 달성 시 **3,361 rpm** 사용 — 장비 최대까지 가지 않아도 충분.
> 위키 [[휠-20도-Ø125-1-1]]의 "장비 최대(6,000 rpm) 사용 금지" 판정은 그대로 유효.

---

## 7. 후속 조치

| # | 조치 | 상태 |
|---|------|------|
| 1 | 본 검증 노트 wiki/reports/에 저장 | ✅ 완료 (본 문서) |
| 2 | [[index|휠 카탈로그]]에 Norton Winter 출처 추가 | ✅ 완료 (별도 편집) |
| 3 | v3 시트 수정 (Sweet Spot 30 → 22, 시나리오 명확화) | ⏸️ 보류 (사용자 판단) |
| 4 | 보유 휠 측면 각인 확인 (Vmax 라벨) | ⏸️ 사용자 작업 |

---

## 출처

### 1차 (Tier 1.5 — 제조사 실측)

1. **[Saint-Gobain Norton Winter Tool Grinding Catalog 2023](https://media.saint-gobain.com/Abrasives/Norton/Sweden/2023/NORTON-WINTER-TOOL-GRINDING/)** (162p) — p.18~34, p.39~43 case studies. 초경+Resin Diamond ANCA 가공 8건, HSS+CBN 2건 등 총 12+ case.

### 1차 (Tier 1 — ISO 표준)

2. **ISO 12413:2019** — *Bonded abrasive products: Safety requirements*. §6.6 Vmax 표시 의무.
3. **ISO 16089:2015** — *Machine tools: Safety: Stationary grinding machines*.

### 2차 (Tier 2 — 학술 핸드북)

4. Marinescu, I. D., Hitchiner, M., Uhlmann, E., Rowe, W. B., & Inasaki, I. (2016). *Handbook of Machining with Grinding Wheels* (2nd ed.). CRC Press. Ch.4 (일반 연삭).
5. Malkin, S. & Guo, C. (2008). *Grinding Technology: Theory and Applications of Machining with Abrasives* (2nd ed.). Industrial Press. Ch.3.
6. Rowe, W. B. (2014). *Principles of Modern Grinding Technology* (2nd ed.). Elsevier. Ch.6.
7. Klocke, F. (2009). *Manufacturing Processes 2: Grinding, Honing, Lapping*. Springer.

### 검증 대상 (Tier 5 — 사내 작성물)

8. `raw/notes/휠RPM_권장도표_v3_정밀화.xlsx` (사용자 작성, 2026-05-15)
9. [[index|휠 카탈로그]] (2026-04-21 초안)
10. [[홍익다이아-본드-체계]] (2026-05-15)

---

## 관련 페이지

- [[index|상위: 휠 카탈로그]]
- [[tools/wheels/catalog/index|홍익다이아 카탈로그 인덱스]]
- [[홍익다이아-본드-체계]]
- [[휠-20도-Ø125-1-1]] 등 보유 휠 5종 (Vc 25 m/s 상한 정책 유지)
