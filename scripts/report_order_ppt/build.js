// 재연마 수주 감소 원인 분석 — 워크숍 발표 (2026-11-27). 코고툴 발표양식 B안(templates/코고툴양식_만들기/build_ppt_sample.js 디자인)
// 실행: node build.js 출력.pptx   · 실명판: REAL=1 node build.js wiki/_private/reports/…_실명.pptx
const pptxgen = require('pptxgenjs');
const path = require('path');
const { applyTheme } = require('./apply_theme.js');
const { apply: R } = require('../report_order_decline/realname.js');
const D = require('../report_order_decline/data.json');
const E = require('../report_order_summary_1010/data2.json');
const OUT = process.argv[2] || 'deck.pptx';
const LOGO = path.join(__dirname, 'logo.png');

const NAVY = '231F20', INK = '231F20', GRAY = '58595B', LAV = 'E4E0F0', BLUE = 'D7D2E9', ORANGE = 'E8581C', CREAM = 'FFFBE5', LIGHT = 'A7A9AC', MID = '8C86B4';
const THEME = { name: 'COGO TOOL', headFontFace: '맑은 고딕', bodyFontFace: '맑은 고딕',
  colors: { dk1: INK, lt1: 'FFFFFF', dk2: NAVY, lt2: LAV, accent1: NAVY, accent2: GRAY, accent3: LIGHT, accent4: '2A3E92', accent5: '99D420', accent6: 'D22027', hlink: NAVY, folHlink: GRAY } };
const KO = '맑은 고딕', LATIN = 'Arial';
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.theme = { headFontFace: KO, bodyFontFace: KO };
pres.title = '재연마 수주 감소 원인 분석'; pres.author = '생산팀 한경준';
const W = 13.333, H = 7.5, M = 0.6;
const SECTIONS = ['요약', '전년 비교', '하반기 수주', '원인', '결론'];
const f = (n) => Number(n).toLocaleString('en-US');
const pct = (a, b) => { const v = (b - a) / a * 100; return (v >= 0 ? '+' : '') + v.toFixed(1); };
const sum = (a, i, j) => a.slice(i, j).reduce((x, y) => x + y, 0);

pres.defineSlideMaster({ title: 'CONTENT', background: { color: 'FFFFFF' }, objects: [
  { rect: { x: 0, y: 0, w: W, h: 1.1, fill: { color: NAVY }, line: { color: NAVY } } },
  { text: { text: 'COGOTOOL', options: { x: W - 2.9, y: H - 0.5, w: 1.6, h: 0.3, fontFace: LATIN, fontSize: 12, color: GRAY, align: 'right', margin: 0 } } },
  { text: { text: '자료 기준 2026. 11. 10. ERP 저장본, 재연마 수주 감소 원인 분석 보고 제1판', options: { x: M, y: H - 0.5, w: 9, h: 0.3, fontFace: KO, fontSize: 12, color: GRAY, margin: 0 } } },
  { placeholder: { options: { name: 'title', type: 'title', x: M, y: 0.2, w: 9.0, h: 0.7, fontFace: KO, fontSize: 36, bold: true, color: 'FFFFFF', align: 'left', valign: 'middle', margin: 0 }, text: '' } },
  { placeholder: { options: { name: 'msg', type: 'body', x: M, y: 1.35, w: W - 2 * M - 0.5, h: 0.6, fontFace: KO, fontSize: 22, bold: true, color: NAVY, valign: 'middle', margin: 0 }, text: '' } },
], slideNumber: { x: W - 1.2, y: H - 0.5, w: 0.6, h: 0.3, fontFace: LATIN, fontSize: 12, color: GRAY, align: 'right' } });

const msg = (s, t) => s.addText([{ text: '▶ ', options: { color: ORANGE } }, { text: R(t) }], { placeholder: 'msg' });
function tabs(s, cur) {
  SECTIONS.forEach((_, i) => { const on = i === cur;
    s.addShape(pres.shapes.RECTANGLE, { x: W - 0.42, y: 1.35 + i * 0.62, w: 0.42, h: 0.54, fill: { color: on ? ORANGE : LAV }, line: { color: on ? ORANGE : LAV }, objectName: `tab-${i + 1}` });
    s.addText(String(i + 1), { x: W - 0.42, y: 1.35 + i * 0.62, w: 0.42, h: 0.54, fontFace: LATIN, fontSize: 16, bold: true, color: INK, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: `tab-num-${i + 1}` }); });
}
const code = (s, c) => s.addText(c, { x: W - 4.1, y: 0.2, w: 3.5, h: 0.7, fontFace: LATIN, fontSize: 26, bold: true, italic: true, color: 'FFFFFF', align: 'right', valign: 'middle', margin: 0, isTextBox: true, objectName: 'code' });
const hdr = (t) => ({ text: R(t), options: { bold: true, fill: { color: LAV }, color: INK } });
const cell = (t, o = {}) => ({ text: R(String(t)), options: o });
const num = (t, o = {}) => cell(t, { align: 'right', ...o });
const cap = (s, t, x, y, w) => s.addText(R(t), { x, y, w, h: 0.35, fontFace: KO, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'cap-' + t.slice(0, 4) });
const TB = { fontFace: KO, color: INK, valign: 'middle', border: { type: 'solid', pt: 0.75, color: 'C9C7C7' }, margin: [0.03, 0.1, 0.03, 0.1] };
const CH = { valAxisLabelColor: GRAY, catAxisLabelColor: INK, valAxisLabelFontSize: 14, catAxisLabelFontSize: 14, valAxisLabelFontFace: '+mn-lt', catAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'E1E0E0', size: 0.5 }, catGridLine: { style: 'none' }, showLegend: true, legendPos: 'b', legendFontSize: 14, legendColor: INK, legendFontFace: '+mn-lt',
  titleFontSize: 14, titleColor: INK, titleFontFace: '+mn-lt', showTitle: true, valAxisLabelFormatCode: '#,##0' };
function stat(s, x, y, w, h, label, value, unit, note, fill = BLUE, id = 's') {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, objectName: id + '-bg' });
  s.addText(R(label), { x: x + 0.2, y: y + 0.15, w: w - 0.4, h: 0.4, fontFace: KO, fontSize: 16, bold: true, color: INK, margin: 0, isTextBox: true, objectName: id + '-label' });
  s.addText([{ text: value, options: { fontSize: 44, bold: true, color: NAVY, fontFace: LATIN } }, { text: unit, options: { fontSize: 20, color: NAVY, fontFace: LATIN } }], { x: x + 0.2, y: y + 0.6, w: w - 0.4, h: 0.8, margin: 0, isTextBox: true, objectName: id + '-value' });
  if (note) s.addText(R(note), { x: x + 0.2, y: y + 1.45, w: w - 0.4, h: h - 1.6, fontFace: KO, fontSize: 14, color: INK, margin: 0, valign: 'top', isTextBox: true, objectName: id + '-note' });
}
module.exports = { pres, W, H, M, R, D, E, f, pct, sum, msg, tabs, code, hdr, cell, num, cap, TB, CH, stat, LOGO, OUT, THEME, applyTheme, NAVY, INK, GRAY, LAV, BLUE, ORANGE, CREAM, LIGHT, MID, KO, LATIN };
require('./slides.js');
