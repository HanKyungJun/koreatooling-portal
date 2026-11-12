---
type: report
tags: [양식, 코고툴, 디자인, 발표, 보고서, 스크립트]
sources:
  - "[SYS-COWORK]"
updated: 2026-11-02
---

# 코고툴 발표 · 보고서 양식 만들기 스크립트

양식 파일 `templates/코고툴_발표양식_v1.pptx` · `templates/코고툴_보고서양식A_v1.docx` 와 견본 2개를 다시 만드는 스크립트다. 근거 결정: decisions 2026-11-02 (4) · (5).

| 파일 | 만드는 것 | 실행 |
|---|---|---|
| `build_ppt_template.js` | 발표 양식(빈 칸 6장, 발표자 노트에 장별 쓰는 법) | `node build_ppt_template.js 출력.pptx` → `python chart_dash.py 출력.pptx` |
| `build_ppt_sample.js` | 발표 견본(넥 원통연삭 시험, `ACCENT=1` 이면 주황 포인트) | 같음 |
| `build_docx_template.js` | 보고서 양식 A(빈 칸, 양식 A 뼈대) | `node build_docx_template.js 출력.docx` |
| `build_docx_sample.js` | 보고서 견본(넥 원통연삭 시험 3쪽) | 같음 |
| `chart_dash.py` | PPT 그래프의 기준선 계열을 점선 · 표식 없음으로 바꿈 | pptx 만든 뒤 한 번 |

- 필요한 것: Node.js 의 `pptxgenjs` · `docx` 패키지, 로고 PNG(코고툴 디자인 시스템 Logos 그룹). 스크립트 안 `LOGO` 경로와 `applyTheme` 경로는 Cowork 작업 공간 기준이라 PC 에서 돌리려면 바꿔야 한다
- 보통은 스크립트를 돌리지 않고 **양식 pptx · docx 를 복사해서** 쓴다

## 디자인 기준 (B안)

| 요소 | 값 | 근거 |
|---|---|---|
| 머리 띠 · 요약 라벨 · 강조 숫자 | 검정 ink #231f20 | decisions 2026-11-02 (4) |
| 포인트(PPT만) | 로고 불꽃 주황 #e8581c — ▶ 기호와 지금 단원 탭에만, 글자색 금지 | decisions 2026-11-02 (5) |
| 표 머리칸 · 카드 | 연보라 #e4e0f0 | 디자인 시스템 table-lavender |
| 숫자 강조 칸(PPT) | #d7d2e9 — 빔프로젝터에서 보이는 진한 연보라 | 흰 바탕 대비 1.5:1(옛 연하늘 1.1:1) |
| 경고 상자 | 크림 #fffbe5 + 검정 테두리 + 「경고:」 | 보고서 작성 규칙 §6-8 |
| 글꼴 | 맑은 고딕, 영문 코드 · 숫자는 Arial 굵은 기울임 | 보고서 작성 규칙 §10 |
| 크기 | PPT 제목 36 · 메시지 22 · 본문 18 · 표 16 · 주석 14 pt / 보고서 제목 22 · 본문 15 · 표 13 pt | 사내 타이포그래피 기본값 |
| 쪽 구조 | 머리 띠 오른쪽 영문 코드, 쪽 끝 색인 탭, 쪽 아래 「COGOTOOL 쪽 번호」 | 코고툴 카탈로그 제품 쪽 |
| 특정 시리즈 자료 | 띠를 그 시리즈 색으로(글자색은 디자인 시스템 토큰 설명대로) | decisions 2026-11-02 (4) |

## 관련 페이지

- [[standards/보고서-작성-규칙]] §10 · [[templates/보고서양식-A-시험개선결과]] · [[standards/발표자료-작성-사례]]
