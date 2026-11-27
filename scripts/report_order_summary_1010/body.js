// 2026년 1~10월 재연마 수주와 출하 집계 — 본문 (2026-11-27, 워크숍 보고 대비 요약판)
const D = require('../report_order_decline/data.json');
const E = require('./data2.json');
const f = (n) => Number(n).toLocaleString('en-US');
const pct = (a, b) => { const v = (b - a) / a * 100; return (v >= 0 ? '+' : '') + v.toFixed(1); };
const sum = (a, i, j) => a.slice(i, j).reduce((x, y) => x + y, 0);
module.exports = (H) => {
  const { item, h1, h2, caption, note, gap, table, W, CONTENT_W, NAVY, LAV, AlignmentType, Table, TableRow, Paragraph, TextRun, WidthType, bandCell, DOC_TITLE, LATIN, KO, TITLE, SMALL, img } = H;
  const R = AlignmentType.RIGHT, C = AlignmentType.CENTER;
  const n = (t) => ({ t: String(t), align: R });
  const lab = (t) => ({ t, fill: LAV, bold: true });
  const s25 = D['2025'], s26 = D['2026'], P = E.PROD;
  const so = {}; D['수주'].forEach((r) => { so[Number(r.ym.slice(5))] = r; });
  const sh25 = sum(s25['전체'], 0, 10), sh26 = sum(s26['전체'], 0, 10), pr25 = sum(P['2025'], 0, 10), pr26 = sum(P['2026'], 0, 10);
  const bandW = [CONTENT_W - 1900, 1900];
  const band = new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: bandW, rows: [new TableRow({ children: [
    bandCell(bandW[0], [new Paragraph({ children: [new TextRun({ text: DOC_TITLE, font: KO, size: TITLE - 4, bold: true, color: 'FFFFFF' })] })], { top: 90, bottom: 90, left: 220, right: 100 }),
    bandCell(bandW[1], [new Paragraph({ alignment: R, children: [new TextRun({ text: 'SUMMARY', font: LATIN, size: 22, bold: true, italics: true, color: 'FFFFFF' })] })], { top: 90, bottom: 90, left: 100, right: 220 }),
  ] })] });
  const infoW = [1500, CONTENT_W / 2 - 1500, 1500, CONTENT_W / 2 - 1500];
  const info = table(infoW, [
    [lab('보고일'), '2026. 11. 27.', lab('자료 기간'), '2025. 1. ~ 2026. 10.'],
    [lab('작성'), '생산팀 한경준', lab('검토'), ''],
    [lab('대상'), '재연마 수주, 출하, 생산 수량', lab('제외'), require('../report_order_decline/realname.js').ON ? '금액과 단가. 실명판 사내 전용' : '금액과 단가'],
  ], false);
  const nv = (t) => ({ t, fill: NAVY, bold: true, color: 'FFFFFF', align: C });
  const summary = table([1300, CONTENT_W - 1300], [
    [nv('결론'), `2026년 1~10월 출하는 ${f(sh26)}개, 생산은 ${f(pr26)}개로 전년 같은 기간보다 각각 ${pct(sh25, sh26)} %, ${pct(pr25, pr26)} % 많음. 8월 이후 월 수주는 6~7월보다 낮으나 8~10월 출하는 전년 수준을 유지함`],
    [nv('근거'), `월 수주는 6월 ${f(so[6]['합계'])}개, 8월 ${f(so[8]['합계'])}개, 10월 ${f(so[10]['합계'])}개임. 8월 감소는 거래처 C 거래 종료와 거래처 W 발주 시점, 8월 영업일 감소로 대부분 설명되며 나머지 거래처의 하루 평균 수주는 9~10월에 7월보다 많음`],
    [nv('요청'), '거래처 C 거래 종료 사유와 거래처 O 발주 공백 사유를 영업팀에서 확인해 주기 바람'],
  ], false);
  const t1 = table(W(0.8, 1.2, 1.2, 1.0, 1.2, 1.2, 1.0, 1.3, 1.1), [
    ['월', '출하 2025 (개)', '출하 2026 (개)', '증감 (%)', '생산 2025 (개)', '생산 2026 (개)', '증감 (%)', '수주 2026 (개)', '출하 거래처 2026 (곳)'],
    ...Array.from({ length: 10 }, (_, i) => [`${i + 1}월`, n(f(s25['전체'][i])), n(f(s26['전체'][i])), n(pct(s25['전체'][i], s26['전체'][i])), n(f(P['2025'][i])), n(f(P['2026'][i])), n(pct(P['2025'][i], P['2026'][i])), n(so[i + 1] ? f(so[i + 1]['합계']) : ''), n(s26['고객수'][i])]),
    [{ t: '계', bold: true }, n(f(sh25)), n(f(sh26)), n(pct(sh25, sh26)), n(f(pr25)), n(f(pr26)), n(pct(pr25, pr26)), n(f(sum([6, 7, 8, 9, 10].map((m) => so[m]['합계']), 0, 5))), ''],
  ], true, SMALL);
  const t2rows = [];
  [['출하 전체', s25['전체'], s26['전체']], ['출하 3곳 제외', s25['전체'].map((v, k) => v - s25['대형3'][k]), s26['전체'].map((v, k) => v - s26['대형3'][k])], ['생산', P['2025'], P['2026']]].forEach(([nm, x, y]) => {
    [['1~7월', 0, 7], ['8~10월', 7, 10], ['1~10월', 0, 10]].forEach(([k, i, j], q) => {
      const a = sum(x, i, j), b = sum(y, i, j);
      t2rows.push([q === 0 ? { t: nm, bold: true } : '', k, n(f(a)), n(f(b)), n(f(b - a)), n(pct(a, b))]);
    });
  });
  const t2 = table(W(2.2, 1.4, 1.6, 1.6, 1.4, 1.2), [['지표', '기간', '2025 (개)', '2026 (개)', '증감 (개)', '증감 (%)'], ...t2rows], true, SMALL);
  const t3 = table(W(0.8, 1.8, 1.8, 1.8, 1.3, 2.5), [
    ['순위', '거래처', '2025 1~10월 (개)', '2026 1~10월 (개)', '증감 (개)', '비고'],
    ...E.TOP.map(([k, x, y], i) => [n(i + 1), k, n(f(x)), n(f(y)), n(f(y - x)), { '거래처 W': '2026년 신규', '거래처 C': '7월 뒤 거래 종료', '거래처 O': '5월 뒤 발주 없음' }[k] || '']),
  ], true, SMALL);
  const jul = so[7], aug = so[8], avg = jul['기타'] / jul['영업일'], dEff = Math.round(avg * (jul['영업일'] - aug['영업일'])), rEff = aug['기타'] - jul['기타'] + dEff;
  const t4 = table(W(3.4, 1.4, 4.2), [
    ['구분', '증감 (개)', '내용'],
    ['거래처 W 발주 시점', n(f(aug.W - jul.W)), `7월 ${jul.W}개, 8월 ${aug.W}개, 9월 ${so[9].W}개`],
    ['거래처 C 거래 종료', n(f(aug.C - jul.C)), '2026. 7. 수주 230개가 마지막'],
    ['8월 영업일 감소', n(f(-dEff)), `영업일 ${jul['영업일']}일에서 ${aug['영업일']}일, 하계휴가와 대체공휴일`],
    ['나머지 거래처 하루 평균 감소', n(f(rEff)), `하루 평균 ${avg.toFixed(1)}개에서 ${aug['기타_일평균']}개`],
    [{ t: '계', bold: true }, n(f(aug['합계'] - jul['합계'])), `7월 ${f(jul['합계'])}개에서 8월 ${f(aug['합계'])}개`],
  ], true, SMALL);
  return [
    band, gap(), info, gap(), caption('요약'), summary, gap(),
    h1('1. 월별 집계'),
    caption('표 1. 2026년 1~10월 월별 출하, 생산, 수주'), t1,
    note('※ 출하는 출고 수량, 연마불가 제외. 생산은 ANCA 장비 재연마 수량으로 1~9월은 월간생산일지, 10월은 ERP 작업실적 기준. 코팅만 의뢰와 외주분은 생산에 들어가지 않아 출하보다 적음'),
    note('※ 수주 1~5월은 월별 원자료가 없거나 일부만 있어 비움. 6~9월은 수주현황 내보내기, 10월은 2026. 11. 10. ERP 저장본'),
    h1('2. 기간별 비교'),
    caption('표 2. 2025년과 2026년 같은 기간 비교'), t2,
    note('※ 3곳은 거래처 C, O, W. 한 번에 수백 개씩 발주해 월 변동이 큰 거래처'),
    item('1)', `상반기 출하가 크게 늘었고 8~10월은 전년과 비슷함. 3곳을 뺀 나머지 거래처는 8~10월에도 ${pct(...[sum(s25['전체'], 7, 10) - sum(s25['대형3'], 7, 10), sum(s26['전체'], 7, 10) - sum(s26['대형3'], 7, 10)])} % 늘었음`),
    item('2)', `출하 거래처는 2025년 1~10월 ${E.cust[0]}곳, 2026년 1~10월 ${E.cust[1]}곳임`),
    h1('3. 거래처 상위 10곳'),
    caption('표 3. 2026년 1~10월 출하 상위 10곳'), t3,
    note(`※ 상위 10곳이 2026년 1~10월 출하의 ${E.top10share[0]} %를 차지함`),
    h1('4. 8월 수주 감소 구성'),
    caption('표 4. 7월에서 8월 수주 감소의 구성'), t4,
    note('※ 상세 분석과 근거는 「재연마 수주 감소 원인 분석 보고」 2026. 11. 27. 제1판'),
    h1('5. 결론'),
    item('1.', `2026년 1~10월 출하와 생산은 전년보다 많으며 연간 감소 추세는 없음`),
    item('2.', '하반기 수주가 상반기보다 낮은 지속 요인은 거래처 C 거래 종료와 거래처 O 발주 공백임'),
    item('3.', '두 거래처의 사유 확인과 11월 마감 집계로 하반기 기준선을 다시 정함'),
  ];
};
