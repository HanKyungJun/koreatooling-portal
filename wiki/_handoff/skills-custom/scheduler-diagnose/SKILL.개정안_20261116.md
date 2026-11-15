---
name: scheduler-diagnose
description: |
  [스케줄러 진단] 일일보고 자동화(CNC_Daily_Report 등)가 누락·오류로 보일 때 근본 원인을 심층 진단합니다.
  run.log·generate.log 실측 대조, 원본 재연마_월간생산일지 xls의 해당 일자 시트 직접 확인(무실적 vs 입력누락 vs
  스크립트 오류 구분), Task Scheduler PowerShell 진단(LastRunTime/LastTaskResult/History 로그), 휴무일·공지된
  휴가 일정 대조까지 수행합니다.
  "스케줄러 확인", "스케줄러 진단", "자동화 왜 안 도는지", "누락 원인 확인해줘", "왜 보고서가 안 만들어졌는지" 등으로
  실행합니다. daily-report-check에서 누락·오류가 발견됐을 때 이어서 사용하거나, 사용자가 바로 이 스킬을 지정해
  호출할 수 있습니다.
---

# 스케줄러 심층 진단 스킬

## 목적

`daily-report-check`가 "무엇이 누락됐는지"를 확인하는 스킬이라면, 이 스킬은 **"왜 누락됐는지"를 근거 기반으로
좁혀가는** 스킬입니다. "파일이 없다 = 스케줄러 오류"로 단정하지 않고, 아래 순서로 실제 원인을 분류합니다.

이 스킬은 2026-08-06 세션에서 08-03·08-04 일일보고 누락 건을 실제로 진단한 과정(run.log 실측 → 원본 xls 일자별
시트 직접 열람 → Task Scheduler PowerShell 안내 → 하계휴가 확인)을 표준 절차로 정리한 것입니다.

---

## 실행 순서

### 0단계 — 선행 확인: 휴무 단일 소스 `holidays.md` 와 먼저 대조

깊은 진단에 들어가기 전에, 그 날이 이미 등재된 휴무인지부터 확인해 오탐을 거릅니다.
휴무 판단은 **`wiki/_handoff/holidays.md` 하나만** 봅니다(CLAUDE.md §13 단일 소스) — §1 법정공휴일,
§2 사내 임시휴무·하계휴가·**개인 연차(한경준님 부재 = 생산 정지, 2026-08-27 개정)**.
`decisions.md`·`worklog.md` 를 grep 하지 않습니다(옛 기록은 아카이브로 옮겨져 빠지고, 휴무 정보가 분산됨).

모든 명령은 `device_bash` 에서 `$HOME/mnt/cnc-wiki` 기준으로 실행합니다(경로 하드코딩 금지).

```bash
cd "$HOME/mnt/cnc-wiki" && for d in YYYY-MM-DD YYYY-MM-DD; do
  grep -n "^| $d |" wiki/_handoff/holidays.md || echo "$d — holidays.md 등재 없음"
  TZ=Asia/Seoul date -d "$d" '+  요일: %a'
done
```

- 표 행이 나오면 → "무실적(휴무)"로 잠정 결론, 아래 1~4단계는 생략하고 5단계(기록)로 바로 이동해도 됩니다.
- 「등재 없음」이면 아래 단계를 이어갑니다. 진단 중 사용자가 "그날 쉬었다"고 확인해 주면, 결론을 내기 전에
  `holidays.md` §3 절차대로 **이 파일에 먼저 행을 추가**합니다(추가는 사용자 승인 후 — 아티팩트에만 넣으면
  다음 진단이 또 오판, 2026-08-26 사례).
- 법정공휴일이 정부 발표로 바뀐 의심이 들면(예: 제헌절 2026-05-11 재지정) holidays.md §1 을 갱신하자고
  제안합니다 — 스킬 안에 날짜를 따로 적지 않습니다.

### 1단계 — run.log / generate.log 실측 대조

문제가 된 날짜 전후 구간을 시간순으로 열어, 그 날짜에 어떤 시도 흔적이라도 있었는지 확인합니다. 로그 파일은
UTF-8이지만 일부 구간에 손상/혼입 바이트가 있을 수 있어 `errors='replace'`로 읽습니다.

```bash
python3 -c "
with open('wiki/reports/daily/run.log','rb') as f:
    text = f.read().decode('utf-8', errors='replace')
for i, l in enumerate(text.split(chr(10))):
    if 'YYYY-MM-DD' in l or '오류' in l or 'ERROR' in l:
        print(i, l)
"
```

판단 기준:

- 해당 날짜 관련 줄이 **전혀 없음** → 스케줄러 자체가 트리거되지 않았을 가능성(PC 꺼짐·휴무·절전 등) — 3단계로.
- **오류 메시지가 있음** → 스크립트 실패(원본파일 부재, 예외 등) — 오류 메시지 원문으로 원인 특정, 4단계는 생략 가능.
- **정상 완료 로그는 있는데 보고서 파일이 실제로 없음** → 저장/이동 단계 이상 — 별도 조사 필요(이 스킬 범위 밖,
  daily_report.py 코드 리뷰 필요).

### 2단계 — 원본 xls 해당 일자 시트 직접 확인 (핵심 — 파일 존재 여부만으로 판단 금지)

`raw/출하현황/재연마 작업일지(YYYY)/재연마_월간생산일지 (M월).xls`을 열어 **월간합계표 시트의 해당 일자 행**과
**해당 일자 개별 시트("3", "4" 등)**를 모두 확인합니다. (xls는 pandas + xlrd 필요: 없으면
`pip install xlrd --break-system-packages`)

```python
import pandas as pd
path = "raw/출하현황/재연마 작업일지(2026)/재연마_월간생산일지 (M월).xls"

# 월간합계표: pandas 행 index = day + 1 (1일 = index 2)
summary = pd.read_excel(path, sheet_name=0, header=None)
print(summary.iloc[day + 1])

# 해당 일자 개별 시트(FAST GRIND / GX7 작업 상세)
detail = pd.read_excel(path, sheet_name=str(day), header=None)
print(detail.head(40))
```

판단 기준:

- FG/GX 수량 합계가 0이고 개별 시트도 작업 항목 전부 공란 → **실적 자체가 없었을 가능성** — 사용자에게 직접
  "그 날 실제로 작업이 없었는지"를 확인합니다(휴무·휴가·설비중단 등, AI가 추측으로 결론 내리지 않음).
- 합계는 0인데 다른 경로(구두 보고 등)로 실제 작업이 있었다고 확인되는 경우 → **입력 누락** — 스크립트 문제가
  아니라 현장 입력 누락. 현장에 xls 입력을 요청한 뒤 아래 소급 명령으로 리포트 생성.
- xls 파일 자체가 없음(월초) → `wiki/_handoff/tasks.md`의 기존 항목("매월 1일 전후 당월 파일 사전 생성") 참고 —
  `find_xls()` 실패로 인한 연쇄 실패(daily_report.py가 실패해도 generate.py는 별도 스케줄로 계속 실행되므로
  대시보드는 살아있을 수 있음, 착각 주의).

### 3단계 — Task Scheduler 상태 확인

**Cowork는 Windows PowerShell을 직접 실행할 수 없습니다** — device_bash는 사용자 PC의 Windows 셸이 아니라
격리된 Linux 환경이므로, 아래 명령은 항상 사용자에게 그대로 안내하고 결과를 받아서 해석합니다.

```powershell
Get-ScheduledTaskInfo -TaskName "CNC_Daily_Report" | Format-List *
Get-ScheduledTask -TaskName "CNC_Daily_Report" | Select-Object State
(Get-WinEvent -ListLog "Microsoft-Windows-TaskScheduler/Operational").IsEnabled
```

- `LastTaskResult`가 `0`이 아니면 가장 최근 실행이 실패한 것 — 그 값 자체로 원인 코드 조회 가능.
- `IsEnabled = False`이면 History(이벤트) 로그가 비활성 상태 — **과거 특정 날짜의 개별 실행 이력은 지금
  조회해도 나오지 않습니다.** 이 경우 원인 규명은 여기서 멈추고(추정만 가능), 4단계로 넘어가 재발 방지용으로
  로그를 활성화합니다.
- `IsEnabled = True`이면 특정 기간을 조회할 수 있습니다:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 3000 |
  Where-Object { $_.Message -match "CNC_Daily_Report" -and $_.TimeCreated -ge "YYYY-MM-DD" -and $_.TimeCreated -le "YYYY-MM-DD" } |
  Sort-Object TimeCreated | Select-Object TimeCreated, Id, Message | Format-Table -Wrap
```

### 4단계 — History 로그가 비활성 상태였다면 활성화 안내 (재발 방지, 소급 아님)

```powershell
wevtutil sl Microsoft-Windows-TaskScheduler/Operational /e:true
```

- 일반 PowerShell에서 실행 시 "액세스가 거부되었습니다" 오류가 흔합니다 — **관리자 권한 PowerShell**로
  재실행하도록 안내합니다(시작 메뉴에서 PowerShell 우클릭 → "관리자 권한으로 실행"). 또는 GUI:
  `taskschd.msc`(관리자 권한 실행) → Action → "모든 작업 기록 사용(Enable All Tasks History)".
- 완료 확인: `(Get-WinEvent -ListLog "Microsoft-Windows-TaskScheduler/Operational").IsEnabled` → `True`.
- 활성화는 **이 시점 이후의 실행 이력만** 남기기 시작합니다. 이미 지나간 날짜의 이력을 복원하지는 못합니다 —
  사용자에게 이 한계를 분명히 알립니다.

### 5단계 — 결론 분류 및 기록

아래 4가지 중 하나로 원인을 명확히 분류합니다. 근거가 부족해 분류가 애매하면 "확인 필요"로 얼버무리지 말고,
사용자에게 구체적으로 질문해 답을 얻은 뒤 결론을 내립니다(무실적·휴가 여부는 AI가 추측할 수 없는 사실입니다).

| 분류 | 근거 | 조치 |
|------|------|------|
| 무실적(휴무·휴가) | xls 해당일 시트 전부 공란 + 사용자 확인 | 소급 생성 불필요, 종결 |
| 입력 누락 | xls는 공란이나 실제 작업이 있었다고 확인됨 | 현장에 입력 요청 → 입력 후 `python scripts\daily_report.py YYYY-MM-DD`로 소급 생성 |
| 스크립트/원본파일 오류 | run.log에 오류 메시지 확인 | 오류 메시지 기반 원인 수정(예: 월간 xls 파일 사전 생성) |
| 스케줄러 미실행(PC·트리거 문제) | run.log에 해당일 기록 전무 + History 로그로도 확인 불가 | 재발 방지 위해 History 로그 활성화, PC 전원/절전 설정 점검 권고 |

진단 결과를 `wiki/_handoff/worklog.md` **맨 위**에 다음 형식으로 기록합니다:

```markdown
## YYYY-MM-DD 스케줄러 진단 — Cowork

- 대상: YYYY-MM-DD 일일보고 누락
- 0단계(휴무 대조): [결과]
- 1단계(run.log): [결과]
- 2단계(원본 xls): [결과]
- 3단계(Task Scheduler): [결과]
- 결론: [4분류 중 하나] — [근거]
- 조치: [완료 / 필요 / 사용자 확인 대기]
```

근본 원인 규명으로 새로운 결정(재발방지책, 프로세스 변경 등)이 발생하면 `wiki/_handoff/decisions.md`
**맨 위**에 ADR 형식(§5)으로 추가합니다.

---

## 판단 기준 요약

- 보고서 파일이 없다는 사실 하나만으로 "스케줄러 오류"라고 단정하지 않습니다 — 반드시 원본 xls의 실제 데이터를
  먼저 확인합니다.
- "확인 필요"로 얼버무리지 말고, 근거가 부족하면 사용자에게 구체적으로 질문해 답을 얻습니다.
- Cowork는 Windows PowerShell을 직접 실행할 수 없습니다 — 항상 정확한 명령을 사용자에게 안내하고, 결과를
  받아서 해석하는 역할을 합니다.
- 공휴일·휴가 오탐은 실제로 반복 발생한 이력이 있습니다(2026-07-24, 제헌절 오탐 3연속) — 0단계를 생략하지
  않습니다. 휴무 근거는 `holidays.md` 한 곳뿐입니다(CLAUDE.md §13).

## 주의사항

- `raw/` 폴더는 읽기만 하고 수정하지 않습니다.
- `worklog.md`·`decisions.md`는 항상 맨 위에 추가하고, 기존 내용은 삭제하지 않습니다.
- 이 스킬은 `daily-report-check`가 누락·오류를 발견했을 때 이어서 쓰거나, 사용자가 직접 호출할 수 있습니다.
