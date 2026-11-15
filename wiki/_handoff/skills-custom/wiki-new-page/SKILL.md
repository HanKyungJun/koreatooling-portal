---
name: wiki-new-page
description: >
  [위키 새 페이지] cnc-wiki 새 페이지를 올바른 스키마로 생성합니다.
  "페이지 만들어줘", "X 페이지 추가해줘", "새 위키 작성" 으로 실행합니다.
---

# wiki-new-page 스킬

cnc-wiki에 새 마크다운 페이지를 올바른 스키마로 생성합니다.

## 기본 경로

```
C:\Users\TOOLKOREA\Desktop\cnc-wiki\wiki\
```

## 페이지 타입별 경로

요청 키워드로 타입을 추론합니다. 모호하면 한 번만 확인합니다.

| 타입 | 경로 | 키워드 힌트 |
|------|------|------------|
| `machine` | `wiki/machines/` | ANCA, VOLLMER, Rollomatic, 장비 |
| `material` | `wiki/materials/` | 초경, SUS304, S45C, 알루미늄, WC-Co |
| `tool` | `wiki/tools/` | 엔드밀, 드릴, 코어, 코팅, 수명, 공구 |
| `wheel` | `wiki/tools/wheels/` | 휠, wheel, Diamond, CBN, Resin |
| `gcode` | `wiki/gcode/` | G83, G코드, FANUC, 사이클 |
| `cadcam` | `wiki/cadcam/` | e-Sharp, iBalance, 연삭 테스트 |
| `troubleshoot` | `wiki/troubleshoot/` | 불량, 진동, 화상, 치핑, Ra 악화 |
| `comparison` | `wiki/comparisons/` | 비교, KPI, 3사, vs |
| `report` | `wiki/reports/` | 보고서, 체크리스트 |
| `project` | `wiki/projects/` | 프로젝트, 실험, R&D |
| `script` | `wiki/scripts/` | 스크립트, 자동화, Python |

---

## 실행 순서

### 1단계: 정보 수집

부족한 항목이 있으면 **한 번에 모아서** 질문합니다:
- 페이지 제목
- 페이지 타입 (추론 불가능한 경우만)
- 핵심 기록 내용 (간단히)
- 참조 출처 ID (없으면 "없음" 가능 — 나중에 source-add로 추가 가능)

### 2단계: 파일명 결정

- 소문자 + 하이픈(-) 구분자 (한국어 그대로도 허용)
- 휠 페이지: `휠-{각도}도-Ø{직경}-{스택번호}.md`

### 3단계: 타입별 스키마 적용

**machine:**
```markdown
---
type: machine
manufacturer: ""
model: ""
controller: ""
tags: []
sources: []
updated: YYYY-MM-DD
---
# [장비명]
## 회사 개요 / 시리즈 라인업 / 주요 사양 / 소프트웨어 생태계 / 사내 운영 현황 / 관련 페이지
```

**material:**
```markdown
---
type: material
category: ""
iso_group: ""
hardness_range: ""
tags: []
sources: []
updated: YYYY-MM-DD
---
# [소재명]
## 1. 규격·명칭 (★★★) / 2. 화학 조성 (★★★) / 3. 기계적 물성 (★★★)
## 4. 가공 특성 (★★☆) / 5. 추천 가공 조건 (★★☆) / 6. 코팅 선택 (★★★)
## 7. 절삭유 (★★☆) / 8. 사내 데이터 / 9. 트러블슈팅 / 10. 관련 페이지 / 11. 참고 문헌
```

**tool:**
```markdown
---
type: tool
category: ""
tags: []
sources: []
updated: YYYY-MM-DD
---
# [공구명]
## 1. 개요 / 2. 설계 기준 / 3. 권장 조건 / 4. 수명 관리 / 5. 사내 데이터 / 6. 관련 페이지
```

**wheel:**
```markdown
---
type: wheel
bond: ""
abrasive: ""
shape_code: ""
diameter_mm: 0
angle_deg: 0
stack: ""
tags: []
sources: []
updated: YYYY-MM-DD
---
# 휠 [각도]도 Ø[직경] (스택 [번호])
## 1. 사양 (★★☆) / 2. 용도·사용 공구
## 3. 원주속도 운영 정책 (★★★)
   - Vc 권장 범위: 18–25 m/s [VEN-NORTON-WINTER-2023]
   - 장비 최대 RPM 한계: — rpm
## 4. 카탈로그 매칭 / 5. 드레싱 변수 / 6. 사내 측정 데이터 / 7. 관련 페이지
```

**gcode:**
```markdown
---
type: gcode
controller: "FANUC"
category: ""
tags: []
sources: []
updated: YYYY-MM-DD
---
# [코드] — [한 줄 설명]
## 1. 기능 개요 / 2. 문법 형식 / 3. 파라미터 설명 / 4. 예시 / 5. 주의사항 / 6. 관련 페이지
```

**cadcam:**
```markdown
---
type: cadcam
software: ""
tags: []
sources:
  - "[VEN-ANCA-ESHARP-ARCHIVE]"
updated: YYYY-MM-DD
---
# [주제명]
## 1. 개요 / 2. 설정 방법 / 3. 파라미터 설명 / 4. 사내 적용 사례 / 5. 주의사항 / 6. 관련 페이지
```

**troubleshoot:**
```markdown
---
type: troubleshoot
tags: []
sources: []
updated: YYYY-MM-DD
---
# [증상명] 트러블슈팅
## 증상 설명 / 원인 분류 (표) / 해결 이력 (표) / 예방 조치 / 관련 페이지
```

**그 외 타입 (comparison / report / project / script):**
```markdown
---
type: [타입]
tags: []
sources: []
updated: YYYY-MM-DD
---
# [제목]
## 개요 / 내용 / 결론·결과 / 관련 페이지
```

---

### 4단계: 파일 저장 및 후처리

1. 파일을 결정된 경로에 저장합니다.
2. `wiki/index.md`를 읽고 해당 카테고리 섹션에 줄을 추가합니다:
   ```
   - [[파일명|페이지 제목]] — 한 줄 설명
   ```
3. `wiki/log.md` 맨 위에 추가합니다:
   ```markdown
   ## [YYYY-MM-DD] 신규 — [페이지 제목]
   영향받은 페이지: [[파일명]]
   출처 추가: [ID 목록 또는 "없음"]
   ```

### 5단계: 완료 안내

- 생성된 파일 경로 (computer:// 링크)
- 채워야 할 빈 섹션 목록
- 출처가 없을 경우 `source-add` 스킬로 등재 권고

---

## 신뢰도 표기 규칙

섹션 제목 옆: `★★★` (1차 출처) / `★★☆` (간접 확인) / `★☆☆` (추정)
본문 수치에: `제조사 기준` / `실측 검증` / `사내 경험값` / `추정값`

⚠️ Vc > 30 m/s 조건이 포함되면 `⚠️ 경고:` 표시를 추가합니다.
`raw/` 폴더는 절대 수정하지 않습니다.
