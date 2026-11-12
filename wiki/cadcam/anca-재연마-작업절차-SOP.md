---
type: cadcam
category: "ANCA 작업 절차 (SOP)"
tags: [ANCA, 기계준비, 인터페이스, 휠드레싱, 휠교체, SOP]
sources:
  - "[INT-TOOLKOREA-PRODMANUAL-2026]"
updated: 2026-07-27
---

# ANCA 재연마 작업절차 (기계준비 · 인터페이스 · 휠드레싱 · 휠교체)

> 신뢰도: **사내 경험값** — 코툴스 생산팀 매뉴얼 ver6.0 기준 표준 작업 절차.
> 출처: [INT-TOOLKOREA-PRODMANUAL-2026] §2(재연마 절차, p35~96)
> 장비 개요·스택 구성·소프트웨어 생태계는 [[anca-cnc-tool-grinder]] 참고. 재연마 형상·치수 기준은 [[tools/재연마-형상-치수기준]] 참고.

---

## 1. 기계준비

### 1.1 배전반

전원 계통: TR1(변압기) / 칠러 / 집진기 A·B / 집진기 C(C40) / 필터링 장치 / 콤프레샤 / GX7 / TR2(변압기) / 콘센트 A·B(상시 ON) / CNC 에어컨(FAST용·GX7용 별도).

> ⚠️ **OFF 시 주의**: 모든 장비가 완전히 정지된 것을 확인한 후 배전반 OFF.

### 1.2 순차 기동 절차

| 순서 | 설비 | 조작 |
|------|------|------|
| 1 | 에어컴프레샤 | 녹색 버튼 → 작동, 버튼 좌측 상단 녹색 불 점등 확인 |
| 2 | 에어용기 | 기계 작동 전 하단 밸브를 열어 물 배출(5~10분) → 중단 밸브 개방 |
| 3 | 에어드라이어 | ON 방향 스위치 → 빨간불 점등 확인 |
| 4 | 칠러 | POWER 스위치 위로 → START 스위치 위로 |
| 5 | 필터링 장치 | 패널 좌측 전원 위로 회전 → 녹색 버튼 또는 패널 녹색 자동시작 터치 |
| 6 | CNC 에어컨 | 설정온도 **30℃**, **하절기(5~9월)에만 가동** |
| 7 | Mist collector | ON/OFF 단순 조작. **워밍업 시 OFF**(CNC 내부 온도저하 원인), 작업정지·wheel 검증 시에도 OFF |

### 1.3 CNC 작동 (ANCA 전원 투입 순서)

1. ANCA 메인전원 ON
2. ANCA 장비 빨간색 비상버튼 해제 → CNC 녹색 버튼(Ctrl + On)
3. 전원 인가 후 컴퓨터 부팅 → I-GRIND 가공화면 진입
4. `[Auto]` 버튼 불을 꺼서 수동모드 진입 → `[X]`→`[HOME AXIS]` X축 이동 확인 → `[Y]`→`[HOME AXIS]` Y축 이동 확인
5. 수동모드에서 `[MACH CTRL]` 두 번 또는 우측 메뉴 `[UTIL]`→`[CLX]` → `[Gripper Open]`, `[Wrist Up]`, `[Arm Up]` 선택하여 내부 기계 팔 원위치 상승
6. `[Auto]`(자동모드) → `[HOME AXIS]`→`[ACK]`로 장비 원점 이동

> ⚠️ `[Auto]` 버튼 LED **켜짐=자동 / 꺼짐=수동**. 축 원점을 잡을 때는 **FEEDRATE 100%**로 맞출 것.

### 1.4 CNC 워밍업 (두 가지 방식)

**방식 A (Launch Pad)**
1. 원점 잡은 상태에서 `Util` → `Launch Pad`
2. Launch pad 창에서 시작시간 우측 `...` 클릭 → 현재시간 +1분 입력 → 확인
3. 시작 버튼 클릭 → 카운트다운 후 워밍업 시작

**방식 B (Warm Up 단축)**
1. 원점 잡은 상태에서 `Utilities` → `Warm Up` 클릭

### 1.5 Run-out(런아웃) 잡기

1. `Protrude length` 길이만큼 엔드밀 장착
2. 엔드밀 샹크부에 다이얼게이지 접촉(접촉부는 이물질 없는 깨끗한 면)
3. A축을 수동으로 돌리며 다이얼게이지로 동심 상태 확인 → L자 렌치로 동심도 보정

> 관련: [[런아웃-편심]] — 허용 기준(Premierplus < 5 μm) 및 진단 트리.

### 1.6 콜렛 교체

1. A축을 돌려 콜렛의 파이(π) 표기 부분이 보이게 함
2. L자 렌치로 콜렛 고정나사 풀기
3. 가공할 엔드밀에 맞는 콜렛으로 교체 후 고정나사 조임 — **콜렛 파이 표기부와 고정나사가 일직선상**에 위치시킨 후 조일 것

---

## 2. 인터페이스 — 엔드밀 가공 절차 (10단계)

① 가공 파일 열기 → ② Operation interface → ③ Common parameters → ④ Digitize EOT → ⑤ Digitize Lead/Helix/Shear → ⑥ Endface Gash → ⑦ Endface finish → ⑧ 엔드밀 장착 → ⑨ 가공 → ⑩ 가공 상태 확인

| 단계 | 내용 |
|------|------|
| 가공 파일 열기 | 가공하고자 하는 엔드밀 파일 불러오기 |
| Operation | 실행 시 첫 화면 — 좌측 Simulation(형상 미리보기) + 우측 Operation(가공 parameter 조정) |
| Common parameters | 날경(Common radius)·날수(Number of flutes)·헬릭스 각도(Helix)가 가공 대상 엔드밀과 일치하는지 확인 |
| Digitize EOT | `Protrude length` = 콜렛에 엔드밀 장착 시 나와야 하는 길이. **기계축 간 모션 충돌을 피하는 범위 내 최대한 짧게** 잡을 것 |
| Digitize Lead/Helix/Shear | 엔드밀 형상에 따라 `Index position`, `Lead/Helix/Shear` 조정 |
| Endface Gash | 빨간 원 클릭 → 가공에 맞는 Wheel인지 확인 |
| OD and finish | 빨간 원 클릭 → 가공에 맞는 Wheel인지 확인 |

---

## 3. 휠 드레싱 (Wheel Dressing)

### 3.1 A축 튜닝

`[APPL]` → `[RX7 A-axis Tuning]` → `[Dressing Wheels]` → `[125mm Dressing Wheel]` → `[Modify Tuning Parameters]`

### 3.2 드레싱 프로그램 실행 (7단계)

| 단계 | 조작 |
|------|------|
| 1 | APO창에서 `[프로그램]`→`[작동]`→`[Dress.pp]` 파일 불러오기 |
| 2 | Feedrate를 줄이고 Cycle Start → 드레싱 진행 여부 확인창에 "Y" 입력 → Dressing할 Wheel의 Wheelpack 번호 지정 |
| 3 | Spindle 각도 지정 — **cup wheel은 0도, gash wheel은 -95도 또는 -45도**. ⚠️ wheel 각도가 `+`가 되면 장비 충돌 위험 — **반드시 `-`로 지정** |
| 4 | Dressing Wheel 두께 입력 → 다음 창에서 Dressing 절입량 입력 |
| 5 | Dressing 횟수 입력 → X축 이동 속도(dressing 시) 입력 |
| 6 | Dressing 속도 입력 후 Enter로 다음 창까지 진행 → 메시지 확인 후 Cycle Start → Feedrate를 천천히 올려 A축·C축 센터를 일직선으로 정렬(지정한 C축 각도만큼 이동) |
| 7 | X, Y축 이동으로 Dressing Wheel과 대상 Wheel 접촉(손상 방지를 위해 **얇은 종이 사용**) → 문 닫고 ACK → Dressing 시작 |

### 3.3 Wheel Dressing 실행

Dressing 프로그램 실행 후 Feedrate를 낮추고 `[MPG Feed]` 버튼 → dial을 돌려 Wheel과 Chuck 접촉 여부 확인 → 확인 후 `[MPG Feed]` OFF → Feedrate를 올려 Dressing 진행.

### 3.4 Wheel 측정 (Qualification)

1. Wheel Editor에서 검증할 Wheel 값을 임의 변경 → 창이 뜨면 `[Qualification Bar]` 클릭
2. 측정할 Wheel 체크 (**11V9 = cup wheel / 1V1 = gash wheel**)
3. X, Y축을 이동해 환봉과 Wheel 접촉(드레싱과 동일하게 얇은 종이로 손상 방지) → 접촉 후 `[ACK]`로 기계에 값 적용

### 3.5 휠드레싱 관리표 입력

드레싱 작업 시 해당 휠에 대해 **드레싱 사유·횟수·절입량**을 기록. 절입량은 **마이크로미터(μm)** 단위로 기재.

### 3.6 유의사항

- Dressing Wheel 장착 시 풀리지 않도록 꽉 잡을 것
- Spindle 회전 시 장비와 충돌 위험 — 충분히 이격 후 회전
- Dressing Wheel과 Wheel 접촉 시 X, Y축을 급격히 이동시키지 말 것(손상 위험)
- 접촉 후 Y축을 살짝 뒤로 뺄 것(1~3 μm 정도)
- Dressing 프로그램 실행 후 장비와 Wheel 접촉 여부 확인 후에 Dressing 실행
- **Wheel의 Round(마모된 둥근 부분)가 없어질 때까지** Dressing 진행

---

## 4. 휠 교체

### 4.1 휠팩 분리

Wheel pack을 분리 후 wheel 분리대에 꽂고, handle을 Wheel pack에 장착 후 **시계방향**으로 돌려 분리.

> ⚠️ 작업 시 장갑 착용. handle에 과도한 힘을 주지 말 것(wheel과 충돌 가능). 분리가 잘 안 될 때 고무망치 사용 가능하나 **장착 시에는 고무망치 사용 금지**.

### 4.2 Wheel pack 장착

Wheel이 돌아가지 않게 고정한 뒤 T렌치를 wheel pack 중간에 꽂아 **시계반대 방향**으로 회전(분리 절차의 역순). 부착 시 반대로 진행.

> ⚠️ Wheel 고정하는 손은 반드시 장갑 착용. 과도한 힘 금지.

---

## 5. 관련 페이지

- [[anca-cnc-tool-grinder]] — ANCA 장비 개요·스택 구성·소프트웨어 생태계
- [[tools/재연마-형상-치수기준]] — 형상·치수 기준표·가공 Know-how
- [[cadcam/재연마-작업준비-절차]] — 선별·레이저마킹·밑작업(C40)
- [[런아웃-편심]] — Run-out 허용 기준·진단
- [[휠-밸런싱-iBalance]] — iBalance 소프트웨어 기반 휠 밸런싱(본 절차와 별개 기능)
- [[스택-1-1]], [[스택-1-2]] — 사내 운용 휠 스택 구성

## 6. 변경 이력

| 날짜 | 변경 내용 | 사유 | 출처 |
|------|----------|------|------|
| 2026-07-27 | 신규 작성 — 기계준비·인터페이스·휠드레싱·휠교체 전체 절차 이관 | 코툴스 생산팀 매뉴얼 ver6.0 위키 반영 | [INT-TOOLKOREA-PRODMANUAL-2026] |
