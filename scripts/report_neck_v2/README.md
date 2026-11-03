# 넥 원통연삭 시험결과 보고 제2판 생성 스크립트 (2026-10-21, Cowork 컴퓨터1)

산출물: `wiki/reports/01_연삭조건/넥_원통연삭_시험결과_보고_20261022_v2.docx` (12쪽)

## 다시 만드는 순서
1. `python figs.py` — 그림 3장(fig1 ~ fig3.png). 글꼴 맑은 고딕 또는 Noto Sans CJK KR 필요
2. `node build.js` — docx 생성 (`npm docx` 패키지). `pg.json`(쪽번호)을 읽음 — 처음엔 `{}` 로 만들고 시작
3. LibreOffice 로 PDF 변환 → `python pages.py <pdf>` — 표 · 그림 · 장 쪽번호를 `pg.json` 에 기록
4. 2 → 3 을 한 번 더 돌려 목차 쪽번호 확정

## 주의
- 줄 간격은 모두 고정값(EXACT) — 「배수(auto)」로 두면 Word(맑은 고딕)에서 줄이 약 1.3배 넓어져 쪽 나눔이 어긋남(2026-10-21 Word PDF 17쪽 vs 미리보기 12쪽 사례)
- 장 시작 쪽: 1. 서론 · 3. 시험 결과 · 5. 결론 · 5-라 · 부록은 pageBreakBefore
- 문체 · 서식 규칙: `wiki/standards/연구보고서-양식-사례.md` 양식 B · AI 티 12항목, `standards/보고서-작성-원칙.md` §0 · §5-A
