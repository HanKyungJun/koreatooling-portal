---
type: reference
category: "예약 작업 프롬프트"
subject: "예약작업 프롬프트 정본 폴더 — 색인"
tags: [예약작업, trigger, 색인, 자동화]
updated: 2026-09-22
---

# 예약작업 프롬프트 정본 — 색인

> 🔴 **클라우드 예약작업의 프롬프트는 저장소에 없다.** 유실되면 복구가 어렵고, 실행 세션이 실제로 무엇을 지시받는지 나중에 확인할 방법도 없다.
> **이 폴더가 정본이다.** 프롬프트를 바꿀 때 해당 파일도 같이 갱신한다.

## 활성 예약작업 (2026-09-22 기준 5개)

| 파일 | 이름 | 발사 시각 (KST) | trigger_id | 모델 |
|---|---|---|---|---|
| [[trigger-prompts/통합-아침브리핑]] | cnc-wiki 아침 브리핑 | **평일 08:15** (월요일만 B절 추가) | `trig_01BHsVdEvj8R7u5KNuxVToHK` | opus-5 |
| [[trigger-prompts/금요일-마무리-점검]] | cnc-wiki 금요일 마무리 점검 | **금 15:30** ⚠️ (파일 제목은 16:10 — 아래 참조) | `trig_011eUN7NjcvnwTNif2j6WSHj` | opus-5 |
| [[trigger-prompts/월초-마감점검]] | cnc-wiki 월초 마감 점검 | **매월 1일 10:00** | `trig_01DXfqMnFiH19LAqSGrsi5SS` | opus-5 |
| (정본 없음) | GitHub 토큰 만료 1주일 전 알림 | 2026-11-19 (일회성) | `trig_01HCp6RnuePYHjr2Bo2r141K` | opus-5 |
| (정본 없음) | GitHub 토큰 만료 당일 — 예비 | 2026-11-26 (일회성) | `trig_016jtw4e73dApw9CLd2oMVoz` | opus-5 |

> 토큰 만료 알림 2건은 일회성이고 실행 후 소멸하므로 정본 파일을 두지 않았다. 절차 본문은 `wiki/scripts/github-token-발급-체크리스트.md` 에 있다.

## 비활성 — 2026-09-21 통합으로 흡수 (되살리지 말 것)

| 이름 | 흡수처 | trigger_id |
|---|---|---|
| `[통합됨→아침브리핑]` 주간 KPI 브리핑 | 통합 브리핑 **B절** | `trig_01R8ahHuSuRDZGj3eQeTxnSA` |
| `[통합됨→아침브리핑]` cnc-wiki 주간 검수 | lint → 월초 점검 **⑤** / 대장 재생성 → 통합 브리핑 **B절 10번** | `trig_018RiZqu51WfW25iRxmYEuiT` |
| `[통합됨→월초점검⑥]` 월간 출하현황 마감 알림 | 월초 점검 **⑥** | `trig_014654SQz5aSzyNkRyVAG9tA` |

🔴 **다시 켜면 캐치업 1회가 즉시 발사된다** — 2026-09-03 에 그 실행이 `.git/index.lock` 을 남겨 커밋이 막힌 전례가 있다.
🔴 그 위의 옛 5개(`cnc-morning-briefing`·`cnc-weekly-lint`·`cnc-weekly-decisions`·`cnc-worklog-check`·`cnc-overview-daily`)는 **낡은 저장소(HanKyungJun/cnc-wiki)를 읽던 것들로 재활성 금지**다.

## ⚠️ 발견된 불일치 (2026-09-22, 실측)

> [작성자: Cowork / 날짜: 2026-09-22]
> `금요일-마무리-점검.md` 정본의 cron 표기는 `10 7 * * 5 (UTC) = 금 16:10 KST` 인데, **실제 가동 값은 `CRON_TZ=Asia/Seoul 30 15 * * 5` = 금 15:30 KST** 다 (`next_run_at` 2026-09-25 06:38 UTC = **15:38 KST**).
> 예약작업 이름도 「금 16:10」을 달고 있다. 기존 값은 지우지 않고 병기해 둔다 — **어느 쪽이 의도인지 한경준님 확인 필요**.
> 근거: [SYS-COWORK] 2026-09-22 `list_triggers` 실측.

같은 유형으로, 「아침 브리핑」도 이름은 **08:00** 이나 실제 발사는 **08:15** 다(이쪽은 2026-09-21 개편 시 의도된 변경 — decisions.md 2026-09-21 (4)).

## 프롬프트를 바꿀 때

1. `update_trigger(prompt=...)` 를 **먼저 시도**한다 (2026-09-21 성공: `prompt re-signed by Claude Desktop (Windows)`)
2. 막히면 Cowork 예약작업 UI 에서 직접 붙여넣기
3. 🔴 **삭제하고 새로 만들지 말 것** — 실행 이력과 컴퓨터 연결이 사라진다
4. 🔴 **알림 채널(이메일 ON/OFF)은 도구로 못 바꾼다** — 예약작업 설정에서 직접
5. **이 폴더의 정본 파일과 변경 이력 표를 같이 갱신**한다
6. 신설·수정했으면 **정규 발사를 기다리지 말고 `fire_trigger` 로 즉시 1회 발사해 검증**한다 (decisions.md 2026-09-22 (1) §②)

## 관련 페이지

- `wiki/_handoff/decisions.md` **2026-09-21 (4)**·**(5)** · **2026-09-22 (1)**
- 프로젝트 메모리 `automation-triggers-cnc-wiki`
