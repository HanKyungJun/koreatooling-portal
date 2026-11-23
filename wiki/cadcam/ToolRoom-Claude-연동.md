---
type: cadcam
tags: [ANCA, ToolRoom, iGrind, MCP, Claude, 공구파일, tom, 휠팩, wpk, 자동화]
sources:
  - "[VEN-ANTHROPIC-CONNECTOR-UNLISTED]"
  - "[VEN-MCP-LOCAL-SERVERS]"
updated: 2026-11-23
---

# ANCA ToolRoom – Claude 연동 (로컬 MCP)

> 요약: 컴퓨터2 의 ANCA ToolRoom 공구 파일(.tom) · 휠팩(.wpk)을 Claude 가 읽어 요약 · 비교하고, 시험용 새 공구 파일을 만든다. 연동 서버는 Claude 설정 파일에 등록해 쓴다. **생성한 공구 파일은 시험용 — 양산 적용 전 테스트 → 측정 → 검증 필수.** 근거: decisions 2026-11-23 (3) ~ (6).

⚠️ 주의: 사내 ToolRoom 공구 라이브러리(.tom)는 검증된 조건 모음이 아니다. 공구 요약 · 비교 · 파라미터 조회 결과를 가공 · 연삭 조건의 근거로 인용하지 않는다.

## 1. 구성 (2026-11-23 동작 확인)

| 항목 | 값 | 신뢰도 |
|------|-----|--------|
| 설치 PC | 컴퓨터2 (ToolRoom 설치 PC, cnc-wiki 없음) | 실측 검증 |
| 연동 서버 | `Claude outputs\ToolRoom연동\server\node.exe` + `index.js`, 서버 이름 `anca-toolroom`, v0.3.0 | 실측 검증 (컴퓨터2 Cowork) |
| 등록 방식 | `claude_desktop_config.json`(Windows 기본 위치 `%APPDATA%\Claude\`)의 `mcpServers` 에 등록 | 제조사 기준 [VEN-MCP-LOCAL-SERVERS] |
| 인식 결과 | 공구 183개 · 휠팩 36개 | 실측 검증 |
| ToolRoom 빌드 | 9.22 patch 60.15 / Build 682 | 실측 검증 — RN 표기와의 관계는 §7 |
| 예비 | `.mcpb` 확장 파일 — 회사 계정에서 확장 설치가 허용될 때만 | decisions 2026-11-23 (6) |

## 2. 왜 설정 파일 등록인가 ★★★

- 회사 계정은 데스크톱 확장 설치 메뉴가 꺼져 있다 — 설정에 「확장 프로그램」이 없고 「커스텀 커넥터 추가」가 비활성(2026-11-23 컴퓨터2 확인).
- Claude 공식 문서: 조직이 확장을 끄면 설정에 Extensions 가 나타나지 않는다(*When extensions are turned off, Extensions doesn't appear in settings*) [VEN-ANTHROPIC-CONNECTOR-UNLISTED] — 제조사 기준.
- 그래서 확장(.mcpb) 대신 로컬 MCP 서버를 설정 파일에 직접 등록했다 [VEN-MCP-LOCAL-SERVERS].

## 3. 기능 (v0.3.0)

| 기능 | 내용 | 비고 |
|------|------|------|
| 공구 요약 · 비교 · 파라미터 조회 | .tom 파일 읽기 | ToolRoom 원본은 읽기만 |
| 휠 원주속도 점검 | 휠 지름 · RPM 으로 Vc 계산 | 기준은 [[tools/wheels/index]] 「원주속도 기준」 |
| ToolRoom 화면 보기 | 캡처만(조작 없음) | |
| 새 공구 파일 만들기 | 기존 공구를 바탕으로 값 일부 변경 | 규칙 §5 · 못 바꾸는 값 있음 |

⚠️ 경고: 휠 원주속도 점검에서 Vc > 30 m/s 가 나오면 레진 본드 한계를 넘을 수 있다 — 휠 제조사 최고 사용 속도부터 확인한다.

## 4. 휠 번호 읽는 법 ★★★ (실측 검증)

| 구분 | 순서 |
|------|------|
| 휠팩(.wpk) 파일 안 나열 | 스핀들 쪽부터 |
| ToolRoom · iGrind 화면 번호 | **아버 끝(스핀들에서 먼 쪽)부터 1번** — 파일 순서의 역순 |
| 화면 표기 예 | `w3 p1` = 3번 휠 · 1번 팩 |

- 계기: 현장 지적 — 4F CO 의 「7. Endface Gash」 · 「9. OD Corner End Finishing」 휠이 반대로 나옴(v0.1.0).
- 대조: 사내 공구 파일 41개의 뒷면(back) 사용 70건 — 파일 순서로 번호를 매기면 49건이 뒷면 연삭면이 없는 11V9 휠(`Qualify_Back = false`)에 걸리고, 역순이면 0건. 역순 번호가 iGrind 화면의 9개 오퍼레이션 휠 · 팩 번호와 일치.
- v0.1.0 의 휠 대응 결과는 폐기, v0.1.1 부터 수정(decisions 2026-11-23 (5)).

## 5. 공구 파일 만들기 규칙

### 5-1. 저장 위치 (decisions 2026-11-23 (3))

- 새 공구 파일은 `toolroom\user\tools\_Claude\` 에만 저장한다. 같은 이름이 있으면 만들지 않는다(덮어쓰기 없음).
- ToolRoom 원본 공구 파일은 읽기만 한다.
- 이 폴더를 고른 이유: 경로가 짧고(P: 기준 약 41 byte) 사내 공구 라이브러리와 섞이지 않음.

### 5-2. 전체 경로 100 byte 이하 (decisions 2026-11-23 (4)) ★★★

- 증상: iGrind 경고 「PPI Execution Error — p:/3dx/tmp/sim/igrind1/map1/map1.pp line 182, String too long to fit into variable」 → Invalid Tool.
- 원인: iGrind 가 만드는 내부 프로그램에서 `tom_filename` 에 .tom 전체 경로를 넣다가 길이 초과.

| 전체 경로 길이 | 결과 | 신뢰도 |
|------|------|------|
| 64 byte (106 byte 와 같은 내용) | 정상 | 실측 검증 |
| 99 · 100 byte | 정상 | 실측 검증 |
| 106 byte | Invalid Tool | 실측 검증 |

- 한글 1자 = 2 byte 로 센다. 영문 이름 + 짧은 폴더를 쓰고, 100 byte 를 넘으면 만들지 않는다. 사람이 저장할 때도 깊은 한글 폴더 · 긴 파일명은 피한다.
- 정확한 한계는 100 ~ 105 byte 사이로 미확정 → 100 byte 로 보수 적용.

### 5-3. 생성 기능으로 못 바꾸는 값 (2026-11-23 기준)

- 0(ZERO) 저장값 · 함수형 값 · 선택형 값.

### 5-4. 첫 생성본 — `4FCO_R05_T1.tom`

| 항목 | 값 | 신뢰도 |
|------|-----|--------|
| 바탕 | 4F CO | — |
| 바꾼 값 | 코너 R 0.5 mm · 외경 1차 여유각 12° · 「7. Endface Gash」 이송 120 mm/min | 추정값(시험용 입력값) |
| 시뮬레이션 | iGrind Simulation Complete (2026-11-23 11:27 KST) | 실측 검증 |
| 실가공 | 안 함 | 확인 필요 |

⚠️ 주의: 시뮬레이션 완료는 가공 조건 검증이 아니다. 실가공 전 테스트 → 측정 → 검증([[standards/테스트-기록-표준]]).

## 6. 갱신 · 문제 해결

- 서버 갱신: `server\index.js` 교체 → Claude 앱을 **완전히 종료**하고 다시 실행(창만 닫으면 설정을 다시 읽지 않음) [VEN-MCP-LOCAL-SERVERS].
- 연결이 안 될 때: 설정 파일 문법 · 경로가 절대 경로인지 확인 → 로그 `%APPDATA%\Claude\logs\mcp.log`(연결 전반) · `mcp-server-anca-toolroom.log`(서버 출력) [VEN-MCP-LOCAL-SERVERS].

| 버전 | 바뀐 것 | 날짜 |
|------|------|------|
| v0.1.0 | 첫 판 — 휠 대응을 파일 순서로 매김(결과 폐기) | 2026-11-23 |
| v0.1.1 | 휠 번호를 아버 끝부터(역순)로 수정 | 2026-11-23 |
| v0.3.0 | 설정 파일 등록으로 동작 확인(공구 183 · 휠팩 36) | 2026-11-23 |

## 7. 확인 필요

- .tom 경로 길이 한계의 정확한 값(100 ~ 105 byte 사이).
- ToolRoom 버전 표기: 컴퓨터2 「9.22 patch 60.15 / Build 682」 ↔ 위키의 장비 iGrind 「RN32.1-1」([[cadcam/원통연삭-넥-시험-AFCY-D3-2026-10-20]]) · 「사내 ToolRoom은 RN35」([[projects/ANCA-장비-투자-생산력강화-검토]]) — 같은 버전을 다르게 적은 것인지, PC마다 다른 것인지 미확인.
- 생성 공구 `4FCO_R05_T1.tom` 실가공 결과.

## 8. 변경 이력

| 날짜 | 변경 | 사유 | 양산 적용 |
|------|------|------|------|
| 2026-11-23 | 신규 작성 | decisions 2026-11-23 (3) ~ (6) 을 위키 페이지로 | 해당 없음(생성 파일은 시험용) |

## 9. 관련 페이지

- [[cadcam/CAD-3D-프로그램-역할-정의]] — Claude 연결 프로그램 역할(연삭 원본은 ANCA ToolRoom)
- [[cadcam/Blender-3D-시각화-MCP-연동]] — 같은 방식(로컬 MCP)의 다른 연동
- [[cadcam/재연마-프로그램-워크플로우]] — iGrind/ToolRoom 작업 흐름
- [[cadcam/iGrind-원통연삭-넥가공-2JJCR040010200]] — iGrind 화면의 Pack / Wheel 표기 사례
- [[machines/anca-cnc-tool-grinder]] — 장비
- [[tools/wheels/index]] — 휠 원주속도 기준
