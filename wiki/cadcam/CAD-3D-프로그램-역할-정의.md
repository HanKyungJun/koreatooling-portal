---
type: cadcam
software: "CADCraft · SolidCraft · FreeCAD · Blender"
tags: [CAD, 3D, CAM, MCP, CADCraft, SolidCraft, FreeCAD, Blender, 역할정의, STEP]
sources:
  - "[VEN-SOLIDCRAFT-MCP]"
  - "[VEN-FREECAD-CAM-SRC]"
  - "[VEN-BLENDER-LAB-MCP]"
  - "[SYS-COWORK]"
updated: 2026-11-12
---

# CAD · 3D 프로그램 역할 정의 (CADCraft · SolidCraft · FreeCAD · Blender)

> 요약: Claude 와 연결된 프로그램 4개에 **한 가지 일씩** 맡긴다. 2D 도면 = CADCraft, 3D 솔리드 = SolidCraft, MCT CAM(G코드) = FreeCAD, 그림 · 영상 = Blender. 연삭 프로그램 · 공구 설계의 원본은 계속 **ANCA ToolRoom** 이며, 이 4개는 도면 · 시각화 · MCT 보조용이다. 근거: decisions 2026-11-12 (2).

## 1. 역할

| 프로그램 | 맡는 일 | 원본 파일 | 맡기지 않는 일 | 연결일 |
|---|---|---|---|---|
| CADCraft | 2D 치수 도면(작업도면 · CAM용 DXF 사본) | DXF | 3D · G코드 · 원본 DWG 덮어쓰기 | 2026-10-14 |
| SolidCraft | 3D 솔리드(공구 외형 · 소재 · 지그), 치수 변수(d · L 등), 부피 · 질량 측정 | `.sc` · STEP | G코드 · 렌더 영상 · CAM 윤곽 원본(§3) | 2026-11-12 |
| FreeCAD | MCT CAM(G코드). 입력 = CADCraft DXF · FreeCAD 직접 모델 · **변환한** SolidCraft STEP | `.FCStd` · `.nc` | 3D 모델 원본 만들기 | 2026-10-23 |
| Blender | 그림 · 영상(렌더 · 가공 영상 · 발표). SolidCraft 에서 OBJ · glTF 로 받음 | `.blend` · png · mp4 | 치수 · 조건 근거 · G코드 검증 | 2026-10-22 |

파일 흐름: CADCraft(2D) → SolidCraft(3D) → FreeCAD(G코드) 또는 Blender(그림).

쉬운 말로 시키면 Claude 가 프로그램을 고른다: 「도면 그려 줘」→ CADCraft · 「3D 만들어 줘」→ SolidCraft · 「G코드 만들어 줘」→ FreeCAD · 「그림 · 영상 만들어 줘」→ Blender.

## 2. 연결 설정

| 프로그램 | 연결 방식 | 설정 |
|---|---|---|
| SolidCraft | Claude 설정 `mcpServers.solidcraft` — 화면 없이 실행(headless) | `C:\Program Files\SolidCraft\solidcraft-cli.exe mcp --allow-path <cnc-wiki>\outputs\02_도면_3D_CAM` — 파일 읽기 · 쓰기는 이 폴더로 제한 [VEN-SOLIDCRAFT-MCP] |
| CADCraft | `mcpServers.cadcraft` — 화면 없이 실행 | `outputs/02_도면_3D_CAM/add_cadcraft_mcp.py` |
| FreeCAD | `mcpServers.freecad` — **FreeCAD 창을 켜 둬야 함**(RPC 9875 자동 시작) | `outputs/02_도면_3D_CAM/add_freecad_mcp.py` |
| Blender | 확장 프로그램 — **Blender 창을 켜 둬야 함** | [[cadcam/Blender-3D-시각화-MCP-연동]] |

- Claude 설정 파일 위치(이 PC, 실측 2026-11-12): `%LOCALAPPDATA%\Claude-Data\claude_pzs8sxrjxfjjc\claude_desktop_config.json`. `%APPDATA%\Claude\` 에는 없다. `...\Claude-3p\` 사본은 쓰이지 않는다(비어 있음, 2026-04-15 수정).
- SolidCraft 설정 스크립트: `outputs/02_도면_3D_CAM/add_solidcraft_mcp.py` (`--config <경로>` · `--exe <경로>` · `--watch` = 앱 화면 연결 방식, 앱을 `--control 7878` 로 켜야 함). 실행 전 설정 파일 백업을 만든다.
- 화면 방식 · 백그라운드 방식은 SolidCraft 2026-11-12 기준 백그라운드만 씀(앱 화면에는 작업이 안 보임 — 결과는 파일로 확인).

## 3. SolidCraft 시험 결과 (2026-11-12)

### 3-1. 모델링

| 시험 | 계산값 | 측정값 | 판정 | 신뢰도 |
|---|---|---|---|---|
| 원통 D10 × 75 mm | V = π × 5² × 75 = 5,890.49 mm³ | 5,889.51 mm³ (−0.017 %) | 합격 | 실측 검증 |
| 나선 날 시험 모델(아래 조건) | 5,523.88 mm³ | SolidCraft 5,523.22 (−0.012 %) · FreeCAD 5,522.40 (−0.027 %) | 합격 | 실측 검증 |
| 나선 방향 | 오른나선 | z = 6 mm 좌 · 우 시험 상자 깎기 → 오른나선 쪽 빈 홈 | 합격 | 실측 검증 |
| 구멍 판 30 × 20 × 10 mm · Ø6 관통 | 6,000 − π × 3² × 10 = 5,717.26 mm³ | 5,717.30 mm³ | 합격 | 실측 검증 |

- 나선 날 시험 모델 조건(**모양 확인용 — 제품 설계값 아님, 추정값**): D = d = 10 mm · 2날 · 헬릭스 30° · 날장 Lc 25 mm · 전장 75 mm · 심압 Ø6 mm(60 %) · 홈 단면 R3.5 원호.
- 만드는 법: 홈 단면 스케치를 공구 축 직선을 따라 **비틀며 쓸어 깎기**(`solid.sweep` · `twist` · `operation: cut`). 리드 = π × D ÷ tan β = 31.416 ÷ 0.57735 = 54.41 mm. 쓸어 간 길이 26 mm(끝 1 mm 바깥부터) → 비틀림 = 360° × 26 ÷ 54.41 = 172.01°. 역산 tan β = π × 10 × 172.01 ÷ (360 × 26) = 0.57735 → 30.0°. `twist` 양수 = 오른나선(실측).
- 한계: 날 끝맺음(홈이 빠지는 부분) · 경사각 · 여유각 · 끝날 · 갭 없음. **외형 확인 · 시각화용**이고, 공구 형상 기준은 ANCA ToolRoom.

### 3-2. STEP 을 FreeCAD 1.1.4 에서 쓸 때

SolidCraft STEP 은 원을 **반원 자유곡선(B-spline) 2개**로 저장한다. 날 홈을 쓸어 깎은 모델은 외경 면 전체(생크 포함)도 자유곡면이 된다(원통만 있는 모델의 외경은 원통면). [VEN-FREECAD-CAM-SRC]

| 항목 | SolidCraft 원본 STEP | 변환 후(§3-3) | 비교용(FreeCAD 직접 모델) | 신뢰도 |
|---|---|---|---|---|
| CAM 윤곽 가공 원호 G2/G3 | 나옴 — 원호 맞춤(`FitArcs` 기본 켜짐)이 원으로 되돌림 | 나옴 | 나옴 | 실측 검증 |
| 외곽 윤곽 경로 | 비교용과 0.001 mm 이내 같음(65줄) | 같음 | — | 실측 검증 |
| 드릴 작업 구멍 자동 찾기 | **0개** — 구멍 원통 면 모서리 5개(FreeCAD 는 원 2 + 이음선 1 = 3개만 인정) | 1개 | 1개 | 실측 검증 |
| 측정 기능 반지름(모서리 클릭) | **0 mm** | 3.000 mm | 3.000 mm | 실측 검증 |
| 윤곽 가공 「둥근 구멍 제외」(`processCircles` 기본 꺼짐) | **구멍까지 깎음**(G3 15블록) | 건너뜀 | 건너뜀 | 실측 검증 |

- 구멍 윤곽 반지름 R 1.997 mm(기대 3 − 1 = 2.000) — 비교용도 1.9969 mm 라 FreeCAD 계산 정밀도(Accuracy 0.01 mm) 탓이다. 실측 검증.
- `Path.fromShapes` 를 직접 부르면 원호 맞춤을 건너뛰어 G1 60줄(현 오차 최대 0.012 mm)이 된다. 실제 CAM 작업 경로와 다르니 판단 근거로 쓰지 않는다.

### 3-3. 변환 스크립트 `sc_step_canon.py`

- 위치: `outputs/02_도면_3D_CAM/스크립트/sc_step_canon.py`. FreeCAD 안에서 실행: `exec(open(r"<경로>").read()); canon_step(r"입력.step", r"출력.step")`
- 하는 일: 자유곡선 원 → 진짜 원, 구멍 · 보스 원통 면 다시 만들기(모서리 3개). 결과가 정상 솔리드가 아니거나 부피가 0.001 % 넘게 바뀌면 **파일을 쓰지 않고 멈춘다**.
- 범위: 평면 + 온전한 원통만. 필렛 · 부분 원통 · 자유곡면(나선 날)은 처리하지 않고 멈춘다(나선 날 STEP 으로 확인).
- 시험: 구멍 판 → 원 모서리 0 → 2개 · 드릴 구멍 1개 · 반지름 3.000 mm · 부피 5,717.257 mm³ 그대로. 실측 검증.

### 3-4. 사내 포스트 출력 시험

변환한 구멍 판 → FreeCAD 윤곽 가공(외곽 + 구멍, Ø2 엔드밀, 깊이 10 mm, 2 mm 씩) → `qp2040_post.py` → `outputs/02_도면_3D_CAM/O9101_SolidCraft변환_포스트시험_시험전용_20261112.nc`(122줄).

| 항목 | 결과 | 판정 |
|---|---|---|
| 원호 | G2 25블록(R 1.000 mm) · G3 15블록(R 1.997 mm) · 시작/끝 반지름 차 최대 0.0002 mm | 합격 |
| 매크로 변수 `#` | 0 | 합격 |
| 보정 · 끝맺음 | `G90 G43 Z20. H01` · `M30` · `%` | 합격 |

⚠️ 주의: O9101 은 **포스트 출력 확인용**이다(S8000 · F300 · F100 은 임의 시험값, 구멍 윤곽 수직 진입). 장비에 넣지 않는다.

## 4. 주의사항

1. ⚠️ 주의: **SolidCraft STEP 을 FreeCAD CAM 에 넣기 전에는 반드시 `sc_step_canon.py` 로 변환한다.** 그대로 넣으면 드릴로 뚫을 구멍을 엔드밀 윤곽 가공이 깎는다(§3-2).
2. 나선 날 등 자유곡면 모델은 변환이 안 된다 → CAM 원본으로 쓰지 않는다. 치수는 SolidCraft 측정값 · 도면 값으로 확인한다(FreeCAD 에서 클릭 측정 불가).
3. ⚠️ 주의: FreeCAD 스크립트로 이송을 넣을 때는 **단위를 붙인다**(`"300 mm/min"`). 숫자만 넣으면 mm/s 로 읽혀 F18000 이 된다(2026-11-12 실측).
4. FreeCAD 로 만든 G코드는 CAMotics · 공운전 확인 전 장비 입력 금지(decisions 2026-10-23).
5. FreeCAD 는 한글 경로 DXF 가져오기가 아무 말 없이 0개 → 영문 임시 경로로 복사해서 연다(06_FreeCAD_CAM README §7-4). 변환 스크립트도 `%TEMP%` 를 거친다.
6. SolidCraft Windows 설치본은 코드 서명 없음(설치 시 SmartScreen 경고) · 2026-10 공개 · MIT/Apache-2.0 [VEN-SOLIDCRAFT-MCP].
7. ⚠️ 주의: SolidCraft 화면 없는 방식은 **한 작업이 약 90 s 를 넘으면 서버가 다시 시작되어 저장 안 한 작업이 사라진다**(2026-11-12 실측: D6 코너R 4날 나선 홈 — 50 mm 몸체에 홈 4개 순서대로 깎기 39 → 90 s → 3 · 4번째 및 코너 R 회전 깎기에서 끊김, 오류 보고 0건). 대처: ① 단계마다 `.sc` 저장 ② 날부만 짧은 몸체(코너 R 포함 회전체 z 0 ~ 9)로 만들어 홈을 하나씩 깎기(6.5 · 17.8 · 25.6 · 22.2 s) ③ 넥 · 생크는 별도 몸체로 두기(합치기도 시간 초과 — STEP 은 솔리드 2개). 부피는 계산값과 −0.015 % (SMP-02).

## 5. 시험 파일 (`outputs/02_도면_3D_CAM/`, 2026-11-12)

- `solidcraft_test_blank_D10x75.step` · `.png` — 원통 시험
- `solidcraft_helix_test_D10_2F_30deg.step` · `.sc` · `_front.png` · `_iso.png` — 나선 날 시험
- `solidcraft_hole_test_plate_30x20x10_D6.step` · `_canon.step` — 구멍 판 원본 · 변환본
- `O9101_SolidCraft변환_포스트시험_시험전용_20261112.nc` — 포스트 출력 시험
- `add_solidcraft_mcp.py` · `스크립트/sc_step_canon.py`

## 6. 관련 페이지

- [[cadcam/Blender-3D-시각화-MCP-연동]] — Blender 연결 · 그림 · 영상 전용
- [[projects/파일럿2기-발표-소재-모음]] — CADCraft · Blender · FreeCAD 연결 사례 표
- [[재연마-프로그램-워크플로우]] — ANCA CAD → CAM → 시뮬 → 머신 → 검증 (연삭 쪽 원본)
- `raw/도면 작업/연습 1/06_FreeCAD_CAM/README.md` — FreeCAD CAM 시험 · 사내 포스트 `qp2040_post.py`
