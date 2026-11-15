---
name: "tool-generator"
description: "「공구 만들어 줘」「공구 도면 · 3D 만들어 줘」+ 사양 한 줄(EM 4날 D6 d6 L50 Lc9 R0.5 넥5.7×18 헬릭스35)로 cnc-wiki 공구 도면(DXF·PDF·PNG)과 SolidCraft 3D(STEP)를 만들 때 사용"
---

# 공구 생성기 (cnc-wiki `scripts/tool_gen.py`)

자세한 규칙 · 기본값 · 실측은 `wiki/cadcam/공구-도면-3D-생성기.md`. 모양 확인용 — 공구 형상 기준은 ANCA ToolRoom.

## 순서

1. 사양 확인: 종류(EM) · 날 수(2~4) · D · d · L · Lc 가 다 있는지. 빠진 값은 한 줄로만 묻는다. 생크경 표기는 항상 d.
2. 검사: PC 쪽 shell(device_bash)에서 cnc-wiki 폴더로 가서
   `python3 scripts/tool_gen.py "<사양>" --tpl "raw/도면 작업/양식/도면양식_A4가로_공구용_v1.dxf" --out outputs/02_도면_3D_CAM/공구생성기 --check`
   - 결과가 「불가능」이면 우회안 없이 「불가능」과 이유만 알린다. 끝.
   - ezdxf 가 없으면 `pip install --user ezdxf matplotlib shapely`.
3. 도면: 같은 명령에서 `--check` 대신 `--sc-root 'C:\Users\TOOLKOREA\Desktop\cnc-wiki\outputs\02_도면_3D_CAM\공구생성기' --date <오늘 KST>` → 폴더 `<이름>_vN` 생성(덮어쓰지 않음).
4. 3D: `<이름>_3d_recipe.json` 을 읽고 SolidCraft `new_design(name=design_name)` → 각 stage 마다 `batch(commands=stage.commands, expect=stage.expect, timings=true, verbose=false)` → 마지막에 recipe.screenshot 값으로 `screenshot`.
   - expect 불일치 · 오류면 멈추고 보고. 90 s 넘게 끊기면 `_작업` 의 마지막 저장본을 open 해서 다음 stage 부터.
5. 점검: FreeCAD `execute_code`(include_screenshot=false)로 STEP 읽기 → 솔리드 2 · isValid · 부피 · optimalBoundingBox. FreeCAD 창이 꺼져 있으면 「확인 필요」로 표시.
6. 보고: 도면 PNG 를 보여 주고(staging 후 Read 로 확인), 폴더 이름 · 축척 · 부피(계산 대 측정 %) · 걸린 시간만 짧게. 대외로 낼 때는 사양표의 소재 · 코팅을 채워야 한다고 한 줄.
7. 기록: 여러 건이거나 의견이 나오면 `wiki/cadcam/공구-도면-3D-생성기.md` §3 표 또는 tasks 해당 항목에 한 줄. 결정 기록은 규칙이 바뀔 때만.

## 주의

- 판단(새 기본값 · 규칙)은 추천 1개 + 이유 → 승인.
- 파일 삭제 · 이동은 먼저 묻는다 (`.sc.bak` 포함).
- 시각은 KST 로 말한다.