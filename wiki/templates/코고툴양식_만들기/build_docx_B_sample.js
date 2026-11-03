// 코고툴 보고서 양식 B 견본 — 재연마 입고 검수 기준 안내(거래처용). 2026-11-02
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, VerticalAlign, Header, Footer, PageNumber, ImageRun, TabStopType, HeadingLevel,
} = require('docx');

const OUT = process.argv[2] || 'sample.docx';
// 대외 발신 명의 = 코리아툴링(2026-11-02 한경준님, 코고툴 · 마이다스는 나중에 추가) — 로고는 코리아툴링 디자인 시스템 Logos
const LOGO = '/tmp/claude-0/-home-claude/17c73168-ad5d-5efd-9107-971fbd8b4d63/scratchpad/artifact-files/40ff8e12-9999-4454-bd3a-9459d70de1d6/0dbf785009edf7d6ca3bba0e37cac495.png';

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
  spacing: { before: 240, after: 100 }, keepNext: true });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: KO, size: BODY, bold: true, color: INK })],
  spacing: { before: 140, after: 80 }, keepNext: true });
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
      children: [new Paragraph({ children: [new TextRun({ text: '재연마 입고 검수 기준 안내', font: KO, size: TITLE, bold: true, color: 'FFFFFF' })] })] }),
    new TableCell({ width: { size: bandW[1], type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: 'auto', fill: NAVY },
      borders: { top: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, bottom: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } },
      verticalAlign: VerticalAlign.CENTER, margins: { top: 90, bottom: 90, left: 100, right: 220 },
      children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: 'TECH DATA', font: LATIN, size: 32, bold: true, italics: true, color: 'FFFFFF' })] })] }),
  ] })],
});

// ── 머리 정보 표 ──


const lab = (t) => ({ t, fill: LAV, bold: true });
const infoW = [1400, CONTENT_W / 2 - 1000, 1200, CONTENT_W / 2 - 1600];
const info = table(infoW, [
  [lab('수신'), '(거래처명) ○○○ 담당자님', lab('문서번호'), 'TD-20261102-01'],
  [lab('발신'), '(주)코리아툴링 생산팀 ○○○', lab('발행일'), '2026. 11. 2.'],
  [lab('문의 내용'), '재연마 접수 기준과 금액이 바뀌는 경우', lab('검토'), '(승인자 서명)'],
], false);
const t1W = [2600, CONTENT_W - 2600];
const t1 = table(t1W, [
  ['항목', '접수 기준'],
  ['날경 D', 'D1 이하 공구는 접수하지 않음'],
  ['코팅', '다이아몬드 코팅 공구는 접수하지 않음'],
  ['다른 회사 공구', '접수함'],
  ['부러진 공구', '날장이 남아 있으면 재연마 가능'],
  ['재연마 횟수', '횟수 제한 없음. 남은 날장으로 판단'],
]);
const t2W = [2300, 2600, CONTENT_W - 4900];
const t2 = table(t2W, [
  ['항목', '확인 방법', '주문 내용과 다를 때'],
  ['브랜드', '생크와 몸통의 각인', '할인 대상이 아니면 일반 금액으로 다시 안내'],
  ['사양', '날수, 형상, 날경, 재질, 작업 부위, 코팅을 실물로 확인', '실물 기준으로 견적하고, 주문과 다르면 연락드린 뒤 진행'],
  ['날끝 손상', '확대해서 손상 위치와 크기 확인', '밑날 작업은 손상 크기와 관계없이 같은 금액. 잘라 내는 길이를 알려 드림'],
  ['남은 날장', '측정', '날장이 남지 않으면 날을 새로 만드는 제작으로 견적'],
  ['전장 L', '측정', '할증 구간(표 3)에 해당하면 다시 안내'],
]);
const t3W = [2000, 3000, CONTENT_W - 5000];
const t3 = table(t3W, [
  ['구분', '전장 L (mm)', '적용 작업'],
  ['Long', '100 초과 ~ 150 이하', '외경, 옆날, 골수리'],
  ['Ex-Long', '150 초과', '외경, 옆날, 골수리'],
]);
const warnB = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W],
  rows: [new TableRow({ children: [new TableCell({ width: { size: CONTENT_W, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, color: 'auto', fill: CREAM },
    borders: { top: { style: BorderStyle.SINGLE, size: 8, color: INK }, bottom: { style: BorderStyle.SINGLE, size: 8, color: INK }, left: { style: BorderStyle.SINGLE, size: 8, color: INK }, right: { style: BorderStyle.SINGLE, size: 8, color: INK } },
    margins: { top: 100, bottom: 100, left: 160, right: 160 },
    children: [new Paragraph({ children: [run('견본: ', { bold: true, size: TBL }), run('보고서 양식 B 견본임. 실제 발송 전 승인자 검토와 서명이 필요하며, 할증률과 확정 금액은 정가표와 입고 검수 결과로 안내함', { size: TBL })] })] })] })],
});

const children = [
  band,
  p([run('거래처용 기술 자료', { color: GRAY })], { spacing: { before: 120, after: 160 } }),
  info,
  new Paragraph({ children: [], spacing: { after: 80 } }),
  warnB,
  p('재연마를 맡기시기 전에 확인하실 내용과, 공구가 들어온 뒤 당사가 확인하는 항목을 정리하여 드립니다. 주문 화면에 표시되는 금액은 선택하신 사양 기준의 예상 금액이며, 입고 검수를 마친 뒤 확정 금액을 안내드립니다.', { spacing: { before: 200, after: 140, line: 312 } }),
  h1('1. 요약'),
  item('가.', '입고 후 브랜드, 사양, 손상 상태를 확인하고 확정 금액을 안내함'),
  item('나.', '전장 100 mm 초과 공구는 외경, 옆날, 골수리 작업에 할증이 붙음'),
  item('다.', '날장이 남지 않은 공구는 날을 새로 만들어야 하므로 제작으로 견적함'),
  h1('2. 대상 공구'),
  caption('표 1. 재연마 접수 기준'),
  t1,
  h1('3. 입고 검수 항목'),
  caption('표 2. 입고 검수 항목과 처리'),
  t2,
  h1('4. 금액이 바뀌는 경우'),
  h2('가. 전장 할증'),
  caption('표 3. 전장 할증 구간'),
  t3,
  note('※ 전장이 정확히 100 mm, 150 mm 인 공구는 할증하지 않음. 밑날 작업은 전장 할증 대상이 아님. 할증률은 당사 재연마 정가표를 따름'),
  h2('나. 그 밖의 경우'),
  item('1)', '주문 때 고른 사양과 실물이 다르면 실물 기준으로 다시 견적함'),
  item('2)', '할인 대상 브랜드가 아닌 공구는 일반 금액으로 안내함'),
  h1('5. 재연마가 어려운 경우'),
  item('가.', '날경 D1 이하 공구, 다이아몬드 코팅 공구는 접수하지 않음'),
  item('나.', '날장이 남지 않은 공구는 제작 견적으로 안내함'),
  item('다.', '형상이나 장비 조건으로 연삭이 어려운 공구는 사유를 알려 드리고 반송함. 반송 비용은 당사가 부담함'),
  h1('6. 유의 사항'),
  item('가.', '금액이나 작업 내용이 바뀌면 작업 전에 전화나 팩스로 먼저 연락드림'),
  item('나.', '재연마 후 날경과 날장은 신품보다 줄어듦'),
  note('※ 참고 자료: 당사 재연마 정가표(2026. 11. 1. 적용)'),
];

const doc = new Document({
  creator: '생산팀', title: '재연마 입고 검수 기준 안내 (견본 B)',
  styles: { default: { document: { run: { font: KO, size: BODY, color: INK } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: KO, size: 34, bold: true, color: NAVY }, paragraph: { outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: KO, size: BODY, bold: true, color: INK }, paragraph: { outlineLevel: 1 } },
    ] },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 850, bottom: 850, left: MARGIN_LR, right: MARGIN_LR, header: 400, footer: 400 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 120 },
      children: [new ImageRun({ type: 'png', data: fs.readFileSync(LOGO), transformation: { width: 120, height: 40 }, altText: { title: '코리아툴링', description: '(주)코리아툴링 로고', name: 'logo' } })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
      children: [
        new TextRun({ text: '재연마 입고 검수 기준 안내', font: KO, size: 20, color: GRAY }),
        new TextRun({ text: '\tKOREA TOOLING  ', font: LATIN, size: 20, color: GRAY }),
        new TextRun({ children: [PageNumber.CURRENT], font: LATIN, size: 20, color: GRAY }),
      ] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log('written', OUT); });
