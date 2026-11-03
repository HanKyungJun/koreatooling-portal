// 코고툴 디자인 시스템 v3 적용 보고서 샘플 — 넥 원통연삭 시험 결과(견본 A v4 내용을 줄여 옮김)
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
      children: [new Paragraph({ children: [new TextRun({ text: '넥 원통연삭 시험 결과 보고', font: KO, size: TITLE, bold: true, color: 'FFFFFF' })] })] }),
    new TableCell({ width: { size: bandW[1], type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: 'auto', fill: NAVY },
      borders: { top: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, bottom: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } },
      verticalAlign: VerticalAlign.CENTER, margins: { top: 90, bottom: 90, left: 100, right: 220 },
      children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: 'NECK TEST', font: LATIN, size: 32, bold: true, italics: true, color: 'FFFFFF' })] })] }),
  ] })],
});

// ── 머리 정보 표 ──
const lab = (t) => ({ t, fill: LAV, bold: true });
const infoW = [1500, CONTENT_W / 2 - 1500, 1500, CONTENT_W / 2 - 1500];
const info = table(infoW, [
  [lab('과제명'), '초경 엔드밀 넥 원통연삭 조건 확립', lab('문서번호'), '넥_원통연삭_시험결과_보고_20261022_v4'],
  [lab('보고일'), '2026. 10. 29.', lab('시험 기간'), '2026. 10. 19. ~ 2026. 10. 20.'],
  [lab('작성'), '생산팀 한경준, 자료 정리 및 계산 보조 Claude', lab('상태'), '시험 단계(양산 미적용)'],
  [lab('장비'), 'ANCA GX7, iGrind 원통연삭', lab('시험 대상'), 'D3 엔드밀 2개(실측 D 2.955 mm, 2.970 mm)'],
], false);

// ── 요약 3줄 ──
const sumW = [1300, CONTENT_W - 1300];
const nv = (t) => ({ t, fill: NAVY, bold: true, color: 'FFFFFF', align: AlignmentType.CENTER });
const summary = table(sumW, [
  [nv('결론'), '정삭만 적용한 테스트 1은 넥 지름 합격, 황삭 대각선 진입을 추가한 테스트 2는 진입부 자국이 없어졌으나 넥 끝 쪽 지름 초과로 보류함'],
  [nv('근거'), '테스트 1 넥 지름 2.853 ~ 2.862 mm(허용 2.807 ~ 2.881 mm). 두 공구 모두 측정값이 입력값보다 0.063 ~ 0.065 mm 큼(공구 2개 실측)'],
  [nv('요청'), '요청 없음(참고 보고). 휠 드레싱 후 테스트 3 진행 예정'],
], false);

const t1W = [2400, 2300, 2409, 2529];
const t1 = table(t1W, [
  ['평가 항목', '판정 기준', '테스트 1, 1번 공구', '테스트 2, 2번 공구'],
  ['넥 지름 (mm)', '0.95 ~ 0.975 × 실측 D', '2.853 ~ 2.862, 합격', '2.890 ~ 2.907, 보류'],
  ['진입부 자국', '없음', '있음, 불합격', '없음, 합격'],
  ['측정값 − 입력값 (mm)', '판정 대상 아님', '머리 쪽 +0.063', '머리 쪽 +0.065'],
]);

const t2W = [3200, 3219, 3219];
const t2 = table(t2W, [
  ['항목 (단위)', '테스트 1, 1번 공구', '테스트 2, 2번 공구'],
  ['입력 지름 (mm)', '3.05, 2.93, 2.860, 2.790 연속 4회', '2.825 1회'],
  ['황삭', '사용 안 함', '대각선 진입, 반경 0.075 mm 1패스'],
  ['정삭 여유 (mm)', '1.333', '0.020'],
  ['정삭 진입 속도 (mm/min)', '1 ~ 3회 5.0, 4회 1.0', '0.5'],
  ['정삭 이송 (mm/min), 공구 회전 (rpm)', { t: '3.0, 25', span: 2, align: AlignmentType.CENTER }],
]);

const t3W = [1900, 2000, 1869, 2000, 1869];
const t3 = table(t3W, [
  ['위치', '테스트 1, 4회 (mm)', '판정', '테스트 2 (mm)', '판정'],
  ['머리 쪽', '2.853 ~ 2.854', '합격', '2.890', '합격'],
  ['중간', '2.854 ~ 2.855', '합격', '2.905', '보류'],
  ['테이퍼 쪽', '2.858 ~ 2.862', '합격', '2.907', '보류'],
]);

// 경고 상자(table-cream 바탕, 「경고:」 글자)
const warnW = [CONTENT_W];
const warn = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: warnW,
  rows: [new TableRow({ children: [new TableCell({ width: { size: CONTENT_W, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, color: 'auto', fill: CREAM },
    borders: { top: { style: BorderStyle.SINGLE, size: 8, color: INK }, bottom: { style: BorderStyle.SINGLE, size: 8, color: INK }, left: { style: BorderStyle.SINGLE, size: 8, color: INK }, right: { style: BorderStyle.SINGLE, size: 8, color: INK } },
    margins: { top: 100, bottom: 100, left: 160, right: 160 },
    children: [new Paragraph({ children: [run('경고: ', { bold: true, size: TBL }), run('테스트 3의 테이퍼 쪽 패스당 반경 절입은 약 0.19 mm(계산)로 사내 실적 0.075 mm의 약 2.5배임. 첫 패스 부하가 5%를 넘으면 중단함', { size: TBL })] })] })] })],
});

const children = [
  band,
  p([run('D3 초경 엔드밀 시험 공구 2개, ANCA GX7 원통연삭', { color: GRAY })], { spacing: { before: 120, after: 160 } }),
  info,
  h1('요약'),
  summary,
  caption('표 1. 시험 결과 요약'),
  t1,
  note('※ 신뢰도 구분: 실측(사내에서 직접 측정), 계산(측정값으로 계산), 추정(해석)'),

  h1('1. 서론'),
  item('가.', '넥은 날 뒤쪽 몸통을 날지름(D)보다 가늘게 깎은 부분으로, 깊은 가공에서 공구 몸통이 가공 벽에 닿지 않게 하는 역할을 함'),
  item('나.', '본 시험은 ANCA GX7에서 넥 지름을 목표 범위에 넣는 입력 조건을 찾고, 넥 시작부 진입 자국을 없애는 방법을 확인하는 데 목적이 있음'),
  item('다.', '평가 항목은 넥 지름 3곳, 진입부 자국, 스핀들 부하이며 진원도, 표면 거칠기(Ra), 양산 적용은 제외함'),

  h1('2. 시험 방법'),
  h2('가. 시험 조건'),
  caption('표 2. 시험 조건'),
  t2,
  note('※ 휠 지름 125.102 mm, 회전수 3,500 rpm. Vc = π × 125.102 × 3,500 ÷ 60,000 = 22.93 m/s(계산, 사내 상한 25 m/s 이내)'),
  h2('나. 판정 기준'),
  item('1)', '넥 지름은 실측 날지름 D의 0.95 ~ 0.975배를 허용 범위로 함. 제조사 롱넥 엔드밀 31개 품목에서 역산한 사내 기준임'),
  item('2)', '허용 범위: 1번 공구 2.807 ~ 2.881 mm, 2번 공구 2.822 ~ 2.896 mm. 상한 초과는 보류, 하한 미만은 불합격'),

  h1('3. 시험 결과'),
  caption('표 3. 넥 위치별 지름 (디지털 마이크로미터, 실측)'),
  t3,
  new Paragraph({ children: [], spacing: { after: 60 } }),
  item('가.', '테스트 1은 4회째에 세 곳 모두 허용 범위 안에 들었으나, 진입부 같은 위치에 매회 자국이 남음'),
  item('나.', '테스트 2는 진입부 자국이 없음. 현장에서 현미경 사진으로 확인함. 중간과 테이퍼 쪽은 상한을 0.009 ~ 0.011 mm 넘음'),
  item('다.', '측정값과 입력값의 차이는 테스트 1 머리 쪽 +0.063 mm, 테스트 2 머리 쪽 +0.065 mm로 거의 같음'),

  h1('4. 고찰'),
  p('정삭은 항상 넥 시작 쪽 끝에서 지름 방향으로 진입하므로, 정삭 여유가 크면 같은 위치에 진입 자국이 남는 것으로 판단된다. 황삭으로 대부분을 깎고 정삭 여유를 0.020 mm로 작게 남긴 테스트 2에서 자국이 없어진 것과 맞는다.'),
  p('실제로 깎인 양이 약 10배 달랐는데도 측정값과 입력값의 차이는 +0.055 ~ +0.075 mm 범위에서 거의 일정했다. 깎는 양에 따라 커지는 공구 처짐보다는 휠 지름이나 위치 기준의 고정 오차일 가능성이 높다고 판단된다. 휠 지름은 시험 중 다시 측정하지 않았다.'),
  p('넥 뒤 테이퍼 각도(12°)가 휠 12° 면의 각도와 같아, 넥 끝의 테이퍼는 휠 12° 면이 만든 것으로 판단된다. 테스트 1의 계산 L2 12.44 mm는 측정 약 12.5 mm와 맞으나 테스트 2는 약 1.1 mm 차이가 있어, 이 관계는 사내 기준으로 정하지 않는다.'),

  h1('5. 결론 및 향후 계획'),
  h2('가. 결론'),
  item('1)', '정삭만으로 연삭한 테스트 1은 4회째 넥 지름 2.853 ~ 2.862 mm로 치수 합격임'),
  item('2)', '황삭 대각선 진입, 정삭 여유 0.020 mm, 정삭 진입 속도 0.5 mm/min을 함께 적용하면 진입부 자국이 없어짐'),
  item('3)', '드레싱 전 휠 기준으로는 입력값을 목표보다 약 0.065 mm 작게 넣어야 했음'),
  item('4)', '모든 결과는 공구 2개의 시험값이며 양산에는 적용하지 않음'),
  h2('나. 향후 계획'),
  item('1)', '휠 드레싱 전후 휠 지름을 측정하고 다시 등록함'),
  item('2)', '테스트 3에서 넥 구간을 3번 나눠 깎고 패스마다 지름과 부하를 측정함'),
  new Paragraph({ children: [], spacing: { after: 60 } }),
  warn,
  note('※ 이 문서는 코고툴 디자인 시스템 v3 적용 샘플임. 내용은 넥 원통연삭 시험 결과 보고 제4판(2026. 10. 29.)을 줄여 옮김'),
];

const doc = new Document({
  creator: '생산팀 한경준', title: '넥 원통연삭 시험 결과 보고 (코고툴 디자인 샘플)',
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
        new TextRun({ text: '넥 원통연삭 시험 결과 보고', font: KO, size: 20, color: GRAY }),
        new TextRun({ text: '\tCOGOTOOL  ', font: LATIN, size: 20, color: GRAY }),
        new TextRun({ children: [PageNumber.CURRENT], font: LATIN, size: 20, color: GRAY }),
      ] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log('written', OUT); });
