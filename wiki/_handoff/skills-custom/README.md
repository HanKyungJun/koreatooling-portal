# 사내 스킬 원본 · 목록 (skills-custom)

> 계정에 저장된 사내 스킬의 **정상본**(마지막으로 쓰고 있는 원본)을 보관한다. 스킬이 깨지거나 개정이 잘못되면 여기서 되돌린다.
> 계기: wikidocs 19445 「Claude로 일하는 법」 13-7 · 14-3(보조 참고) — 2026-11-16 이전에는 사내 스킬 원본이 위키 어디에도 없었다.
> Anthropic 기본 스킬(docx · pdf · pptx · xlsx · skill-creator 등)은 `../skills-updated/` — 이 폴더는 사내 스킬만.

## 1. 목록

정상본 날짜 = 계정 저장 시각(manifest `updatedAt`, KST 환산). 「마지막 시험」은 [[테스트카드]] 에 기록이 있는 것만, 없으면 미확인.

| 스킬 | 하는 일 | 부르는 말 | 정상본 | 마지막 시험 | md5(앞 8) |
|---|---|---|---|---|---|
| cnc-handoff | 세션 시작 요약 · 종료 블록 | 세션 시작 · 마무리해줘 | 2026-11-16 10:37 | 2026-11-16 (카드 #4, 3가지 통과) | c07b49fa |
| daily-report-check | 일일보고 누락 점검 | 일일보고서 확인 | 2026-09-21 13:29 | 미확인 | cde24c45 |
| grinding-calc | 연삭 휠 Vc ↔ RPM · Q'w 계산 | D125 Vc 20 m/s RPM은? · Ø125 3,000 rpm 원주속도는? | 2026-11-16 13:09 | 2026-11-16 (카드 #5, 3가지 통과 · ② 2판 재시험) | cc368c1a |
| refine-request | 요청문 다듬기 | 요청 다듬어 줘 | 2026-11-16 08:13 | 2026-11-16 (카드 #1 ① · ③ 통과) | 3c930646 |
| python-review | 파이썬 코드 검토표(P1~P9 · W1~W8) — review-role 이 .py 때 부름 | (직접 부르지 않음) | 2026-11-20 13:34 | 2026-11-20 (카드 #8, 3가지 통과) | a81a4316 |
| review-role | 역할 검토표 적용(.py 면 python-review 연결 · 결론 블록) | 검수해 줘 | 2026-11-20 09:41 | 2026-11-20 (카드 #8, 3가지 통과) | 74005e46 |
| scheduler-diagnose | 자동화 누락 원인 진단 | 스케줄러 진단 | 2026-11-16 08:55 | 2026-11-16 (카드 #2, 3가지 통과) | 3069de6f |
| source-add | sources.md 출처 등재 | 출처 추가 | 2026-05-22 10:07 | 미확인 | f57ff65a |
| test-record | 시험 결과 표준 기록 | 테스트 결과 기록 | 2026-05-22 10:07 | 미확인 | 9322152a |
| tool-generator | 공구 도면 · 3D 생성 | 공구 만들어 줘 | 2026-11-12 14:53 | 미확인 | 739cf915 |
| wiki-lint | 위키 품질 점검 | 위키 검수 | 2026-11-16 09:29 | 2026-11-16 (카드 #3, 3가지 통과) | 5451aaa4 |
| wiki-new-page | 새 위키 페이지 생성 | ○○ 페이지 만들어줘 | 2026-11-16 10:38 | 2026-11-16 (카드 #6, 3가지 통과 · ② 1항목 미충족) | 9898bf4d |

## 2. 개정 후보 (원본을 읽으며 찾은 것 — 고치지 않았음, 승인 대기)

| 스킬 | 지금 내용 | 문제 | 근거 |
|---|---|---|---|
| scheduler-diagnose — ✅ **반영 완료 11-16** ([[테스트카드]] #2 통과 · 정상본 교체) | 0단계 휴무 확인을 `decisions.md` · `worklog.md` grep 으로 함 | 휴무 단일 소스는 `holidays.md`(CLAUDE.md §13). §13 은 이 스킬이 holidays.md 를 본다고 적혀 있으나 실제 본문은 아님 | CLAUDE.md §13 |
| wiki-lint — ✅ **반영 완료 11-16** ([[테스트카드]] #3 통과 · 3판 정상본 교체) | 실행 방법이 `mcp__workspace__bash` · `/sessions/.../` 경로 · 파일마다 Read | 옛 도구 · 경로 하드코딩(daily-report-check 가 금지한 방식). device_bash + `$HOME/mnt/cnc-wiki` 로 | daily-report-check §① |
| cnc-handoff — ✅ **반영 완료 11-16** ([[테스트카드]] #4 통과 · 정상본 교체) | 종료 안내가 `git add -A` · 커밋 전 `--check` 수동 확인 | ① add 는 실제 변경 파일만 경로로(프로젝트 메모 git-eol) ② `--check` 는 pre-commit 훅이 대신(2026-11-16 (1)) | decisions 2026-11-16 (1) |
| grinding-calc — ✅ **반영 완료 11-16** ([[테스트카드]] #5 통과 · 2판 정상본 교체 — 1판은 RPM → Vc 질문에 안 불림) | 「Vc 권장 18–25 m/s [VEN-NORTON-WINTER-2023] (제조사 기준)」 | 위키 원본은 Norton 실사용 17~22 m/s, 25 m/s 는 **사내 자체 상한** — 출처 · 신뢰도 표기가 섞임 | [[tools/wheels/index]] 113 · 115행 |
| wiki-new-page — ✅ **반영 완료 11-16** ([[테스트카드]] #6 통과 · 정상본 교체 — 남은 일: 스키마 §6-5 정리 뒤 「원본끼리 다르면」 예시 갱신) | 페이지 스키마를 본문에 통째로 적음 | 원본 [[standards/위키-페이지-스키마]] 와 두 곳 관리(review-role 원칙 「두 곳 관리 금지」) | 2026-11-10 CLAUDE.md 다이어트 |
| wiki-lint | 점검 항목 ① ~ ⑤(프론트매터 · 출처 없는 수치 · 고아 · index 미등재 · 빨간 링크) | CLAUDE.md 옛 §8-4 의 「페이지 간 가공 조건 모순」 · 「sources.md ID 미등재 인용」 두 항목이 없음 | [[standards/세션-위키-작업절차]] §8-4 (2026-11-23) |
| source-add | 섹션 위치 · APA 항목 · 프론트매터 안내 | 옛 §8-3 ② 「섹션 7 내부 위키 페이지 맵에 페이지 ↔ 출처 ID 매핑 추가」 단계 없음 | 같은 문서 §8-3 (2026-11-23) |
| wiki-new-page | 중복 확인 · 스키마 · index · log | 옛 §8-1 ① 「context.md · decisions.md 확인 → 방향 정합」 없음 · 기존 페이지 「보강」(§8-2 — updated 갱신 · log [업데이트])을 맡는 스킬이 없음 | 같은 문서 §8-1 · 8-2 (2026-11-23) |
| cnc-handoff | 전체 읽기 = decisions 최신 5건 · tasks P0 · P1 전문 | 옛 §0-A2 는 decisions · tasks 전체 — 스킬 쪽이 최신이라 문제 아님(기록만) · 경로 `C:\Users\TOOLKOREA` 는 연결 폴더로 동작(decisions 2026-11-19 (1)) | 같은 문서 §0-A2 (2026-11-23) |

## 3. 개정 절차 (13-7 을 사내에 맞춤)

1. 고치기 전에 이 폴더의 정상본을 그대로 둔다(덮어쓰지 않음 — 개정본이 통과한 뒤에 교체).
2. 바꿀 위치 · 새 규칙 · **유지할 규칙** · 기대 결과를 [[테스트카드]] 에 먼저 적는다.
3. 개정본을 저장 카드로 저장(Claude 가 propose → 한경준님 저장).
4. 새 대화에서 3가지 시험 — ① 전에 잘되던 요청 ② 바뀐 규칙 요청 ③ 범위 밖 요청(엉뚱한 스킬이 끼어들지 않는지). 못 한 시험은 「미실행」.
5. 통과 → 이 폴더 SKILL.md 교체 · 목록의 정상본 날짜 · md5 · 마지막 시험 갱신. 실패 → 이 폴더 정상본으로 되돌려 다시 저장.

- md5 는 **LF 줄바꿈 기준**이다. git 이 작업 파일을 CRLF 로 바꾼 뒤에는 `python -c "import hashlib,sys;print(hashlib.md5(open(sys.argv[1],'rb').read().replace(b'\r\n',b'\n')).hexdigest()[:8])" 파일` 처럼 LF 로 맞춰 대조한다.
- 원본 꺼내기: 세션에서 스킬을 「불러오기만」 하면 계정 저장본이 작업 공간에 내려온다 → 파일 그대로 복사(손으로 다시 치지 않음) → md5 대조.
- 공개 저장소에 올라간다(`wiki/_handoff/` 추적). 넣기 전 실명 검사는 pre-commit 훅이 한다.

## 4. 외부 스킬 · 플러그인 검토 이력 (2026-11-23 신설)

> 인스타 · 블로그 · 지인 추천으로 들어온 외부 스킬 · 플러그인 · 프롬프트를 한 번 본 기록. 같은 도구가 다시 오면 이 표부터 본다.
> 판정은 넷 중 하나 — 도입 · 일부 이식 · 보류 · 제외. 근거가 decisions 에 있으면 번호를 적고, 없으면 검토한 곳(챗 · Cowork)과 날짜.

### 4-1. 검토 순서

1. 같은 도구 기록부터 찾는다 — 이 표 → `decisions.md` · `decisions-archive/` 에서 도구 이름 grep → 관련 페이지(예: [[standards/문서작성-AI티-점검표]] §4-A). 있으면 다시 검토하지 않고 그 판정 · 근거를 답한다. 「다시 볼 조건」에 해당할 때만 재검토
2. 새 도구만 아래를 본다
   - 원본 저장소를 직접 찾는다. 게시물의 「댓글 달면 DM 으로 링크」는 받지 않는다(같은 이름 · 복사본이 많음)
   - 기존 사내 스킬과 겹치는가 · 부르는 말이 경쟁하는가
   - Windows · Cowork 에서 도는가(Claude Code 전용 · Mac 전용 여부)
   - 사내 양식(개조식 보고서 · 코고툴 디자인 시스템) · 출처 원칙(5순위 단독 근거 금지)과 충돌하는가
   - 라이선스 · 외부 접속 · 훅 자동 실행 · 파일 자동 생성
   - 실행 스크립트가 든 외부 스킬은 들이기 전에(일부 이식 포함) 챗 샌드박스에서 `skillspector scan <원본 저장소> --no-llm` 을 돌린다. 「DO_NOT_INSTALL」이 나오면 지적된 줄을 직접 읽어 진짜 위험인지 오탐인지 가르고, 결과를 이력 표 근거 칸에 적는다(정적 검사만으로 판정하지 않는다) (11-23 추가)
3. 판정을 이 표에 한 줄 더한다. 조건 · 안전 · 대외 · 돈 · 규칙에 걸리는 것만 decisions 에 올린다(CLAUDE.md §5-A)

### 4-2. 이력

| 도구 | 원본 | 처음 본 곳 | 판정 | 근거 | 다시 볼 조건 |
|---|---|---|---|---|---|
| everything-claude-code (ECC) | github.com/affaan-m/ECC (MIT) | 인스타 2건 (11-19 · 11-20) | 일부 이식 — python-reviewer → python-review | decisions 2026-11-20 (3) · 테스트카드 #8 | 통째 설치는 안 함 — Claude Code 명령줄 대상, 스킬 300개 넘게 깔려 부르는 말이 겹침, 훅 자동 실행 |
| im-not-ai (humanize-korean) | github.com/epoko77-ai/im-not-ai (MIT) | 챗 10-28 · 인스타 Humanizer 대안으로 11-19 | 보류 — 어휘 사전만 점검기 [참고] | decisions 2026-11-20 (2) ② · (4) · 점검표 §4-A | 보고서 장르에서 개조식을 유지하고 docx 를 직접 다룰 때 |
| Humanizer | github.com/blader/humanizer | 인스타 (지식채널 2건) | 제외 — 영어 글 기준 | 원 출처(위키백과 「Signs of AI writing」)는 점검표 §1 [IND-WIKI-AISIGNS] 에 이미 있음 | — |
| unslop | 같은 이름 여러 개: heydamir/unslop(화면) · 0design/unslop-skill(화면 감사, 외부 서버 규칙) · theclaymethod/unslop(글) | 인스타 (지식채널 11-16) | 제외 — 화면용은 아래 디자인 도구와 같고, 글쓰기용은 점검표와 겹침 | 챗 11-23 | — |
| Hallmark · Taste Skill · UI/UX Pro Max · Impeccable | Nutlope/hallmark · Leonxlnx/taste-skill · nextlevelbuilder/ui-ux-pro-max-skill · pbakaus/impeccable | 인스타 (지식채널) | 보류 — 코고툴 디자인 시스템이 기본인데 도구가 스스로 테마를 고름 · 네 개가 같은 요청에 겹침 | decisions 2026-11-20 (2) ① (배치 규칙만 반영) · 챗 11-19 | 마이다스 몰 화면에 디자인 감사가 따로 필요해질 때 Impeccable 의 감사 기능만 |
| Diagram Design | github.com/cathrynlavery/diagram-design (MIT) | 인스타 (지식채널 2건) | 보류 | 챗 11-19 | 위키 · 보고서 도식이 잦아질 때 (저장소에 Cowork 설치법 있음) |
| Ponytail | 저장소 확인 안 함 | 인스타 (지식채널 2건) | 제외 — 코드 줄이기는 python-review · code-review 와 겹침 | 챗 11-19 | — |
| Caveman | github.com/JuliusBrussee/caveman | 인스타 (지식채널 11-16) | 제외 — 출력을 축약 말투로 줄이고 매 턴 입력이 늘어남, CLAUDE.md 같은 메모 파일을 축약체로 다시 씀 | 챗 11-23 | — |
| Scrapling | github.com/D4Vinci/Scrapling | 인스타 (지식채널 2건) | 제외 — 강점이 봇 차단 우회라 남의 사이트에는 약관 문제, 사내 포털 알림은 지금 방식으로 충분 | 챗 11-19 | — |
| Last 30 Days | github.com/mvanhorn/last30days-skill | 인스타 (지식채널 2건) | 제외 — Reddit · X 등 최근 여론 요약, 출처 5순위 | 챗 11-19 | — |
| REA | morluto/rea | 인스타 (지식채널) | 제외 — 분석이 Mac 에서 돎, 상용 소프트웨어(ANCA 포함) 리버스 엔지니어링은 라이선스 위반 소지 | 챗 11-19 | — |
| book-to-skill | github.com/virgiliojr94/book-to-skill | 인스타 (지식채널 11-16) | 보류 — 책을 요약 스킬로 바꾸는 과정에서 수치 · 쪽수 출처가 끊김 | 챗 11-23 | 매뉴얼 「어느 장에 뭐가 있나」 찾기 용도가 필요할 때 |
| Superpowers | github.com/obra/superpowers (MIT, Anthropic 공식 플러그인 마켓플레이스) | 인스타 (지식채널 11-16) | 보류 — 테스트 주도 개발 바탕의 큰 개발 방법론, 사내 스크립트에는 무거움 · 「검수해 줘」와 겹침 | 챗 11-23 | 사내 개발 규모가 커질 때 |
| 화면 배치 이름 9종 | 게시물 (uxwoodytips) | 인스타 | 반영 — 디자인 시스템 「화면 배치」 5줄 | decisions 2026-11-20 (2) ① | — |
| 학습 프롬프트 6개 | 게시물 (alligator.9958261) | 인스타 | 일부 — 3번 시험 · 6번 파인만만 신입 교육에 | 챗 11-20 · tasks P3 「신입 교육 — 위키 페이지로 시험 문제 내기」 | — |
| 질문 프롬프트 10가지 | 게시물 (promppy_com, 캡션만) | 인스타 | 제외 — 「요청 다듬어 줘」(refine-request) · 「검수해 줘」와 같은 내용 | 챗 11-20 | — |
| security-audit-skill | github.com/cloudflare/security-audit-skill (Cloudflare 공식, MIT) | 인스타 (_choosit 11-23) | 보류 — 찾은 구멍을 다른 에이전트가 반박해 살아남은 것만 남기는 방식은 python-review 의 「오탐 반증」과 같은 생각. 병렬 하위 에이전트를 많이 쓰는 무거운 감사, Node.js(skills CLI) 필요, 사내 공개 코드는 정적 페이지 · 접수 폼뿐 | 챗 11-23 | 외부에 공개되는 사내 코드를 넘기기 전(예: 재연마 견적 계산기 꾸러미, decisions 2026-11-18 (3)) 1회 |
| claude-seo | github.com/AgriciDaniel/claude-seo (MIT) — 같은 이름 복사본 여러 개 | 인스타 (_choosit 11-23) | 보류 — 고객에게 안내 · 운영하는 공개 사이트가 아직 없음(GitHub Pages 포털은 올라가 있으나 안내 전 · 코고툴 이름 · 문구 보류, decisions-archive 2026-10-12 (4)), 마이다스 몰은 개발사 소관 | 챗 11-23 | 새 고객용 사이트를 공개 운영할 때 |
| agent-browser | 확인 안 함 | 인스타 (_choosit 11-23) | 제외 — Claude in Chrome 이 이미 연결돼 있음 | 챗 11-23 | — |
| t3code | 확인 안 함 | 인스타 (_choosit 11-23) | 제외 — Claude 앱에서 Cowork · Claude Code 를 휴대폰으로 이어 볼 수 있음 | 챗 11-23 | — |
| Claude-BugHunter | 확인 안 함 | 인스타 (_choosit 11-23) | 제외 — 공격 기법 학습 도구. 사내 원칙상 바깥에서 사내 시스템 시험 호출 금지(tasks-archive 「ERP 서비스 외부 접속」 ⚠️) | 챗 11-23 | — |
| ffmpeg-skill | 확인 안 함 | 인스타 (_choosit 11-23) | 제외 — 영상 편집 업무 없음, 필요하면 말로 시켜 ffmpeg 명령을 짜는 것은 지금도 됨 | 챗 11-23 | — |
| hyperframes · claude-animated-shorts · line-art-animation | 확인 안 함 | 인스타 (_choosit 11-23) | 제외 — 영상 · 애니메이션 제작은 업무 범위 밖 | 챗 11-23 | — |
| instagram-agent-skill | 확인 안 함 | 인스타 (_choosit 11-23) | 제외 — 업무 무관(릴스 문구 점수) | 챗 11-23 | — |
| Claude Code 폴더 구조 (CLAUDE.md · rules · skills · agents · hooks) | 게시물 (dannyoff.ai, 원 구성 shiva.bytes) · 공식 문서 code.claude.com/docs/en/memory | 인스타 (11-23) | 제외(11-23 시험) — Cowork 에서 경로 규칙은 안 켜지고, 무조건 규칙은 CLAUDE.md 와 같이 폴더 첫 접근 때 들어와 맥락이 안 줆. 나머지는 이미 있음(CLAUDE.md · 계정 스킬 · 검수 스킬 · git pre-commit 훅). ~~일부 — `.claude/rules/`(경로 지정 규칙)만 후보~~(챗 11-23) | 챗 11-23 · Cowork 시험 11-23(worklog 2026-11-23 #5 · #7) | Cowork 가 경로 규칙을 지원한다고 공지될 때 · Claude Code 전용 작업이 늘 때 |
| SkillSpector | github.com/NVIDIA/SkillSpector (NVIDIA, Apache-2.0, v2.12.0 · 패턴 71개 · 17분류) — 같은 이름 복사본 있음 | 인스타 (hongik.man 11-23) | 도입 — 검토 도구로만. 회사 PC 에 설치하지 않고 챗 샌드박스에서 정적 검사(`--no-llm`)를 돌린다 | 챗 11-23 시험(표 아래 ※ SkillSpector 시험) | — |
| Modern Web Guidance | github.com/GoogleChrome/modern-web-guidance (Chrome · Edge · Firefox 팀, 1.0 = 2026-11-10 발표 · 11-13 정리 글) | 인스타 (aiscene.kr 11-24) | 보류 — 코딩 에이전트가 옛 웹 방식 대신 요즘 HTML · CSS · 웹 API 를 쓰게 하는 스킬 + CLI(안내서 200개 넘음, 브라우저 호환 정보 포함). 지금 진행 중인 사내 웹 코드 작업이 없고, 실행 CLI(npx)가 딸려 있음 | 챗 11-24 | 웹 코드(재연마 견적 계산기 꾸러미 · 포털 템플릿 · B2B 사이트)를 새로 짜거나 크게 고칠 때 — 들이기 전 SkillSpector 검사 |
| Chrome DevTools MCP (Chrome DevTools for agents) | github.com/ChromeDevTools/chrome-devtools-mcp (Chrome 팀) | 인스타 (aiscene.kr 11-24) | 보류 — 에이전트가 크롬으로 페이지 성능 · 오류를 직접 재는 도구, Modern Web Guidance 와 짝. 지금 진단할 웹 성능 과제가 없고 Claude in Chrome 이 연결돼 있음 | 챗 11-24 | 위 행과 같음, 또는 사이트가 느리거나 오류가 난다는 보고가 있을 때 |
| Univer | github.com/dream-num/univer (Apache-2.0) | 인스타 (aiscene.kr 11-24) | 제외 — 웹 서비스 안에 표 · 문서 편집기를 넣는 개발 부품. 사내에 그런 웹 서비스 개발이 없음(ERP 뷰어는 파이썬 exe, 마이다스 몰은 개발사 소관) | 챗 11-24 | 사내에서 웹 서비스를 직접 만들 때 |
| Open Code Review (알리바바) | github.com/alibaba/open-code-review (Apache-2.0) | 인스타 (aiscene.kr 11-24) | 제외 — AI 코드 검사, 「검수해 줘」(code-review · python-review)와 겹침 | 챗 11-24 | — |
| Plannotator | github.com/backnotprop/plannotator | 인스타 (aiscene.kr 11-24) | 제외 — AI 계획서에 메모를 달아 돌려보내는 검토 창. 사내는 계획을 대화에서 추천안 → 「승인」으로 처리 | 챗 11-24 | — |
| AG-UI | github.com/ag-ui-protocol/ag-ui | 인스타 (aiscene.kr 11-24) | 제외 — 에이전트를 웹 · 휴대폰 · 슬랙 화면에 붙이는 연결 규격(개발 인프라) | 챗 11-24 | — |
| Astryx 아스트릭스(메타 화면 부품 세트, 베타) | astryx.atmeta.com (Meta, MIT) | 인스타 (aiscene.kr 11-24) | 제외 — 화면 부품은 코고툴 디자인 시스템이 기본 · 아직 베타 | 챗 11-24 | — |
| Claude 트레이딩 스킬 | 확인 안 함 | 인스타 (aiscene.kr 11-24) | 제외 — 업무 무관(개인 투자용) | 챗 11-24 | — |
| 러스트 애니링(가칭 — 영문 이름 확인 안 함) | 확인 안 함 | 인스타 (aiscene.kr 11-24) | 제외 — 느린 프로그램을 Rust 로 조금씩 옮기는 도구, 사내 필요 없음 · 생긴 지 6일 | 챗 11-24 | — |

※ SkillSpector 시험(챗 샌드박스 2026-11-23, v2.12.0, `--no-llm`): 악성 견본(챗이 만든 것 — 숨은 주석 지시 + 환경변수 중 KEY · TOKEN 외부 전송) 위험 100 · DO_NOT_INSTALL · HIGH 6 → 숨은 지시 · 유출 모두 잡음 / python-review 1차안(11-19 챗) 위험 7 · SAFE · MEDIUM 1 → 정상 / im-not-ai DO_NOT_INSTALL · HIGH 9(캐시 파일 제외) → 시험 · 설치 스크립트와 git 훅의 명령 실행이 걸림, 악성 아님(오탐) / cloudflare/security-audit-skill 위험 86 · DO_NOT_INSTALL · HIGH 6 → 공격 유형을 설명하는 보안 문서가 걸림, 오탐. ⇒ 명백한 악성은 잡지만 정상 스킬도 「설치 금지」로 자주 나와 지적 줄 판독까지 해야 판정. LLM 분석 단계는 외부 API 키가 필요해 쓰지 않음. 저장소 메타(라이선스 · 버전 · 패턴 수 · `--no-llm` 옵션)는 Cowork 가 원본 저장소에서 확인(11-23), 시험 재현은 안 함

※ 게시물에 함께 붙은 주장 중 확인한 것: ECC 해커톤 우승은 Anthropic · Forum Ventures 공동 주최(2025-09), 「하버드 연구」는 맞춤 제작 AI 튜터 · 물리 2개 주제 · 단기 결과(Kestin 외, Scientific Reports 2025), 「20시간이면 충분」은 연구가 아니라 Josh Kaufman 의 책 주장. 위키 근거로 쓰지 않는다.
