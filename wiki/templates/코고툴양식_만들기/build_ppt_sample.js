// 코고툴 디자인 시스템 v3 적용 PPT 샘플 — 넥 원통연삭 시험 결과(견본 A v4 내용)
const pptxgen = require('pptxgenjs');
const { applyTheme } = require('/root/.claude/skills/synced/b975f8eb-8440-4783-8ac8-024b9f4448eb_d9575592-dd32-4ad8-8939-5359bb80f9d7/pptx/scripts/apply_theme.js');
const path = require('path');

const OUT = process.argv[2] || 'sample.pptx';
const LOGO = '/tmp/claude-0/-home-claude/17c73168-ad5d-5efd-9107-971fbd8b4d63/scratchpad/artifact-files/e6859726-bfc2-48ef-9dbf-1ed44d28f91f/29ba0de898e2b746aa3d101ed92b49c8.png';

// 코고툴 토큰(v3)
const NAVY = '231F20';   // 띠 · 강조 = ink (2026-11-02 사내 문서 기본 띠 검정으로 변경, 옛 cogo-navy 2F3778)
const INK = '231F20';    // ink
const GRAY = '58595B';   // footer-gray
const MUTED = '7B7979';  // ink-muted (선·큰 글자만)
const LAV = 'E4E0F0';    // table-lavender
const BLUE = 'D7D2E9';   // 강조 칸: 빔프로젝터에서 보이도록 table-head-hard 계열(옛 table-blue E6F7FD)
const ACCENT = process.env.ACCENT === '1';
const ORANGE = 'E8581C'; // flame-orange — 그림 요소 전용(▶ · 현재 탭), 글자색 금지
const CREAM = 'FFFBE5';  // table-cream
const LIGHT = 'A7A9AC';  // 차트 비교 계열(밝은 회색)

const THEME = {
  name: 'COGO TOOL', headFontFace: '맑은 고딕', bodyFontFace: '맑은 고딕',
  colors: { dk1: INK, lt1: 'FFFFFF', dk2: NAVY, lt2: LAV, accent1: NAVY, accent2: GRAY, accent3: LIGHT,
    accent4: '2A3E92', accent5: '99D420', accent6: 'D22027', hlink: NAVY, folHlink: GRAY },
};
const KO = '맑은 고딕';
const LATIN = 'Arial';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5
pres.theme = { headFontFace: KO, bodyFontFace: KO };
pres.title = '넥 원통연삭 시험 결과 (코고툴 디자인 샘플)';
pres.author = '생산팀 한경준';

const W = 13.333, H = 7.5, M = 0.6;
const SECTIONS = ['요약', '시험 방법', '시험 결과', '고찰', '결론'];

// 본문 레이아웃: 카탈로그 제품 쪽 구조(머리 띠 · 쪽 끝 색인 탭 · 쪽 아래 COGOTOOL과 쪽 번호)
pres.defineSlideMaster({
  title: 'CONTENT',
  background: { color: 'FFFFFF' },
  objects: [
    { rect: { x: 0, y: 0, w: W, h: 1.1, fill: { color: NAVY }, line: { color: NAVY } } },
    { text: { text: 'COGOTOOL', options: { x: W - 2.9, y: H - 0.5, w: 1.6, h: 0.3, fontFace: LATIN, fontSize: 12, color: GRAY, align: 'right', margin: 0 } } },
    { text: { text: '자료 기준 2026. 10. 20. 시험 기록, 넥 원통연삭 시험 결과 보고 제4판', options: { x: M, y: H - 0.5, w: 8, h: 0.3, fontFace: KO, fontSize: 12, color: GRAY, margin: 0 } } },
    { placeholder: { options: { name: 'title', type: 'title', x: M, y: 0.2, w: 9.8, h: 0.7, fontFace: KO, fontSize: 36, bold: true, color: 'FFFFFF', align: 'left', valign: 'middle', margin: 0 }, text: '' } },
    { placeholder: { options: { name: 'msg', type: 'body', x: M, y: 1.35, w: W - 2 * M - 0.5, h: 0.6, fontFace: KO, fontSize: 22, bold: true, color: NAVY, valign: 'middle', margin: 0 }, text: '' } },
  ],
  slideNumber: { x: W - 1.2, y: H - 0.5, w: 0.6, h: 0.3, fontFace: LATIN, fontSize: 12, color: GRAY, align: 'right' },
});

function msg(slide, text) {
  slide.addText([{ text: '▶ ', options: { color: ACCENT ? ORANGE : NAVY } }, { text }], { placeholder: 'msg' });
}

function indexTabs(slide, cur) {
  // 쪽 끝 색인 탭: 지금 단원만 진한 색
  SECTIONS.forEach((s, i) => {
    const on = i === cur;
    slide.addShape(pres.shapes.RECTANGLE, { x: W - 0.42, y: 1.35 + i * 0.62, w: 0.42, h: 0.54,
      fill: { color: on ? (ACCENT ? ORANGE : NAVY) : LAV }, line: { color: on ? (ACCENT ? ORANGE : NAVY) : LAV }, objectName: `tab-${i + 1}` });
    slide.addText(String(i + 1), { x: W - 0.42, y: 1.35 + i * 0.62, w: 0.42, h: 0.54, fontFace: LATIN, fontSize: 16, bold: true,
      color: on ? (ACCENT ? INK : 'FFFFFF') : INK, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: `tab-num-${i + 1}` });
  });
}

function codeLabel(slide, code) {
  // 머리 띠 오른쪽 품목 계열 코드 자리(카탈로그 product-code)
  slide.addText(code, { x: W - 3.6, y: 0.2, w: 3.0, h: 0.7, fontFace: LATIN, fontSize: 28, bold: true, italic: true,
    color: 'FFFFFF', align: 'right', valign: 'middle', margin: 0, isTextBox: true, objectName: 'code' });
}

const hdr = (t) => ({ text: t, options: { bold: true, fill: { color: LAV }, color: INK } });
const cell = (t, o = {}) => ({ text: t, options: o });

// ── 1. 표지 ─────────────────────────────────────────────
pres.addSection({ title: '표지' });
{
  const s = pres.addSlide({ sectionTitle: '표지' });
  s.background = { color: 'FFFFFF' };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.35, fill: { color: NAVY }, line: { color: NAVY }, objectName: 'top-band' });
  s.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 0.35, w: W - 9.3, h: H - 0.35, fill: { color: NAVY }, line: { color: NAVY }, objectName: 'cover-slab' });
  s.addText('NECK\nGRINDING\nTEST', { x: 9.7, y: 4.3, w: 3.3, h: 2.4, fontFace: LATIN, fontSize: 40, bold: true, italic: true,
    color: 'FFFFFF', align: 'left', valign: 'bottom', margin: 0, isTextBox: true, objectName: 'cover-code' });
  s.addImage({ path: LOGO, x: M, y: 0.85, w: 2.16, h: 0.9, altText: 'COGOTOOL 로고', objectName: 'logo' });
  s.addText('넥 원통연삭 시험 결과', { x: M, y: 2.55, w: 8.4, h: 1.0, fontFace: KO, fontSize: 44, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'cover-title' });
  s.addText('D3 초경 엔드밀 시험 공구 2개, ANCA GX7 원통연삭', { x: M, y: 3.6, w: 8.4, h: 0.6, fontFace: KO, fontSize: 22, color: INK, margin: 0, isTextBox: true, objectName: 'cover-sub' });
  s.addText([
    { text: '생산팀 한경준', options: { breakLine: true } },
    { text: '2026. 10. 29.  시험 단계(양산 미적용)' },
  ], { x: M, y: 5.6, w: 8.4, h: 0.9, fontFace: KO, fontSize: 18, color: GRAY, margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: 'cover-meta' });
  s.addNotes('[0:30] 넥 원통연삭 시험 결과를 보고드립니다. 10월 19일과 20일 이틀 동안 D3 초경 엔드밀 시험 공구 2개로 GX7에서 시험했고, 아직 시험 단계라 양산에는 적용하지 않았습니다.');
}

// ── 2. 요약 ─────────────────────────────────────────────
pres.addSection({ title: '본문' });
{
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });
  s.addText('시험 결과 요약', { placeholder: 'title' });
  msg(s, '테스트 1은 넥 지름 합격, 테스트 2는 진입부 자국 해소');
  codeLabel(s, 'SUMMARY'); indexTabs(s, 0);
  const lab = (t) => cell(t, { bold: true, color: 'FFFFFF', fill: { color: NAVY }, align: 'center' });
  s.addTable([
    [lab('결론'), cell('정삭만 적용한 테스트 1은 넥 지름 합격. 황삭 대각선 진입을 더한 테스트 2는 자국이 없어졌으나 넥 끝 쪽 지름 초과로 보류')],
    [lab('근거'), cell('테스트 1 넥 지름 2.853 ~ 2.862 mm(허용 2.807 ~ 2.881 mm). 두 공구 모두 측정값이 입력값보다 0.063 ~ 0.065 mm 큼(공구 2개 실측)')],
    [lab('요청'), cell('요청 없음(참고 보고). 휠 드레싱 후 테스트 3 진행 예정')],
  ], { x: M, y: 2.15, w: 11.6, colW: [1.2, 10.4], fontFace: KO, fontSize: 18, color: INK, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: 'C9C7C7' }, rowH: [0.62, 0.62, 0.5], margin: [0.05, 0.12, 0.05, 0.12], objectName: 'summary-3' });
  s.addText('표 1. 시험 결과 요약', { x: M, y: 4.5, w: 6, h: 0.35, fontFace: KO, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 't1-cap' });
  s.addTable([
    [hdr('평가 항목'), hdr('판정 기준'), hdr('테스트 1 (1번 공구)'), hdr('테스트 2 (2번 공구)')],
    [cell('넥 지름 (mm)'), cell('0.95 ~ 0.975 × 실측 D'), cell('2.853 ~ 2.862, 합격'), cell('2.890 ~ 2.907, 보류')],
    [cell('진입부 자국'), cell('없음'), cell('있음, 불합격'), cell('없음, 합격')],
    [cell('측정값 − 입력값 (mm)'), cell('판정 대상 아님'), cell('+0.063 (머리 쪽)'), cell('+0.065 (머리 쪽)')],
  ], { x: M, y: 4.9, w: 11.6, colW: [2.9, 2.9, 2.9, 2.9], fontFace: KO, fontSize: 16, color: INK, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: 'C9C7C7' }, rowH: 0.42, margin: [0.03, 0.1, 0.03, 0.1], objectName: 't1' });
  s.addNotes('[1:10] 결론부터 말씀드리면 정삭만 한 테스트 1은 넥 지름이 허용 범위에 들어 합격이고, 황삭 대각선 진입을 더한 테스트 2는 진입부 자국이 없어졌습니다. 다만 테스트 2는 넥 끝 쪽 지름이 상한을 조금 넘어 보류했습니다. 두 공구 모두 측정값이 입력값보다 0.063에서 0.065 mm 크게 나왔습니다.');
}

// ── 3. 시험 방법 ─────────────────────────────────────────
{
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });
  s.addText('시험 방법', { placeholder: 'title' });
  msg(s, '정삭만 4회(테스트 1)와 황삭 대각선 진입 추가 1회(테스트 2) 비교');
  codeLabel(s, 'METHOD'); indexTabs(s, 1);
  s.addText('표 2. 시험 조건', { x: M, y: 2.15, w: 6, h: 0.35, fontFace: KO, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 't2-cap' });
  s.addTable([
    [hdr('항목 (단위)'), hdr('테스트 1'), hdr('테스트 2')],
    [cell('입력 지름 (mm)'), cell('3.05에서 2.790까지 4회'), cell('2.825 (1회)')],
    [cell('황삭'), cell('사용 안 함'), cell('대각선 진입 0.075 mm')],
    [cell('정삭 여유 (mm)'), cell('1.333'), cell('0.020')],
    [cell('정삭 진입 속도 (mm/min)'), cell('5.0, 4회만 1.0'), cell('0.5')],
    [cell('정삭 이송 (mm/min)'), { text: '3.0, 공구 회전 25 rpm', options: { colspan: 2, align: 'center' } }],
  ], { x: M, y: 2.55, w: 8.1, colW: [2.4, 2.8, 2.9], fontFace: KO, fontSize: 16, color: INK, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: 'C9C7C7' }, rowH: 0.5, margin: [0.03, 0.1, 0.03, 0.1], objectName: 't2' });
  // 오른쪽 숫자 강조(원주속도)
  s.addShape(pres.shapes.RECTANGLE, { x: 9.0, y: 2.55, w: 3.3, h: 3.0, fill: { color: BLUE }, line: { color: BLUE }, objectName: 'stat-bg' });
  s.addText('휠 원주속도', { x: 9.2, y: 2.75, w: 2.9, h: 0.4, fontFace: KO, fontSize: 18, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'stat-label' });
  s.addText([{ text: '22.93', options: { fontSize: 54, bold: true, color: NAVY, fontFace: LATIN } }, { text: ' m/s', options: { fontSize: 22, color: NAVY, fontFace: LATIN } }],
    { x: 9.2, y: 3.2, w: 2.95, h: 0.95, margin: 0, isTextBox: true, objectName: 'stat-value' });
  s.addText([
    { text: 'Vc = π × D × N ÷ 60,000', options: { breakLine: true } },
    { text: 'D 125.102 mm, N 3,500 rpm', options: { breakLine: true } },
    { text: '사내 상한 25 m/s 이내(계산)' },
  ], { x: 9.2, y: 4.2, w: 2.95, h: 1.2, fontFace: KO, fontSize: 14, color: INK, margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: 'stat-note' });
  s.addText('판정 기준: 넥 지름 = 실측 D의 0.95 ~ 0.975배(제조사 롱넥 31개 품목에서 역산한 사내 기준)', { x: M, y: 6.35, w: 11.7, h: 0.45, fontFace: KO, fontSize: 16, color: INK, margin: 0, isTextBox: true, objectName: 'criteria' });
  s.addNotes('[1:00] 장비는 ANCA GX7, 휠은 지름 125.102 mm이고 3,500 rpm으로 돌려 원주속도는 22.93 m/s입니다. 테스트 1은 같은 공구를 정삭만으로 네 번 깎아 내려갔고, 테스트 2는 황삭 대각선 진입을 넣고 정삭 여유를 0.020 mm로 줄였습니다. 판정 기준은 제조사 롱넥 엔드밀 치수에서 역산한 0.95에서 0.975배입니다.');
}

// ── 4. 시험 결과 ─────────────────────────────────────────
{
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });
  s.addText('시험 결과', { placeholder: 'title' });
  msg(s, '테스트 2는 중간과 테이퍼 쪽이 상한을 0.009 ~ 0.011 mm 초과');
  codeLabel(s, 'RESULT'); indexTabs(s, 2);
  const cats = ['머리 쪽', '중간', '테이퍼 쪽'];
  s.addChart(pres.charts.LINE, [
    { name: '테스트 1 (4회)', labels: cats, values: [2.854, 2.855, 2.860] },
    { name: '테스트 2', labels: cats, values: [2.890, 2.905, 2.907] },
    { name: '상한 1번 공구', labels: cats, values: [2.881, 2.881, 2.881] },
    { name: '상한 2번 공구', labels: cats, values: [2.896, 2.896, 2.896] },
  ], {
    x: M, y: 2.1, w: 7.9, h: 4.5, chartColors: [LIGHT, NAVY, LIGHT, NAVY], lineSize: 2.5,
    lineDataSymbol: 'circle', lineDataSymbolSize: 9,
    showTitle: true, title: '그림 1. 넥 위치별 지름 (mm, 실측)', titleFontSize: 14, titleColor: INK, titleFontFace: '+mn-lt',
    valAxisMinVal: 2.84, valAxisMaxVal: 2.92, valAxisMajorUnit: 0.02, valAxisLabelFormatCode: '0.000',
    valAxisLabelColor: GRAY, catAxisLabelColor: INK, valAxisLabelFontSize: 14, catAxisLabelFontSize: 14,
    valAxisLabelFontFace: '+mn-lt', catAxisLabelFontFace: '+mn-lt',
    valGridLine: { color: 'E1E0E0', size: 0.5 }, catGridLine: { style: 'none' },
    showLegend: true, legendPos: 'b', legendFontSize: 14, legendColor: INK, legendFontFace: '+mn-lt',
    objectName: 'chart-neck',
  });
  // 상한선 점선 처리는 차트 후처리 대신 범례 이름으로 구분(색은 같은 계열, 밝기로 구분)
  s.addShape(pres.shapes.RECTANGLE, { x: 8.85, y: 2.2, w: 3.45, h: 1.9, fill: { color: BLUE }, line: { color: BLUE }, objectName: 'k1-bg' });
  s.addText('측정값 − 입력값 (머리 쪽)', { x: 9.05, y: 2.35, w: 3.1, h: 0.4, fontFace: KO, fontSize: 16, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'k1-label' });
  s.addText([{ text: '+0.065', options: { fontSize: 44, bold: true, color: NAVY, fontFace: LATIN } }, { text: ' mm', options: { fontSize: 20, color: NAVY, fontFace: LATIN } }],
    { x: 9.05, y: 2.8, w: 3.1, h: 0.8, margin: 0, isTextBox: true, objectName: 'k1-value' });
  s.addText('두 공구 모두 거의 같음(실측)', { x: 9.05, y: 3.6, w: 3.1, h: 0.35, fontFace: KO, fontSize: 14, color: INK, margin: 0, isTextBox: true, objectName: 'k1-note' });
  s.addShape(pres.shapes.RECTANGLE, { x: 8.85, y: 4.3, w: 3.45, h: 2.3, fill: { color: LAV }, line: { color: LAV }, objectName: 'k2-bg' });
  s.addText('진입부 자국', { x: 9.05, y: 4.45, w: 3.1, h: 0.4, fontFace: KO, fontSize: 16, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'k2-label' });
  s.addText([
    { text: '테스트 1  있음, 불합격', options: { breakLine: true } },
    { text: '테스트 2  없음, 합격', options: { breakLine: true } },
    { text: '판정: 현장 확인(현미경 사진)', options: { fontSize: 14, color: GRAY } },
  ], { x: 9.05, y: 4.9, w: 3.1, h: 1.5, fontFace: KO, fontSize: 18, color: INK, margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'k2-body' });
  s.addNotes('[1:20] 그래프는 넥 세 곳의 지름입니다. 테스트 1의 4회째는 세 곳 모두 상한 2.881 mm 아래라 합격이고, 테스트 2는 머리 쪽은 합격이지만 중간과 테이퍼 쪽이 상한 2.896 mm를 0.009에서 0.011 mm 넘었습니다. 측정값과 입력값 차이는 두 공구 모두 약 0.065 mm였고, 진입부 자국은 테스트 2에서만 없어졌습니다.');
}

// ── 5. 고찰 ─────────────────────────────────────────────
{
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });
  s.addText('고찰', { placeholder: 'title' });
  msg(s, '측정값과 입력값의 차이는 깎는 양과 관계없이 약 +0.065 mm로 일정');
  codeLabel(s, 'ANALYSIS'); indexTabs(s, 3);
  const cards = [
    ['진입부 자국', '정삭은 항상 넥 시작 쪽에서 지름 방향으로 진입', '정삭 여유가 크면 같은 위치에 자국이 남는 것으로 판단', '추정(매뉴얼 원문 대조 전)'],
    ['측정값 > 입력값', '깎인 양이 약 10배 달라도 차이는 +0.055 ~ +0.075 mm', '공구 처짐보다 휠 지름이나 위치 기준의 고정 오차 가능성', '추정(휠 지름 재측정 안 함)'],
    ['넥 끝 지름 증가', '넥 뒤 테이퍼 12°가 휠 12° 면의 각도와 같음', '테스트 1 계산 L2 12.44 mm, 측정 약 12.5 mm', '계산(공구 2개 중 1개만 일치)'],
  ];
  const cw = 3.7, gap = 0.3;
  cards.forEach((c, i) => {
    const x = M + i * (cw + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: 2.2, w: cw, h: 4.2, fill: { color: i === 1 ? BLUE : LAV }, line: { color: i === 1 ? BLUE : LAV }, objectName: `card-${i + 1}` });
    s.addText(c[0], { x: x + 0.25, y: 2.4, w: cw - 0.5, h: 0.5, fontFace: KO, fontSize: 20, bold: true, color: NAVY, margin: 0, isTextBox: true, objectName: `card-h-${i + 1}` });
    s.addText([
      { text: c[1], options: { breakLine: true } },
      { text: c[2] },
    ], { x: x + 0.25, y: 3.05, w: cw - 0.5, h: 2.5, fontFace: KO, fontSize: 18, color: INK, margin: 0, paraSpaceAfter: 12, valign: 'top', isTextBox: true, objectName: `card-b-${i + 1}` });
    s.addText(c[3], { x: x + 0.25, y: 5.75, w: cw - 0.5, h: 0.45, fontFace: KO, fontSize: 14, color: GRAY, margin: 0, isTextBox: true, objectName: `card-src-${i + 1}` });
  });
  s.addNotes('[1:20] 원인은 세 가지로 봤습니다. 첫째, 정삭은 항상 넥 시작 쪽에서 진입하기 때문에 정삭 여유가 크면 같은 자리에 자국이 남습니다. 둘째, 깎인 양이 열 배 달라도 차이가 일정해서 공구 처짐보다는 휠 지름 같은 고정 오차로 봅니다. 셋째, 넥 끝 지름이 커지는 건 휠의 12도 면 때문으로 보이는데, 공구 2개 중 하나만 계산과 맞아 아직 기준으로 정하지 않았습니다.');
}

// ── 6. 결론 및 향후 계획 ─────────────────────────────────
{
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });
  s.addText('결론 및 향후 계획', { placeholder: 'title' });
  msg(s, '양산 미적용, 휠 드레싱 후 테스트 3에서 재현성 확인');
  codeLabel(s, 'NEXT'); indexTabs(s, 4);
  s.addText('결론', { x: M, y: 2.15, w: 6.6, h: 0.45, fontFace: KO, fontSize: 20, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'concl-h' });
  s.addText([
    { text: '정삭만으로 넥 지름 합격(테스트 1, 4회째)', options: { bullet: { type: 'number' }, breakLine: true } },
    { text: '황삭 대각선 진입과 정삭 여유 0.020 mm로 진입부 자국 해소', options: { bullet: { type: 'number' }, breakLine: true } },
    { text: '드레싱 전 휠 기준 입력값을 약 0.065 mm 작게 넣어야 함', options: { bullet: { type: 'number' }, breakLine: true } },
    { text: '공구 2개 시험값, 양산 미적용', options: { bullet: { type: 'number' } } },
  ], { x: M, y: 2.7, w: 6.6, h: 3.2, fontFace: KO, fontSize: 18, color: INK, margin: 0, paraSpaceAfter: 10, valign: 'top', isTextBox: true, objectName: 'concl-list' });
  s.addText('향후 계획', { x: 7.6, y: 2.15, w: 4.7, h: 0.45, fontFace: KO, fontSize: 20, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'plan-h' });
  s.addText([
    { text: '휠 드레싱 전후 휠 지름 측정과 재등록', options: { bullet: true, breakLine: true } },
    { text: '테스트 3: 넥 구간을 3번 나눠 패스마다 지름과 부하 측정', options: { bullet: true } },
  ], { x: 7.6, y: 2.7, w: 4.7, h: 1.6, fontFace: KO, fontSize: 18, color: INK, margin: 0, paraSpaceAfter: 10, valign: 'top', isTextBox: true, objectName: 'plan-list' });
  s.addShape(pres.shapes.RECTANGLE, { x: 7.6, y: 4.45, w: 4.7, h: 1.45, fill: { color: CREAM }, line: { color: INK, width: 1 }, objectName: 'warn-bg' });
  s.addText([
    { text: '경고: ', options: { bold: true } },
    { text: '테스트 3 테이퍼 쪽 패스당 반경 절입 약 0.19 mm(계산)로 사내 실적 0.075 mm의 약 2.5배. 첫 패스 부하가 5%를 넘으면 중단' },
  ], { x: 7.8, y: 4.6, w: 4.3, h: 1.2, fontFace: KO, fontSize: 16, color: INK, margin: 0, valign: 'top', isTextBox: true, objectName: 'warn-text' });
  s.addNotes('[1:00] 정리하면 정삭만으로도 치수는 맞출 수 있고, 자국은 황삭 대각선 진입과 작은 정삭 여유로 없앨 수 있었습니다. 지금 휠 상태에서는 입력값을 약 0.065 mm 작게 넣어야 합니다. 공구 2개 결과라 양산에는 적용하지 않고, 드레싱 뒤 테스트 3에서 다시 확인하겠습니다. 테스트 3은 절입이 사내 실적의 2.5배라 첫 패스 부하를 보고 진행하겠습니다.');
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('written', OUT);
})();
