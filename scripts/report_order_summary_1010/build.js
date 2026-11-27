// 재연마 수주 감소 원인 분석 보고 (2026-11-27) — 코고툴 B안, report_ai_trend_v2/build.js 복사본
// 실행: node build.js 출력.docx   (본문 데이터: content.js 참고 문헌, body.js 본문)
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, VerticalAlign, Header, Footer, PageNumber, ImageRun, TabStopType, HeadingLevel, ExternalHyperlink,
} = require('docx');
const { REFS } = require('../report_order_decline/content.js');

const OUT = process.argv[2] || 'report.docx';
const LOGO = path.join(__dirname, 'logo.png');
const DOC_TITLE = '2026년 1~10월 재연마 수주와 출하 집계';

const NAVY = '231F20', INK = '231F20', GRAY = '58595B', LAV = 'E4E0F0', CREAM = 'FFFBE5', LINE = 'C9C7C7', LINK = '1F4E9A';
const KO = '맑은 고딕', LATIN = 'Arial';
const BODY = 30, TBL = 26, TITLE = 44, SMALL = 22;
const PAGE_W = 11906, MARGIN_LR = 1134, CONTENT_W = PAGE_W - 2 * MARGIN_LR;

const run = (t, o = {}) => new TextRun({ text: t, font: KO, size: BODY, color: INK, ...o });
const p = (children, o = {}) => new Paragraph({ children: Array.isArray(children) ? children : [run(children)], spacing: { after: 140, line: 312 }, ...o });
const item = (mark, text, level = 0) => new Paragraph({ children: [run(`${mark} `), run(text)], indent: { left: 360 + level * 400, hanging: 360 }, spacing: { after: 60, line: 312 } });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: KO, size: 34, bold: true, color: NAVY })], spacing: { before: 280, after: 120 }, keepNext: true });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: KO, size: BODY, bold: true, color: INK })], spacing: { before: 160, after: 80 }, keepNext: true });
const caption = (t) => new Paragraph({ children: [run(t, { size: TBL, bold: true })], spacing: { before: 120, after: 60 }, keepNext: true });
const note = (t) => new Paragraph({ children: [run(t, { size: SMALL, color: GRAY })], spacing: { before: 40, after: 120 } });
const gap = () => new Paragraph({ children: [], spacing: { after: 60 } });

const border = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const borders = { top: border, bottom: border, left: border, right: border };
const NB = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
function tcell(text, width, o = {}) {
  const { fill, bold, color, align, span, size } = o;
  return new TableCell({ width: { size: width, type: WidthType.DXA }, borders, columnSpan: span,
    shading: fill ? { type: ShadingType.CLEAR, color: 'auto', fill } : undefined,
    verticalAlign: VerticalAlign.CENTER, margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: String(text).split('\n').map((line) => { const m = line.match(/^(하는 일|방법): (.*)$/);
      return new Paragraph({ alignment: align || AlignmentType.LEFT, spacing: { after: 30 }, children: m
        ? [run(m[1] + ': ', { size: size || TBL, bold: true, color: color || INK }), run(m[2], { size: size || TBL, bold, color: color || INK })]
        : [run(line, { size: size || TBL, bold, color: color || INK })] }); }) });
}
function table(widths, rows, headRow = true, size) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({ tableHeader: headRow && ri === 0, cantSplit: true, children: r.map((c, ci) => {
      const o = typeof c === 'string' ? { t: c } : c;
      const w = o.span ? widths.slice(ci, ci + o.span).reduce((a, b) => a + b, 0) : widths[ci];
      return tcell(o.t, w, headRow && ri === 0 ? { fill: LAV, bold: true, size } : { ...o, size });
    }) })) });
}
const W = (...fr) => { const s = fr.reduce((a, b) => a + b, 0); const w = fr.map((f) => Math.floor(CONTENT_W * f / s)); w[w.length - 1] += CONTENT_W - w.reduce((a, b) => a + b, 0); return w; };
const bandCell = (w, children, m) => new TableCell({ width: { size: w, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: 'auto', fill: NAVY },
  borders: { top: NB, bottom: NB, left: NB, right: NB }, verticalAlign: VerticalAlign.CENTER, margins: m, children });
const warnBox = (label, text) => new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W],
  rows: [new TableRow({ children: [new TableCell({ width: { size: CONTENT_W, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: 'auto', fill: CREAM },
    borders: { top: { style: BorderStyle.SINGLE, size: 8, color: INK }, bottom: { style: BorderStyle.SINGLE, size: 8, color: INK }, left: { style: BorderStyle.SINGLE, size: 8, color: INK }, right: { style: BorderStyle.SINGLE, size: 8, color: INK } },
    margins: { top: 100, bottom: 100, left: 160, right: 160 },
    children: [new Paragraph({ children: [run(label, { bold: true, size: TBL }), run(text, { size: TBL })] })] })] })] });
const refParas = () => REFS.map(([pub, date, title, url], i) => new Paragraph({ indent: { left: 560, hanging: 560 }, spacing: { after: 70, line: 280 },
  children: [run(`[${i + 1}] `, { size: SMALL, bold: true }), run(`${pub}, ${date.endsWith('.') ? date : date + '.'} 「${title}」 `, { size: SMALL }),
    new ExternalHyperlink({ link: url, children: [new TextRun({ text: url, font: LATIN, size: 18, color: LINK, underline: {} })] })] }));

const img = (file, wCm, alt) => { const b = fs.readFileSync(path.join(__dirname, 'fig', file)); const pw = b.readUInt32BE(16), ph = b.readUInt32BE(20);
  const w = Math.round(wCm / 2.54 * 96), h = Math.round(w * ph / pw);
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 40 }, keepNext: true,
    children: [new ImageRun({ type: 'png', data: b, transformation: { width: w, height: h }, altText: { title: alt, description: alt, name: file } })] }); };
const H = { img, run, p, item, h1, h2, caption, note, gap, table, W, warnBox, refParas, CONTENT_W, NAVY, LAV, SMALL, AlignmentType, TableCell, TableRow, Table, Paragraph, TextRun, WidthType, VerticalAlign, ShadingType, bandCell, DOC_TITLE, LATIN, KO, TITLE };
const children = require('./body.js')(H);

const doc = new Document({ creator: '생산팀 한경준', title: DOC_TITLE,
  styles: { default: { document: { run: { font: KO, size: BODY, color: INK } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: KO, size: 34, bold: true, color: NAVY }, paragraph: { outlineLevel: 0, keepNext: true, spacing: { before: 280, after: 120 } } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: KO, size: BODY, bold: true, color: INK }, paragraph: { outlineLevel: 1, keepNext: true, spacing: { before: 160, after: 80 } } },
    ] },
  sections: [{ properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 850, bottom: 850, left: MARGIN_LR, right: MARGIN_LR, header: 400, footer: 400 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 120 },
      children: [new ImageRun({ type: 'png', data: fs.readFileSync(LOGO), transformation: { width: 96, height: 40 }, altText: { title: 'COGOTOOL', description: 'COGOTOOL 로고', name: 'logo' } })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }], children: [
      new TextRun({ text: DOC_TITLE, font: KO, size: 20, color: GRAY }), new TextRun({ text: '\tCOGOTOOL  ', font: LATIN, size: 20, color: GRAY }),
      new TextRun({ children: [PageNumber.CURRENT], font: LATIN, size: 20, color: GRAY })] })] }) },
    children }] });
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log('written', OUT); });
