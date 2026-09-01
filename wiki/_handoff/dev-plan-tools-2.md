# 독립 실행 도구 개발 계획서 — 2차
작성일: 2026-06-10

---

## 도구 4 — 휠 수명 추적기

### 목적
CBN/다이아 연삭휠의 드레싱 횟수·누적 사용시간을 기록하고, 교체 기준 초과 시 카카오톡 알림.
현재 교체 판단이 작업자 경험에만 의존 → 재현 가능한 기준으로 정량화.

### 데이터 구조

`data/wheel_life.json` (신규)

```json
{
  "wheels": [
    {
      "id": "W001",
      "spec": "D125×T10×H32 CBN B126 V",
      "machine": "FAST",
      "installed_date": "2026-01-15",
      "dressing_count": 12,
      "total_time_sec": 185000,
      "threshold_dressing": 30,
      "threshold_time_sec": 600000,
      "status": "active",
      "log": [
        {"date": "2026-06-10", "type": "dressing", "note": "Ra 불량 후 드레싱"}
      ]
    }
  ]
}
```

### 작업 순서

1. `data/wheel_life.json` 스키마 설계 및 초기 데이터 입력 (현재 사용 중 휠)
2. `scripts/wheel_log.py` 작성
   - `add` 서브커맨드: 드레싱 또는 사용시간 기록
   - `status` 서브커맨드: 전체 휠 현황 출력
   - 교체 기준 초과 시 exit code 1 + 경고 메시지 출력
3. `scripts/check_wheel.py` 작성 (30줄 이내)
   - wheel_life.json 읽어 기준 초과 휠 검사
   - 초과 시 카카오톡 MemoChat 알림
4. Cowork 스케줄: 평일 오전 8:10 `check_wheel.py` 자동 실행
5. `run_wheel_log.bat` — 더블클릭 실행용

### 파일

| 파일 | 용도 |
|------|------|
| `data/wheel_life.json` | 휠 수명 데이터 저장소 |
| `scripts/wheel_log.py` | 드레싱/시간 기록 CLI |
| `scripts/check_wheel.py` | 교체 기준 점검 + 알림 |
| `run_wheel_log.bat` | 더블클릭 실행 |

### 실행 예시

```powershell
# 드레싱 1회 기록
python scripts\wheel_log.py add --id W001 --type dressing --note "Ra 불량 후"

# 사용시간 추가 (초 단위)
python scripts\wheel_log.py add --id W001 --type time --sec 3600

# 전체 현황 출력
python scripts\wheel_log.py status
```

### 알림 예시

```
⚠️ 휠 교체 권고
W001 (D125×T10×H32 CBN B126 V) — FAST
드레싱 횟수: 31회 / 기준: 30회 초과
누적 사용시간: 185,000s
```

### 교체 기준 (초기값 — 추정값, 실측 후 업데이트)

| 항목 | FAST | GX7 |
|------|------|-----|
| 드레싱 횟수 | 30회 | 20회 |
| 누적 사용시간 | 600,000s (~167h) | 400,000s (~111h) |

> ⚠️ 기준값은 추정값. 실측 데이터 3개월 누적 후 재검토 필수.

### 예상 소요 시간: 2~3시간

---

## 도구 5 — G코드 파라미터 검증기

### 목적
ANCA 출력 NC 파일을 실행 전 파싱해, 위험한 이송속도·절입 깊이를 감지하고 경고.
잘못된 조건으로 양산 적용되는 사고 방지.

### 검사 항목

| 항목 | 경고 기준 | 근거 |
|------|-----------|------|
| 이송속도 F | > 500 mm/min (드릴), > 2000 mm/min (엔드밀) | 사내 경험값 |
| 절입 깊이 ae | > 0.05 mm (CBN 초경 1패스) | 추정값 |
| 스핀들 RPM S | > 6000 RPM (FAST), > 4500 RPM (GX7) | 장비 사양 |
| 절삭속도 Vc | > 35 m/s (CBN) | 제조사 기준 |
| 급이송 G0 후 즉시 절삭 | G0 → G1 사이 안전 높이 없음 | 충돌 위험 |

> ⚠️ 기준값은 사내 경험값·추정값. 장비별 실측 검증 후 확정 필요.

### 작업 순서

1. ANCA NC 파일 샘플 수집 (현재 사용 중 프로그램 3~5개)
2. `scripts/gcode_check.py` 작성
   - NC 파일 한 줄씩 파싱
   - 위험 라인 번호·값·기준 출력
   - exit code: 0(정상), 1(경고), 2(위험)
3. 기준값 설정 파일 `config/gcode_limits.json`
   - 장비별(FAST/GX7)·공구별(드릴/엔드밀) 분리
4. `run_gcode_check.bat` — NC 파일 드래그앤드롭 실행
5. (선택) wiki/gcode/ 에 검증 결과 md 자동 저장

### 파일

| 파일 | 용도 |
|------|------|
| `scripts/gcode_check.py` | NC 파일 파싱·검증 |
| `config/gcode_limits.json` | 장비·공구별 기준값 |
| `run_gcode_check.bat` | 드래그앤드롭 실행 |

### 실행 예시

```powershell
python scripts\gcode_check.py path\to\program.nc --machine FAST

# 드래그앤드롭
run_gcode_check.bat program.nc
```

### 출력 예시

```
[검사 대상] program.nc  /  장비: FAST
──────────────────────────────────────
⚠️  LINE 47 — F600 이송속도 초과 (기준: 500 mm/min)
    → G83 Z-12.0 R2.0 Q1.5 F600
⚠️  LINE 112 — S6500 RPM 초과 (기준: 6000 RPM)
    → G0 S6500 M3
──────────────────────────────────────
총 2건 경고. 실가공 전 조건 재확인 권장.
```

### 전제 조건 (진행 전 확인 필요)

- [ ] ANCA NC 파일 샘플 제공 (파싱 대상 확인용)
- [ ] FAST / GX7 스핀들 최대 RPM 확인
- [ ] 공구 종류별 이송속도 안전 기준 확인

### 예상 소요 시간: 2~3시간 (샘플 파일 있을 경우)

---

## 우선순위 및 순서

| 순서 | 도구 | 이유 |
|------|------|------|
| 1 | 도구 4 휠 수명 추적기 | 데이터 구조 단순, 즉시 시작 가능 |
| 2 | 도구 5 G코드 검증기 | NC 파일 샘플 필요 — 샘플 준비 후 진행 |

---

## 결정 사항

2026-06-10: 도구 4·5 계획서 확정
- 결정: 휠 수명 추적기 먼저 진행
- 근거: 데이터 구조 설계 선행 필요, NC 파일 샘플 확보 대기
- 출처: 챗
- 영향: 도구 5는 NC 파일 샘플 제공 후 착수
