// 슬라이드 내용 (build.js 에서 부름)
const B = require('./build.js');
const { pres, W, H, M, R, D, E, f, pct, sum, msg, tabs, code, hdr, cell, num, cap, TB, CH, stat, LOGO, OUT, THEME, applyTheme, NAVY, INK, GRAY, LAV, BLUE, CREAM, LIGHT, MID, KO, LATIN } = B;
const s25 = D['2025'], s26 = D['2026'], O = D['수주'], P = D['기간'];
const jul = O[1], aug = O[2];
const avgJul = jul['기타'] / jul['영업일'], dEff = Math.round(avgJul * (jul['영업일'] - aug['영업일'])), rEff = aug['기타'] - jul['기타'] + dEff, tot = aug['합계'] - jul['합계'];
const sh25 = sum(s25['전체'], 0, 10), sh26 = sum(s26['전체'], 0, 10);
const ex810 = P['8~10월']['대형3제외'];
const c26 = sum(s26['거래처 C'], 0, 7), o26 = sum(s26['거래처 O'], 0, 7);
const months = Array.from({ length: 10 }, (_, i) => `${i + 1}월`);

// 1. 표지
pres.addSection({ title: '표지' });
{ const s = pres.addSlide({ sectionTitle: '표지' });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.35, fill: { color: NAVY }, line: { color: NAVY }, objectName: 'top-band' });
  s.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 0.35, w: W - 9.3, h: H - 0.35, fill: { color: NAVY }, line: { color: NAVY }, objectName: 'cover-slab' });
  s.addText('ORDER\nANALYSIS\n2026', { x: 9.7, y: 4.3, w: 3.3, h: 2.4, fontFace: LATIN, fontSize: 40, bold: true, italic: true, color: 'FFFFFF', valign: 'bottom', margin: 0, isTextBox: true, objectName: 'cover-code' });
  s.addImage({ path: LOGO, x: M, y: 0.85, w: 2.16, h: 0.9, altText: 'COGOTOOL 로고', objectName: 'logo' });
  s.addText('재연마 수주 감소 원인 분석', { x: M, y: 2.55, w: 8.5, h: 1.0, fontFace: KO, fontSize: 44, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'cover-title' });
  s.addText('2026년 1~10월 수주와 출하의 전년 동기 비교', { x: M, y: 3.6, w: 8.5, h: 0.6, fontFace: KO, fontSize: 22, color: INK, margin: 0, isTextBox: true, objectName: 'cover-sub' });
  s.addText([{ text: '생산팀 한경준', options: { breakLine: true } }, { text: '2026. 11. 28.  참고 보고' }], { x: M, y: 5.6, w: 8.4, h: 0.9, fontFace: KO, fontSize: 18, color: GRAY, margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: 'cover-meta' });
  s.addNotes(R('[0:20] 8월 이후 재연마 수주가 줄어든 원인을 사내 수주와 출하 자료, 외부 업황 자료로 확인한 결과를 보고드립니다.'));
}
pres.addSection({ title: '본문' });
const add = () => pres.addSlide({ masterName: 'CONTENT', sectionTitle: '본문' });

// 2. 요약
{ const s = add(); s.addText('분석 결과 요약', { placeholder: 'title' });
  msg(s, '8월 이후 감소는 거래처 3곳의 발주 변화와 영업일 감소가 원인'); code(s, 'SUMMARY'); tabs(s, 0);
  const lab = (t) => cell(t, { bold: true, color: 'FFFFFF', fill: { color: NAVY }, align: 'center' });
  s.addTable([
    [lab('결론'), cell('거래처 C 거래 종료, 거래처 O 발주 공백, 거래처 W 발주 시점 변동, 8월 영업일 감소가 겹친 결과. 나머지 거래처의 수주와 출하는 줄지 않음')],
    [lab('근거'), cell(`7월에서 8월 감소 972개 중 거래처 W 398개, 거래처 C 230개, 영업일 ${dEff}개. 1~10월 출하는 전년보다 ${pct(sh25, sh26)} %`)],
    [lab('요청'), cell('거래처 C 거래 종료 사유와 거래처 O 발주 공백 사유를 영업팀에서 확인')],
  ], { ...TB, x: M, y: 2.2, w: 8.6, colW: [1.2, 7.4], fontSize: 18, rowH: [1.05, 1.05, 0.75], objectName: 'summary-3' });
  stat(s, 9.55, 2.2, 2.85, 2.1, '1~10월 출하 전년 대비', pct(sh25, sh26), ' %', `전년 ${f(sh25)}개`, BLUE, 'k1');
  stat(s, 9.55, 4.5, 2.85, 2.1, '3곳 제외 8~10월 출하', pct(...ex810), ' %', '전년 같은 기간 대비', LAV, 'k2');
  s.addNotes(R(`[1:00] 결론부터 말씀드리면 8월 이후 수주 감소는 시장 전체가 줄어든 것이 아니라 거래처 세 곳의 발주 변화와 8월 영업일 감소 때문입니다. 거래처 C는 거래가 끝났고, 거래처 O는 5월 이후 발주가 없고, 거래처 W는 달마다 발주량이 크게 오르내립니다. 이 세 곳을 빼면 8월부터 10월 출하는 작년보다 ${pct(...ex810)} % 많습니다. 1월부터 10월까지 전체 출하도 작년보다 ${pct(sh25, sh26)} % 많습니다.`));
}

// 3. 전년 비교
{ const s = add(); s.addText('전년 같은 기간 비교', { placeholder: 'title' });
  msg(s, `1~10월 출하 ${f(sh26)}개로 전년보다 많고 8~10월은 같은 수준`); code(s, 'YEAR ON YEAR'); tabs(s, 1);
  s.addChart(pres.charts.BAR, [
    { name: '2025년', labels: months, values: s25['전체'].slice(0, 10) },
    { name: '2026년', labels: months, values: s26['전체'].slice(0, 10) },
  ], { ...CH, x: M, y: 2.1, w: 7.3, h: 4.6, barDir: 'col', barGrouping: 'clustered', barGapWidthPct: 60, chartColors: [LIGHT, NAVY],
    title: '그림 1. 월별 출하 (개)', valAxisMinVal: 0, valAxisMaxVal: 2500, valAxisMajorUnit: 500, objectName: 'chart-yoy' });
  s.addText('표 1. 기간별 출하 (개)', { x: 8.15, y: 2.15, w: 4.2, h: 0.35, fontFace: KO, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 't1-cap' });
  const rows = [[hdr('기간'), hdr('2025'), hdr('2026'), hdr('증감 (%)')]];
  ['1~7월', '8~10월', '1~10월'].forEach((k) => rows.push([cell(k), num(f(P[k]['전체'][0])), num(f(P[k]['전체'][1])), num(pct(...P[k]['전체']))]));
  rows.push([cell('8~10월 3곳 제외', { bold: true }), num(f(ex810[0])), num(f(ex810[1])), num(pct(...ex810), { bold: true })]);
  s.addTable(rows, { ...TB, x: 8.15, y: 2.55, w: 4.25, colW: [1.45, 0.95, 0.95, 0.9], fontSize: 14, rowH: 0.5, objectName: 't1' });
  s.addText(R('주: 3곳은 거래처 C, O, W. 출하는 연마불가 제외 수량'), { x: 8.15, y: 5.75, w: 4.25, h: 0.7, fontFace: KO, fontSize: 14, color: GRAY, margin: 0, valign: 'top', isTextBox: true, objectName: 'note' });
  s.addNotes(R(`[1:20] 작년과 같은 기간을 비교했습니다. 2025년 수주 원자료가 없어 출하로 비교했습니다. 상반기 출하가 크게 늘었고 8월부터 10월은 작년과 거의 같습니다. 큰 거래처 세 곳을 빼고 보면 8월부터 10월도 ${pct(...ex810)} % 늘어, 나머지 거래처의 물량은 줄지 않았습니다.`));
}

// 4. 하반기 수주
{ const s = add(); s.addText('2026년 6~10월 수주', { placeholder: 'title' });
  msg(s, `8월 수주는 ${f(aug['합계'])}개로 줄었으나 나머지 거래처 하루 평균은 9~10월에 회복`); code(s, 'ORDERS'); tabs(s, 2);
  const lb = O.map((r) => `${Number(r.ym.slice(5))}월`);
  s.addChart(pres.charts.BAR, [
    { name: '나머지 거래처', labels: lb, values: O.map((r) => r['기타']) },
    { name: R('거래처 W'), labels: lb, values: O.map((r) => r.W) },
    { name: R('거래처 C'), labels: lb, values: O.map((r) => r.C) },
  ], { ...CH, x: M, y: 2.1, w: 7.4, h: 4.6, barDir: 'col', barGrouping: 'stacked', barGapWidthPct: 70, chartColors: [MID, BLUE, NAVY],
    title: '그림 2. 월별 수주 (개)', valAxisMinVal: 0, valAxisMaxVal: 2500, valAxisMajorUnit: 500, objectName: 'chart-orders' });
  s.addText('표 2. 영업일과 하루 평균 수주', { x: 8.35, y: 2.15, w: 4.0, h: 0.35, fontFace: KO, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 't2-cap' });
  const rows = [[hdr('월'), hdr('영업일 (일)'), hdr('수주 (개)'), hdr('나머지 하루 평균 (개)')]];
  O.forEach((r) => rows.push([cell(`${Number(r.ym.slice(5))}월`), num(r['영업일']), num(f(r['합계'])), num(r['기타_일평균'].toFixed(1), r.ym === '2026-08' ? { bold: true } : {})]));
  s.addTable(rows, { ...TB, x: 8.35, y: 2.55, w: 4.05, colW: [0.7, 1.0, 1.05, 1.3], fontSize: 14, rowH: [0.6, 0.45, 0.45, 0.45, 0.45, 0.45], objectName: 't2' });
  s.addText('주: 6~9월은 수주현황 내보내기 자료이고 10월은 2026. 11. 10. ERP 저장본임. 8월 영업일은 하계휴가 2일과 대체공휴일 1일을 뺀 값', { x: 8.35, y: 5.6, w: 4.05, h: 1.0, fontFace: KO, fontSize: 14, color: GRAY, margin: 0, valign: 'top', isTextBox: true, objectName: 'note' });
  s.addNotes(R(`[1:20] 6월부터 10월 수주입니다. 8월은 ${f(aug['합계'])}개로 크게 줄었지만 수주 건수는 64건에서 77건 사이로 비슷했고, 한 건당 수량이 줄었습니다. 8월은 영업일이 18일로 7월보다 4일 적었습니다. 하루 평균으로 보면 나머지 거래처는 8월에 조금 줄었다가 9월 ${O[3]['기타_일평균']}개, 10월 ${O[4]['기타_일평균']}개로 7월보다 많아졌습니다.`));
}

// 5. 8월 감소 구성
{ const s = add(); s.addText('8월 수주 감소의 구성', { placeholder: 'title' });
  msg(s, `감소 972개 중 ${(((jul.W - aug.W) + (jul.C - aug.C) + dEff) / -tot * 100).toFixed(0)} %는 거래처 W와 C의 발주 변화와 영업일 감소`); code(s, 'BREAKDOWN'); tabs(s, 3);
  const items = [['거래처 W 발주 시점', aug.W - jul.W, `9월 ${O[3].W}개로 회복`], ['거래처 C 거래 종료', aug.C - jul.C, '2026. 7. 수주 230개가 마지막'],
    ['8월 영업일 감소', -dEff, `${avgJul.toFixed(1)}개/일 × 4일`], ['나머지 거래처 하루 평균 감소', rEff, `${avgJul.toFixed(1)}개에서 ${aug['기타_일평균']}개로`]];
  s.addChart(pres.charts.BAR, [{ name: '감소 (개)', labels: items.map((i) => R(i[0])).reverse(), values: items.map((i) => -i[1]).reverse() }],
    { ...CH, x: M, y: 2.1, w: 6.1, h: 4.6, barDir: 'bar', chartColors: [NAVY], showLegend: false, showValue: true, dataLabelPosition: 'outEnd', dataLabelFontSize: 14, dataLabelColor: INK, dataLabelFontFace: '+mn-lt',
      title: '그림 3. 7월에서 8월 수주 감소 (개)', valAxisMinVal: 0, valAxisMaxVal: 450, valAxisMajorUnit: 100, objectName: 'chart-break' });
  const rows = [[hdr('구분'), hdr('감소 (개)'), hdr('내용')]];
  items.forEach((i) => rows.push([cell(i[0]), num(f(-i[1])), cell(i[2])]));
  rows.push([cell('계', { bold: true }), num(f(-tot), { bold: true }), cell(`${f(jul['합계'])}개에서 ${f(aug['합계'])}개`)]);
  s.addTable(rows, { ...TB, x: 6.95, y: 2.2, w: 5.45, colW: [2.1, 0.95, 2.4], fontSize: 14, rowH: [0.5, 0.7, 0.6, 0.6, 0.7, 0.6], objectName: 't3' });
  s.addText(`계산: 7월 하루 평균 ${f(jul['기타'])} ÷ ${jul['영업일']}일 = ${avgJul.toFixed(1)}개`, { x: 6.95, y: 6.2, w: 5.45, h: 0.35, fontFace: KO, fontSize: 14, color: GRAY, margin: 0, isTextBox: true, objectName: 'calc' });
  s.addNotes(R(`[1:20] 7월에서 8월로 줄어든 972개를 나눠 봤습니다. 가장 큰 것은 거래처 W로 398개인데, 7월에 많이 들어왔다가 8월에 적었고 9월에 다시 322개로 회복했습니다. 거래처 C는 거래 종료로 230개가 빠졌습니다. 8월 영업일이 4일 적어서 빠진 몫이 약 ${dEff}개이고, 나머지 거래처가 실제로 덜 맡긴 몫은 약 ${-rEff}개입니다.`));
}

// 6. 대형 거래처
{ const s = add(); s.addText('대형 거래처 3곳', { placeholder: 'title' });
  msg(s, `하반기 기준선은 거래처 C 거래 종료와 거래처 O 발주 공백으로 월 약 ${Math.round((c26 + o26) / 7)}개 낮아짐`); code(s, 'CUSTOMERS'); tabs(s, 3);
  const cards = [
    ['거래처 C', '거래 종료', `2025년 출하 1위로 연 ${f(sum(s25['거래처 C'], 0, 12))}개`, `2026년 1~7월 ${f(c26)}개, 8~10월 ${sum(s26['거래처 C'], 7, 10)}개`, '2026. 7. 수주 230개가 마지막, 2026. 9. 3. 거래 종료 확인'],
    ['거래처 O', '발주 공백 6개월', `2026년 1~6월 출하 1위로 ${f(o26)}개`, '1월, 4월, 6월에 370 ~ 401개씩 출하', '2026. 5. 13. 수주 370개 뒤 11. 10.까지 수주 없음. 사유 확인 필요'],
    ['거래처 W', '거래 유지', `2026년 새로 커진 거래처로 1~10월 ${f(sum(s26['거래처 W'], 0, 10))}개`, `월 수주 7월 ${jul.W}개, 8월 ${aug.W}개, 9월 ${O[3].W}개`, `달마다 크게 오르내림. 11. 1. ~ 10. 수주 ${D['W_11월']}개`],
  ];
  const cw = 3.7, gap = 0.3;
  cards.forEach((c, i) => { const x = M + i * (cw + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: 2.2, w: cw, h: 4.4, fill: { color: i === 2 ? LAV : BLUE }, line: { color: i === 2 ? LAV : BLUE }, objectName: `card-${i + 1}` });
    s.addText(R(c[0]), { x: x + 0.25, y: 2.4, w: cw - 0.5, h: 0.5, fontFace: KO, fontSize: 22, bold: true, color: NAVY, margin: 0, isTextBox: true, objectName: `card-h-${i + 1}` });
    s.addText(c[1], { x: x + 0.25, y: 2.95, w: cw - 0.5, h: 0.45, fontFace: KO, fontSize: 18, bold: true, color: INK, margin: 0, isTextBox: true, objectName: `card-s-${i + 1}` });
    s.addText([{ text: c[2], options: { breakLine: true } }, { text: c[3] }], { x: x + 0.25, y: 3.55, w: cw - 0.5, h: 1.9, fontFace: KO, fontSize: 16, color: INK, margin: 0, paraSpaceAfter: 10, valign: 'top', isTextBox: true, objectName: `card-b-${i + 1}` });
    s.addText(c[4], { x: x + 0.25, y: 5.55, w: cw - 0.5, h: 0.9, fontFace: KO, fontSize: 14, color: GRAY, margin: 0, valign: 'top', isTextBox: true, objectName: `card-n-${i + 1}` }); });
  s.addNotes(R(`[1:20] 큰 거래처 세 곳입니다. 거래처 C는 작년 출하 1위였는데 7월을 마지막으로 거래가 끝났습니다. 거래처 O는 두세 달마다 400개 가까이 맡기던 곳인데 5월 이후 6개월째 발주가 없습니다. 작년에도 넉 달 쉬었다가 다시 온 적이 있지만 이번이 더 깁니다. 두 곳이 1월부터 7월까지 맡긴 물량이 한 달 평균 약 ${Math.round((c26 + o26) / 7)}개라, 하반기 수주가 상반기보다 낮은 주된 이유입니다. 거래처 W는 거래가 이어지고 있고 달마다 들쭉날쭉한 편입니다.`));
}

// 7. 외부 업황
{ const s = add(); s.addText('외부 업황', { placeholder: 'title' });
  msg(s, '수도권 산단 가동률은 68 %대이나 사내 나머지 거래처 수주는 유지'); code(s, 'MARKET'); tabs(s, 3);
  s.addText('표 3. 외부 업황 지표', { x: M, y: 2.15, w: 6, h: 0.35, fontFace: KO, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 't4-cap' });
  s.addTable([
    [hdr('지표'), hdr('값'), hdr('출처')],
    [cell('반월과 시화 산단 기계업종 가동률 2026년 3분기'), cell('68.6 %, 68.3 %. 1998년 외환위기 때와 비슷'), cell('한국경제 2026. 11. 24.')],
    [cell('중소 제조업 평균가동률 2026. 8.'), cell('74.6 %'), cell('철강금속신문 2026. 9. 30.')],
    [cell('중소기업 경영 애로 2026. 9.'), cell('매출 부진 54.7 %, 업체 간 경쟁 33.5 %'), cell('산업일보 2026. 9. 30.')],
    [cell('공작기계 수주 2026. 1. ~ 7.'), cell('전년보다 23 % 증가. 수출 및 자동차와 반도체 업종이 이끎'), cell('산업일보 2026. 9. 12.')],
    [cell('초경 원료 APT 해외 가격'), cell('2025. 11. 780달러에서 2026. 11. 2,400 ~ 2,900달러/MTU'), cell('영업진단, Pertechtual')],
  ], { ...TB, x: M, y: 2.55, w: 11.6, colW: [4.3, 4.9, 2.4], fontSize: 15, rowH: 0.56, objectName: 't4' });
  s.addText('주: 기사로 확인한 값(추정값). 원 통계표는 열람하지 않음', { x: M, y: 6.55, w: 11.6, h: 0.3, fontFace: KO, fontSize: 14, color: GRAY, margin: 0, isTextBox: true, objectName: 'note' });
  s.addNotes(R('[1:00] 외부 업황도 확인했습니다. 수도권 산단의 기계업종 가동률은 외환위기 때와 비슷한 68 % 수준이고, 중소기업은 매출 부진을 가장 큰 어려움으로 꼽았습니다. 반면 공작기계 수주는 수출과 반도체 쪽이 이끌어 늘었습니다. 초경 원료 가격은 1년 사이 3배 이상 올라 새 공구 대신 재연마를 고를 이유는 커졌습니다. 이런 업황 악화가 우리 나머지 거래처 수주에는 아직 나타나지 않았습니다.'));
}

// 8. 결론
{ const s = add(); s.addText('결론 및 요청', { placeholder: 'title' });
  msg(s, '거래처 C와 O 사유 확인 뒤 11월 마감 집계로 하반기 기준선 재설정'); code(s, 'NEXT'); tabs(s, 4);
  s.addText('결론', { x: M, y: 2.15, w: 6.6, h: 0.45, fontFace: KO, fontSize: 20, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'concl-h' });
  s.addText([
    { text: R('8월 감소 972개는 거래처 W 398개, 거래처 C 230개, 영업일 ' + dEff + '개, 나머지 ' + (-rEff) + '개'), options: { bullet: { type: 'number' }, breakLine: true } },
    { text: `나머지 거래처 8~10월 출하는 전년보다 ${pct(...ex810)} %`, options: { bullet: { type: 'number' }, breakLine: true } },
    { text: R('하반기 지속 요인은 거래처 C 거래 종료와 거래처 O 발주 공백'), options: { bullet: { type: 'number' }, breakLine: true } },
    { text: '업황 악화와 고객사 자체 재연마 전환은 사내 자료에서 아직 확인 안 됨', options: { bullet: { type: 'number' } } },
  ], { x: M, y: 2.7, w: 6.6, h: 3.6, fontFace: KO, fontSize: 18, color: INK, margin: 0, paraSpaceAfter: 10, valign: 'top', isTextBox: true, objectName: 'concl-list' });
  s.addShape(pres.shapes.RECTANGLE, { x: 7.6, y: 2.15, w: 4.75, h: 1.85, fill: { color: CREAM }, line: { color: INK, width: 1 }, objectName: 'req-bg' });
  s.addText([{ text: '요청 ', options: { bold: true, breakLine: true } }, { text: R('영업팀: 거래처 C 거래 종료 사유와 거래처 O 발주 공백 사유 확인') }],
    { x: 7.8, y: 2.3, w: 4.35, h: 1.55, fontFace: KO, fontSize: 18, color: INK, margin: 0, valign: 'top', paraSpaceAfter: 6, isTextBox: true, objectName: 'req-text' });
  s.addText('향후 계획', { x: 7.6, y: 4.25, w: 4.7, h: 0.45, fontFace: KO, fontSize: 20, bold: true, color: INK, margin: 0, isTextBox: true, objectName: 'plan-h' });
  s.addText([
    { text: '생산팀: 12. 1. ~ 5. 11월 마감 재집계', options: { bullet: true, breakLine: true } },
    { text: '생산팀: 2025년 수주 원자료 내보내기', options: { bullet: true, breakLine: true } },
    { text: R('영업팀: 거래처 C와 O 몫을 메울 거래처 점검'), options: { bullet: true } },
  ], { x: 7.6, y: 4.75, w: 4.75, h: 1.8, fontFace: KO, fontSize: 16, color: INK, margin: 0, paraSpaceAfter: 8, valign: 'top', isTextBox: true, objectName: 'plan-list' });
  s.addNotes(R(`[1:00] 정리하면 8월 감소는 대부분 거래처 W의 발주 시점, 거래처 C 거래 종료, 영업일 감소로 설명됩니다. 나머지 거래처는 작년보다 오히려 늘었습니다. 다만 거래처 C와 O가 빠진 만큼 하반기 기준선이 내려간 상태라, 영업팀에 두 곳의 사유 확인을 부탁드립니다. 생산팀은 12월 초에 11월 마감 자료로 다시 집계하겠습니다.`));
}

(async () => { await pres.writeFile({ fileName: OUT }); await applyTheme(OUT, THEME); console.log('written', OUT); })();
