# AI 공작기계 동향 월간 보고 — 작성 도구 (2026-11-18 신설)

매월 예약 작업 「AI 공작기계 월간 동향 조사」가 전월 발표를 조사해 이 폴더로 보고서를 만든다. 작성법: `wiki/standards/동향조사-보고서-작성법.md`, 양식 D(`wiki/templates/보고서양식-D-동향조사.md`). 기준 연간 보고: `scripts/report_ai_trend_v2/`(제1판, 2026-11-18).

## 파일

| 파일 | 내용 |
|---|---|
| `items_master.csv` | 누적 항목 목록. 행은 지우지 않고 추가만. 상태가 바뀌면 `상태` 를 고치고 `상태이력` 에 `YYYY-MM 이전→지금` 을 덧붙인다 |
| `build.js` · `body.js` · `content.js` · `fix_normal.py` · `logo.png` | 보고서 생성(docx-js, 코고툴 B안) |
| `charts.py` | 최근 12개월 누적 그래프 2개 |
| `sample_month.json` · `sample_search_log.csv` | 데이터 구조 견본(시험용) |
| `YYYYMM/` | 그 달 데이터: `month.json` · `search_log.csv` · `fig/` |

## 한 달 실행 순서

```bash
cd "$HOME/mnt/cnc-wiki/scripts/report_ai_trend_monthly"
M=202612; mkdir -p $M/fig            # month.json, search_log.csv 를 $M 에 쓴다
python3 charts.py items_master.csv 2026-12 $M/fig
TREND_DIR=$PWD/$M TREND_DATA=$PWD/$M/month.json TREND_MONTH_LABEL='2026. 12.' node build.js "../../outputs/AI공작기계_월간동향_$M.docx"
python3 fix_normal.py "../../outputs/AI공작기계_월간동향_$M.docx"
python3 ../doc_style_check.py "../../outputs/AI공작기계_월간동향_$M.docx"   # 기준 넘은 항목 0
cd ../../outputs && soffice --headless --convert-to pdf "AI공작기계_월간동향_$M.docx"
```

## month.json 구조

`sample_month.json` 참고. `summary`(결론 · 근거 · 요청), `new_items`(업체 · 이름 · 분류 A ~ D · 지역 · 상태 · 구분 · 확인수 · 하는일 · refs), `changed`(항목 · 이전 · 지금 · 근거 · refs), `conditions`(조건 · 해당 · 근거), `implications`, `next`, `media`([설명, 주소]), `excluded` · `unread`([자료, 이유]), `refs`([발행처, 날짜, 제목, 주소]), `revisions`.
