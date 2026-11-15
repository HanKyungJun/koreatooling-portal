---
name: "daily-report-check"
description: "[일일보고서 점검] wiki/reports/daily/ 폴더에서 최근 보고서 생성 현황을 확인하고 누락 날짜와 원인을 파악합니다. \"일일보고서 확인\", \"보고서 누락 확인\", \"daily report 상태\", \"보고서 생성됐어?\" 등으로 실행합니다. 보고서가 안 보인다거나, 자동화가 돌고 있는지 의심될 때 반드시 이 스킬을 사용합니다."
---

# 일일보고서 확인 스킬

## 목적

`wiki/reports/daily/` 를 점검해 최근 7영업일 기준 누락 파일을 탐지하고, `generate.log` 로
실행 결과를 확인해 **결과를 호출한 쪽에 돌려줍니다.**

🔴 **이 스킬은 `worklog.md` 를 자동으로 쓰지 않습니다** (2026-09-21 변경 — 아래 4단계 참조).

---

## 🔴 시작 전 반드시 읽을 3가지

### ① 경로를 하드코딩하지 않는다

세션마다 마운트 경로가 바뀝니다. **절대경로를 스킬에 적어두면 다음 세션에서 빈 결과가 나옵니다**
(2026-09-08 실제 발생 — 옛 세션 경로가 박혀 있어 점검이 조용히 0건을 냈다).
모든 명령은 `device_bash` 에서 `$HOME/mnt/cnc-wiki` 를 기준으로 실행합니다.

```bash
cd "$HOME/mnt/cnc-wiki" && pwd && ls wiki/reports/daily/ | tail -3
```

위 명령이 실패하면 폴더가 연결되지 않은 것이므로 진단을 진행하지 말고 사용자에게 알립니다.

### ② 시각은 전부 KST 로 환산해 말한다

`device_bash` 의 `ls`·`stat` 타임스탬프와 컨테이너 `date` 는 **UTC** 입니다. **+9시간** 해야 KST 입니다.
예: mtime `2026-09-07 07:00:15 +0000` = **16:00:15 KST** (= 정규 실행 시각).

```bash
TZ=Asia/Seoul date '+지금 KST: %Y-%m-%d %H:%M (%A)'
stat -c '%y  %n' wiki/reports/daily/*.xlsx | tail -5   # +0000 = UTC, +9h 환산
```

환경이 알려주는 날짜가 하루 이전인 사례가 3회 있었습니다. **날짜 판단은 위 명령 결과로 합니다.**

### ③ 생성 시각은 16:00 KST 다 (17:30 아님)

| 작업 | 시각 | 성격 |
|---|---|---|
| `CNC_Daily_Report` | **평일 16:00 KST** | 정규 |
| `CNC_Daily_Report_OnBoot` | PC 부팅 시 | 캐치업 |

🔴 **07~08시대 로그는 OnBoot 캐치업이며 정규 실행 성공의 근거가 되지 못한다.**
실행 주체가 달라 권한·자격증명이 다릅니다(2026-09-07 에 이것을 혼동해 「복구됐다」고 오판한 사례 있음).
**정규 실행을 판정할 때는 16:00 블록을 봐야 합니다.**

---

## 실행 순서

### 0단계 — 휴무일 대조 (먼저 한다)

누락으로 보이는 날이 **휴무일이면 정상**입니다. 휴무일 판단은 반드시 단일 소스를 씁니다.

```bash
cd "$HOME/mnt/cnc-wiki" && sed -n '20,63p' wiki/_handoff/holidays.md
```

`wiki/_handoff/holidays.md` 가 **유일한 진실 공급원**입니다 — §1 법정공휴일, §2 사내 임시휴무·연차.
**개인 연차도 포함**됩니다(한경준님 부재 = 실질 생산 정지, 2026-08-27 개정).
스킬에 공휴일을 따로 하드코딩하지 않습니다.

### 1단계 — 보고서 파일 목록

```bash
cd "$HOME/mnt/cnc-wiki" && ls -1 wiki/reports/daily/*.xlsx | sort | tail -12
```

파일명 형식: `YYYY-MM-DD_일일보고.xlsx`

### 2단계 — 누락 날짜 계산

```bash
cd "$HOME/mnt/cnc-wiki" && python3 - <<'EOF'
from datetime import date, timedelta
from zoneinfo import ZoneInfo
import datetime as dt, os

base = "wiki/reports/daily"
today = dt.datetime.now(ZoneInfo("Asia/Seoul")).date()   # KST 기준
print(f"기준일(KST): {today}")

days, d = [], today
while len(days) < 7:
    if d.weekday() < 5:
        days.append(d)
    d -= timedelta(days=1)

for d in sorted(days):
    p = os.path.join(base, f"{d:%Y-%m-%d}_일일보고.xlsx")
    wd = ['월','화','수','목','금','토','일'][d.weekday()]
    if os.path.exists(p):
        m = dt.datetime.fromtimestamp(os.path.getmtime(p), ZoneInfo("Asia/Seoul"))
        print(f"{d} ({wd}) ✅  생성 {m:%H:%M} KST")
    else:
        print(f"{d} ({wd}) ❌ 없음")
EOF
```

생성 시각이 16:00 대가 아니면 그 자체가 단서입니다(OnBoot 캐치업 또는 수동 실행).

### 3단계 — generate.log 판독 (해당 날짜 블록을 직접 본다)

```bash
cd "$HOME/mnt/cnc-wiki" && tail -60 wiki/reports/daily/generate.log
```

로그 타임스탬프는 **로컬(KST) 기준으로 기록**됩니다. 확인할 4줄:

| 로그 줄 | 정상 | 비정상 |
|---|---|---|
| `→ YYYY-MM-DD 재연마_월간생산일지` | 날짜가 해당일 | 날짜 불일치 = 원본 미갱신 |
| `사내 배포 단계 종료 — 성공` | 성공 + 파일 수 | `실패/건너뜀`, `WinError 1312` |
| `[git] add 단계 완료: N개 대상` | 실패 줄 없음 | `git add 실패 N건` |
| `[git] commit` | `code=0` 또는 `code=1` | 그 외 |

🟢 **`commit code=1` 은 오류가 아니다** — 재생성 결과가 이전과 같아 커밋할 것이 없는 정상 동작입니다.
2026-09-08 부터 일일보고 xlsx·`overview.md` 가 add 대상에 포함돼 **`code=0` 도 정상**입니다.

⚠️ **사내 배포 경로는 2026-09-21 에 바뀌었습니다** — SMB 서버(`\\192.168.0.252\...`)를 운용 중단하고
로컬 폴더 `C:\Users\TOOLKOREA\Desktop\현황판` 으로 전환했습니다. 서버 관련 오류(1312·1326)를 찾지 마세요.

### 4단계 — 결과 반환 (🔴 worklog 자동 기록 없음)

결과를 **호출한 쪽에 요약해 돌려줍니다.** `worklog.md` 에는 **쓰지 않습니다.**

🔴 **2026-09-21 변경 이유 — 이중 기록.** 이 스킬이 스스로 worklog 를 쓰던 시절, 예약작업
「통합 브리핑」이 이 스킬을 호출하면 **한 실행에 worklog 블록이 2개** 생겼습니다(스킬 블록 + 브리핑 블록).
두 블록의 내용이 겹칠 뿐 아니라 **서로 모순되기까지 했습니다** — 스킬 블록은 점검 시점 상태를,
브리핑 블록은 그 뒤 해소된 상태를 적었기 때문입니다. `worklog.md` 는 이미 85블록·295 KB 이고,
이대로면 매 호출마다 두 배로 불어납니다.

같은 원칙이 「주간 위키 검수」에도 이미 적용돼 있었습니다 — *"검수 결과를 worklog 에 자동으로 쓰지 마세요.
한경준님이 원하시면 그때 기록합니다."* **점검은 기록이 아닙니다.**

**worklog 에 남길지는 호출한 쪽이 정합니다.** 사용자가 명시적으로 요청했거나 예약작업 프롬프트가
지시한 경우에만, 호출한 쪽에서 아래 형식으로 **맨 위에 추가**합니다(덮어쓰지 않음.
한글 파일 쓰기는 PowerShell 대신 `device_bash` 의 python UTF-8 로).

```markdown
## YYYY-MM-DD 일일보고서 점검 — Cowork

- 점검 범위: 최근 7영업일 (YYYY-MM-DD ~ YYYY-MM-DD), 휴무일 대조: `holidays.md` (해당 없음 / N일)
- 정상: N일 (날짜 나열) — 생성 시각 확인 방식 명시(파일 mtime 실측)
- 누락: N일 (날짜) / 0일
- 마지막 로그: YYYY-MM-DD HH:MM KST — 정규(16:00) / OnBoot 캐치업 구분해서 적을 것
- 사내 배포: 성공 N개 파일 / 실패(사유)
- 조치 필요: 없음 / (구체적 조치)
```

---

## 판단 기준

| 상황 | 판정 |
|---|---|
| 오늘 파일 없음 + **16:00 KST 이전** | 정상 — 생성 시각 전 |
| 오늘 파일 없음 + 16:00 KST 이후 | 🔴 스케줄러 확인 → `scheduler-diagnose` 스킬 |
| 누락일이 `holidays.md` 에 등재 | 정상 — 휴무일 |
| 2일 이상 연속 누락(휴무 아님) | 🔴 `scheduler-diagnose` 후 수동 실행 권고 |
| 파일은 있는데 생성 시각이 16:00 대가 아님 | OnBoot 캐치업 가능 — 정규 실행 실패 여부 확인 |
| 로그에 `사내 배포 실패` | 🔴 현황판이 옛 데이터로 남는다 — 즉시 보고 |

---

## 🔴 스케줄러 상태 판정 — `LastTaskResult` 를 근거로 쓰지 않는다

```powershell
Get-ScheduledTask -TaskName "CNC_Daily_Report" | Select-Object TaskName, State,
  @{n='LogonType';e={$_.Principal.LogonType}}
Get-ScheduledTaskInfo -TaskName "CNC_Daily_Report" | Select-Object LastRunTime, LastTaskResult, NextRunTime
```

- 🔴 **`LastTaskResult = 0` 은 「정상」의 근거가 아니다.** 2026-09-03 실측: ANCA 모니터가 5개 소스
  **전량 실패**(404·SSL·403)했는데 종료코드는 **0** 이었고 60회 전부 정상으로 보였습니다.
  → **판정은 산출물로 한다** — 여기서는 일일보고 xlsx 존재와 `generate.log` 내용.
- ⚠️ **`NextRunTime` 도 근거가 아니다** — 비활성 작업도 예정 시각을 그대로 표시합니다. **판정 기준은 `State`.**
- ⚠️ `LastTaskResult = 1` 이면 파이프라인이 살아 있어도 **작업은 실패로 끝난 것**입니다(둘 다 참일 수 있음).

수동 실행:

```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
scripts\daily_and_upload.bat     # 4단계 전체(보고서+캘린더+overview+포털) — 정규 배치와 동일
scripts\run_daily_report.bat     # 보고서 + Sheets 업로드만
```

🟢 **`python generate.py --local` 은 git 을 건드리지 않습니다** — `upload_to_github()` 블록 전체를
건너뛰므로 인덱스 락 위험 없이 포털·사내 배포만 재생성해 볼 수 있습니다(2026-09-21 실측 검증).

---

## 주의사항

- `raw/` 폴더는 수정하지 않습니다(읽기 전용).
- 🔴 **이 스킬은 어떤 파일도 쓰지 않습니다** — 점검과 보고만 합니다. 기록 여부는 호출한 쪽이 정합니다.
- worklog 에 기록할 때는 **맨 위에 추가**하고 기존 내용을 덮어쓰지 않습니다.
- 단가·금액은 위키에 기록하지 않습니다. 거래처는 A/B/C 로 익명화합니다.
- `device_bash` 에서 git 은 **읽기 전용 명령만** 사용합니다(`log`·`status`·`diff`·`ls-files`·`rev-parse`,
  전부 `--no-optional-locks` 와 함께). `add`·`commit`·`rm`·`fetch` 는 **`--dry-run` 이라도** 인덱스 락을
  잡고 이 마운트에서는 락을 지울 권한이 없어 다음 정규 실행을 망칩니다 — **PowerShell 에서만** 실행합니다.
- 추정과 실측을 구분해 적습니다. 「일시적 현상으로 보인다」 같은 문장에는 **[추정값]** 을 명시하고,
  실측으로 확인된 것에는 **[실측 검증]** 을 붙입니다.