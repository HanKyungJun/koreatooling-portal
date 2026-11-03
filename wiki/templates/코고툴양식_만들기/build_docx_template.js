// 코고툴 보고서 양식 v1 (B안 디자인: 검정 띠, 맑은 고딕 22/15/13 pt) — 양식 A 뼈대. 2026-11-02, decisions 2026-11-02 (5)
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, VerticalAlign, Header, Footer, PageNumber, ImageRun, TabStopType, HeadingLevel,
} = require('docx');

const OUT = process.argv[2] || 'sample.docx';
const LOGO = '/tmp/claude-0/-home-claude/17c73168-ad5d-5efd-9107-971fbd8b4d63/scratchpad/artifact-files/e6859726-bfc2-48ef-9dbf-1ed44d28f91f/29ba0de898e2b746aa3d101ed92b49c8.png';

// 코고툴 토큰(v3)
const NAVY = '231F20', INK = '231F20', GRAY = '58595B', LAV = 'E4E0F0', BLUE = 'E6F7FD', CREAM = 'FFFBE5', LINE = 'C9C7C7';
const KO = '맑은 고딕', LATIN = 'Arial';
const BODY = 30, TBL = 26, TITLE = 44; // half-points: 15 pt, 13 pt, 22 pt

const PAGE_W = 11906, MARGIN_LR = 1134, CONTENT_W = PAGE_W - 2 * MARGIN_LR; // A4, 좌우 20 mm

const run = (t, o = {}) => new TextRun({ text: t, font: KO, size: BODY, color: INK, ...o });
const p = (children, o = {}) => new Paragraph({ children: Array.isArray(children) ? children : [run(children)], spacing: { after: 140, line: 312 }, ...o });
// 개조식 항목: 기호 + 내어쓰기
const item = (mark, text, level = 0) => new Paragraph({
  children: [run(`${mark} `), run(text)],
  indent: { left: 360 + level * 400, hanging: 360 }, spacing: { after: 60, line: 312 },
});
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: KO, size: 34, bold: true, color: NAVY })],
  spacing: { before: 280, after: 120 } });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: KO, size: BODY, bold: true, color: INK })],
  spacing: { before: 160, after: 80 } });
const caption = (t) => new Paragraph({ children: [run(t, { size: TBL, bold: true })], spacing: { before: 120, after: 60 } });
const note = (t) => new Paragraph({ children: [run(t, { size: TBL, color: GRAY })], spacing: { before: 40, after: 120 } });

const border = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const borders = { top: border, bottom: border, left: border, right: border };
function tcell(text, width, o = {}) {
  const { fill, bold, color, align, span } = o;
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders, columnSpan: span,
    shading: fill ? { type: ShadingType.CLEAR, color: 'auto', fill } : undefined,
    verticalAlign: VerticalAlign.CENTER, margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ alignment: align || AlignmentType.LEFT, children: [run(text, { size: TBL, bold, color: color || INK })] })],
  });
}
function table(widths, rows, headRow = true) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({ tableHeader: headRow && ri === 0, children: r.map((c, ci) => {
      const o = typeof c === 'string' ? { t: c } : c;
      const w = o.span ? widths.slice(ci, ci + o.span).reduce((a, b) => a + b, 0) : widths[ci];
      return tcell(o.t, w, headRow && ri === 0 ? { fill: LAV, bold: true } : o);
    }) })),
  });
}

// ── 머리 띠(카탈로그 제품 쪽 머리 띠, 화면 규칙대로 단색) ──
const bandW = [CONTENT_W - 3000, 3000];
const band = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: bandW,
  rows: [new TableRow({ children: [
    new TableCell({ width: { size: bandW[0], type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: 'auto', fill: NAVY },
      borders: { top: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, bottom: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } },
      verticalAlign: VerticalAlign.CENTER, margins: { top: 90, bottom: 90, left: 220, right: 100 },
      children: [new Paragraph({ children: [new TextRun({ text: '○○○ 시험 결과 보고', font: KO, size: TITLE, bold: true, color: 'FFFFFF' })] })] }),
    new TableCell({ width: { size: bandW[1], type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: 'auto', fill: NAVY },
      borders: { top: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, bottom: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } },
      verticalAlign: VerticalAlign.CENTER, margins: { top: 90, bottom: 90, left: 100, right: 220 },
      children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: 'TEST REPORT', font: LATIN, size: 32, bold: true, italics: true, color: 'FFFFFF' })] })] }),
  ] })],
});

// ── 머리 정보 표 ──

const lab = (t) => ({ t, fill: LAV, bold: true });
const infoW = [1500, CONTENT_W / 2 - 1500, 1500, CONTENT_W / 2 - 1500];
const info = table(infoW, [
  [lab('과제명'), '', lab('문서번호'), '○○○_시험결과_보고_YYYYMMDD'],
  [lab('시험 기간'), 'YYYY. MM. DD. ~ MM. DD.', lab('보고일'), 'YYYY. MM. DD.'],
  [lab('장비'), '', lab('작성'), '생산팀 ○○○, 검토 ○○○'],
  [lab('시험 대상'), '공구 번호, 실측 치수', lab('상태'), '시험 단계(양산 미적용)'],
  [lab('프로그램'), '파일명, 버전', lab('비고'), '자료 정리 및 계산 보조 Claude'],
], false);
const sumW = [1300, CONTENT_W - 1300];
const nv = (t) => ({ t, fill: NAVY, bold: true, color: 'FFFFFF', align: AlignmentType.CENTER });
const summary = table(sumW, [
  [nv('결론'), '무엇이 어떻게 되었나, 무엇을 하자는가 한 문장'],
  [nv('근거'), '핵심 수치 1 ~ 2개, 단위와 구분'],
  [nv('요청'), '결정이나 확인할 것. 없으면 요청 없음(참고 보고)'],
], false);
const t1W = [2400, 2300, 1700, 1700, 1538];
const t1 = table(t1W, [['평가 항목', '판정 기준', '1차', '2차', '판정'], ['항목 (단위)', '허용 범위', '', '', ''], ['', '', '', '', '']]);
const t2W = [2400, 1300, 1600, 1600, 1538, 1200];
const t2 = table(t2W, [['변수', '단위', '1차', '2차', '고정 조건', '구분'], ['', '', '', '', '', ''], ['', '', '', '', '', '']]);
const t3W = [1300, 2100, 2100, 2100, 2038];
const t3 = table(t3W, [['회차', '입력값 (mm)', '측정값 (mm)', '차이 (mm)', '판정'], ['1', '', '', '', ''], ['2', '', '', '', '']]);
const t4W = [2400, 1800, 1800, 1600, 2038];
const t4 = table(t4W, [['평가 항목', '목표', '결과', '달성 여부', '비고'], ['', '', '', '', '']]);
const warn = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W],
  rows: [new TableRow({ children: [new TableCell({ width: { size: CONTENT_W, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, color: 'auto', fill: CREAM },
    borders: { top: { style: BorderStyle.SINGLE, size: 8, color: INK }, bottom: { style: BorderStyle.SINGLE, size: 8, color: INK }, left: { style: BorderStyle.SINGLE, size: 8, color: INK }, right: { style: BorderStyle.SINGLE, size: 8, color: INK } },
    margins: { top: 100, bottom: 100, left: 160, right: 160 },
    children: [new Paragraph({ children: [run('경고: ', { bold: true, size: TBL }), run('경고 대상(Vc 30 m/s 초과, CBN 고RPM, 초경 고절입, MCT 고이송)일 때만 쓰는 상자. 없으면 지움', { size: TBL })] })] })] })],
});
const guide = (t) => new Paragraph({ children: [run(t, { size: TBL, color: GRAY })], spacing: { after: 80 } });

const children = [
  band,
  p([run('대상과 범위 한 줄', { color: GRAY })], { spacing: { before: 120, after: 160 } }),
  info,
  h1('요약'),
  summary,
  caption('표 1. 시험 결과 요약'),
  t1,
  note('※ 신뢰도 구분: 실측(사내에서 직접 측정), 계산(측정값으로 계산), 제조사(카탈로그, 매뉴얼), 추정(해석)'),
  h1('1. 서론'),
  h2('가. 시험 배경 및 목적'),
  item('1)', '내용을 개조식 「~함 · ~임」으로 씀'),
  h2('나. 시험 범위'),
  guide('시료 수, 대상 품목, 이번 시험에서 다루지 않는 것'),
  h1('2. 시험 방법'),
  h2('가. 시험 장비 및 공구'),
  h2('나. 시험 조건'),
  caption('표 2. 시험 조건'),
  t2,
  note('※ 계산은 중간 과정을 적음. 예: N = 60,000 × Vc ÷ (π × D)'),
  h2('다. 설비 상태'),
  guide('런아웃, 휠 밸런스, 드레싱, 쿨런트, 예열. 기록하지 않았으면 그렇게 적음'),
  h2('라. 측정 방법'),
  guide('측정 장비, 분해능, 측정 위치, 횟수'),
  h2('마. 판정 기준'),
  guide('허용 범위와 합격 조건. 결과보다 먼저 씀'),
  h1('3. 시험 결과'),
  h2('가. ○○ 측정 결과'),
  caption('표 3. ○○ 측정 결과'),
  t3,
  note('※ 측정 원값은 반올림 전 값. 사진은 그림 아래에 판정 주체(현장 확인 또는 사진 판독)를 적음'),
  h1('4. 고찰'),
  p('측정 사실과 해석을 문단으로 나눠 쓴다. 고찰만 서술식을 쓸 수 있고, 해석마다 근거가 된 측정값을 붙인다. 추정은 추정이라고 쓴다.'),
  h2('가. 시험의 한계'),
  guide('표본 수, 미측정 항목, 이 결과는 시험한 공구에만 해당'),
  h1('5. 결론 및 향후 계획'),
  h2('가. 결론'),
  item('1)', '본문에 있는 내용만 번호 목록으로 씀'),
  item('2)', '양산 적용 여부를 함께 적음'),
  h2('나. 목표 달성도'),
  caption('표 4. 목표 달성도'),
  t4,
  h2('다. 향후 계획 및 요청 사항'),
  item('1)', '다음 시험에서 바꿀 변수 1개, 필요한 장비 시간'),
  new Paragraph({ children: [], spacing: { after: 60 } }),
  warn,
  h1('참고 문헌'),
  guide('제조사 카탈로그 · 매뉴얼, 표준, 문헌 순. 블로그 · 커뮤니티는 단독 근거로 쓰지 않음'),
  h1('부록'),
  item('가.', '측정 원자료'),
  item('나.', '프로그램 파일명 및 버전, 사진 원본 파일명'),
  item('다.', '사내 기록 위치(결정 번호, 위키 페이지, 기록표)'),
  item('라.', '사진 자료(공구 전체, 장비, 셋업)'),
  item('마.', '개정 이력(날짜, 변경, 사유, 양산 적용)'),
];

const doc = new Document({
  creator: '생산팀', title: '코고툴 보고서 양식 v1',
  styles: { default: { document: { run: { font: KO, size: BODY, color: INK } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: KO, size: 34, bold: true, color: NAVY }, paragraph: { outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: KO, size: BODY, bold: true, color: INK }, paragraph: { outlineLevel: 1 } },
    ] },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 850, bottom: 850, left: MARGIN_LR, right: MARGIN_LR, header: 400, footer: 400 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 120 },
      children: [new ImageRun({ type: 'png', data: fs.readFileSync(LOGO), transformation: { width: 96, height: 40 }, altText: { title: 'COGOTOOL', description: 'COGOTOOL 로고', name: 'logo' } })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
      children: [
        new TextRun({ text: '○○○ 시험 결과 보고', font: KO, size: 20, color: GRAY }),
        new TextRun({ text: '\tCOGOTOOL  ', font: LATIN, size: 20, color: GRAY }),
        new TextRun({ children: [PageNumber.CURRENT], font: LATIN, size: 20, color: GRAY }),
      ] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log('written', OUT); });
