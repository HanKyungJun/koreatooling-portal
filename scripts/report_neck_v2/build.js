const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  AlignmentType, WidthType, ShadingType, BorderStyle, LevelFormat, Footer,
  PageNumber, HeadingLevel, VerticalAlign, PageBreak, LineRuleType, TabStopType, LeaderType
} = require('docx');

const FONT = '맑은 고딕';
const W = 9638; // content width (DXA)
const SZ_BODY = 30, SZ_TABLE = 26, SZ_NOTE = 26; // half-points: 15pt, 13pt

function runs(text, o = {}) {
  // **bold** 표기 지원
  const parts = String(text).split(/(\*\*[^*]+\*\*)/g).filter(s => s.length);
  return parts.map(s => {
    const b = s.startsWith('**');
    return new TextRun({ text: b ? s.slice(2, -2) : s, bold: b || o.bold, size: o.size || SZ_BODY, font: FONT, color: o.color });
  });
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, o), alignment: o.align, spacing: { before: o.before ?? 60, after: o.after ?? 60, line: o.line ?? (o.size && o.size <= 26 ? 340 : 440), lineRule: LineRuleType.EXACT }, pageBreakBefore: o.pb, indent: o.indent, keepNext: o.keepNext });
const H1 = (t, pb) => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: !!pb, children: [new TextRun({ text: t, font: FONT })], spacing: { before: pb ? 0 : 280, after: 120, line: 500, lineRule: LineRuleType.EXACT }, keepNext: true });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })], spacing: { before: 160, after: 80, line: 440, lineRule: LineRuleType.EXACT }, keepNext: true });
const B = (t, lvl = 0) => new Paragraph({ numbering: { reference: 'bul', level: lvl }, children: runs(t), spacing: { before: 30, after: 30, line: 440, lineRule: LineRuleType.EXACT } });
const NOTE = t => new Paragraph({ children: runs('※ ' + t, { size: SZ_NOTE }), spacing: { before: 20, after: 20, line: 340, lineRule: LineRuleType.EXACT }, indent: { left: 200 } });
const CAP = t => new Paragraph({ children: [new TextRun({ text: t, bold: true, size: SZ_TABLE, font: FONT })], alignment: AlignmentType.CENTER, spacing: { before: 160, after: 80, line: 440, lineRule: LineRuleType.EXACT }, keepNext: true });
const CAPB = t => new Paragraph({ children: [new TextRun({ text: t, bold: true, size: SZ_TABLE, font: FONT })], alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200, line: 340, lineRule: LineRuleType.EXACT } });

const bd = { style: BorderStyle.SINGLE, size: 4, color: '808080' };
const borders = { top: bd, bottom: bd, left: bd, right: bd };
function cell(t, w, o = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: o.head ? { fill: 'E7EDF3', type: ShadingType.CLEAR, color: 'auto' } : (o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: 'auto' } : undefined),
    margins: { top: 30, bottom: 30, left: 90, right: 90 }, verticalAlign: VerticalAlign.CENTER,
    columnSpan: o.span,
    children: String(t).split('\n').map(line => new Paragraph({ children: runs(line, { size: SZ_TABLE, bold: o.head || o.bold }), alignment: o.align ?? (o.head ? AlignmentType.CENTER : AlignmentType.LEFT), keepNext: o.keep, spacing: { before: 0, after: 0, line: 330, lineRule: LineRuleType.EXACT } }))
  });
}
function table(cols, head, rows, o = {}) {
  const sum = cols.reduce((a, b) => a + b, 0);
  const ws = cols.map(c => Math.round(c * W / sum));
  ws[ws.length - 1] += W - ws.reduce((a, b) => a + b, 0);
  const aligns = o.aligns || [];
  const trs = [];
  if (head) trs.push(new TableRow({ tableHeader: true, cantSplit: true, children: head.map((h, i) => cell(h, ws[i], { head: true, keep: true })) }));
  rows.forEach((r, ri) => trs.push(new TableRow({ cantSplit: true, children: r.map((c, i) => cell(o.compact ? String(c).replace(/ ~ /g, '~') : (o.wrapRange ? String(c).replace(/ ~ /g, ' ~\n') : c), ws[i], { align: aligns[i], keep: ri < rows.length - 1, fill: o.labelCols && o.labelCols.includes(i) ? 'F2F2F2' : undefined, bold: o.labelCols && o.labelCols.includes(i) })) })));
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: ws, rows: trs });
}
const C = AlignmentType.CENTER;
function img(file, w, h) {
  return new Paragraph({ alignment: C, keepNext: true, spacing: { before: 120, after: 0 }, children: [new ImageRun({ type: 'png', data: fs.readFileSync(file), transformation: { width: w, height: h } })] });
}
const PB = () => new Paragraph({ children: [new PageBreak()] });

const body = [];
const add = (...x) => body.push(...x);

// ───── 표지부 ─────
add(new Paragraph({ alignment: C, spacing: { before: 1400, after: 160, line: 640, lineRule: LineRuleType.EXACT }, children: [new TextRun({ text: '넥 원통연삭 시험 결과 보고', bold: true, size: 44, font: FONT })] }));
add(new Paragraph({ alignment: C, spacing: { before: 0, after: 600, line: 400, lineRule: LineRuleType.EXACT }, children: [new TextRun({ text: 'D3 초경 엔드밀 시험 공구 2개, ANCA GX7 원통연삭', size: 28, font: FONT })] }));
add(table([16, 34, 16, 34], null, [
  ['과제명', '초경 엔드밀 넥 원통연삭 조건 확립', '문서번호', '넥_원통연삭_시험결과_보고_20261022_v2'],
  ['보고일', '2026. 10. 22.', '시험 기간', '2026. 10. 19. ~ 2026. 10. 20.'],
  ['작성', '생산팀 한경준\n(자료 정리 및 계산 보조: Claude)', '판', '제2판 (초판 2026. 10. 20.)'],
  ['장비', 'ANCA GX7, iGrind 원통연삭', '시험 대상', 'D3 엔드밀 2개\n(실측 D 2.955 mm, 2.970 mm)'],
  ['자료 기준', '2026. 10. 20. 16:23 시험 기록까지', '상태', '시험 단계(양산 미적용)'],
], { labelCols: [0, 2] }));

add(P('요약', { bold: true, size: 32, before: 600, after: 80 }));
add(table([100], null, [[
  '○ 결론: 정삭만 적용한 테스트 1은 넥 지름 합격, 황삭 대각선 진입을 추가한 테스트 2는 진입부 자국이 없어졌으나 넥 끝 쪽 지름 초과로 보류함\n' +
  '○ 근거: 테스트 1 넥 지름 2.853 ~ 2.862 mm(허용 2.807 ~ 2.881 mm), 두 공구 모두 측정값이 입력값보다 0.063 ~ 0.065 mm 큼(공구 2개 실측)\n' +
  '○ 요청: 없음(참고 보고). 휠 드레싱 후 테스트 3 진행 예정'
]]));

add(P('목차', { bold: true, size: 32, before: 0, after: 200, pb: true }));
const PG = JSON.parse(fs.readFileSync('pg.json', 'utf8'));
const TOC = (t, pg, lvl, sz) => new Paragraph({ indent: { left: lvl ? 800 : 400 }, tabStops: [{ type: TabStopType.RIGHT, position: W, leader: LeaderType.DOT }], spacing: { before: sz ? 10 : (lvl ? 20 : 120), after: sz ? 10 : 20, line: sz ? 340 : 440, lineRule: LineRuleType.EXACT },
  children: [new TextRun({ text: t, size: sz || SZ_BODY, font: FONT, bold: !lvl && !sz }), new TextRun({ text: '\t' + pg, size: sz || SZ_BODY, font: FONT })] });
[['1. 서론', '1. 서론', 0], ['2. 시험 방법', '2. 시험 방법', 0], ['3. 시험 결과', '3. 시험 결과', 0], ['가. 테스트 1 (정삭만 4회)', '가. 테스트 1', 1], ['나. 테스트 2 (황삭 대각선 진입 추가)', '나. 테스트 2', 1], ['다. 넥 형상 측정 결과', '다. 넥 형상', 1], ['4. 고찰', '4. 고찰', 0], ['5. 결론 및 향후 계획', '5. 결론', 0], ['참고 문헌', '참고 문헌', 0], ['부록', '부록', 0]].forEach(([t, k, l]) => add(TOC(t, PG[k] || '?', l)));
add(P('표 목차', { bold: true, size: SZ_BODY, before: 360, after: 60 }));
['표 1. 시험 장비 및 공구', '표 2. 시험 조건', '표 3. 측정 항목 및 방법', '표 4. 테스트 1 넥 지름 측정 결과', '표 5. 테스트 2 넥 지름 측정 결과', '표 6. 넥 시작 위치와 L2', '표 7. 목표 달성도'].forEach(t => add(TOC(t, PG[t.split('.')[0]] || '?', 1, SZ_TABLE)));
add(P('그림 목차', { bold: true, size: SZ_BODY, before: 240, after: 60 }));
['그림 1. 테스트 1 회차별 입력값과 측정값', '그림 2. 넥 위치별 지름', '그림 3. 휠 형상과 넥 끝 위치의 관계'].forEach(t => add(TOC(t, PG[t.split('.')[0]] || '?', 1, SZ_TABLE)));
add(P('표와 그림의 신뢰도 구분: 실측(사내에서 직접 측정), 화면값(장비 프로그램 표시), 계산(측정값으로 계산), 추정(해석), 제조사(매뉴얼, 카탈로그)', { size: SZ_NOTE, before: 360, color: '404040' }));
// ───── 1. 서론 ─────
add(H1('1. 서론', true));
add(H2('가. 시험 배경 및 목적'));
add(B('넥은 날 뒤쪽 몸통을 날지름(D)보다 가늘게 깎은 부분으로, 깊은 가공에서 공구 몸통이 가공 벽에 닿지 않게 하는 역할을 함'));
add(B('사내에서는 넥을 원통연삭으로 가공하나, 입력값과 가공 결과의 관계가 정리되어 있지 않음'));
add(B('본 시험은 ANCA GX7에서 넥 지름을 목표 범위에 넣는 입력 조건을 찾고, 넥 시작부 진입 자국을 없애는 방법을 확인하는 데 목적이 있음'));
add(H2('나. 시험 범위'));
add(B('대상: D3 2날 초경 엔드밀 시험 공구 2개(1번 공구 4회 연삭, 2번 공구 1회 연삭)'));
add(B('평가 항목: 넥 지름(3곳), 진입부 자국, 스핀들 부하, 가공 시간. 진원도, 표면 거칠기(Ra), 양산 적용은 제외'));

// ───── 2. 시험 방법 ─────
add(H1('2. 시험 방법'));
add(H2('가. 시험 장비 및 공구'));
add(CAP('표 1. 시험 장비 및 공구'));
add(table([24, 56, 20], ['항목', '내용', '구분'], [
  ['연삭기, 프로그램', 'ANCA GX7, ToolRoom RN32.1-1 iGrind 원통연삭(Cylindrical Grinding), 3시 방향', '화면값'],
  ['휠 형상, 지름', '원통부 약 2.8 mm + 생크 쪽 12° 면 약 7.0 mm, 지름 125.102 mm', '실측'],
  ['휠 등록 형상', '폭 10.487 mm 원통으로 단순 등록(12° 면 미반영, 좌표상 폭 9.801 mm와 차이 확인 필요)', '화면값'],
  ['휠 회전수', '3,500 rpm (원주속도 22.93 m/s)', '화면값, 계산'],
  ['시험 공구', 'D3 2날 초경 엔드밀, 생크 지름 d 6 mm', '실측'],
  ['측정기', '디지털 마이크로미터 Mitutoyo 293-340-30 (분해능 0.001 mm)', '판매처 사양'],
], { aligns: [C, undefined, C] }));
add(NOTE('Vc = π × 125.102 × 3,500 ÷ 60,000 = 22.93 m/s(사내 상한 25 m/s 이내). 기본값 4,000 rpm(26.20 m/s)은 사용하지 않음'));

add(H2('나. 시험 조건'));
add(CAP('표 2. 시험 조건'));
add(table([40, 30, 30], ['항목 (단위)', '테스트 1 (1번 공구)', '테스트 2 (2번 공구)'], [
  ['입력 지름, Final diameter (mm)', '3.05, 2.93, 2.860, 2.790\n(같은 공구 4회 연속)', '2.825 (1회)'],
  ['황삭', '사용 안 함', '대각선 진입(Diagonal), 반경 0.075 mm 1패스\n이송 10 mm/min(가공 중 4로 낮춤), 공구 회전 50 rpm'],
  ['정삭 여유, Finish stock (mm)', '1.333', '0.020'],
  ['정삭 진입 속도, Infeed rate (mm/min)', '5.0 (1 ~ 3회), 1.0 (4회)', '0.5'],
  ['정삭 이송 (mm/min), 공구 회전 A Spin (rpm)', '3.0, 25', '3.0, 25'],
  ['넥 시작 X Start, 넥 길이 Step length (mm)', '−4.100, 15.340', '−4.100, 15.340'],
], { aligns: [undefined, C, C] }));
add(NOTE('두 시험 모두 휠 돌출 허용(Allow Wheel Overhang) 끔, 워시아웃(Washout) 0. 넥 끝 입력 위치 X End = 4.1 + 15.34 = 19.44 mm'));

add(H2('다. 측정 방법'));
add(CAP('표 3. 측정 항목 및 방법'));
add(table([22, 38, 40], ['항목', '방법', '비고'], [
  ['넥 지름', '디지털 마이크로미터, 머리 쪽, 중간, 테이퍼 쪽 3곳', '2날 공구, 마주 보는 두 랜드에 접촉'],
  ['넥 시작 위치, L2', '현장 메모', '측정 방법 확인 필요'],
  ['진입부 표면', '현미경 사진 (같은 배율 비교)', ''],
  ['미측정 항목', '측정 위치의 축 방향 거리, 진원도, Ra', '쿨런트, 런아웃, 휠 밸런스, 드레싱 시점도 기록하지 않음'],
]));

add(H2('라. 판정 기준'));
add(B('넥 지름은 실측 날지름 D의 0.95 ~ 0.975배를 허용 범위로, 0.96배를 목표로 함. 제조사 롱넥 엔드밀 31개 품목의 넥 치수에서 역산한 사내 기준임(2026. 10. 20. 결정, 참고 문헌 3)'));
add(B('판정: 넥 3곳 모두 범위 안이면 합격, 상한 초과는 보류(재연삭 가능), 하한 미만은 불합격. 진입부 자국은 현미경 사진으로 판정'));
add(B('허용 범위(0.95 ~ 0.975 × D): 1번 공구 2.807 ~ 2.881 mm(목표 0.96 × 2.955 = 2.837 mm), 2번 공구 2.822 ~ 2.896 mm(목표 2.851 mm)'));

// ───── 3. 시험 결과 ─────
add(H1('3. 시험 결과', true));
add(H2('가. 테스트 1 (1번 공구, 정삭만 4회)'));
add(CAP('표 4. 테스트 1 넥 지름 측정 결과'));
add(table([8, 12, 18, 16, 18, 17, 11], ['회차', '입력값 (mm)', '머리 쪽 (mm)', '중간 (mm)', '테이퍼 쪽 (mm)', '측정 − 입력 (mm)', '판정'], [
  ['1', '3.05', '3.000', '미측정', '미측정', '비접촉', '재연삭'],
  ['2', '2.93', '2.985 ~ 2.987', '미측정', '2.988 ~ 2.992', '+0.055 ~ +0.062', '재연삭'],
  ['3', '2.860', '2.920 ~ 2.922', '미측정', '2.928 ~ 2.935', '+0.060 ~ +0.075', '재연삭'],
  ['4', '2.790', '2.853 ~ 2.854', '2.854 ~ 2.855', '2.858 ~ 2.862', '+0.063 ~ +0.072', '합격'],
], { aligns: [C, C, C, C, C, C, C], wrapRange: true }));
add(NOTE('1회는 가공 전 넥 구간 지름(2.990 ~ 3.003 mm)이 입력값 3.05 mm보다 작아 휠이 닿지 않은 것으로 확인함'));
add(NOTE('4회 비율: 2.853 ÷ 2.955 = 0.9655, 2.862 ÷ 2.955 = 0.9685로 허용 0.95 ~ 0.975 안임'));
add(B('정삭 진입 속도를 5.0에서 1.0 mm/min으로 낮춘 4회에서도 측정값과 입력값의 차이는 같은 수준(머리 쪽 +0.063 mm)이었음'));
add(B('진입부의 같은 위치에 매회 자국이 남음. 4회에서는 줄무늬가 약해졌으나 자국은 남음'));
add(B('4회 테이퍼 쪽 지름이 머리 쪽보다 0.004 ~ 0.009 mm 크고, 이 구간에서 스핀들 부하가 3 ~ 4% 오름(현장 관찰)'));
add(B('1회 가공 시간은 프로그램 표시 기준 약 4 ~ 5분임'));
add(img('fig1.png', 486, 270));
add(CAPB('그림 1. 테스트 1 회차별 입력값과 측정값'));

add(H2('나. 테스트 2 (2번 공구, 황삭 대각선 진입 추가)'));
add(CAP('표 5. 테스트 2 넥 지름 측정 결과'));
add(table([20, 20, 22, 18, 20], ['위치', '측정값 (mm)', '측정 − 입력 (mm)', 'dn ÷ D', '판정'], [
  ['머리 쪽', '2.890', '+0.065', '0.973', '합격'],
  ['중간', '2.905', '+0.080', '0.978', '상한 초과'],
  ['테이퍼 쪽', '2.907', '+0.082', '0.979', '상한 초과'],
], { aligns: [C, C, C, C, C] }));
add(NOTE('입력값 2.825 mm, 허용 범위 2.822 ~ 2.896 mm(0.95 ~ 0.975 × 2.970)'));
add(B('진입부 자국이 없음. 넥 시작부의 둥근 점이 있는 면은 머리 랜드의 원래 면으로 확인함(현장 확인, 현미경 사진)'));
add(B('황삭 이송 10 mm/min에서 진입 부하가 5%를 넘어 가공 중 4 mm/min으로 낮춤(부하 4%)'));
add(B('휠이 테이퍼 쪽에 닿고 약 3초 뒤 부하가 5 ~ 10%로 오름. 정삭 진입 부하는 약 3%임'));
add(B('가공 시간은 약 8분(실측)으로, 시뮬레이션 6분 28초에 황삭 감속분(15.34 ÷ 4 − 15.34 ÷ 10 = 2.3분)을 더한 값과 맞음'));
add(B('넥 중간과 테이퍼 쪽이 상한을 0.009 ~ 0.011 mm 넘었으나 재연삭은 하지 않고 시험품으로 보존함'));
add(img('fig2.png', 600, 300));
add(CAPB('그림 2. 넥 위치별 지름'));

add(H2('다. 넥 형상 측정 결과'));
add(CAP('표 6. 넥 시작 위치와 L2'));
add(table([34, 16, 16, 16, 18], ['항목', '입력값 (mm)', '테스트 1 (mm)', '테스트 2 (mm)', '구분'], [
  ['넥 시작 위치', '4.1', '4.2 ~ 4.3', '4.5', '현장 메모'],
  ['L2 (공구 끝 ~ 테이퍼 시작)', '−', '약 12.5', '11.335', '현장 메모'],
  ['L2 뒤 테이퍼 각도 (한쪽)', '−', '12°', '12°', '현장 확인'],
], { aligns: [undefined, C, C, C, C] }));
add(NOTE('실제 넥 시작 위치는 입력값보다 생크 쪽으로 0.1 ~ 0.4 mm 밀려 있음'));

// ───── 4. 고찰 ─────
add(H1('4. 고찰'));
add(H2('가. 진입부 자국의 원인'));
add(P('정삭만 적용한 테스트 1은 매회 같은 위치에 자국이 남았고, 황삭 대각선 진입과 작은 정삭 여유(0.020 mm)를 적용한 테스트 2는 자국이 없었다. 정삭은 항상 넥 시작 쪽 끝에서 지름 방향으로 진입하므로, 정삭 여유가 크면 같은 위치에 진입 자국이 남는 것으로 판단된다. 대각선 진입은 황삭에만 적용되므로, 황삭으로 대부분을 깎고 정삭 여유를 작게 남기는 방법이 효과가 있었던 것으로 판단된다. 다만 근거 매뉴얼은 장비 PC에서 전달받은 요약이며 원문 대조 전이다.'));
add(H2('나. 측정값이 입력값보다 큰 원인'));
add(P('실제로 깎인 양이 반경 0.004 ~ 0.039 mm로 약 10배 달랐는데도 측정값과 입력값의 차이는 +0.055 ~ +0.075 mm 범위에서 거의 일정했고, 테스트 2 머리 쪽도 +0.065 mm였다. 깎는 양에 따라 커지는 공구 처짐보다는 휠 지름이나 위치 기준의 고정 오차일 가능성이 높다고 판단된다. 휠이 마모되어 실제 휠 지름이 등록값보다 약 0.065 mm 작다면 같은 차이가 생기나, 휠 지름은 시험 중 다시 측정하지 않았다. 테스트 2 중간과 테이퍼 쪽의 추가 차이(약 +0.015 mm)는 부하가 큰 구간에서 공구가 밀린 영향으로 추정된다.'));
add(H2('다. 넥 끝 지름 증가와 부하 상승의 원인'));
add(P('실제 휠은 공구 끝 쪽 원통부 약 2.8 mm와 생크 쪽 12° 면 약 7.0 mm로 되어 있으나, 프로그램에는 폭 10.487 mm의 원통으로 등록되어 있다. 넥 뒤 테이퍼 각도(12°)가 휠 12° 면의 각도와 같으므로, 넥 끝의 테이퍼는 휠 12° 면이 만든 것으로 판단된다(그림 3). 이 경우 넥의 곧은 구간은 입력 끝 위치(X End)보다 12° 면 폭만큼 앞에서 끝나며, 테스트 1은 19.44 − 7.0 = 12.44 mm로 측정 L2 약 12.5 mm와 맞는다.'));
add(P('반면 테스트 2의 L2는 11.335 mm로 같은 계산과 약 1.1 mm 차이가 있어 원인을 확인하지 못했다. 공구 2개 중 1개만 맞으므로 이 관계는 사내 기준으로 정하지 않고 테스트 3에서 다시 확인한다. 넥 끝 구간의 부하 상승은 휠 12° 면이 테이퍼를 깎으면서 접촉 면적이 늘어난 영향으로 추정된다.'));
add(img('fig3.png', 600, 275));
add(CAPB('그림 3. 휠 형상과 넥 끝 위치의 관계 (테스트 1, 개념도, 지름 방향 확대)'));
add(P('시험 중에 처음 해석을 정정한 5건은 부록 라에 정리함.', { before: 120 }));

// ───── 5. 결론 ─────
add(H1('5. 결론 및 향후 계획', true));
add(H2('가. 결론'));
[
  '(1) 정삭만으로 연삭한 테스트 1은 4회째 넥 지름 2.853 ~ 2.862 mm로 허용 범위(2.807 ~ 2.881 mm) 안에 들어 치수 합격임',
  '(2) 황삭 대각선 진입, 정삭 여유 0.020 mm, 정삭 진입 속도 0.5 mm/min을 함께 적용하면 진입부 자국이 없어짐(테스트 2)',
  '(3) 두 공구 모두 측정값이 입력값보다 0.063 ~ 0.065 mm 크게 나와, 드레싱 전 휠 기준으로는 입력값을 목표보다 약 0.065 mm 작게 넣어야 했음. 드레싱 후에는 이 값을 다시 측정함',
  '(4) 넥 끝은 휠 12° 면 때문에 입력 끝 위치보다 약 7 mm 앞에서 끝나는 것으로 보이나, 공구 2개 중 1개만 맞아 추가 확인이 필요함',
  '(5) 모든 결과는 공구 2개의 시험값이며 양산에는 적용하지 않음',
].forEach(t => add(P(t, { indent: { left: 560, hanging: 560 }, before: 30, after: 30 })));
add(H2('나. 목표 달성도 및 미달성 항목 대책'));
add(CAP('표 7. 목표 달성도'));
add(table([22, 18, 18, 11, 31], ['평가 항목', '목표', '결과', '달성 여부', '미달성 원인 및 대책'], [
  ['넥 지름\n(테스트 1)', '2.807 ~ 2.881 mm', '2.853 ~ 2.862 mm', '달성', ''],
  ['넥 지름\n(테스트 2)', '2.822 ~ 2.896 mm', '2.890 ~ 2.907 mm', '미달성', '넥 끝 구간 부하 상승(추정). 테스트 3에서 패스별 측정'],
  ['진입부 자국', '없음', '테스트 2 없음', '달성', '테스트 1은 자국 있음'],
  ['재현성', '같은 조건 2개 이상', '조건별 1개', '미달성', '같은 조건으로 반복 시험'],
  ['진원도, Ra', '측정', '미측정', '미달성', '측정 장비 확인 후 측정'],
], { aligns: [undefined, C, C, C, undefined], compact: true }));
add(H2('다. 시험의 한계'));
add(B('표본은 공구 2개이며, 테스트 1은 같은 공구를 4회 이어 깎은 결과임'));
add(B('측정 위치, 진원도, Ra, 쿨런트 및 설비 상태를 기록하지 않았고, 넥 시작 위치와 L2는 현장 메모 값임'));
add(B('입력 보정값(+0.065 mm 등)은 현재 휠 드레싱 상태에서만 유효함'));
add(B('매뉴얼 근거는 장비 PC에서 전달받은 요약이며 원문 대조 전임'));
add(new Paragraph({ heading: HeadingLevel.HEADING_2, pageBreakBefore: true, children: [new TextRun({ text: '라. 향후 계획 및 요청 사항', font: FONT })], spacing: { before: 0, after: 80, line: 440, lineRule: LineRuleType.EXACT }, keepNext: true }));
add(B('휠 드레싱 전후 휠 지름을 측정하고 다시 등록(Qualify)함'));
add(B('테스트 3: 3번 공구(날장 L1 5.4 mm, 목표 L2 14 mm)로 넥 구간을 3번 나눠 깎고 패스마다 지름과 부하를 측정함'));
add(B('**경고:** 테스트 3의 테이퍼 쪽 패스당 반경 절입은 약 0.19 mm(계산)로 사내 실적 0.075 mm의 약 2.5배임. 첫 패스 부하가 5%를 넘으면 중단함'));
add(B('요청 사항은 없음(참고 보고)'));

// ───── 참고 문헌 ─────
add(H1('참고 문헌'));
[
  '1. ANCA Pty Ltd (2014). iGrind Grinding Manual, §30 Cylindrical Grinding (igrind_cycles_en.pdf). 장비 PC 열람 요약, 원문 대조 전.',
  '2. Mitutoyo. Digimatic Micrometer 293-340-30 사양. 판매처 게시 사양, 카탈로그 원문 확인 필요.',
  '3. OSG. AE-LNBD-N(List 8990), WXL-LN-EBD(List 3690), AE-LN-VMSS(List 8230) 치수표 / Mitsubishi Materials. VQ2XLB, VF2XLB, MS2XL 제품 정보 (2026. 10. 20. 열람).',
  '4. Micro 100. End Mills, Corner Radius, 2 Flute, Reduced Neck 제품 정보 (넥 지름 공차 +0.00 / −0.13 mm).',
].forEach(t => add(P(t, { indent: { left: 400, hanging: 400 } })));

// ───── 부록 ─────
add(H1('부록', true));
add(H2('가. 측정 원자료 (테스트 1 가공 전 넥 지름)'));
add(CAP('부록 표 1. 테스트 1 회차별 가공 전 넥 지름'));
add(table([20, 40, 40], ['회차', '가공 전 넥 지름 (mm)', '비고'], [
  ['1', '2.990 ~ 3.003', '가공 전 몸통 지름'],
  ['2', '약 3.00', '1회 측정값'],
  ['3', '약 2.986 / 2.990', '2회 측정값(머리 쪽 / 테이퍼 쪽)'],
  ['4', '약 2.921 / 2.932', '3회 측정값(머리 쪽 / 테이퍼 쪽)'],
], { aligns: [C, C, undefined] }));
add(H2('나. 프로그램 및 휠 파일'));
add(B('테스트 1: GX7_AFCY_D3.8_S6.tom (회차마다 같은 파일에 덮어씀, 2026. 10. 19. 원본은 GX7_AFCY_D3.8_S6_20261019_원본.tom으로 백업)'));
add(B('테스트 2: GX7_AFCY_D3.8_S6_Roughing.tom'));
add(B('휠: GX7_Cylindrical_HID12_PRE_1.wpk (폭 10.487 mm 원통으로 단순 등록)'));
add(H2('다. 사내 기록 위치'));
add(B('시험 기록: cnc-wiki wiki/cadcam/원통연삭-넥-시험-AFCY-D3-2026-10-20.md'));
add(B('기록표: wiki/reports/01_연삭조건/넥_원통연삭_시험연삭_기록표_v1.xlsx'));
add(B('결정 기록: decisions.md 2026-10-20 (2) 넥 기준, (4) 실측 D 기준, (5) 진입 자국 대책, 2026-10-21 (3) 넥 끝 보정 보류 및 드레싱'));
add(B('출처: [VEN-ANCA-IGRIND-CYCLES], [VEN-MITUTOYO-293-340], [VEN-OSG-AELNBDN], [VEN-OSG-WXLLNEBD], [VEN-OSG-AELNVMSS], [VEN-MITSU-XLB], [VEN-MITSU-MS2XL], [VEN-MICRO100-REDNECK]'));
add(H2('라. 시험 중 정정한 해석'));
add(CAP('부록 표 2. 시험 중 정정한 해석'));
add(table([38, 32, 30], ['처음 해석', '정정 내용', '정정 근거'], [
  ['1회에 반경 0.475 mm를 깎아 측정값이 입력보다 0.05 mm 작음', '1회는 휠이 닿지 않음', '가공 전 넥 구간 지름 2.990 ~ 3.003 mm'],
  ['진입부 머무름(Dwell) 때문에 머리 쪽이 가늚', '머무름은 넥 끝에서 일어남', '매뉴얼(전달 요약)'],
  ['넥 끝이 원래 있던 15° 테이퍼 면을 깎음', '테이퍼는 12°이며 휠 12° 면이 만든 것', '현장 측정'],
  ['넥 끝에 15° 워시아웃 0.28 mm를 넣어 테이퍼와 이음', '테이퍼는 휠 면이 만들므로 적용하지 않음', '현장 측정'],
  ['넥 시작 위치 오차 +0.25 mm', '+0.1 ~ +0.4 mm', '현장 메모'],
]));

add(H2('마. 변경 이력'));
add(CAP('부록 표 3. 변경 이력'));
add(table([22, 12, 66], ['일자', '판', '내용'], [
  ['2026. 10. 20.', '초판', '테스트 1, 2 결과 보고 (2026. 10. 20. 14:07 기록 기준)'],
  ['2026. 10. 21.', '제2판', '같은 날 16:05 ~ 16:23 정정 반영(넥 뒤 테이퍼 15°에서 12° 휠 면으로, L2 측정값, 넥 시작 위치 오차, 테스트 2 재연삭 안 함). 다음 시험 계획 변경(섹션 분할과 15° 워시아웃 안 철회). 연구보고서 양식(서론, 시험 방법, 결과, 고찰, 결론)으로 재구성. 양산 적용 없음'],
], { aligns: [C, C, undefined] }));

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: SZ_BODY } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 34, bold: true, font: FONT }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 30, bold: true, font: FONT }, paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 1 } },
    ]
  },
  numbering: { config: [{ reference: 'bul', levels: [
    { level: 0, format: LevelFormat.BULLET, text: '-', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 300 } } } },
    { level: 1, format: LevelFormat.BULLET, text: '-', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 800, hanging: 300 } } } },
  ] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 850, bottom: 850, left: 1134, right: 1134, footer: 400 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: '넥 원통연삭 시험 결과 보고 (제2판)   - ', size: 20, font: FONT, color: '606060' }), new TextRun({ children: [PageNumber.CURRENT], size: 20, font: FONT, color: '606060' }), new TextRun({ text: ' -', size: 20, font: FONT, color: '606060' })] })] }) },
    children: body
  }]
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync('넥_원통연삭_시험결과_보고_20261022_v2.docx', b); console.log('written', b.length); });
