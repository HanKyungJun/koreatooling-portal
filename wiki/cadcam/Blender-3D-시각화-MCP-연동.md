---
type: cadcam
tags: [Blender, 3D, 시각화, MCP, 렌더링, G코드, 시뮬레이션]
sources:
  - "[VEN-BLENDER-LAB-MCP]"
  - "[VEN-ANTHROPIC-BLENDER-CONNECTOR]"
updated: 2026-10-22
---

# Blender 3D 시각화 (Claude MCP 연동)

> 요약: Blender를 Claude Cowork와 연결해 공구와 명판의 3D 모델, 렌더 이미지, G코드 가공 영상을 만든다. **그림과 영상 전용**이며 가공 조건이나 G코드 검증의 근거로 쓰지 않는다. 치수 도면은 CADCraft로 그린다.

## 1. 구성 (2026-10-22 연동 확인)

| 항목 | 값 | 신뢰도 |
|------|-----|--------|
| Blender | 5.2.2 LTS, 설치 폴더 `C:\Program Files\Blender Foundation\Blender 5.2\` | 실측 검증 |
| MCP 애드온 | Blender Lab 공식 MCP 1.0.3, 유형은 확장 | 제조사 기준 [VEN-BLENDER-LAB-MCP] |
| 애드온 설정 | Host localhost / Port 9876 / Auto Start 켜짐, 지연 1 s | 실측 검증 |
| Claude 커넥터 | 「Blender」 확장 프로그램 1.0.1, Blender Lab 제작, 도구 26개 | 제조사 기준 [VEN-ANTHROPIC-BLENDER-CONNECTOR] |
| 최소 Blender 버전 | 5.1 이상 | 제조사 기준, 아래 주 참고 |

주: Anthropic 튜토리얼은 「4.2 이상」이라고 적었다. 그러나 blender.org 애드온 내려받기 링크의 최소 버전은 5.1.0 이다. 이 위키는 배포처 값인 5.1 이상을 따른다.

## 2. 설치 순서

1. Blender 5.1 이상을 설치한다.
2. blender.org/lab/mcp-server에서 **「디스크에서 다운로드」** 링크로 애드온 zip을 받는다. 끌어다 놓기 방식은 2026-10-22 사내 PC에서 실패했다.
3. Blender 메뉴 **편집 > 환경 설정 > 애드온 > 오른쪽 위 ⌄ > 디스크에서 설치**를 눌러 zip을 고르고 MCP를 켠다.
4. 확인: Blender Python 콘솔에서 아래 한 줄이 `(True, True)`를 돌려주면 설치와 활성화가 끝난 것이다.
   `import addon_utils; print([(m.__name__, addon_utils.check(m.__name__)) for m in addon_utils.modules() if 'mcp' in m.__name__.lower()])`
5. Claude 데스크톱 앱 **설정 > 커넥터**에서 Blender를 추가한다. 앱을 완전히 종료한 뒤 다시 켠다.

## 3. 쓰는 방식 두 가지

| 방식 | 작동 | 쓰는 곳 |
|------|------|---------|
| **화면 방식**: Blender 창을 켜 둠 | 정상 | 모델링, 렌더, 영상 등 모든 작업. Blender를 닫으면 연결이 끊긴다 |
| **백그라운드 방식**: 도구 이름 끝이 `for Command-Line` | 실행은 되나 약 2분 걸림 | 결과가 파일로 남는 작업만. 60 s 제한 때문에 응답은 돌아오지 않는다 |

백그라운드 방식 설정 경위, 2026-10-22:
- 사용자 환경변수 `BLENDER_PATH`는 커넥터에 전달되지 않았다. 커넥터가 일부 환경변수만 넘겨받는 것으로 추정한다.
- 사용자 PATH에 Blender 폴더를 추가하고 Claude 앱을 다시 켜자 실행 파일을 찾았다.
- PowerShell에서 직접 `blender --background`를 돌리면 즉시 끝난다. Claude를 거칠 때만 느리며 원인은 확인 필요.

## 4. 작업 흐름

### 4-1. 도면 → 공구 3D
- 외형은 도면 치수로 회전체 단면 r(x)를 만든다.
- 날 홈은 실제 형상 자료가 있을 때 그것을 쓴다. CIM3D가 내보낸 3DFACE 메시 DXF를 불러와 단면 r(x, φ) 표를 뽑고 지름 비율로 줄여 입힌다.
- 2JJCR 040 010 200 사례: 외형은 도면값이다. 날 형상은 3F_SQ_1 CIM3D 메시를 D4로 줄였다. 이 메시는 D6, 2날, 헬릭스 30.3°, 심경 0.575D다. 날 홈 빠짐 길이는 휠 지름에 좌우되므로 줄이지 않았으며 추정값이다.

### 4-2. 명판 → 3D + 가공 영상
- DXF 음각 레이어 윤곽을 2D 곡선으로 채워 깊이만큼 빼낸다.
- G코드 G00/G01/G02/G03을 클라우드에서 파싱한다. 급속 이송은 30 m/min으로 가정했다. 시간대별로 공구를 움직이며 지나간 자리를 0.1 mm/px 마스크 이미지에 쌓아 아노다이징 색을 벗긴다.
- RuRu HOUSE 사례: O1002 T01 Ø2 포켓 9분 34초와 O1003 T02 Ø1 정삭 11분 36초를 26.8 s 영상으로 압축했다. 약 51배속이다.

### 4-3. 긴 렌더
- 브리지 응답 제한이 60 s 라서 한 번의 실행에 렌더를 몰아넣지 않는다.
- `bpy.app.timers.register`로 한 프레임씩 넘기고 바로 반환한다. 진행은 출력 폴더의 파일 수로 본다.
- 실적: EEVEE 1600×900 한 프레임 약 4.4 s, 642프레임에 45분.

## 5. 주의

⚠️ 주의: 공식 애드온은 Claude가 쓴 Python 코드를 **보호장치 없이** Blender 안에서 실행한다 [VEN-BLENDER-LAB-MCP]. 쓰기와 삭제 도구 7개는 「항상 허용」으로 바꾸지 않는다. Cowork에서는 조직 관리자가 「항상 허용」을 막아 두었다. 2026-10-22 설정 화면에서 확인했다.

⚠️ 주의: 가공 영상은 보여 주기용이다. 간섭, 과삭, 깊이를 검사하지 않는다. 실가공 전 공운전 DRY RUN은 그대로 한다.

- 도면에 없는 헬릭스, 심경, 도장 높이, 색은 추정값으로 표시한다.
- CIM3D와 ToolRoom에서 가져온 형상은 사내 프로그램 기반이라 그림 용도로만 쓴다.
- `render_viewport_to_path` 도구는 지정한 경로를 무시하고 Temp 폴더에 저장한다. 위키 폴더에 바로 쓰려면 Python 코드에서 `scene.render.filepath`를 정하고 렌더한다.
- 같은 이름으로 다시 저장하면 `.blend1` 백업이 생긴다. 정리할 때 `_중간파일/`로 옮긴다.

## 6. 결과물 위치

| 결과물 | 위치 |
|--------|------|
| 2JJCR 040 010 200 공구 3D, v5 최종과 이전판 v1 ~ v4 | `outputs/3D_Blender_20261022/2JJCR_040_010_200/` |
| 3F_SQ_1 CIM3D 변환 메시·반경표 | `outputs/3D_Blender_20261022/3F_SQ_1_CIM3D참조/` |
| RuRu HOUSE 명판 3D·가공 영상·좌표 | `raw/도면 작업/연습 1/05_3D_영상/` |

## 7. 문제 해결 기록

| 날짜 | 증상 | 원인 | 해결 |
|------|------|------|------|
| 2026-10-22 | 애드온 목록에 MCP 없음 | 끌어다 놓기 설치 실패 | zip을 디스크에서 설치 |
| 2026-10-22 | Cowork에 Blender 도구 안 보임 | 도구 목록 갱신 전 | 앱 재시작 후 도구 목록 새로 고침 |
| 2026-10-22 | 「Cannot connect to Blender at localhost:9876」 | Blender 꺼짐 | Blender 실행, Auto Start로 서버 시작 |
| 2026-10-22 | 「Blender executable not found at 'blender'」 | 커넥터가 `BLENDER_PATH`를 못 받음, 추정 | 사용자 PATH에 Blender 폴더 추가 |
| 2026-10-22 | 백그라운드 도구가 60 s 안에 응답 없음 | Claude 경유 실행이 약 2분 걸림, 원인 확인 필요 | 화면 방식으로 작업. 남은 프로세스는 `Stop-Process -Name blender` |

## 8. 관련 페이지
- [[cadcam/iGrind-원통연삭-넥가공-2JJCR040010200]]: 2JJCR 040 010 200 넥 설정, 3D 모델 외형의 근거
- [[cadcam/MRR-기반-연삭공정-분석]]: CIMulator3D 활용
- [[projects/파일럿2기-발표-소재-모음]]: 발표 자료 소재
