// 코고툴 발표 양식 v1 (B안: 검정 띠 + 주황 포인트) — 2026-11-02, decisions 2026-11-02 (5). 다시 만들기: node 이 파일 출력.pptx
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
const ACCENT = true; // B안 확정
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
pres.title = '코고툴 발표 양식 v1';
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
    { text: { text: '자료 기준 YYYY. MM. DD., 근거 문서 이름', options: { x: M, y: H - 0.5, w: 8, h: 0.3, fontFace: KO, fontSize: 12, color: GRAY, margin: 0 } } },
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
  s.addText('ENGLISH\nCODE', { x: 9.7, y: 4.3, w: 3.3, h: 2.4, fontFace: LATIN, fontSize: 40, bold: true, italic: true,
    color: 'FFFFFF', align: 'left', valign: 'bottom', margin: 0, isTextBox: true, objectName: 'cover-code' });
  s.addImage({ path: LOGO, x: M, y: 0.85, w: 2.16, h: 0.9, altText: 'COGOTOOL 로고', objectName: 'logo' });
  s.addText('발표 제목(명사형, 한 줄)', { x: M, y: 2.55, w: 8.4, h: 1.0, fontFace: KO, fontSize: 44, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'cover-title' });
  s.addText('대상과 범위 한 줄', { x: M, y: 3.6, w: 8.4, h: 0.6, fontFace: KO, fontSize: 22, color: INK, margin: 0, isTextBox: true, objectName: 'cover-sub' });
  s.addText([
    { text: '생산팀 ○○○', options: { breakLine: true } },
    { text: 'YYYY. MM. DD.  상태(양산 미적용 등)' },
  ], { x: M, y: 5.6, w: 8.4, h: 0.9, fontFace: KO, fontSize: 18, color: GRAY, margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: 'cover-meta' });
  s.addNotes('[양식 안내] 표지. 오른쪽 검정 덩어리의 영문 코드는 2 ~ 3단어 대문자 기울임. 로고는 흰 바탕 위에만 둔다. 발표자 노트는 [m:ss] 시간과 존댓말 말투로 쓰고, 화면 글자는 명사형.');
}

// ── 2. 요약 ─────────────────────────────────────────────
pres.addSection({ title: '본문' });
{
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });
  s.addText('요약', { placeholder: 'title' });
  msg(s, '메시지 줄: 결론 한 문장, 숫자 하나, 명사형 끝맺음');
  codeLabel(s, 'SUMMARY'); indexTabs(s, 0);
  const lab = (t) => cell(t, { bold: true, color: 'FFFFFF', fill: { color: NAVY }, align: 'center' });
  s.addTable([
    [lab('결론'), cell('무엇이 어떻게 되었나, 무엇을 하자는가 한 문장')],
    [lab('근거'), cell('핵심 수치 1 ~ 2개, 단위와 구분(실측, 계산, 제조사, 추정)')],
    [lab('요청'), cell('결정이나 확인할 것. 없으면 요청 없음(참고 보고)')],
  ], { x: M, y: 2.15, w: 11.6, colW: [1.2, 10.4], fontFace: KO, fontSize: 18, color: INK, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: 'C9C7C7' }, rowH: [0.62, 0.62, 0.5], margin: [0.05, 0.12, 0.05, 0.12], objectName: 'summary-3' });
  s.addText('표 1. 결과 요약', { x: M, y: 4.5, w: 6, h: 0.35, fontFace: KO, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 't1-cap' });
  s.addTable([
    [hdr('평가 항목'), hdr('판정 기준'), hdr('1차'), hdr('2차')],
    [cell('항목 (단위)'), cell('허용 범위'), cell('값, 합격'), cell('값, 보류')],
    [cell('항목'), cell('기준'), cell('값, 판정'), cell('값, 판정')],
    [cell('항목 (단위)'), cell('판정 대상 아님'), cell('값'), cell('값')],
  ], { x: M, y: 4.9, w: 11.6, colW: [2.9, 2.9, 2.9, 2.9], fontFace: KO, fontSize: 16, color: INK, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: 'C9C7C7' }, rowH: 0.42, margin: [0.03, 0.1, 0.03, 0.1], objectName: 't1' });
  s.addNotes('[양식 안내] 요약 장. 결론 · 근거 · 요청 3줄(보고서 작성 규칙 §2) + 결과 요약표. 판정은 합격 · 보류 · 불합격 글자로. 머리 띠 오른쪽 영문 코드(SUMMARY 등)는 장 성격을 나타내는 한 단어.');
}

// ── 3. 시험 방법 ─────────────────────────────────────────
{
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });
  s.addText('방법', { placeholder: 'title' });
  msg(s, '메시지 줄: 무엇을 무엇과 비교했는지');
  codeLabel(s, 'METHOD'); indexTabs(s, 1);
  s.addText('표 2. 조건', { x: M, y: 2.15, w: 6, h: 0.35, fontFace: KO, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 't2-cap' });
  s.addTable([
    [hdr('항목 (단위)'), hdr('1차'), hdr('2차')],
    [cell('변수 1 (단위)'), cell('값'), cell('값')],
    [cell('변수 2 (단위)'), cell('값'), cell('값')],
    [cell('변수 3 (단위)'), cell('값'), cell('값')],
    [cell('변수 4 (단위)'), cell('값'), cell('값')],
    [cell('고정 조건 (단위)'), { text: '두 차수 같은 값', options: { colspan: 2, align: 'center' } }],
  ], { x: M, y: 2.55, w: 8.1, colW: [2.4, 2.8, 2.9], fontFace: KO, fontSize: 16, color: INK, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: 'C9C7C7' }, rowH: 0.5, margin: [0.03, 0.1, 0.03, 0.1], objectName: 't2' });
  // 오른쪽 숫자 강조(원주속도)
  s.addShape(pres.shapes.RECTANGLE, { x: 9.0, y: 2.55, w: 3.3, h: 3.0, fill: { color: BLUE }, line: { color: BLUE }, objectName: 'stat-bg' });
  s.addText('강조할 숫자 이름', { x: 9.2, y: 2.75, w: 2.9, h: 0.4, fontFace: KO, fontSize: 18, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'stat-label' });
  s.addText([{ text: '00.00', options: { fontSize: 54, bold: true, color: NAVY, fontFace: LATIN } }, { text: ' 단위', options: { fontSize: 22, color: NAVY, fontFace: LATIN } }],
    { x: 9.2, y: 3.2, w: 2.95, h: 0.95, margin: 0, isTextBox: true, objectName: 'stat-value' });
  s.addText([
    { text: '계산식(중간 과정)', options: { breakLine: true } },
    { text: '입력값과 단위', options: { breakLine: true } },
    { text: '기준과 비교, 구분' },
  ], { x: 9.2, y: 4.2, w: 2.95, h: 1.2, fontFace: KO, fontSize: 14, color: INK, margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: 'stat-note' });
  s.addText('판정 기준: 허용 범위와 합격 조건, 근거', { x: M, y: 6.35, w: 11.7, h: 0.45, fontFace: KO, fontSize: 16, color: INK, margin: 0, isTextBox: true, objectName: 'criteria' });
  s.addNotes('[양식 안내] 표 + 숫자 강조 칸. 강조 칸 바탕은 연보라(#d7d2e9), 숫자는 검정 54 pt. 표 단위는 머리 괄호에 한 번. 판정 기준은 결과 장보다 먼저.');
}

// ── 4. 시험 결과 ─────────────────────────────────────────
{
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });
  s.addText('결과', { placeholder: 'title' });
  msg(s, '메시지 줄: 그래프에서 읽을 한 가지');
  codeLabel(s, 'RESULT'); indexTabs(s, 2);
  const cats = ['항목 1', '항목 2', '항목 3'];
  s.addChart(pres.charts.LINE, [
    { name: '비교 계열(밝은 회색)', labels: cats, values: [2.854, 2.855, 2.860] },
    { name: '주 계열(검정)', labels: cats, values: [2.890, 2.905, 2.907] },
    { name: '기준선 1(점선)', labels: cats, values: [2.881, 2.881, 2.881] },
    { name: '기준선 2(점선)', labels: cats, values: [2.896, 2.896, 2.896] },
  ], {
    x: M, y: 2.1, w: 7.9, h: 4.5, chartColors: [LIGHT, NAVY, LIGHT, NAVY], lineSize: 2.5,
    lineDataSymbol: 'circle', lineDataSymbolSize: 9,
    showTitle: true, title: '그림 1. 제목 (단위, 구분) — 예시 값', titleFontSize: 14, titleColor: INK, titleFontFace: '+mn-lt',
    valAxisMinVal: 2.84, valAxisMaxVal: 2.92, valAxisMajorUnit: 0.02, valAxisLabelFormatCode: '0.000',
    valAxisLabelColor: GRAY, catAxisLabelColor: INK, valAxisLabelFontSize: 14, catAxisLabelFontSize: 14,
    valAxisLabelFontFace: '+mn-lt', catAxisLabelFontFace: '+mn-lt',
    valGridLine: { color: 'E1E0E0', size: 0.5 }, catGridLine: { style: 'none' },
    showLegend: true, legendPos: 'b', legendFontSize: 14, legendColor: INK, legendFontFace: '+mn-lt',
    objectName: 'chart-neck',
  });
  // 상한선 점선 처리는 차트 후처리 대신 범례 이름으로 구분(색은 같은 계열, 밝기로 구분)
  s.addShape(pres.shapes.RECTANGLE, { x: 8.85, y: 2.2, w: 3.45, h: 1.9, fill: { color: BLUE }, line: { color: BLUE }, objectName: 'k1-bg' });
  s.addText('강조할 숫자 이름', { x: 9.05, y: 2.35, w: 3.1, h: 0.4, fontFace: KO, fontSize: 16, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'k1-label' });
  s.addText([{ text: '+0.000', options: { fontSize: 44, bold: true, color: NAVY, fontFace: LATIN } }, { text: ' 단위', options: { fontSize: 20, color: NAVY, fontFace: LATIN } }],
    { x: 9.05, y: 2.8, w: 3.1, h: 0.8, margin: 0, isTextBox: true, objectName: 'k1-value' });
  s.addText('한 줄 설명(구분)', { x: 9.05, y: 3.6, w: 3.1, h: 0.35, fontFace: KO, fontSize: 14, color: INK, margin: 0, isTextBox: true, objectName: 'k1-note' });
  s.addShape(pres.shapes.RECTANGLE, { x: 8.85, y: 4.3, w: 3.45, h: 2.3, fill: { color: LAV }, line: { color: LAV }, objectName: 'k2-bg' });
  s.addText('판정 항목', { x: 9.05, y: 4.45, w: 3.1, h: 0.4, fontFace: KO, fontSize: 16, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'k2-label' });
  s.addText([
    { text: '1차  값, 판정', options: { breakLine: true } },
    { text: '2차  값, 판정', options: { breakLine: true } },
    { text: '판정 주체: 현장 확인 또는 사진 판독', options: { fontSize: 14, color: GRAY } },
  ], { x: 9.05, y: 4.9, w: 3.1, h: 1.5, fontFace: KO, fontSize: 18, color: INK, margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'k2-body' });
  s.addNotes('[양식 안내] 그래프 + 강조 칸 2개. 그래프는 실측 데이터로만. 계열은 색이 아니라 밝기로 구분(검정 · 밝은 회색), 기준선은 점선. 그래프 데이터는 차트를 오른쪽 클릭 → 데이터 편집.');
}

// ── 5. 고찰 ─────────────────────────────────────────────
{
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });
  s.addText('고찰', { placeholder: 'title' });
  msg(s, '메시지 줄: 원인 분석의 결론 한 문장');
  codeLabel(s, 'ANALYSIS'); indexTabs(s, 3);
  const cards = [
    ['원인 1', '측정 사실 한 줄', '해석 한 줄', '구분(근거)'],
    ['원인 2', '측정 사실 한 줄', '해석 한 줄', '구분(근거)'],
    ['원인 3', '측정 사실 한 줄', '해석 한 줄', '구분(근거)'],
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
  s.addNotes('[양식 안내] 카드 3개. 카드는 바탕색만(옆 줄무늬 · 그림자 없음). 사실과 해석을 나눠 쓰고 아래에 구분(실측 · 계산 · 추정)과 근거.');
}

// ── 6. 결론 및 향후 계획 ─────────────────────────────────
{
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });
  s.addText('결론 및 향후 계획', { placeholder: 'title' });
  msg(s, '메시지 줄: 결론과 다음 할 일');
  codeLabel(s, 'NEXT'); indexTabs(s, 4);
  s.addText('결론', { x: M, y: 2.15, w: 6.6, h: 0.45, fontFace: KO, fontSize: 20, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'concl-h' });
  s.addText([
    { text: '결론 1', options: { bullet: { type: 'number' }, breakLine: true } },
    { text: '결론 2', options: { bullet: { type: 'number' }, breakLine: true } },
    { text: '결론 3', options: { bullet: { type: 'number' }, breakLine: true } },
    { text: '표본 수와 양산 적용 여부', options: { bullet: { type: 'number' } } },
  ], { x: M, y: 2.7, w: 6.6, h: 3.2, fontFace: KO, fontSize: 18, color: INK, margin: 0, paraSpaceAfter: 10, valign: 'top', isTextBox: true, objectName: 'concl-list' });
  s.addText('향후 계획', { x: 7.6, y: 2.15, w: 4.7, h: 0.45, fontFace: KO, fontSize: 20, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'plan-h' });
  s.addText([
    { text: '다음 할 일 1', options: { bullet: true, breakLine: true } },
    { text: '다음 할 일 2', options: { bullet: true } },
  ], { x: 7.6, y: 2.7, w: 4.7, h: 1.6, fontFace: KO, fontSize: 18, color: INK, margin: 0, paraSpaceAfter: 10, valign: 'top', isTextBox: true, objectName: 'plan-list' });
  s.addShape(pres.shapes.RECTANGLE, { x: 7.6, y: 4.45, w: 4.7, h: 1.45, fill: { color: CREAM }, line: { color: INK, width: 1 }, objectName: 'warn-bg' });
  s.addText([
    { text: '경고: ', options: { bold: true } },
    { text: '경고 대상(Vc 30 m/s 초과, CBN 고RPM, 초경 고절입, MCT 고이송)일 때만 쓰는 상자. 없으면 지운다' },
  ], { x: 7.8, y: 4.6, w: 4.3, h: 1.2, fontFace: KO, fontSize: 16, color: INK, margin: 0, valign: 'top', isTextBox: true, objectName: 'warn-text' });
  s.addNotes('[양식 안내] 결론 및 향후 계획. 결론은 번호 목록, 본문에 없는 내용은 넣지 않는다. 경고 상자는 크림 바탕 + 검정 테두리 + 「경고:」 글자.');
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('written', OUT);
})();
