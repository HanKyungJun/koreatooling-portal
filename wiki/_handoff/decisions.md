# 결정사항 로그

> 무엇을(What), 왜(Why), 출처(Where)를 **시간 역순(최신이 맨 위)** 으로 기록합니다.
> 챗에서 결정된 내용도 반드시 여기로 옮겨야 Code/Cowork가 따라옵니다.

## 2026-11-27 (6): AL 「2차 ALEC」 시험일 = 2024-03-10(폴더 7) · 2024 AL 3사 공구 모두 비코팅 · 작업일지 「스퀘어」 = 「평」(FL) 옛 이름

- 결정: ① J.J.(장진) 3ALEC 「2차」 시험 날짜를 2026-07 → 2024-03-10(폴더 7)으로 병기 정정 — 결론(코팅이 개선 요인)은 유지, 「약 1.16배」 → RPM 1.16배 · Vf 1.26배. 폴더 7 「파손 형태 X」 = 파손 없음 ② 2024년 AL 3사 공구(J.J 3ALE · OKE OMAL-3E-100 · YG-1 E5D70100) 모두 비코팅으로 통일(옛 코팅 추정은 취소선) ③ 작업일지 형상 「스퀘어」는 2023-04 에 「평」으로 이름만 바뀐 같은 FL — `연삭-조건-스퀘어` 는 2022 ~ 2023-04 기록으로 보존하고 새 기록은 `연삭-조건-평`, `scripts/make_tool_pages.py` 분류 스퀘어 → 평 · 「R01.2」 → 코너R · 데이터 없는 형상은 페이지를 덮어쓰지 않음 ④ 넥 기준표 §4 에 AFCY 테스트 1 · 2 · 4 실측 추가
- 근거: 폴더 7 xlsx(2024-03-10) 장진 열과 폴더 13 xlsx(2026-07-10) 2차 열의 값 7개 일치(품번 · OH 40 · 241.5 m/min · 7,687 rpm · 1,798 mm/min · fz 0.078 · 부하 17/18/18 %) · 같은 양식 NC드릴 보고서 NC_3 · NC_4 용례(「X」 열 = 시험 결과 「매우 우수」) · 폴더 13 공구 시트 3ALE 「비코팅」 · 작업일지 2022 ~ 2026 형상 이름별 재집계(2023-03 스퀘어만 · 04 둘 다 · 05 부터 평만, FL 합 19,663개). 검토한 대안: 스퀘어 페이지를 평 페이지로 합쳐 옮기기 — 이동이라 안내 머리만 둠
- 출처: Cowork(위키 중복 · 불일치 점검 2차, 한경준님 승인)
- 영향: comparisons/AL엔드밀 3종 · JJ종합 · 호닝 · AL코팅 · tools/연삭-조건-스퀘어 · 연삭-조건-목록 · index · scripts/make_tool_pages.py · standards/넥-지름-기준-굽힘강성표 §4

## 2026-11-27 (5): D6 4날 코너R End Face Gash 3,850 rpm(25.2 m/s)은 「사내 상한 초과 이력」으로 표기 — 다시 쓸 때 3,820 rpm 이하

- 결정: 2026-04-21 현장 판정 「확정 3,850 rpm」은 기록으로 보존하되, 위키 12곳의 「확정 · 권장 구간」 표기를 「확정(04-21) · ⚠️ 사내 상한 초과 — 재사용 시 3,820 rpm 이하(현장 확인 뒤)」로 통일한다. D8 4날 코너R 상향 목표 「3,500 ~ 3,850」 → 「3,500 ~ 3,820」. 사내 운용 상한 25 m/s 는 그대로 둔다. 2026-08-24 ②(a) 「홍익다이아 서면 회신 전까지 미종결 병기」는 종결한다
- 근거: Vc = π × 125 × 3,850 ÷ 60,000 = 25.20 m/s > 25 m/s(N 상한 = 60,000 × 25 ÷ (π × 125) ≈ 3,820 rpm). 미종결 근거였던 서면 회신은 decisions 2026-11-06 (1) 「문의 안 함」으로 경로가 없어짐. 위키 중복 · 불일치 점검(2026-11-27)에서 「상한 초과」를 적은 곳이 휠-45도 페이지 1곳뿐이고 나머지 12곳은 「확정 · 권장」으로 남아 있었음. 검토한 대안: 상한 예외로 3,850 인정(휠 Vmax 미확보라 근거 없음) · 현장 재시험(별도 일정 필요 — 재사용 때 3,820 이하 현장 확인으로 대신)
- 출처: Cowork 점검 → 현장(한경준님 승인 2026-11-27)
- 영향: tools/연삭-조건-D6-4날-코너R-GASH · 연삭-조건-D8-4날-코너R-GASH · wheels/스택-1-2(Ø125 판정표 이름 정정 포함) · 휠-45도 · 휠-5도 · 연삭-조건-코너R · 입력양식 · 목록 · 기록 · index · overview · troubleshoot/표면조도-불량 예시

## 2026-11-27 (4): 양날 공구의 「연마불가」 반 나눔 기록은 품질 지표(연마불가율 · 양품율)에서 따로 본다

- 결정: 출하현황 「연마불가」 칸에 양날 공구를 반으로 나눠 적은 수량(예: 09-18 코팅만 100개 중 50개)은 품질 문제가 아니므로, 연마불가율 · 양품율을 품질 판단에 쓸 때는 따로 빼서 본다. 원본 집계값은 지우지 않고 병기
- 근거: 한경준님 설명(11-27) — 「양날이라서 반을 나눈 것, 문제가 있어서 한 건 아님」. KPI 중간점검 자료 검토 중 9월 65개 중 50개가 이 1건임을 `raw/출하현황/출하현황_9월.xlsx` 에서 확인
- 출처: Cowork 검토 → 현장(한경준님)
- 영향: [[comparisons/출하현황-KPI-트렌드-2022-2026]] §1 주석 · `wiki/reports/07_KPI/생산팀_KPI_중간점검_20261128.pptx` 6장 카드 3(「연마불가 1건 집중」 → 「로더 활용 저조」) · 앞으로 월 마감 연마불가율 계산 시 같은 기록이 있으면 확인

## 2026-11-27 (3): Codex 한 줄 지시 — Claude가 카드를 쓰고 사용자는 「카드 진행해」만, 검산은 Claude가 먼저

- 결정: ① Claude 는 Codex 일을 작업 카드로 쓰고 답 끝에 복사용 `Codex — 「카드 진행해」` 한 줄을 낸다(급하지 않으면 카드를 모아서) ② Codex 는 「카드 진행해」만 받으면 담당 Codex · 대기 카드를 순서대로 모두 처리, 멈추면 그 자리에서 중단(`AGENTS.md` 「한 줄 지시」) ③ Claude 는 세션 시작 때 「마침」 카드를 사용자 말 없이 먼저 검산하고 「마침 · 검산 통과」로 바꾼다
- 근거: Claude → Codex 직접 지시 불가 — Cowork device_bash 에서 api.openai.com · chatgpt.com 접속 000(11-27 실측, 네트워크 허용 목록 밖) · Codex 는 데스크톱 앱. 첫 카드 시험(11-27) 사용량 1%p · 1분 59초 · 검산 통과(커밋 7010f32). 검토한 대안: Codex CLI 자동 호출 — 관리자 허용 목록 변경 + CLI 포함 요금제 필요(무료판 CLI 포함 여부 확인 필요)라 보류
- 출처: Cowork 추천 → 한경준님 「ㅇㅋ … 한 줄 지시 할 수 있게 해줘」 11-27
- 영향: `AGENTS.md` 「한 줄 지시」 · `wiki/_handoff/ai-handoff.md` 「한 줄 지시 흐름」 · 카드 상태 값 · `CLAUDE.md` §0-D

## 2026-11-27 (2): Claude ↔ Codex 역할 분담 — Codex(무료)는 Claude가 만든 작업 카드의 작은 일만, 시작 읽기를 작업 카드 중심으로 축소

- 결정: ① 판단 · 작성(자료 조사 · 도면 · 3D · 보고서 · 위키 · 검수 · 작업 카드 작성)은 Claude, Codex는 작업 카드 1장 = 작은 일 1개(파이썬 실행 · 문법 확인 · 엑셀 · ERP 숫자 검산 · 작은 코드 수정 · git 상태 읽기 · Claude 숫자 재검산) ② Codex 시작 읽기는 `ai-handoff-current.md` + 카드의 읽을 파일(최대 3개)만, decisions 는 맨 위 제목 3줄 · worklog · tasks · index 는 검색으로 부분만 ③ Codex 한도로 멈추면 Claude가 이어받고, Claude 한도 때 Codex는 카드 범위 밖 새 판단(조건 · 대외 · 규칙 · 삭제 · 이동)을 보류 ④ Codex 남은 사용량 30% 아래면 검산 카드만
- 근거: Codex 는 ChatGPT 무료 요금제 — 공식 요금 페이지 「Limited trial access to Codex」 · 메시지와 문맥 제한(2026-11-27 확인, 횟수 미공개) · Codex 화면 「남은 사용량 1개월 77% · 12월 26일」(11-27 한경준님 캡처 — 월 한도, 11-26 하루 시험에 약 23% 사용). 기존 `AGENTS.md` 시작 읽기 7개 파일 합계 176,754자(worklog 90,106 · decisions 42,797 · index 29,003 · 나머지 14,848, 11-27 `wc -m` 실측) + `ai-handoff.md` 의 tasks.md 28,733자 = 약 20만 자 → 토큰 환산 약 10만~20만(추정값). 검토한 대안: Codex 와 반반 분담(무료 한도로 불가) · Codex 미사용(Claude 주간 한도 소진 때 대안 없음)
- 출처: Cowork 추천 → 한경준님 「고칠 파일 진행」 11-27
- 영향: `AGENTS.md`(시작 읽기 · 기록 위치) · `wiki/_handoff/ai-handoff.md`(읽는 순서 · 역할 분담 · 작업 카드 양식) · `README.md`(decisions 기록 주체 · 커밋 경로 `D:\cnc-wiki` · 바꾼 파일만 add) · `ai-handoff-current.md`(Codex 대기 카드 1장)

## 2026-11-27 (1): cnc-wiki 저장 위치 C → D 드라이브 이전 — 원래 경로에 연결 폴더(Junction)

- 결정: cnc-wiki 전체를 `D:\cnc-wiki` 로 옮기고, 원래 경로 `C:\Users\HAN\Desktop\cnc-wiki` 에 Junction(→ D:\cnc-wiki)을 만든다. 스크립트 · 예약 작업 · 스킬의 고정 경로는 고치지 않는다(TOOLKOREA → HAN → D 순서로 열림). Cowork 는 앞으로 `D:\cnc-wiki` 를 연결 폴더로 쓴다(Junction 경로로는 마운트 안 됨, 11-27 실측). 원본 `cnc-wiki_old_20261127` 은 11-27 오전 한경준님이 삭제(16:00 확인 전 — 되돌릴 원본 없음, D 9,937개 재확인)
- 근거: C 드라이브 남은 용량 7.3 GB / 118.6 GB(11-27 실측) · cnc-wiki 3,878 MB(raw 2,926 MB) — 일부만 옮기는 안(약 640 MB)보다 효과 6배. 고정 경로 61곳 이상 · Windows 예약 작업 7개가 경로를 써서 옮기기만 하면 깨짐 → 11-19 PC 이전 때 쓴 Junction 방식(decisions 2026-11-19 (1))을 그대로 씀. 복사 대조 C 9,937개 / 3,878 MB = D 9,937개 / 3,878 MB · Junction 경로에서 git status · `update_overview.py --dry-run` 정상(174)
- 출처: Cowork
- 영향: 예약 작업(CNC_Daily_Report 등) — 11-27 16:00 첫 실행 확인 필요 · Cowork 세션 연결 폴더 D:\cnc-wiki · Codex(GPT)도 같은 Junction 경로로 열림

## 2026-11-25 (2): 인스타 디자인 스킬 — oil-ui 화면 검토 순서는 「검수해 줘」(review-role) R6-A 로, dimensional-drawing 은 사내 「치수 기호도」 스킬 · 양식으로 일부 이식

- 결정: ① review-role 에 「R6-A 화면 다듬기」(R6-9 규격 이탈 · R6-10 배치 세 곳 · R6-11 읽힘(대비 · 첫 화면) · R6-12 움직임 · R6-13 뺄 것, 점수 없음 · 브랜드 교체 제안 없음 · PC 1440 · 휴대폰 390 스크린샷 증거)를 넣는다 ② 새 사내 스킬 dimension-symbol-sheet(「치수 기호도 만들어 줘」) — 공구 한 계열을 기호 치수 + 값 · 식 표로 그린 설명 그림(카탈로그 · 몰 상품 · 신입 교육용), 양식 `wiki/templates/치수기호도-양식/치수기호도_양식_v1.html`. 제작 도면은 tool-generator 그대로 ③ oil-ui · dimensional-drawing 통째 설치 · motion 짝 스킬 · taste-skill · brand-identity · awwwards-mcp 는 들이지 않는다
- 근거: Cowork 시범 2건(11-25) — 시범 A 엔드밀 기호도(식 검산 P = π×6÷tan35° = 26.92 · Lt = 0.15÷tan15° = 0.56 맞음) · 시범 B 포털 견적 문의 화면 검토(규격 이탈 4 · 배치 3 · 뺄 것 2, Playwright 측정). oil-ui 의 핵심 「안 2~3개 비교」는 decisions 2026-11-20 (2) ① 에 이미 있고, 딸린 스크립트가 자동 업데이트 · 유료 이미지 크레딧 · 외부 이미지 API 에 접속 → 글로 된 검토 순서만 옮김(스크립트 없음). dimensional-drawing 은 실행 스크립트 없음, MIT 고지를 양식 머리 주석 · `LICENSE-dimensional-drawing.txt` 로 남김. 검토한 대안: 원본 그대로 설치 — 중국어 본문 · 영문 대문자 · 상호 없음 규칙이 사내 대외 명의 · 한글 표기와 맞지 않아 기각. SkillSpector 는 Cowork 에서 실행이 막혀 못 돌림(옮긴 것이 글 · 그리기 JS 뿐)
- 출처: Cowork 추천 → 한경준님 「①과 ② 둘 다 진행 승인」 11-25
- 영향: `skills-custom/review-role/SKILL.개정안_20261125.md` · `skills-custom/dimension-symbol-sheet/SKILL.초안_20261125.md` · 테스트카드 #9(시험 4가지 미실행) · README §4-2 두 행 판정 · `wiki/templates/치수기호도-양식/`. 정상본 교체는 시험 통과 뒤(README §3)

## 2026-11-25 (1): Claude 토큰 절감 도구 — Graphify · Ponytail 1주 시험(SkillSpector 검사 통과 뒤), OmniRoute 제외

- 결정: ① Graphify(무료 빌드만 — 문서 의미 추출 `/graphify` 는 안 씀) · Ponytail(기본 꺼둠, ERP · 스크립트 작업 때만 켬)을 cnc-wiki PC(DESKTOP-DQDPA0J)에서 1주 시험한다. 설치 전에 README §4-1 2단계 SkillSpector 정적 검사(챗 샌드박스)를 먼저 통과해야 한다 ② OmniRoute · claude-code-router(한도가 차면 다른 모델로 넘기는 중계기)는 들이지 않는다 ③ Ponytail 판정은 2026-11-19 「제외」 → 「시험 1주」로 바꾸고 이력 표에 옛 판정을 취소선으로 남긴다 ④ 공식 절감 습관(작업이 바뀌면 /clear · 모델 구분 · 파일은 붙여넣지 말고 경로로 · 큰 변경 전 계획)은 그대로 쓴다. CLAUDE.md 길이는 2026-11-23 (7)(371줄 유지)을 따른다
- 근거: 챗 격리 시험(설치 · 실행 · 제거, 한글 시험 폴더) — 두 도구 모두 외부 전송 없음 · 설치 · 제거 뒤 원래대로 돌아옴. OmniRoute 는 사내 자료가 외부 제공사로 나가고 국가 차단 우회 · 구독 공유 등 약관 회피 기능이 있음, 구독 계정을 물리면 Anthropic 약관 위반. 출처: Anthropic 지원 문서 「Claude Code의 모델, 사용량 및 제한」, 각 저장소 README · 패키지 코드(제조사 기준), 챗 시험값(Linux 1코어 격리 환경 — 추정값, Windows 실측 아님). 검토한 대안: 챗 원문 그대로 6행 추가 — Ponytail · Caveman 행이 이미 있어 겹치고 「CLAUDE.md 200줄 안팎」이 2026-11-23 (7)과 어긋나 기각
- 출처: 챗(Drive 「cnc-wiki 인계/챗핸드오프_20261125_토큰절감도구_시험.md」) → Cowork 대조 · 추천 → 한경준님 「승인」 11-25
- 영향: `wiki/_handoff/skills-custom/README.md` §4-2(새 4행 · Ponytail 판정 변경 · Caveman 근거 덧붙임) · `tasks.md` P2 1줄(시험). 설치하면 CLAUDE.md 에 graphify 섹션 1개(약 320토큰 — 챗 시험값, 매 턴 실림) · `.claude/settings.json` 훅 3개 · `.gitignore` · `.graphifyignore` 가 추가됨 — 1주 뒤 채택 / 제거 판정. 비교 방법(`/context` · `/usage`)과 훅은 Claude Code 기준이라 Cowork 세션에서도 같은지 시험 때 함께 본다 · 11-25 SkillSpector 검사 통과 — 두 도구 모두 DO_NOT_INSTALL(위험 100)이나 지적 줄 판독 결과 오탐(챗 · Drive 「cnc-wiki 인계/챗핸드오프_20261125_SkillSpector_Graphify_Ponytail.md」 → 한경준님 「진행」 11-25)

## 2026-11-24 (1): F 장비 DC-UPS 배터리 — 예비 ROCKET ES2-12 2개 폐기, 새 12 V 2 Ah 배터리 2개 구매(교체 1 · 예비 1)

- 결정: ① 사내 예비 ROCKET ES2-12 2개는 폐기(납축전지 재활용 수거로) ② 같은 규격 12 V 2 Ah 밀폐형(ROCKET ES2-12 또는 지금 달린 E&P KB1220) 새것 2개 구매 → 1개는 F 장비 PULS DC-UPS 에 교체, 1개는 예비 ③ 예비품은 보관 중에도 몇 달마다 개방전압 확인(12.4 V 아래면 보충전)
- 근거: 11-24 13:48 · 13:52 F 장비 정전 2회에 PC 가 꺼짐 — ANCA ErrorLog.epl `Power failure occured`, UPS 감시 기록(Rupsd.evt)은 2024 ~ 2026-06 정전 때 PC 를 지켰으나 이번엔 기록 없음 → UPS 미동작 추정. 예비 배터리 실측: 1개 개방전압 10.90 V(HIOKI 3244-50, DC V), 다른 1개는 충전기(디포스 PB1202CR, 7 ~ 13 Ah 용)로 충전 중 완료 안 됨 · 두 번째는 충전기가 경보음으로 거부 → 장기 보관 방전 손상. 배터리 수명 기준: 설계수명 3 ~ 5년(20 °C), 정격 80 % 에서 수명 끝 [VEN-PULS-UB10]
- 출처: Cowork(현장 실측 · 한경준님 결정)
- 영향: [[troubleshoot/장비-전원-갑자기-꺼짐]] 해결 기록 · 교체 뒤 같은 시간대 재발 여부 관찰 · RUPS 2000 이 감시하는 AC UPS 가 따로 있는지는 별도 확인

## 2026-11-23 (8): 월초 마감 점검 · AI 동향 월간 조사를 v3(드라이브 방식)로 다시 만듦 — 출하현황 자동 반영은 대화 세션으로

- 결정: ① 월초 점검 — PC 16:00 배치가 매월 1 ~ 5일 첫 실행 때 `scripts/export_monthly_check.py` 로 ① ~ ⑥ 측정값(읽기 · 드라이런만, 거래처 실명 줄 뺌)을 드라이브 `cnc-wiki-auto/monthly_check.txt` 에 올리고, 클라우드 예약 작업 「월초 마감 점검 v3」(매월 1 ~ 5일 16:41)이 읽어 판정 · 보고 ② 🔴 ⑥ 출하현황 `--apply` 는 예약 작업이 하지 않고 대화 세션에서 「승인」 뒤 실행(2026-11-10 의 조건부 자동 반영 승인을 바꿈) ③ AI 동향 — 클라우드 예약 작업 「AI 동향 v3」(매월 3 ~ 9일 14:13)가 공개 저장소를 받아 조사 · 보고서 생성까지 하고 결과를 드라이브 `cnc-wiki-auto/ai_trend_YYYYMM/` 에 올림 → 대화 세션에서 「AI 동향 가져와 줘」로 위키 반영 · 커밋 ④ 옛 v2 두 작업은 끈 채 이름에 「대체됨」
- 근거: 11-23 예약 진단 2회(드라이브 「cowork_예약진단_20261123」 · 「_2」, 실측) — 예약 실행을 이 컴퓨터에 묶으면 device_bash 는 생기나 연결 폴더 0개, 작업에 폴더를 지정해도 0개 · 한경준님 확인: 앱에 승인할 항목 없음. 드라이브 방식은 업무일지 v2 · 주간 정리 v2 로 11-19 부터 동작 중. 클라우드에서 공개 저장소 받기 · node docx · soffice · 보고서 생성 시험 통과(11-23, 견본 month.json 으로 docx · pdf 생성, 문체 점검 기준 넘은 항목 0). 측정 스크립트 2026-10 으로 시험 — ① 대조 5일 늦은 입력 +39 · ⑥ 「이미 반영됨」 판정 · ⑤ 미등재 출처 1(VEN-HID-VMAX-2026) 실제로 잡음. 검토한 대안: 대화 세션 예약 메시지 이어 붙이기 — 한 번 끊기면 다음 달이 안 돎, 기각
- 출처: Cowork 추천 → 한경준님 「승인」(진단) · 「없음」(앱 승인 화면 없음 → 드라이브 방식) 11-23
- 영향: `scripts/export_monthly_check.py` 신규 · `scripts/daily_and_upload.bat` 7) 1줄(백업 `.bak_20261123`) · 예약 작업 2개 신규 · 2026-11-10 ⑥ 자동 반영 → 대화 세션 · AI 동향 산출물 경로는 같음(가져올 때 넣음)

## 2026-11-23 (7): CLAUDE.md 3차 줄이기는 하지 않음 — 지금 판(371줄) 유지, 머리 「마지막 갱신」 줄만 주간 정리 때 1줄로

- 결정: ① CLAUDE.md 의 「특정 폴더」 절(§3 · §4-1 · §6 · §7 · §8 요약 · §10 · §12 · §14, 135줄)을 standards 로 옮기지 않는다 ② 머리말 「마지막 갱신」 줄(941 B, 갱신 이력 나열)만 다음 주간 정리(금) 때 최근 1건 + 「이력은 decisions」 1줄로 줄인다(약 −0.8 KB) ③ 다시 볼 조건: Cowork 가 경로 규칙을 지원할 때 · 「지시를 안 지킨다」 사례가 CLAUDE.md 길이 탓으로 보일 때
- 근거: 2차 뒤 다시 잼(`outputs/CLAUDE_md_측정_20261123.md` §7, 실측) — 모든 세션 217줄 · 특정 폴더 135줄 · 절차 19줄 = 371줄 · 24,908 B. 모든 세션 몫만 217줄이라 특정 폴더를 다 빼도 200줄 아래로 못 감 · Cowork 에서 경로 규칙이 안 켜져(2026-11-23 (2) ③, worklog #7) standards 로 빼면 그 페이지를 읽기 전엔 정가표 · 보고서 규칙을 못 봄 — 빠뜨림 위험이 맥락 절약보다 큼 · 200줄은 공식 문서의 권장 목표(code.claude.com/docs/en/memory, 제조사 기준). 검토한 대안: 특정 폴더 절 이전 — 위 이유로 기각
- 출처: Cowork 추천 → 한경준님 「승인」 11-23
- 영향: 2026-11-23 (2) 「남은 일」(특정 폴더 절 이전 판단) 닫음 · `tasks.md` P3 1줄(머리 줄 정리, 금요일) · CLAUDE.md 는 이번에 안 고침

## 2026-11-23 (6): ToolRoom–Claude 연동은 Claude 설정 파일 등록(로컬 MCP) 방식으로 운영

- 결정: 컴퓨터2에 연동 서버(`Claude outputs\ToolRoom연동\server\node.exe` + `index.js`)를 두고 `claude_desktop_config.json` 에 `anca-toolroom` 으로 등록한다. `.mcpb` 확장 파일은 회사 계정에서 확장 설치가 허용될 때 쓰는 예비용.
- 근거: 회사 계정은 데스크톱 확장 설치 메뉴가 꺼져 있음(설정에 「확장 프로그램」 없음, 「커스텀 커넥터 추가」 비활성). Claude 공식 문서 "Add a connector that isn't in the directory" — 조직이 확장을 끄면 설정에 Extensions 가 나타나지 않음. 설정 파일 등록 후 v0.3.0 동작 확인(공구 183개·휠팩 36개 인식, ToolRoom 빌드 9.22 patch 60.15 / Build 682).
- 출처: Cowork (컴퓨터2 — Drive 「cnc-wiki 인계/컴퓨터2/decisions_추가분_2026-11-23.md」)
- 영향: 서버 갱신 시 `server\index.js` 교체 후 Claude 앱 완전 종료·재실행 필요. 기능 — 공구 요약·비교·파라미터 조회·휠 원주속도 점검, ToolRoom 화면 보기(캡처만), 새 공구 파일 만들기.

## 2026-11-23 (5): ToolRoom 휠 번호는 아버 끝(스핀들에서 먼 쪽)부터 1번

- 결정: 휠팩(.wpk) 파일은 스핀들 쪽부터 휠을 나열하므로 번호는 역순으로 매긴다. 화면 표기 `w3 p1` = 3번 휠·1번 팩.
- 근거: 현장 지적(4F CO 의 7. Endface Gash·9. OD Corner End Finishing 휠이 반대) + 사내 공구 파일 41개의 뒷면(back) 사용 70건 대조 — 파일 순서로 번호를 매기면 49건이 뒷면 연삭면이 없는 11V9(Qualify_Back = false)에 걸리고, 역순이면 0건 + iGrind 화면과 9개 오퍼레이션 휠·팩 번호 일치(실측 검증).
- 출처: Cowork (컴퓨터2 — Drive 「cnc-wiki 인계/컴퓨터2/decisions_추가분_2026-11-23.md」)
- 영향: 연동 v0.1.0 의 휠 대응 결과는 폐기(v0.1.1 부터 수정).

## 2026-11-23 (4): .tom 파일 전체 경로는 100 byte 이하로 (한글 1자 = 2 byte)

- 결정: Claude 가 만드는 공구 파일은 영문 이름 + 짧은 폴더, 전체 경로 100 byte 를 넘으면 만들지 않는다. 사람이 저장할 때도 깊은 한글 폴더·긴 파일명은 피한다.
- 근거: iGrind 경고 「PPI Execution Error — p:/3dx/tmp/sim/igrind1/map1/map1.pp line 182, String too long to fit into variable」. iGrind 가 만드는 내부 프로그램에서 `tom_filename` 에 .tom 전체 경로를 넣다가 길이 초과. 실측: 경로 99·100 byte 정상 / 106 byte Invalid Tool / 같은 내용을 64 byte 경로에 두면 정상(실측 검증).
- 출처: Cowork (컴퓨터2 — Drive 「cnc-wiki 인계/컴퓨터2/decisions_추가분_2026-11-23.md」)
- 영향: 정확한 한계는 100~105 byte 사이로 미확정 → 100 byte 로 보수 적용.

## 2026-11-23 (3): Claude 생성 공구 파일 저장 위치 = toolroom\user\tools\_Claude\

- 결정: 새 공구 파일은 이 폴더에만 저장하고, 같은 이름이 있으면 만들지 않는다(덮어쓰기 없음). ToolRoom 원본 파일은 읽기만 한다.
- 근거: 경준님 승인(2026-11-23). 경로가 짧고(P: 기준 약 41 byte) 사내 공구 라이브러리와 섞이지 않음. 첫 생성본 `4FCO_R05_T1.tom`(4F CO 바탕, 코너 R 0.5 mm·외경 1차 여유각 12°·7. Endface Gash 이송 120 mm/min) iGrind Simulation Complete 확인(2026-11-23 11:27 KST).
- 출처: Cowork (컴퓨터2 — Drive 「cnc-wiki 인계/컴퓨터2/decisions_추가분_2026-11-23.md」)
- 영향: 생성 파일은 시험용 — 양산 적용 전 테스트 → 측정 → 검증 필수. 0(ZERO) 저장값·함수형 값·선택형 값은 아직 생성 기능으로 못 바꿈.

## 2026-11-23 (2): CLAUDE.md 줄이기 2차 — 절차 4개 절 원문을 standards 로, `.claude/rules/` 는 쓰지 않음

- 결정: ① CLAUDE.md §0-A2 · §0-B · §8 · §15-4 원문을 [[standards/세션-위키-작업절차]] 로 그대로 옮기고(절 번호 같음) CLAUDE.md 에는 요약 · 🔴 규칙(Cowork git 쓰기 금지 · 바꾼 파일만 add · 검토 줄 정의 · 검수 제외 · 메모 공개 저장소 금지 · 3,000자 상한)만 남김 · §9 4줄 → 1줄. 447 → 371줄 · 28,811 → 약 24.9 KB ② 지금 따르는 절차는 스킬(cnc-handoff · wiki-new-page · source-add · wiki-lint) — 스킬에 아직 없는 항목 4개는 README §2 개정 후보로만 올리고 계정 스킬은 고치지 않음(개정 절차 §3 · 테스트카드 필요) ③ `.claude/rules/` 는 도입하지 않음
- 근거: 공식 문서 「파일당 200줄 아래 — 길수록 맥락을 더 쓰고 지시를 덜 지킴」(code.claude.com/docs/en/memory, 1순위 · 제조사 기준) · 11-23 시험(worklog #6 · #7): Cowork 에서 경로 규칙은 안 켜지고 무조건 규칙은 CLAUDE.md 와 같이 폴더 첫 접근 때 들어옴 → 맥락이 안 줆. 2026-11-10 (6) 다이어트와 같은 방식(원문 이전 · 절 번호 유지). 검토한 대안: 스킬 본문에 옮기기 — 계정 스킬 4개를 고쳐 다시 시험해야 해 이번엔 원문 보존 + 개정 후보로만
- 출처: Cowork 추천 → 한경준님 「승인」 11-23
- 영향: `CLAUDE.md`(원본 `CLAUDE.md.bak_20261123`, 추적 제외) · `wiki/standards/세션-위키-작업절차.md` 신규 · `wiki/index.md` · `wiki/log.md` · `wiki/_handoff/skills-custom/README.md` §2 · §4-2. 남은 일: 200줄까지는 「특정 폴더」 절(§3 · §6 · §7 · §12 · §14 등 약 136줄)도 standards 로 옮겨야 함 — 다음 판단(→ 2026-11-23 (7) 에서 하지 않기로)

## 2026-11-23 (1): 외부 스킬 · 플러그인 검토 이력 표를 두고, 새 추천은 같은 도구 기록부터 찾는다

- 결정: ① `wiki/_handoff/skills-custom/README.md` §4 에 검토 이력 표(도구 · 원본 · 처음 본 곳 · 판정 · 근거 · 다시 볼 조건)를 두고 11-19 ~ 22 인스타 스크랩 7건(도구 15 · 요령 3)을 올린다 ② 새 스크랩 · 추천이 오면 이 표 → decisions(아카이브 포함) → 관련 페이지 순으로 같은 도구 기록부터 찾고, 있으면 다시 검토하지 않는다 · 실행 스크립트가 든 스킬은 챗 샌드박스에서 SkillSpector 정적 검사 뒤 지적 줄 판독(11-23 추가 — 챗 핸드오프 추가3) ③ 판정은 도입 · 일부 이식 · 보류 · 제외 넷
- 근거: 11-19 ~ 22 챗이 im-not-ai 「Cowork 설치 승인 대기」를 다음 작업으로 올렸으나 이미 decisions 2026-11-20 (2) ② · (4) 에서 보류 · 어휘 사전만 반영으로 정해져 있었음(챗이 내부 기록을 11-23 에야 Drive 사본으로 대조) · 같은 도구가 게시물마다 되풀이(ECC 2회 · 지식채널 목록 6개 중복). 검토한 대안: 검토 때마다 decisions 전체 grep 만 — 챗 · 휴대폰에서 어렵고 「제외」 판정은 §5-A 대상이 아니라 decisions 에 남지 않아 기각
- 출처: 챗 (한경준님 「적용 가능한 부분이 있다면 내부 내용과 검토해서 적용 해보자」 11-23)
- 영향: `wiki/_handoff/skills-custom/README.md` §4 신설 · `tasks.md` P3 1줄(신입 교육 시험 문제) · §4-1 2단계 1줄 · §4-2 SkillSpector 행(11-23 추가3)

## 2026-11-20 (9): `erp/` 폴더 전체를 공개 저장소에서 추적 제외 — 소스 백업은 Drive 로

- 결정: ① `.gitignore` 에 `erp/` 추가 · `git rm -r --cached erp`(파일은 PC 에 그대로, 저장소에서만 빠짐 — 추적 33개) ② git 이력 · 원격 백업이 없어지는 대신 `scripts/sync_to_gdrive.py` 가 매일 Drive 동기화 때 erp 소스 39개(.py · .bat · .spec · requirements · 사용설명서)를 Drive `cnc-wiki-erp` 에 올림 — build/ · dist/ exe · snapshot/ · 조회 결과 txt 는 안 올림 · 실패해도 wiki 동기화에는 영향 없음 ③ 지난 이력에 남은 erp 파일은 그대로 둠(2026-11-20 (6) 과 같은 이유)
- 근거: 공개 저장소에 ERP 호출 형식(조회 · 저장 메서드 · 화면 코드 구조)이 들어 있을 이유가 없음 — 포털 페이지 · 자동 커밋 · GitHub Actions 어디도 erp 파일을 쓰지 않음(실측: html · js 참조 0 · workflows 없음, generate.py 는 PC 의 erp 모듈을 직접 import) · Drive 동기화는 원래 `wiki/` 만 올려 추적 제외 뒤 erp 소스가 PC 밖 백업 0 이 되는 것을 막음 · 대안: 별도 비공개 GitHub 저장소 — 계정 작업이 필요해 보류
- 출처: Cowork 추천 → 한경준님 「진행해」 11-20
- 영향: `.gitignore` · `scripts/sync_to_gdrive.py` (`.bak_20261120` / `.bak_20261120i`) · 저장소에서 erp/ 33개 삭제 커밋(PC 파일 유지). Drive 백업은 다음 Drive 동기화(16:30 무렵) 출력의 `[erp] 소스 백업` 줄로 확인 필요 · `anonymize_public.py --check` · 차단어 검사 대상에서 erp/ 가 빠짐

## 2026-11-20 (8): 보고서에 AI 사용을 표기하지 않음 — 사내 보고서 · 대외 기술자료 모두

- 결정: ① 사내 보고서의 「자료 정리 · 계산: Claude Cowork 보조」 한 줄 폐지 ② 대외 기술자료도 표기하지 않음(회사 명의 + 담당자) ③ 내용은 작성자 · 검토자가 확인하고 책임진다 ④ 수치 출처는 표 「구분」 열과 부록의 사내 기록 위치로 추적(대외본은 사내 사본에 남김)
- 근거: AI 기본법(2026-01-22 시행) 생성형 AI 결과물 표시 의무는 AI 제품 · 서비스를 제공하는 사업자 대상이고 업무에 쓰는 이용자는 대상 아님(보도 · 과기정통부 투명성 가이드라인 해설, 법률 자문 아님 — 사업자 · 이용자 구분 혼선 보도 있음) · 한경준님: 사람이 한 것처럼 책임지고 행동하면 된다 · 거래처 요구 · 대표님 방침이 생기면 다시 정함
- 출처: Cowork 추천(대외만 표기 안 함) → 한경준님 「둘 다 표기하지 말자」 11-20
- 영향: `wiki/standards/보고서-작성-규칙.md` §11 · `wiki/standards/보고서-작성-원칙.md` 머리 정보 줄(취소선) · `wiki/templates/보고서양식-A-시험개선결과.md` 비고 칸 · `wiki/templates/코고툴_보고서양식A_v1.docx` 비고 칸 (`.bak_20261120`). 합격 견본 docx 와 지난 보고서 스크립트(`scripts/report_neck_t4/`)는 기록이라 그대로 둠

## 2026-11-20 (7): 보고서 작성 규칙 §6-2 신뢰도 구분을 위키 공통 4단계로 통일 · 여백 확정 · 양식 A 머리 상태 「확정」

- 결정: ① 보고서 표 「구분」 열은 「제조사 기준 · 실측 검증 · 사내 경험값 · 추정값」(CLAUDE.md §2)을 그대로 쓴다. 계산값은 넣은 값 중 가장 낮은 단계 + 「계산」(옛 「실측 · 계산 · 제조사 · 추정」 폐지). 대외 기술자료의 「카탈로그 값 · 당사 시험값」 두 가지는 그대로 ② §10 여백 위 · 아래 15 mm, 좌 · 우 20 mm 확정(줄 간격 130 % 는 권장 유지) ③ 양식 A 페이지 머리 상태 줄 「초안」 → 「확정(2026-11-02)」 ④ §10 양식 파일 경로를 `wiki/templates/` 로 바로잡음
- 근거: 규칙 검토(R5 주 · R4, 11-20) — 옛 구분은 「사내 경험값」이 없고 계정 선호 · CLAUDE.md 4단계와 달랐음 · 합격 견본 A docx 에 「구분」 열이 없어 바꿔도 견본 영향 없음(실측) · 양식 A · 견본 A · 견본 B docx 3개 여백 실측 모두 15/15/20/20 mm · 견본 A 합격은 decisions 2026-10-29 (1)
- 출처: Cowork (한경준님 「보고서 규칙 지적 수정 진행」 11-20)
- 영향: `wiki/standards/보고서-작성-규칙.md` · `wiki/templates/보고서양식-A-시험개선결과.md` (`.bak_20261120`). 남은 지적: 일일보고 xlsx 표기(「─」 · 「▲▼」)는 16:00 배치 확인 뒤 `daily_report.py` 수정 · 대외 AI 사용 표기는 한경준님 판단

## 2026-11-20 (6): 공개 저장소 — 사내 ERP 서버 주소는 이력을 다시 쓰지 않고 지금 판에서만 빼며, 커밋 전 차단어 검사를 추가

- 결정: ① 이력(루트 커밋 d034561)에 남은 사내 ERP 서버 주소는 **받아들이고 기록**만 한다 — D안 4차(이력 다시 쓰기) 안 함 ② 지금 판에서는 뺀다 — 문제해결 페이지 21행 · 루트 `납기알림_자동화_개발보고서_v2.docx` 1곳 ③ pre-commit 훅에 차단어 검사 추가 — `scripts/check_blocklist.py --staged`, 차단어 목록은 git 제외 `private_local/public_blocklist.txt`(공개 파일에 차단어를 적지 않음, 목록 없으면 경고만) ④ 바깥망(휴대폰 LTE)에서 ERP 접속이 안 되는지 한경준님 1회 확인 ⑤ GitHub 지원 요청은 한경준님 제출 · 3차 백업은 11-26 뒤 판단
- 근거: 11-18 에 지금 판에서 뺐던 주소가 11-19 문제해결 페이지에 다시 들어감 — 기존 훅은 거래처 실명 대조표만 봐서 못 잡음 · 공개 DNS 조회(dns.google, 11-20)에서 이 주소가 공인 IP 로 해석됨 → 이름 자체는 숨길 수 없는 값이고 실제 보호는 포트 차단 · 이력을 다시 써도 옛 커밋은 SHA 주소로 계속 열림(금액 커밋 3개가 11-20 에도 200) → 비용(저장소 재생성 · Pages · 토큰 · 예약 작업) 대비 효과 작음 · 차단어 검사 `--all` 실행 결과 개발보고서 docx 1곳 추가 발견 → 고친 뒤 0곳, 양성 대조(가짜 md 에 주소) 1곳 잡음
- 출처: Cowork 추천안 → 한경준님 「추천안으로 순차적으로 진행」 11-20
- 정정(2026-11-20 14:30, 한경준님 LTE · 5G 확인): 근거의 「실제 보호는 포트 차단」은 **틀린 전제** — 휴대폰 5G 에서 ERP 서비스 안내 페이지(WCF, http 평문, WSDL 공개)가 열림. 서버는 바깥에서 접속된다. ① 이력 수용은 유지(주소는 공개 DNS 로 누구나 찾을 수 있어 이력을 지워도 노출은 그대로) · 진짜 조치는 서버 쪽 접속 제한 → tasks P0 「ERP 서비스 외부 노출」 · 커밋 전 검사는 a742f5a 커밋 때 Windows 에서 정상 동작 확인
- 영향: `.githooks/pre-commit` · 신규 `scripts/check_blocklist.py` · `wiki/troubleshoot/TricoERP-납기알림-메일-미발송.md` · `납기알림_자동화_개발보고서_v2.docx` (`.bak_20261120` / `.bak_20261120h`). 다른 PC 에서 커밋하면 목록 파일이 없어 이 검사는 건너뜀(경고 표시)

## 2026-11-20 (5): 일일 배치 「실패인데 성공으로 보임」 구멍 막기 — generate.py · daily_and_upload.bat 수정, 옛 등록 스크립트 · 일회용 스크립트에 실행 금지 표시

- 결정: ① generate.py — 「변경 없음」이어도 안 올라간 커밋이 있으면 push · 사내 배포 실패 알림을 공용 `_send_alert_mail` 로(토큰 없을 때 `sys.exit` 가 업로드를 막지 않게) · 「보냄」 기록은 발송 성공 뒤에만 · push 시간 제한 600 s(타임아웃 메시지의 인증 헤더 가림 포함) · 스테이징에 이 프로그램 밖 파일이 있으면 커밋하지 않고 실패 · 직원 비밀번호 `json.dumps` · 안 쓰는 import 제거 ② `.gitignore` 에 `submissions-data.js` · `order-status.html` 루트 · dist/ 4줄(공개 저장소 제외) ③ `daily_and_upload.bat` — 1단계(일일보고) 종료 코드를 받아 5단계가 정상일 때 작업 결과로 넘김 ④ `setup_scheduler.ps1` · `_v2.ps1` 맨 위 「OLD VERSION - DO NOT RUN」, `price_consolidate.py` 맨 위 「일회용 · 다시 실행 금지」
- 근거: generate.py 검수 2회(1차 · 재시험)를 합친 지적 · 테스트 git 저장소 4가지 경우 실행 확인(변경 없음 ahead 0 → 생략 / ahead 1 → push 후 0 / 다른 파일 스테이징 → 실패 / 정상 변경 → push) · 알림 함수에 `sys.exit(1)` 스텁 → SystemExit 안 새고 notified_on 그대로 · 최근 자동 커밋 18개 경로 모두 허용 목록 안(오차단 0) · run.log 에서 1단계 실패는 ERP 전환(10-23) 뒤 0건(새 실패 알림이 잦아질 근거 없음) · 등록 스크립트를 다시 돌리면 9월 설정이 되돌아감(검수 ③). 검토한 대안: 등록 스크립트를 지금 설정으로 고쳐 쓰기 — 실제 설정 XML 을 먼저 받아야 해 보류
- 출처: Cowork (한경준님 「ㅇㅋ 승인」 11-20)
- 영향: `generate.py` · `.gitignore` · `scripts/daily_and_upload.bat` · `scripts/setup_scheduler.ps1` · `scripts/setup_scheduler_v2.ps1` · `scripts/price_consolidate.py` — 모두 `.bak_20261120`. 예약 작업 CNC_Daily_Report 결과가 1단계 실패 때도 0 이 아니게 됨(scheduler-diagnose · daily-report-check 판단에 반영). bat 동작은 다음 16:00 실행으로 확인 필요

## 2026-11-20 (4): AI 티 점검기에 im-not-ai 어휘 사전을 「참고」 항목으로 추가 — 스킬 설치는 계속 보류

- 결정: ① im-not-ai(humanize-korean) 스킬은 설치하지 않는다((2)② 유지) ② 어휘 사전 1.3(115항목, MIT)만 `scripts/doc_style_lexicon.json` 으로 복사해 `doc_style_check.py` 에 [참고] 출력으로 붙인다 — 기준값 없음, 「기준 넘은 항목」 수에 넣지 않음 ③ 기계 용어 오탐 4항목(모서리 · 렌즈 · 틈 · 파고들다)은 주변에 휠 · 공구 · 연삭 등이 있으면 뺀다 ④ 점검기가 스타일 없는 문단에서 멈추던 오류도 고친다
- 근거: 검토(R4 주 · R5) — 넥 보고 v1(반려) · v4(합격)에 돌리니 사내 점검기 넘은 항목 7 → 0, im-not-ai 정량 점수는 둘 다 「낮음 · 1점」으로 구분 못함 · 보고서 장르 규칙 C-2(항목 → 산문) · E-1(긴 문장 만들기)이 개조식 양식과 충돌 · 평문 입출력이라 docx 서식 못 다룸. 사전 시험(위키 docx · pptx 60개): 걸린 8건 중 AI 티 4 · 오탐 4 → 제외 추가 뒤 오탐 0, 기존 판정 변화 0개 파일 [실측]. 검토한 대안: 스킬 설치(위 이유로 기각) · 아무것도 안 함(사전은 독자 평가 근거라 참고 가치 있음)
  - 출처: [IND-IMNOTAI2026] epoko77-ai (2026). im-not-ai v2.4.7, lexicon.json 1.3. https://github.com/epoko77-ai/im-not-ai
- 출처: Cowork (한경준님 「추천안으로 승인」 · 「내용 폴더에 정리」 11-20)
- 영향: `scripts/doc_style_check.py`(원본 `.bak_20261120`) · 신규 `scripts/doc_style_lexicon.json` · `scripts/doc_style_lexicon.LICENSE.txt` · `standards/문서작성-AI티-점검표.md` §4 · §4-A · `_handoff/sources.md` [IND-IMNOTAI2026] 보강
- 정정: 같은 날 앞 답에서 v2.4.7 수정을 「하였체를 AI 티로 잡던 문제」라고 했으나, 실제는 문장을 나눌 때 「하였」이 늘어나는 것을 격식 상향으로 오판하던 게이트 문제(#184)

## 2026-11-20 (3): 파이썬 코드 검수 스킬 python-review 추가 — 「검수해 줘」 대상이 .py 면 review-role 이 code-review 와 함께 부름

- 결정: 사내 스킬 python-review 를 만들고 review-role §1-A 에 연결한다. 내용 = 파이썬 고유 항목 P1~P9(everything-claude-code `python-reviewer` 에서 골라 사내 심각도 상 · 중 · 하로) + 사내 실행 환경 W1~W8(인코딩 · 작업 스케줄러 경로 · PyInstaller exe · 엑셀 · 삭제 · KST · 종료 코드 · PC 고정 경로). 챗 1차안 검토에서 고친 3가지: ① W2 근거를 커뮤니티 → Microsoft Learn(시작 위치가 비면 `%windir%\system32`) ② W6 은 `utcnow()` 그대로 = 상, `utcnow()+9시간` = 하(결과 맞음 · 사용 중단 예고) ③ W8 `C:\Users\TOOLKOREA` 는 연결 폴더로 열리므로 파일마다 지적하지 않고 「연결 폴더 없애기 전 고칠 목록」 1건. 실제 코드 시험으로 보정 3가지 추가: bat 의 `PYTHONUTF8=1` · `>> run.log` · 단계별 종료 코드를 보고 심각도를 내리거나 올림
- 근거: Python 3.15(2026-10-09)부터 `encoding` 없는 `open()` 이 UTF-8 [PEP 686] — 11-19 새 PC 에 3.15 가 기본 설치돼 3.14 로 되돌린 일이 있음(PC이전_체크리스트 116행) · pandas `read_csv` 는 원래 UTF-8 기본 · 실제 코드 80개 grep 시험 상 0(하 위주) → 기존 코드보다 새 코드 예방용 · `scripts/daily_report.py` 1개 전체 적용 지적 1(W7 중 — `daily_and_upload.bat` 가 1단계 종료 코드를 작업 결과로 안 넘김, run.log 에는 남음) · 오탐 반증 3. 검토한 대안: 챗 1차안 그대로 — W8 만으로 19개 파일 지적이 나와 기각. 챗 원본 zip 은 이 PC 에서 못 읽어 ECC 원본(MIT, Copyright (c) 2026 Affaan Mustafa)과 승인 내용으로 다시 만듦
- 출처: Cowork (한경준님 「1. 승인 2. 폴더에 추가 해줘」 11-20)
- 영향: `wiki/_handoff/skills-custom/python-review/SKILL.초안_20261120.md` · `LICENSE-ECC.txt`(MIT 고지, 지우지 않음) · `review-role/SKILL.개정안_20261120.md`(정상본은 시험 통과 뒤 교체, README §3) · 테스트카드 #8 · AI 역할 검토표 4주 측정(12-03) 중 11-20 부터 python-review 가 더해짐 — worklog 검토 줄에 `Py` 로 구분. 별도: `daily_and_upload.bat` W7 고침은 승인 대상(아직 안 고침)

## 2026-11-20 (2): 코고툴 디자인 시스템에 「화면 배치」 절 추가 · im-not-ai(humanize-korean) Cowork 설치 보류

- 결정: ① COGO TOOL 디자인 시스템 README 「배치·모서리」 다음에 「화면 배치」 절을 둔다 — 용도별 배치 이름 5줄(쇼핑몰 첫 화면 히어로 + 카드 그리드 · 제품 목록 사이드바 + 표 · ERP·일일보고 대시보드 · 대외 자료 스플릿/매거진 · 인쇄물 풀블리드와 도련), F·Z 시선 순서, 디자인을 맡기면 이름 붙은 안 2~3개를 먼저 내고 고르는 방식. 게시물의 9종 전체 표는 넣지 않음 ② im-not-ai 는 설치하지 않고 보류. 필요하면 최신 분류표에서 `standards/문서작성-AI티-점검표.md` 에 빠진 패턴만 골라 옮긴다
- 근거: ① 배치 이름 게시물(인스타그램 uxwoodytips)은 5순위라 단독 근거로 쓰지 않고, F자는 Nielsen Norman Group 시선 추적 연구(2006), Z자는 디자인 관례로 구분해 적음. 9종 원문은 다시 확인하지 못함 ② 패턴 분류는 이미 점검표(38 ~ 59행) · `doc_style_check.py` 에 반영([IND-IMNOTAI2026]) · 자동 윤문이 개조식 사내 보고서(보고서-작성-규칙 83행)를 서술식으로 바꿀 가능성(추정값, 실행 안 해 봄) · 수치·용어 변경 위험(자체 변경률 30 % 경고 · 50 % 중단 장치) · 공식 지원 런타임은 Claude Code · Codex · Copilot CLI · Gemini CLI 로 Cowork 없음(github.com/epoko77-ai/im-not-ai, 2026-11-20 확인) · 스킬 수가 늘면 부르는 말이 헷갈림. 검토한 대안: 9종 전체 표 추가 — 출처 확인 안 되고 배치 이름은 Claude 가 이미 알고 있어 기각
- 출처: Cowork (한경준님 「1번 진행 2번 보류」 11-20)
- 영향: 디자인 시스템 「COGO TOOL」 README(아티팩트 버전 1795132105-1332, index lastChange 1795132110-2051) · 마이다스 쇼핑몰 · ERP 화면 디자인 때 이 절 기준 · im-not-ai 는 다시 꺼낼 때 점검표 보강 건으로 처리

## 2026-11-20 (1): 작업 답 끝에 「결론」 블록 고정 — 현황 · 완료 · 미완 · 다음 작업(경준님 / Claude / 대기) · 승인 요청

- 결정: Claude 가 한 단위 일을 끝내고 멈추는 답은 맨 끝(검토 줄 다음)에 결론 블록을 둔다. 항목 이름은 한경준님 수정안대로 현황 · 완료 · 다음 작업, 여기에 미완 · 승인 요청을 더함. 현황 값은 ✅ 마침 / 🔄 진행 중 / ⏸ 승인 대기 / ⛔ 막힘(「완료」와 겹치지 않게 「마침」). 다음 작업은 경준님 · Claude · 대기 3줄, 「경준님」 줄은 「없음」이라도 항상 남김. 없는 줄은 생략, 7줄 안팎, 간단한 답은 `결론: …` 한 줄. 써 보고 다시 고친다.
- 근거: 2026-11-16 ~ 19 세션 28개 모두 worklog 블록은 있으나 대화 마지막 답은 「파일 고침 + 커밋 명령」으로 끝나 다음 진행이 불분명 · 11-18 #2 ~ #7 은 6개 세션 내내 「승인 시 …」로 끝났으나 승인 대기라는 말이 대화에 없었음. worklog(다음 세션용)와 결론 블록(지금 읽는 사람용)은 역할이 달라 둘 다 둔다. 검토한 대안: worklog 블록을 채팅에 그대로 붙이기 — 「한 일」 위주라 누가 무엇을 할지가 섞여 기각.
- 출처: Cowork (한경준님 「대화의 마지막은 늘 결론이 있으면 좋겠다」 → 2차안 「좋아 이렇게 진행 해보고 나중에 다시 수정 해보자」 11-20)
- 영향: `CLAUDE.md` §0-D 신설 · `wiki/_handoff/ai-instructions-universal.md` v4 [마무리] 줄(붙여넣기 본문 1,495자 — [목적] 중복 문장 · 긴 세션 문장 압축) · `wiki/_handoff/chat-project-instructions.md` §4-A — 모두 `.bak_20261120`. claude.ai 개인 설정 · 챗 프로젝트 지침 칸은 한경준님이 다시 붙여넣기

## 2026-11-19 (5): 새 PC 에서 Claude 예약 작업은 PC 폴더를 못 읽는다 — 16:00 배치가 재료를 구글 드라이브에 바로 올리고, 예약 작업은 클라우드에서 그 파일만 읽는다

- 결정: ① 신규 `scripts/drive_upload.py`(token.json · drive.file 범위, 갱신 실패 때 브라우저 로그인 안 띄움 · 대기 60초) — 내 드라이브 `cnc-wiki-auto/` 에 작은 파일을 바로 올림 ② 16:00 배치(`daily_and_upload.bat`)에 `export_calendar_data.py`(캘린더 · (4) 의 올리는 경로를 이것으로 바꿈) · `export_worklog_material.py`(업무일지 재료) 추가, push 뒤에 금요일만 `export_weekly_metrics.py`(주간 정리 측정값 — 드라이런 · 읽기만) ③ Claude 예약 작업: 「업무일지 초안 v2」 평일 16:13 · 「주간 정리 제안 v2」 금 16:23 — 둘 다 클라우드 전용(PC 불필요) ④ 옛 작업(옛 PC DESKTOP-35OSE6P 고정)은 끔: 업무일지 16:07 · 주간 정리 금 14:47 · 월초 점검 v2 · AI 월간 동향 · GitHub 토큰 알림 2개(→ 클라우드 v2 2개 새로 만듦). 월초 점검 · AI 동향은 12-01 · 12-03 전에 같은 방식으로 다시 만듦(11-26 10:20 알림)
- 근거: 11-19 14:09 KST 진단 예약 실행(한경준님 허용) 결과를 드라이브 「cowork_예약진단_20261119」로 받음 — 새 PC 예약 실행에 `device_bash` · `update_artifact` 없음, 예약 작업에 폴더를 지정해도 `connectedFolders` 빈 배열(파일 내용 못 읽음, 이름만). 옛 예약 작업 프롬프트 변경은 「옛 PC 에서 승인 필요」로 거절됨 = 옛 PC 고정 확인. 드라이브 전체 동기화(16:30)는 로그가 없고 11-17 일부만 · 11-18 0건 올라감(드라이브 수정 시각 실측) → 기대지 않음. 시험: 재료 · 측정값 생성(11-18 자료 · 클라우드 복제본, 핸드오프 파일 안 바뀜 확인) · 업로드는 모의 [실측 — 업로드 실물은 11-19 16:00 첫 실행]
- 출처: Cowork (한경준님 「원인 찾아 고치기」 · 「진단 예약 만들어도 돼. 예약 작업 5개 고치는 것도 허용」 11-19)
- 영향: `scripts/daily_and_upload.bat`(원본 `.bak_20261119`) · 신규 `scripts/drive_upload.py` · `export_worklog_material.py` · `export_weekly_metrics.py` · `export_calendar_data.py` 수정 · `private_local/worklog_material/` · `private_local/weekly_metrics/` · CLAUDE.md §15-3 시각 · 업무일지 결과는 이제 알림 · 세션 응답으로만(옛 `outputs/업무일지/*.txt` 저장 없음)

## 2026-11-19 (4): 캘린더 아티팩트가 열릴 때 구글 드라이브의 실적 파일을 직접 읽는다 — (3)의 「Claude 예약 작업 반영」 대체

- 결정: ① 16:00 배치에 `scripts/export_calendar_data.py` 1줄 추가(`daily_and_upload.bat`, 원본 `.bak_20261119`) — 사본의 PROD · CLAUDE_WORK 중 `private_local/calendar/artifact_base.txt`(2026-11-19) 7일 전부터를 `wiki/_private/calendar/calendar_data.txt` 로 내보냄 ② 16:30 「cnc-wiki Drive 동기화」가 그 파일을 올림(본인만 보기 폴더) ③ 아티팩트 「Weekly Calendar Overview」는 열 때 구글 드라이브 `search_files` · `read_file_content` 로 그 파일을 읽어 PROD · CLAUDE_WORK 를 덮어씀(11-19 14:0x KST 이 대화에서 1회 고침). 아래 「업데이트:」 줄에 「실적 YYYY-MM-DD HH:MM 기준」 표시 ④ (3)의 Claude 예약 작업 `trig_01Vogy3u4cZ9B3HWyzoP1xYZ` 는 끔(지우지 않음)
- 근거: 11-19 13:43 KST (3) 방식 시험 실행 보고 — 예약 실행에는 `update_artifact` · `create_artifact` 도구가 없고, 연결 폴더도 0개(예약 작업에 폴더를 지정했는데도). 드라이브 읽기 도구는 파일을 마크다운으로 바꿔 돌려줌(`\[` `\_` 이스케이프 · 이모지 깨짐 — holidays.md 로 실측) → JSON 을 16진수로 바꿔 `CALDATABEGIN` ~ `CALDATAEND` 사이에 넣음. 클라우드 시험: 마크다운식으로 망가뜨린 파일에서 복원 · 화면에 드라이브 값(시험값 99개)이 그려짐 [실측 — Playwright, 도구 응답은 모의]. 대안: 대화 시작 때 반영 · 말할 때만 반영 → 한경준님 「캘린더가 스스로 읽기」(추천안) 선택
- 확인 필요: 실제 앱에서 드라이브 도구 호출 응답 모양 · 처음 열 때 드라이브 연결 허용 창 — 11-19 16:30 뒤 캘린더를 열어 「실적 2026-11-19 16:0x 기준」이 보이면 통과
- 한계: 실적이 16:30 뒤에 보임(전엔 16:00). 파일이 몇 달 쌓이면 대화 세션에서 아티팩트를 사본으로 한 번 갱신하고 `artifact_base.txt` 날짜를 바꿈
- ⚠️ 정정 병기(11-19 14:3x): ② 의 「16:30 동기화가 올림」은 (5) 로 바뀜 — 파일은 `private_local/calendar/calendar_data.txt` 에 두고 16:00 배치가 드라이브 `cnc-wiki-auto/` 로 바로 올림(16:30 동기화는 11-17 · 11-18 누락 실측). 실적은 16:00 뒤 바로 보임
- 출처: Cowork
- 영향: `scripts/daily_and_upload.bat` · 신규 `scripts/export_calendar_data.py` · `private_local/calendar/artifact_base.txt` · 아티팩트 · (3) ③ 대체

## 2026-11-19 (3): 캘린더 아티팩트 자동 갱신 — 스크립트는 cnc-wiki 안 사본만 고치고, 사이드바 반영은 Claude 예약 작업(평일 16:10)

- 결정: ① `scripts/update_calendar_artifact.py` · `update_calendar_claude_work.py` 의 대상 파일을 옛 `C:\Users\TOOLKOREA\Documents\Claude\Artifacts\weekly-calendar-overview\index.html` → `private_local/calendar/weekly-calendar-overview.html`(git · Drive 제외)로 바꾼다(환경변수 `CALENDAR_HTML` 로 바꿔 쓸 수 있음, 원본 `.bak_20261119`) ② 사본은 11-19 13:3x KST 현재 아티팩트 내용 그대로로 시작 ③ Claude 예약 작업 「캘린더 아티팩트 반영 (평일 16:10)」(`trig_01Vogy3u4cZ9B3HWyzoP1xYZ`, 이 PC 필요 · 자동 승인)이 사본을 스테이징 → 아티팩트와 다르면 `update_artifact` 로 올림. 같으면 아무것도 안 함
- 근거: 새 PC 데스크톱 앱(6.6395)은 아티팩트를 앱 내부 폴더에 둬 파이썬이 못 고침 → 11-19 11:59 · 13:08 수동 실행에서 `[calendar-work] ERROR - artifact not found`(다른 단계 rc=0). 아티팩트는 Google 캘린더를 실시간으로 부르므로(`window.cowork.callMcpTool` list_events) 브라우저용 HTML 로 바꾸면 그 기능을 잃음. 대안 ② 사본만 두고 반영은 손으로 — 사용량 0 이나 사이드바가 안 바뀜 ③ 캘린더 단계 끄기 — ERROR 만 사라짐. 한경준님 ① 선택(추천안, 11-19). 클라우드 시험: 11-18 PROD 줄 다시 넣기 · 같은 값 SKIP · CLAUDE_WORK 11-19 추가 모두 rc=0 [실측 — 사본 복제본]
- 출처: Cowork
- 영향: `scripts/update_calendar_artifact.py` · `scripts/update_calendar_claude_work.py` · 신규 `private_local/calendar/` · Claude 예약 작업 1개 추가 · 16:00 배치(`daily_and_upload.bat`)는 그대로. 확인: 11-19 16:40 KST 후속 점검(send_later)
- ⚠️ 정정 병기(11-19 14:0x): ③ 은 동작하지 않음 — 예약 실행에 `update_artifact` 없음 · 연결 폴더 0개(13:43 시험). → (4) 로 대체, 예약 작업은 끔. ① ② 는 그대로 유효

## 2026-11-19 (2): 작업 PC 전환을 오늘(11-19) 16:00 전에 한다 — 두 PC 병행 운용 안 함

- 결정: ① 옛 PC(DESKTOP-35OSE6P) cnc-wiki 예약 작업 7개 「사용 안 함」 → 새 PC 에 같은 7개 등록(XML 의 옛 SID · `DESKTOP-35OSE6P\TOOLKOREA` 를 새 PC 사용자로 바꿔 등록), 오늘 16:00 일일보고부터 새 PC 가 실행 ② 옛 PC 는 1 ~ 2주 끄지 않고 보관 — 문제 시 예약 작업만 다시 켜서 되돌림 ③ 전환 전까지 새 PC 에서 `daily_report.py` · 일일보고 bat · `update_dashboard_now.bat` 실행 금지(끝에 `generate.py` 업로드를 자동 실행 — `scripts/daily_report.py` 737 ~ 740행)
- 근거: 11-19 10:51 KST 새 PC 시험 — ERP 조회 231회 실패 0 · 일일보고 xlsx 생성 · `generate.py --local` 사내 배포 23개 성공, 남은 것은 Git 설치뿐. 병행하면 두 PC 가 같은 GitHub 저장소에 push 해 충돌 · 보고서 중복. 옛 PC 의 cnc-wiki 쓰기는 16:00 일일보고 전까지 없음(07:54 OnBoot 실행 이후 · 09:00 알림 2개는 메일만) → 자료 재복사 불필요. 대안: 며칠 병행 시험 — 충돌 위험만 늘고 얻는 것 없음
- 출처: Cowork (추천안 → 한경준님 「승인」 11-19)
- 영향: 예약 작업 7개(옛 PC 사용 안 함 · 새 PC 등록) · `private_local/pc_migration/PC이전_체크리스트.md` §5 전환일 · 옛 PC 백업 XML 기준 ANCA_Scraper_Daily · DailyDlvAlert · DailyZeroPriceAlert 는 이미 「사용 안 함」 상태라 새 PC 에도 꺼진 채 등록됨

## 2026-11-19 (1): 새 작업 PC 이전 — 사용자 이름이 HAN 이라 `C:\Users\TOOLKOREA` → `C:\Users\HAN` 연결 폴더(정션)로 옛 경로 유지

- 결정: ① 새 PC(사용자 `HAN`)에 정션 `C:\Users\TOOLKOREA` → `C:\Users\HAN` 1개를 두어 스크립트 · bat · vbs · `.env`(`INTERNAL_DIR`) · `run_scraper.ps1` · 예약 작업의 `C:\Users\TOOLKOREA\...` 고정 경로를 코드 수정 없이 그대로 쓴다(2026-11-19 09:35 KST 생성) ② 예약 작업은 XML 가져오기 때 사용자를 HAN 으로 다시 지정(XML 에 옛 PC SID) ③ 정션 제거는 `cmd /c rmdir C:\Users\TOOLKOREA` 만 — `Remove-Item -Recurse` · 탐색기 삭제 금지(대상 실제 파일까지 지울 수 있음)
- 근거: 옛 PC 실측 — `C:\Users\TOOLKOREA` 고정 경로가 실행 파일 약 20개(cnc-wiki 경로) · `.env` 1줄(`Desktop\현황판`) · Python 경로 4곳(예약 작업 3 · `run_scraper.ps1`)에 있음. 대안 ① 경로를 상대 경로 · 환경 변수로 고치기 — 정석이나 파일 20개+ 수정 · 시험 부담, 이전 당일엔 위험 ② 새 Windows 계정 TOOLKOREA 생성 — 프로그램 · 로그인 재설정이 두 배. Windows 사용자 이름을 바꿔도 프로필 폴더 이름은 그대로라 해결 안 됨
- 출처: Cowork (추천안 → 한경준님 새 PC 에서 직접 실행 = 승인)
- 영향: 이전 체크리스트 `private_local/pc_migration/PC이전_체크리스트.md`(git · Drive 제외 — 설치 목록 · 알FTP · MCT 접속 정보) · 고정 경로 정리(상대 경로화)는 나중 과제로 남김 · 옛 PC 예약 작업 7개는 새 PC 시험 통과 당일 「사용 안 함」

## 2026-11-18 (6): 매출 현황판 자료 위치를 wiki/ 밖 `private_local/sales_board/` 로 — 16:30 Drive 동기화 제외

- 결정: ① 매출 현황판의 결과 · 입력 · 캐시 · 주간 엑셀을 `wiki/_private/sales_board/` → 저장소 루트 `private_local/sales_board/` 로 옮긴다(`.gitignore` 에 `private_local/` 추가) ② `erp/sales_board.py` · `erp/probe_purchase.py` 경로를 바꾸고 `scripts/sync_to_gdrive.py` 는 건드리지 않는다
- 근거: 검토(11-18 16:0x KST) 중 `scripts/sync_to_gdrive.py` 가 `wiki/` 를 제외 목록 없이 통째로 올림을 확인(`sync_folder` 재귀, 건너뛰는 것은 `~$` 잠금 파일뿐) — 매일 16:30 「cnc-wiki Drive 동기화」로 거래처별 매출 · 전체 매입처 금액 캐시가 Google Drive 에 올라갈 뻔함(첫 업로드 16:30 전에 옮김). 앞서 「금액이 PC 밖으로 안 나간다」는 안내가 틀렸음(Claude 실수). 대안: 동기화 스크립트에 제외 줄 추가 — 기존 자동화 수정이라 뺌 · 그대로 둠 — 대외비 원칙과 어긋남. 한경준님 「wiki 밖으로 옮김」(추천안) 선택
- ~~확인 필요: 다른 `wiki/_private/` 파일의 Drive 업로드 의도~~ → 그대로 둠(한경준님 「괜찮을 거 같으면 냅두고」 11-18). Drive `cnc-wiki/wiki/_private`(2026-06-29~) 파일은 모두 소유자만 보기 · 공유 없음 [실측 — Drive 조회]. 매출 현황판 자료만 `private_local/` 로 따로 둠
- 출처: Cowork
- 영향: `.gitignore` · `erp/sales_board.py` · `erp/probe_purchase.py` · `scripts/register_sales_weekly_task.ps1`(주석만, 등록된 예약 작업은 그대로) · decisions (4) (5) · worklog #13 경로 표기

## 2026-11-18 (5): 매출 현황 주간 엑셀 — 매주 수요일 09:00 경준님 PC 예약 작업(CNC_Sales_Weekly)

- 결정: ① `erp/sales_board.py --weekly` 를 Windows 예약 작업 `CNC_Sales_Weekly`(수 09:00 KST · 로그온 중에만 · 놓치면 켜질 때 실행)로 돌린다 — 기준일 = 직전 화요일, 기간 = 그달 1일 ~ 화요일(수기 시트와 같은 월 누계), 전년 같은 기간 ② 결과는 수기 「생산팀 매출 현황」 시트와 같은 모양의 엑셀(`private_local/sales_board/엑셀/매출현황_YYYYMMDD.xlsx`, 입력 값만 숫자 · 이익 · 비율은 수식)을 만들어 화면에 연다. 월평균 출하 수량 줄은 뺌(11-18 경준님 「내가 틀린 것 같음」) ③ 클라우드 예약 작업 · 푸시 · 공유폴더는 쓰지 않는다
- 근거: ERP 는 경준님 PC 에서만 닿음(Cowork VM · 클라우드 403 blocked-by-allowlist, 11-18 재확인) · 금액 대외비라 PC 밖으로 안 내보냄 · 푸시는 거의 안 봄(2026-11-02 아침 브리핑 중단 사유). 대안 검토(11-18): Claude 예약 작업만 — ERP 접속 불가로 기각 · Windows 생성 + Claude 알림 — 금액이 클라우드를 거쳐 보류 · ERP 허용 목록 추가 — HTTP 비암호화로 보류 중인 C안 → 한경준님 「1번(Windows 만)으로 해」. 실데이터 엑셀(11-17 기준)을 수식까지 계산해 시트 21칸 일치 [실측 검증]
- 출처: Cowork (경준님 요청 「매주 수요일 오전 9시 … 전날 화요일까지」 2026-11-18)
- 영향: `erp/sales_board.py`(--weekly · 엑셀) · 신규 `scripts/register_sales_weekly_task.ps1`(등록 · 확인 · 되돌리기 1줄) · `private_local/sales_board/weekly.log`(실행 기록). 💰 금액 미기재

## 2026-11-18 (4): 매출 현황판(재연마) — 출하 금액 열 차단의 두 번째 예외 · 결과는 경준님 PC `_private` 에만

- 결정: ① 신규 `erp/sales_board.py` 한 곳에서만 `lem120_jae_g00`(재연마 출하등록, 상세)을 `block_price=False` 로 받고, 받자마자 8열(출하일 · 거래처명 · 출고 · 출고합계 · 연마불가 · 공급가 · 부가세 · 합계금액)만 남긴다 — `trico_client` 기본 차단은 그대로(decisions 2026-11-13 (2) 와 같은 방식) ② 결과 · 입력 · 캐시는 `private_local/sales_board/`(git 추적 제외)에만 쓰고, 공유폴더 현황판 · dist(github.io) · 예약 작업에는 넣지 않는다 — 실행은 저장소 루트 「매출현황판.bat」 손으로만 ③ 범위는 재연마만(영업팀 출하 `lem120_g00` 제외) ④ 계산은 수기 「생산팀 매출 현황」 시트와 같게 — 이익 = 매출 − 외주 매입 합계, 이익률 = 이익 ÷ 매출, 수량 = 출고(연마불가 제외). 목표 · 외주 매입은 입력표(`입력.xlsx`)에 손으로 넣는다(외주 매입 ERP 조회 이름은 캡처 전이라 추측하지 않음)
- 근거: 한경준님 선택(2026-11-18) — 기준 「금액 + 수량」 · 위치 「경준님 PC 전용」 · 범위 「재연마만」(모두 추천안). 금액은 실거래 금액이라 대외비(CLAUDE.md §4) — 공유폴더에 두면 생산팀 누구나 열 수 있어 뺌. 시트 사진(11-17 기준)의 21칸을 모의 데이터로 재현해 21 / 21 같음 [실측 — 계산식 검증, ERP 금액 칸 뜻은 아님]
- 대조(2026-11-18 15:03 KST, PC 실행 `last_run.txt`): 11-01 ~ 17 매출 `mov_amt` 합 · 출고 수량이 수기 시트 26년 · 25년 값 4칸 모두 일치 [실측 검증] — 매출 = 공급가(부가세 제외) 확정, ERP 에 2025-01 부터 출하 기록 있음. ~~확인 필요: 매출 = `mov_amt`(공급가로 추정) 합이 수기 시트 값과 같은지~~ · ~~전년 비교 기준~~ → 같은 기간(1일 ~ 기준일)으로 확정(한경준님 2026-11-18, 기본값 `--py same`) · 시트 맨 아래 월평균 출하 수량(2,357)은 ERP 평균 후보 4개와 모두 달랐고 한경준님 「내가 틀린 것 같음」(11-18) → 판에 넣지 않음 · 외주 매입 = ERP 매입(입고) 조회 `lea110_g00`(11-18 한경준님 Fiddler 캡처, `erp/probe_purchase.py --parse` → `private_local/sales_board/purchase_spec.json`)의 `in_amt`(공급가) 를 업체별로 더함 — 25년 · 26년 11월 1 ~ 17일 외주 2곳 4칸 수기 시트와 일치 [실측 검증, 11-18 15:24 KST]. 업체명은 `private_local/sales_board/외주업체.json` 에만 두고, 없으면 입력표 값을 씀(같은 차단 예외 · 결과 `_private`)
- 출처: Cowork
- 영향: 신규 `erp/sales_board.py` · `매출현황판.bat`(공개 저장소 — 금액 · 실명 없음, `anonymize_public.py --check` 0) · `private_local/sales_board/`(입력.xlsx · 매출현황판.html · cache/). 💰 금액 미기재

## 2026-11-18 (3): 마이다스 몰 재연마 견적 — 이름 「재연마 견적 계산기」 · 몰 안 페이지 1개로 넣는 방향

- 결정: ① 고객 화면 이름은 「재연마 견적 계산기」(챗봇 · 단가 봇 아님) — 사내 문서도 이 이름으로 맞추고 파일명(`정가조회.pyw` · `price-widget.js` 등)은 그대로 ② midastool.co.kr 안에 일반 페이지 1개(예 `/regrind`, 상단 메뉴)로 넣는다 — 팝업 · iframe 은 쓰지 않고, 모달은 마이다스 품번 대응표가 생긴 뒤 상품 페이지 보조로만 ③ 몰 코드는 개발사 소관 → 생산팀은 「엔진 + `price_data.json` + 판정 명세 + 검수 문항」 꾸러미로 넘긴다 ④ 1차는 공표 정가만(할인가 · 품번 자동 입력은 할인율 · 대응표 정해진 뒤)
- 근거: 「챗봇」은 대화형이 아니고 몰의 「AI 공구상담」과 겹침, 「단가」는 사내에서 할인 적용 실거래 단가(대외비, CLAUDE.md §4)라 오해 소지. 페이지 방식 = 로그인 · 장바구니 · 주문이 이어지고 모바일 · 링크 공유 가능 · 몰이 Next.js(보안점검 `outputs/07.마이다스 보안점검/마이다스툴_보안점검_20261112.md` 76행)라 페이지 추가가 쉬움. 팝업 = 브라우저 차단 · 모바일 불가, iframe = 공개 전 넣을 보안 헤더(decisions 2026-11-12 (1))와 충돌. 위젯은 외부 라이브러리 없음(`scripts/price_widget/price-widget.js` 머리말). 한경준님 「그렇게 하면 되겠네」(2026-11-18) — 꾸러미 제작 · 개발사 전달 시점은 아직 정하지 않음
- 출처: Cowork
- 영향: [[projects/신규쇼핑몰-ERP-재연마-연동-준비]](2026-10-30 보류 → 방향 합의) · 넘기기 전 10-30 뒤 정가표 개정 여부 확인 · 검수 문항 재생성(`price_acceptance_cases.py`) · 결제 시점(주문 때 / 검수 뒤)은 개발사 회의 안건

## 2026-11-18 (2): AI 역할 검토표 측정 — worklog 블록에 「검토:」 줄 추가

- 결정: ① 세션 끝 worklog 핸드오프 블록에 `- 검토: R? 주 · R? — 통과 n · 확인 필요 n · 통과 뒤 지적 n` 한 줄을 넣는다(작은 일만 한 세션은 「작은 일(G1)」) ② 「통과 뒤 지적」 = 통과로 낸 뒤 한경준님이 짚은 Claude 실수 건수 ③ 12-03 판정은 11-18 ~ 12-03 실측 + 11-05 ~ 11-17 추정(하한)으로 한다
- 근거: 4주 측정(decisions 2026-11-05 (1) ⑤)의 세 값이 채팅 답 끝 검토 줄에만 있어 파일에 남지 않음 — 11-05 ~ 11-18 worklog 블록 44개 중 검토 결과 기록 2개 [실측]. 대안: 별도 측정 대장 파일 — 세션마다 파일 하나 더 열어야 해 누락이 더 늘 것으로 보고 뺌. 한경준님 승인 「진행 해」(2026-11-18)
- 출처: Cowork
- 영향: `CLAUDE.md` §0-B · §16 · `wiki/_handoff/skills-custom/cnc-handoff/SKILL.md`(계정 스킬은 카드로 반영) · `wiki/standards/AI-역할-검토표.md` §4 중간 점검 · tasks「AI 역할 검토표 4주 측정」

## 2026-11-18 (1): AI 공작기계 동향 월간 조사 예약 작업 신설 · 새 작성법(양식 D) 월간판 사용

- 결정: ① 매월 전월 발표를 조사해 「AI 공작기계 동향 월간 보고」(`wiki/reports/04_비교·분석/AI공작기계_월간동향_YYYYMM.pdf`)를 자동으로 만든다 — 예약 작업 `trig_014TXoCM9qsafKTwpP631DWk`, 매월 3 ~ 9일 중 첫 영업일 14:13 KST(상태 파일 `outputs/.trend_monthly_state.json` 로 한 달 1회) ② 범위는 2026-11-18 합의 그대로(머시닝센터 중심 · 6개 지역 · 성능 시험 · 가격 비교 · 로봇 단독 제외), 검색 회차마다 결과 · 채택 건수 기록 ③ 누적 목록 `scripts/report_ai_trend_monthly/items_master.csv` 는 행 추가만, 상태 변경은 상태이력 열에 덧붙임(옛 값 삭제 금지) ④ 연간 보고(12개월, 제1판 방식)는 매년 12월 대화 세션에서 ⑤ 예약 실행은 git 쓰기 · 삭제 · 이동 없이 커밋 명령만 안내
- 근거: 같은 주제를 기존 제5판 방식과 새 작성법 제1판으로 써서 비교(작성법 §8-A) 뒤 한경준님 「월에 한번씩 조사하고 보고서 만들 수 있게 진행」(2026-11-18). 월간판 생성 도구를 2026-11 견본 데이터로 시험 출력 — 5쪽, doc_style_check 기준 넘은 항목 0. 양식 D 자체 확정(CLAUDE.md §14)은 첫 월간 보고(2026-12) 검토 뒤
- 출처: Cowork (한경준님 요청 2026-11-18)
- 영향: `scripts/report_ai_trend_monthly/`(신규) · 예약 작업 1건 추가 · `wiki/standards/동향조사-보고서-작성법.md` §8-A · 매월 `wiki/reports/04_비교·분석/` · `items_master.csv` · `sources.md` 갱신

## 2026-11-17 (1): 기사 경유 수치 = 「추정값(제조사 주장 · 기사 경유)」 · 자료 조사 스킬 research-deep 신설

- 결정: ① 신뢰도 4단계(CLAUDE.md §2) 적용 — 제조사 원문(보도자료 · 제품 페이지 · 카탈로그)에서 직접 확인한 값 = 「제조사 기준」, 기사 · 보도로만 확인한 값 = 「추정값(제조사 주장 · 기사 경유)」. 4단계 밖 표기(예: 「제조사 발표(기사 경유)」)는 쓰지 않는다 ② 외부 자료 조사는 스킬 research-deep 순서(검색어 장비 × 기능 × 언어로 펼치기 → 출처 다섯 갈래 → 후보 목록 → 걸러내기 F1 ~ F8 → 중점 → 확인 필요 재추적 1회)로 한다. 등재 · 새 페이지는 source-add · wiki-new-page 를 따른다
- 근거: 2026-11-17 AI 탑재 공작기계 조사 — 좁은 검색으로 판매 중 제품(아룸 TTMC)을 놓쳐 결론을 정정. 검수(review-role R4 주 · R1 · R5)에서 보완 8건(1차 자료 확인 · 4단계 밖 표기 · 못 읽은 출처 · 스킬 중복 · 사용량 근거 등). 사용량 실측: 첫 조사 29회 → 세 번 합계 61회(약 2.1배, 호출 수 · 1회). 대안: 기사 경유도 「제조사 기준」(기각 — 기사 요약 · 오기 위험, 오쿠마 시기처럼 기사끼리 다름) · 새 등급 추가(기각 — 4단계 체계 유지)
- 출처: Cowork (한경준님 「그렇게 진행 해」 승인 2026-11-17)
- 영향: `CLAUDE.md` §2 신뢰도 표 아래 1줄 · `wiki/comparisons/AI-탑재-공작기계-동향-2026-11.md` §5 신뢰도 · 스킬 초안 `wiki/_handoff/skills-custom/research-deep/SKILL.초안_20261117.md`(계정 저장 · 테스트카드 #7 시험 뒤 정상본)

## 2026-11-16 (7): `git-commit.bat` 은 수동 백업 버튼 — 목록 표시 + Y 확인 뒤 커밋

- 결정: `git-commit.bat` 은 전체 `git add .` 를 유지하되, 커밋 전에 `git status --short` 목록을 보여 주고 Y 를 입력해야 add · commit 한다(그 외 입력은 취소, 변경 없으면 바로 종료). 세션 끝 커밋은 CLAUDE.md §0-B 「바꾼 파일만 add」 명령만 쓴다. decisions 2026-11-16 (6) ⑤ 「bat 안 바꿈」을 대신한다.
- 근거: bat 은 어느 세션이 무엇을 바꿨는지 알 수 없어 경로 add 로 바꾸면 백업 기능이 사라진다. 남는 위험은 「모르는 변경이 조용히 같이 커밋」이라 확인 단계로 막는다. 실명은 pre-commit 훅이 이미 검사(`core.hooksPath=.githooks` 확인 2026-11-16). 대안: 경로 add 로 변경(기각 — 백업 버튼 역할 상실) · bat 폐기(기각 — 한경준님이 쓰는 파일) · 그대로 둠(기각 — §0-B 와 모순 남음)
- 출처: Cowork (한경준님 「추천대로 진행」 승인 2026-11-16)
- 영향: `git-commit.bat`(백업 `git-commit.bat.bak_20261116b`) · `CLAUDE.md` §0-B 한 줄 · Windows 첫 실행 확인 필요(Enter 만 → 「[취소]」 · Y → 커밋)


## 📁 아카이브 인덱스

> 최근 **15건**만 이 파일에 둡니다. 그 이전 항목은 아래 파일에 **삭제 없이 보존**됩니다.
> 과거 결정을 찾을 때는 `wiki/_handoff/decisions-archive/` 전체를 grep 하세요.

| 기간 | 이 파일 | 아카이브 | 합계 |
|---|---|---|---|
| 2026-11 | 15건 | [[decisions-archive/2026-11]] 43건 | 58건 |
| 2026-10 | 0건 | [[decisions-archive/2026-10]] 13건 | 13건 |
| **합계** | **15건** | **56건** | **71건** |

> 이 파일의 범위: **2026-11 ~ 2026-11** (가장 오래된 항목 — 2026-11-16 (7): `git-commit.bat` 은 수동 백업 버튼 — 목록 표시 + Y 확)

> 재정리: `python scripts/archive_handoff.py --apply` (마지막 실행 2026-11-19)
## 📁 아카이브 인덱스

> 최근 **15건**만 이 파일에 둡니다. 그 이전 항목은 아래 파일에 **삭제 없이 보존**됩니다.
> 과거 결정을 찾을 때는 `wiki/_handoff/decisions-archive/` 전체를 grep 하세요.

| 기간 | 이 파일 | 아카이브 | 합계 |
|---|---|---|---|
| 2026-11 | 2건 | — | 2건 |
| 2026-10 | 13건 | [[decisions-archive/2026-10]] 90건 | 103건 |
| **합계** | **15건** | **90건** | **105건** |

> 이 파일의 범위: **2026-10 ~ 2026-11** (가장 오래된 항목 — 2026-10-29 (5): 드릴 **사업장별 전용 할인율 안 폐기** — 할인율 **0.75 고정**)

> 재정리: `python scripts/archive_handoff.py --apply` (마지막 실행 2026-11-02)
## [폐기 → (5)] 2026-10-29 (4): 초경 드릴 할인율 — **코고 · 창성까지 3사업장 확정**, 대외비 확정본은 `wiki/_private/드릴-재연마-정가-할인율.md` 한 곳에 정리

- 결정: ① 비코팅 · 일반 코팅 할인율을 코툴 · 코고 · 창성 모두 확정 — 세 사업장 인상 폭을 비슷하게(기존 사업장 간격 유지), 마이너스 0. 값은 확정본에만 ② 대외비(할인율 · 할인 적용 단가)는 git 제외 폴더 `wiki/_private/` 의 **확정본 1개 파일**에 모으고, `_private/README.md` 로 보관 규칙(옮겨 적지 않음 · `git add -f` 금지)을 둔다. 검토 파일은 과정 기록으로 남김 ③ 고경도는 범위 밖(한경준님 「신경 쓰지 말고」)
- 근거:
  - 한경준님 「ㅇㅋ 이렇게 한다」 · 「깃에 업로드 안 하는 곳에서 정리해서 기록」(2026-10-29)
  - 🔴 정정: 처음 창성을 정가 × 1.1(ERP 창성 파일의 매출 칸)로 계산 → 창성은 **정가 × 0.95**(매입 칸, 예 2DR0601100 〔금액 _private〕 → 〔금액 _private〕). decisions (2) · (3) 의 「창성 · 코고」는 코고 값
  - `.gitignore` `wiki/_private/` 제외 확인 · 추적 파일 0(실측) · 포털 생성 스크립트가 `_private` 내용을 쓰지 않음(실측)
  - 학술 · 표준 출처: 해당 없음(사내 가격 운영 판단)
- 출처: 챗(Cowork, 한경준님 2026-10-29)
- 영향: 신규 `wiki/_private/드릴-재연마-정가-할인율.md` · `wiki/_private/README.md` · ⬜ 정가표 개정(한경준님) → ERP 일괄 변경 · ⬜ 고경도 · HSS · 3 · 4날 별도

## [폐기 → (5)] 2026-10-29 (3): 초경 드릴 **코팅** — 16이하를 **14이하 / 16이하로 나누고 코팅 16이하 정가 〔금액 _private〕**, 할인율은 마이너스 0 기준으로 사업장별 확정(값은 `_private`)

- 결정: ① 원칙 = **인상이므로 어느 지름도 기존 판매가보다 내려가면 안 된다**(한경준님) ② 초경 드릴 새 정가의 16이하 구간을 14이하 / 16이하로 나눈다 — 14이하는 기존 안의 16이하 값(비코팅 〔금액 _private〕 · 코팅 〔금액 _private〕 · 고경도 〔금액 _private〕), **16이하 코팅 = 〔금액 _private〕** ③ 코팅 할인율 확정(코툴 · 창성 · 코고 값은 `wiki/_private/드릴-할인율-검토-20261029.md` §1-B — ~~창성 · 코고~~ **코고** 값은 비코팅과 같은 사업장 간격으로 Cowork 가 맞춘 것, 한경준님 확인 대기 · 창성은 §1-C 별도) ④ 16이하 고경도 정가는 미정(같은 율이면 최소 〔금액 _private〕)
- 근거:
  - 한경준님 「마이너스는 나면 안 됨… 인상을 하는 건데」 · 「16이하만 〔금액 _private〕으로 고정하면 가능하니 그렇게 할게」(2026-10-29)
  - 마이너스를 만드는 곳은 15.1 ~ 16.0 mm 한 곳(기존 정가가 14.1 mm 에서 코팅 〔금액 _private〕 → 〔금액 _private〕 으로 뜀). 표를 그대로 두면 이 지름 하나 때문에 율을 크게 올려야 하고 6 ~ 12이하 코팅이 +16 ~ +28 % 오름 → 구간을 나눠 16이하만 올림
  - 결과(계산값, 191점): 코툴 코팅 평균 +13.7 %(+2.6 ~ +32 %) · 창성 · 코고 평균 +14.5 %(+3.2 ~ +33 %), 마이너스 0
  - 학술 · 표준 출처: 해당 없음(사내 가격 운영 판단)
- 출처: 챗(Cowork, 한경준님 2026-10-29)
- 영향: `wiki/_private/드릴-할인율-검토-20261029.md` §1-B · ⬜ 고경도 16이하 정가 · ⬜ 창성 · 코고 코팅 율 확인 · ⬜ 정가표 드릴 블록 개정(한경준님) · ⬜ HSS · ⬜ ERP 일괄 변경 · 조회기 · 통합 프로젝트 재생성

## [폐기 → (5)] 2026-10-29 (2): 초경 드릴 재연마 **비코팅** — 새 정가(구간 5개)에 일반 할인율 방식 적용, 율은 **「기존보다 내려가는 품목 없음」 기준의 최저값**으로 사업장별 확정(값은 `_private`)

- 결정: ① 초경 드릴 비코팅은 기존 「정가 × 드릴 배율(가격 네고 X)」 대신 새 정가(6 · 10 · 12 · 16 · 20이하)에 사업장별 할인율을 곱한다 ② 율 = 기존 판매가보다 내려가는 지름이 0 인 가장 낮은 값 — 코툴 · ~~창성(= 코고)~~ **코고** 값은(🔴 10-29 정정: 창성은 정가 × 0.95 기준이라 별도 — 같은 파일 §0 · §1-C) `wiki/_private/드릴-할인율-검토-20261029.md` §1 ③ 코팅 · 고경도 · HSS 는 미결(같은 파일 §3)
- 근거:
  - 한경준님 「마이너스 안 나는 게 그 율이면 그렇게」 · 「비코팅 기준은 그렇게」(2026-10-29)
  - 비교(계산값): 지름 1.0 ~ 20.0 mm 0.1 mm 단위 191점, 기존 = 정가표(26.09) 드릴 블록 × 배율(ERP 등록값 대조), 신규 = ROUNDUP(새 정가 × 율, −1). 율을 정하는 곳은 15.1 ~ 16.0 mm(기존 정가가 14.1 mm 에서 뜀). 평균 약 +17 %, 20이하 오름폭이 큼(+24 ~ +34 %)
  - 평균만 맞추는 율(차이 0)은 코툴 · 창성 모두 지름의 약 절반이 내려가 채택하지 않음
  - ERP 실측: 코고 · 창성 드릴 단가는 정가 × 1.1 을 10원 **버림**, 코툴은 올림
  - 학술 · 표준 출처: 해당 없음(사내 가격 운영 판단)
- 출처: 챗(Cowork, 한경준님 2026-10-29)
- 영향: 신규 `wiki/_private/드릴-할인율-검토-20261029.md`(대외비, git 제외) · ⬜ 정가표 드릴 블록 개정(한경준님, 정가표는 Claude 수정 금지) · ⬜ 코팅 · 고경도 율 / 16이하 구간 나누기 · ⬜ HSS 할인 체계 여부 · ⬜ 20이하 새 정가 재검토 여부 · ⬜ 확정 뒤 ERP 드릴 품목 매출할인율 · 정가 일괄 변경 · `price_lookup.py` · 통합 프로젝트 지식 재생성

## 📁 아카이브 인덱스

> 최근 **15건**만 이 파일에 둡니다. 그 이전 항목은 아래 파일에 **삭제 없이 보존**됩니다.
> 과거 결정을 찾을 때는 `wiki/_handoff/decisions-archive/` 전체를 grep 하세요.

| 기간 | 이 파일 | 아카이브 | 합계 |
|---|---|---|---|
| 2026-10 | 15건 | [[decisions-archive/2026-10]] 13건 | 28건 |
| **합계** | **15건** | **13건** | **28건** |

> 이 파일의 범위: **2026-10 ~ 2026-10** (가장 오래된 항목 — 2026-10-07: 투입 목록 매칭 — **같은 날 안에서는 오더번호 1개 줄을 먼저 배정**, 번호)

> 재정리: `python scripts/archive_handoff.py --apply` (마지막 실행 2026-10-12)
## 📁 아카이브 인덱스

> 최근 **15건**만 이 파일에 둡니다. 그 이전 항목은 아래 파일에 **삭제 없이 보존**됩니다.
> 과거 결정을 찾을 때는 `wiki/_handoff/decisions-archive/` 전체를 grep 하세요.

| 기간 | 이 파일 | 아카이브 | 합계 |
|---|---|---|---|
| 2026-10 | 15건 | — | 15건 |
| 2026-09 | 0건 | [[decisions-archive/2026-09]] 13건 | 13건 |
| **합계** | **15건** | **13건** | **28건** |

> 이 파일의 범위: **2026-10 ~ 2026-10** (가장 오래된 항목 — 2026-10-01: **9월 월간 출하현황 마감** — 9월 시트 신규, 출고 1,358개 / 납품처)

> 재정리: `python scripts/archive_handoff.py --apply` (마지막 실행 2026-10-07)
## 📁 아카이브 인덱스

> 최근 **15건**만 이 파일에 둡니다. 그 이전 항목은 아래 파일에 **삭제 없이 보존**됩니다.
> 과거 결정을 찾을 때는 `wiki/_handoff/decisions-archive/` 전체를 grep 하세요.

| 기간 | 이 파일 | 아카이브 | 합계 |
|---|---|---|---|
| 2026-10 | 2건 | — | 2건 |
| 2026-09 | 13건 | [[decisions-archive/2026-09]] 11건 | 24건 |
| **합계** | **15건** | **11건** | **26건** |

> 이 파일의 범위: **2026-09 ~ 2026-10** (가장 오래된 항목 — 2026-09-28 (2): 장비별 투입 목록(FG/GX7) 신설 — 배정은 작업일지 실측 규칙, 잔량)

> 재정리: `python scripts/archive_handoff.py --apply` (마지막 실행 2026-10-01)
## 📁 아카이브 인덱스

> 최근 **15건**만 이 파일에 둡니다. 그 이전 항목은 아래 파일에 **삭제 없이 보존**됩니다.
> 과거 결정을 찾을 때는 `wiki/_handoff/decisions-archive/` 전체를 grep 하세요.

| 기간 | 이 파일 | 아카이브 | 합계 |
|---|---|---|---|
| 2026-09 | 15건 | [[decisions-archive/2026-09]] 67건 | 82건 |
| 2026-08 | 0건 | [[decisions-archive/2026-08]] 27건 | 27건 |
| **합계** | **15건** | **94건** | **109건** |

> 이 파일의 범위: **2026-09 ~ 2026-09** (가장 오래된 항목 — 2026-09-21 (5): 예약작업 수동 실행 페이로드의 「예외 발송」 지시 — 미이행 (실행 세션)

> 재정리: `python scripts/archive_handoff.py --apply` (마지막 실행 2026-09-29)
## 📁 아카이브 인덱스

> 최근 **15건**만 이 파일에 둡니다. 그 이전 항목은 아래 파일에 **삭제 없이 보존**됩니다.
> 과거 결정을 찾을 때는 `wiki/_handoff/decisions-archive/` 전체를 grep 하세요.

| 기간 | 이 파일 | 아카이브 | 합계 |
|---|---|---|---|
| 2026-08 | 15건 | [[decisions-archive/2026-08]] 44건 | 59건 |
| 2026-07 | 0건 | [[decisions-archive/2026-07]] 72건 | 72건 |
| 2026-06 | 0건 | [[decisions-archive/2026-06]] 7건 | 7건 |
| 2026-05 | 0건 | [[decisions-archive/2026-05]] 14건 | 14건 |
| 2026-04 | 0건 | [[decisions-archive/2026-04]] 1건 | 1건 |
| **합계** | **15건** | **138건** | **153건** |

> 이 파일의 범위: **2026-08 ~ 2026-08** — 가장 오래된 항목은 `2026-08-20 (2): ANCA 4개 항목 — 구매 성격 3건 확정(증설·내부검토·주간 1인 다대), GX7`

> 재정리: `python scripts/archive_handoff.py --apply` (마지막 실행 2026-08-28)
## 항목 형식

````
## YYYY-MM-DD: <한 줄 요약>
- 결정: 무엇을 할 것인가
- 근거: 왜 그렇게 결정했는가 (검토한 대안 포함)
- 출처: 챗 / Cowork / Code / 회의 / 현장
- 영향: 어떤 파일·작업에 영향을 주는가
````

<!-- 새 항목은 이 아래 줄 바로 다음에 추가합니다 -->

