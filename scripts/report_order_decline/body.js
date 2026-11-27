// 재연마 수주 감소 원인 분석 보고 — 본문 (2026-11-27)
// 뼈대: 머리 정보, 요약 3줄과 표 1, 1 서론, 2 분석 방법, 3 분석 결과, 4 고찰, 5 결론 및 향후 계획, 참고 문헌, 부록
// 문체: 개조식, 고찰만 서술식 (standards/보고서-작성-규칙 §5). 수치는 data.json(analyze.py) 값
const D = require('./data.json');
const f = (n) => Number(n).toLocaleString('en-US');
const pct = (a, b) => { const v = (b - a) / a * 100; return (v >= 0 ? '+' : '') + v.toFixed(1); };
const sum = (a, i, j) => a.slice(i, j).reduce((x, y) => x + y, 0);

module.exports = (H) => {
  const { img, run, p, item, h1, h2, caption, note, gap, table, W, refParas, CONTENT_W, NAVY, LAV, AlignmentType, Table, TableRow, Paragraph, TextRun, WidthType, bandCell, DOC_TITLE, LATIN, KO, TITLE, SMALL } = H;
  const C = AlignmentType.CENTER, R = AlignmentType.RIGHT;
  const n = (t) => ({ t: String(t), align: R });
  const lab = (t) => ({ t, fill: LAV, bold: true });
  const O = D['수주'];
  const [jul, aug] = [O[1], O[2]];
  const avgJul = jul['기타'] / jul['영업일'];
  const dayEff = Math.round(avgJul * (jul['영업일'] - aug['영업일']));
  const rateEff = (aug['기타'] - jul['기타']) + dayEff;
  const tot = aug['합계'] - jul['합계'];
  const sh = (v) => (v / tot * 100).toFixed(1);
  const P = D['기간'], s25 = D['2025'], s26 = D['2026'];
  const p8 = P['8~10월']['대형3제외'];
  const bands = ['6 mm 이하', '6 초과 12 mm 이하', '12 초과 20 mm 이하', '20 mm 초과'];
  const cls = [0, 1].map((k) => bands.reduce((s, b) => s + D['지름'][b][k], 0));
  const small = [0, 1].map((k) => (D['지름']['6 mm 이하'][k] / cls[k] * 100).toFixed(1));
  const c26 = sum(s26['거래처 C'], 0, 7), o26 = sum(s26['거래처 O'], 0, 7), t26 = sum(s26['전체'], 0, 7);
  const c25 = sum(s25['거래처 C'], 0, 12);
  const X = { f, pct, sum, n, lab, O, jul, aug, avgJul, dayEff, rateEff, tot, sh, P, s25, s26, p8, bands, cls, small, c26, o26, t26, c25, C, R };

  // 제목 띠와 머리 정보
  const bandW = [CONTENT_W - 2700, 2700];
  const band = new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: bandW, rows: [new TableRow({ children: [
    bandCell(bandW[0], [new Paragraph({ children: [new TextRun({ text: DOC_TITLE, font: KO, size: TITLE, bold: true, color: 'FFFFFF' })] })], { top: 90, bottom: 90, left: 220, right: 100 }),
    bandCell(bandW[1], [new Paragraph({ alignment: R, children: [new TextRun({ text: 'ORDER ANALYSIS', font: LATIN, size: 24, bold: true, italics: true, color: 'FFFFFF' })] })], { top: 90, bottom: 90, left: 100, right: 220 }),
  ] })] });
  const infoW = [1500, CONTENT_W / 2 - 1500, 1500, CONTENT_W / 2 - 1500];
  X.band = band;
  X.info = table(infoW, [
    [lab('과제명'), '2026년 하반기 재연마 수주 감소 원인 분석', lab('문서번호'), '수주감소_원인분석_보고_20261127'],
    [lab('보고일'), '2026. 11. 27.', lab('자료 기간'), '2025. 1. ~ 2026. 11. 10.'],
    [lab('작성'), '생산팀 한경준', lab('검토'), ''],
    [lab('상태'), require('./realname.js').ON ? '참고 보고, 실명판 사내 전용' : '참고 보고', lab('판'), '제1판'],
    [lab('대상'), '재연마 수주와 출하 수량', lab('제외'), '금액과 단가, 신품 공구'],
  ], false);
  const nv = (t) => ({ t, fill: NAVY, bold: true, color: 'FFFFFF', align: C });
  X.summary = table([1300, CONTENT_W - 1300], [
    [nv('결론'), '8월 이후 수주 감소는 거래처 C의 거래 종료와 거래처 W의 발주 시점 변동, 8월 영업일 감소가 겹친 결과임. 거래처 O는 탭 재연마 특수 거래로 따로 봄. 이 3곳을 뺀 나머지 거래처의 수주와 출하는 줄지 않았음'],
    [nv('근거'), '7월에서 8월로 줄어든 수주 972개 중 거래처 W가 398개, 거래처 C가 230개, 영업일 4일 감소가 약 251개를 차지함. 2026년 1~10월 출하는 18,628개로 전년 같은 기간보다 19.9 % 많으며 3곳을 빼도 6.9 % 많음'],
    [nv('요청'), '거래처 AK의 수주 공백을 영업팀에서 확인해 주기 바람. 2022년부터 34개월 거의 매달 거래했으나 2026. 5. 27. 뒤 수주 없음'],
  ], false);
  return require('./body_tables.js')(H, X);
};
