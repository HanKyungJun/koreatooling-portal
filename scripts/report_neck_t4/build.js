// 넥 원통연삭 한계 시험(넥 지름 2 mm, 테스트 4) 결과 보고 — 양식 A · 코고툴 B안
// 실행: node build.js 출력.docx   (같은 폴더 logo.png 필요)
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, VerticalAlign, Header, Footer, PageNumber, ImageRun, TabStopType, HeadingLevel,
} = require('docx');

const OUT = process.argv[2] || 'out.docx';
const LOGO = path.join(__dirname, 'logo.png');
const DOCNO = '넥_원통연삭_한계시험_결과_보고_20261104';
const TITLE_TXT = '넥 원통연삭 한계 시험 결과 보고';

const NAVY = '231F20', INK = '231F20', GRAY = '58595B', LAV = 'E4E0F0', CREAM = 'FFFBE5', LINE = 'C9C7C7';
const KO = '맑은 고딕', LATIN = 'Arial';
const BODY = 30, TBL = 26, TITLE = 44;
const PAGE_W = 11906, MARGIN_LR = 1134, CONTENT_W = PAGE_W - 2 * MARGIN_LR;

const run = (t, o = {}) => new TextRun({ text: t, font: KO, size: BODY, color: INK, ...o });
const p = (children, o = {}) => new Paragraph({ children: Array.isArray(children) ? children : [run(children)], spacing: { after: 140, line: 312 }, ...o });
const item = (mark, text, level = 0) => new Paragraph({
  children: [run(`${mark} `), run(text)],
  indent: { left: 360 + level * 400, hanging: 360 }, spacing: { after: 60, line: 312 },
});
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: KO, size: 34, bold: true, color: NAVY })], spacing: { before: 280, after: 120 } });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: KO, size: BODY, bold: true, color: INK })], spacing: { before: 160, after: 80 } });
const caption = (t) => new Paragraph({ children: [run(t, { size: TBL, bold: true })], spacing: { before: 120, after: 60 }, keepNext: true });
const note = (t) => new Paragraph({ children: [run(t, { size: TBL, color: GRAY })], spacing: { before: 40, after: 120 } });
const gap = () => new Paragraph({ children: [], spacing: { after: 60 } });

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
function widthsOf(pcts) { const r = pcts.map((x) => Math.round(CONTENT_W * x / 100)); r[r.length - 1] += CONTENT_W - r.reduce((a, b) => a + b, 0); return r; }
function table(widths, rows, headRow = true) {
  const sum = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: sum, type: WidthType.DXA }, columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({ tableHeader: headRow && ri === 0, cantSplit: true, children: r.map((c, ci) => {
      const o = typeof c === 'string' ? { t: c } : c;
      const w = o.span ? widths.slice(ci, ci + o.span).reduce((a, b) => a + b, 0) : widths[ci];
      return tcell(o.t, w, headRow && ri === 0 ? { fill: LAV, bold: true, align: AlignmentType.CENTER } : o);
    }) })),
  });
}
const C = (t) => ({ t, align: AlignmentType.CENTER });

const NONE = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const nb = { top: NONE, bottom: NONE, left: NONE, right: NONE };
const bandW = [CONTENT_W - 3000, 3000];
const band = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: bandW,
  rows: [new TableRow({ children: [
    new TableCell({ width: { size: bandW[0], type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: 'auto', fill: NAVY }, borders: nb,
      verticalAlign: VerticalAlign.CENTER, margins: { top: 90, bottom: 90, left: 220, right: 100 },
      children: [new Paragraph({ children: [new TextRun({ text: TITLE_TXT, font: KO, size: TITLE, bold: true, color: 'FFFFFF' })] })] }),
    new TableCell({ width: { size: bandW[1], type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: 'auto', fill: NAVY }, borders: nb,
      verticalAlign: VerticalAlign.CENTER, margins: { top: 90, bottom: 90, left: 100, right: 220 },
      children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: 'NECK TEST 4', font: LATIN, size: 32, bold: true, italics: true, color: 'FFFFFF' })] })] }),
  ] })],
});

const lab = (t) => ({ t, fill: LAV, bold: true });
const infoW = [1500, CONTENT_W / 2 - 1500, 1500, CONTENT_W / 2 - 1500];
const info = table(infoW, [
  [lab('과제명'), '초경 엔드밀 넥 원통연삭 조건 확립', lab('문서번호'), DOCNO],
  [lab('시험 기간'), '2026. 11. 3.', lab('보고일'), '2026. 11. 4.'],
  [lab('장비'), 'ANCA GX7, iGrind 원통연삭', lab('작성'), '생산팀 한경준'],
  [lab('시험 대상'), 'D3 초경 엔드밀 1개, 날장 5.4 mm, 생크 d 6 mm', lab('상태'), '한계 시험, 양산 미적용'],
  [lab('프로그램'), 'GX7_AFCY_D3.8_S6_Test3.tom 기반 6개 섹션', lab('비고'), '자료 정리 및 계산: Claude Cowork 보조'],
], false);

const sumW = [1300, CONTENT_W - 1300];
const nv = (t) => ({ t, fill: NAVY, bold: true, color: 'FFFFFF', align: AlignmentType.CENTER });
const summary = table(sumW, [
  [nv('결론'), 'D3 엔드밀 넥을 6회 나눠 연삭해 목표 넥 지름 2.000 mm에 도달함. 날장 진입 쪽 지름, 유효장 L2 위치, 생크 앞 턱은 다음 시험 과제로 남음'],
  [nv('근거'), '6회 뒤 넥 지름 목 중간 2.01 mm, 테이퍼 진입 2.027 mm, 날장 진입 2.165 mm. 연삭 중 스핀들 부하 5% 이하. 공구 1개 실측'],
  [nv('요청'), '요청 없음(참고 보고). 넥 휠 드레싱 후 테스트 5 진행 예정'],
], false);

const t1 = table(widthsOf([28, 30, 26, 16]), [
  ['평가 항목', '판정 기준', '결과', '판정'],
  ['넥 지름 (mm)', '목표 2.000보다 가늘지 않을 것', '2.01 ~ 2.165', C('합격')],
  ['스핀들 부하 (%)', '10 이하, 이상음 없음', '5 이하, 테이퍼 진입 때 소음', C('보류')],
  ['날 침범', '넥 시작이 날장 5.4 mm 이상', '5.46 mm', C('합격')],
  ['머리 쪽 치핑', '없음', '없음', C('합격')],
]);

const t2 = table(widthsOf([26, 74]), [
  ['구분', '내용'],
  ['연삭기', 'ANCA GX7, ToolRoom RN32.1-1, iGrind 원통연삭(Cylindrical Grinding), 3시 방향 연삭'],
  ['넥 휠', '홍익다이아 다이아몬드 레진 휠 Ø125 mm, 앞면 원통부 2.8 mm와 12° 경사면 7 mm. Qualify 지름 125.102 mm'],
  ['휠 등록 형상', '1A1 원통 폭 10.487 mm로 단순화. 시뮬레이션은 12° 경사면을 반영하지 않음'],
  ['시험 공구', 'D3 초경 엔드밀 1개. 테스트 3용으로 준비한 공구이며 날장 5.4 mm, 생크 d 6 mm, 돌출 25 mm. 머리 D는 재지 않았고 계산은 2.970 mm로 가정'],
  ['측정 장비', '디지털 마이크로미터 Mitutoyo 293-340-30, 분해능 0.001 mm. 사용 장비는 확인 필요'],
]);

const t3 = table(widthsOf([40, 60]), [
  ['조건 (단위)', '값'],
  ['X 시작 위치 (mm)', '−5.400'],
  ['연삭 길이 Step length (mm)', '16.540, 끝 위치 X −21.94'],
  ['휠 회전수 (rpm)', '3,500'],
  ['원주속도 Vc (m/s)', '22.93, 계산'],
  ['황삭', '사용 안 함, 회차마다 정삭 1패스'],
  ['정삭 진입 속도 (mm/min)', '0.5'],
  ['공구 회전 A Spin (rpm)', '25'],
  ['블랭크 지름 Blank OD (mm)', '6.000'],
  ['휠 돌출 허용 Allow Wheel Overhang', '해제'],
]);

const t4 = table(widthsOf([10, 18, 16, 18, 22, 16]), [
  ['회차', '입력 지름 (mm)', '정삭 여유 (mm)', '이송 (mm/min)', '측정 넥 지름 (mm)', '측정 L2 (mm)'],
  [C('1'), C('5.080'), C('0.200'), C('3.5'), C('미수신'), C('미수신')],
  [C('2'), C('4.050'), C('0.200'), C('3.5'), C('미수신'), C('미수신')],
  [C('3'), C('2.670'), C('0.500'), C('4.0'), C('2.78'), C('13.93')],
  [C('4'), C('2.330'), C('0.500'), C('4.0'), C('2.40'), C('13.98')],
  [C('5'), C('2.000'), C('0.500'), C('4.0'), C('2.08'), C('13.95')],
  [C('6'), C('1.920'), C('미기록'), C('미기록'), C('2.01'), C('13.95')],
]);

const t5 = table(widthsOf([30, 22, 22, 26]), [
  ['측정 위치', '측정값 (mm)', '측정 − 입력 (mm)', '목표 대비 (mm)'],
  ['날장 진입', C('2.165'), C('+0.245'), C('+0.165')],
  ['목 중간', C('2.01'), C('+0.090'), C('+0.010')],
  ['테이퍼 진입', C('2.027'), C('+0.107'), C('+0.027')],
]);

const t6 = table(widthsOf([46, 27, 27]), [
  ['항목 (단위)', '값', '구분'],
  ['넥 시작 위치 (mm)', C('5.46'), C('실측')],
  ['유효장 L2 (mm)', C('13.95'), C('실측')],
  ['생크 지름 d (mm)', C('5.98'), C('실측')],
  ['턱 아래 테이퍼 끝 지름 (mm)', C('4.63'), C('실측')],
  ['턱 높이 반경 (mm)', C('0.675'), C('계산')],
  ['턱 위치 X (mm)', C('미측정'), C('')],
]);

const t7 = table(widthsOf([24, 22, 22, 32]), [
  ['회차', '입력 지름 (mm)', '측정 − 입력 (mm)', '명령 반경 절입 (mm)'],
  [C('3'), C('2.670'), C('+0.110'), C('0.150')],
  [C('4'), C('2.330'), C('+0.070'), C('0.225')],
  [C('5'), C('2.000'), C('+0.080'), C('0.200')],
  [C('6'), C('1.920'), C('+0.090'), C('0.080')],
]);

const t8 = table(widthsOf([26, 18, 18, 18, 20]), [
  ['평가 항목', '목표', '결과', '달성 여부', '비고'],
  ['넥 지름 (mm)', C('2.000'), C('2.01'), C('달성'), '목 중간 기준'],
  ['유효장 L2 (mm)', C('15'), C('13.95'), C('미달'), '1.05 mm 짧음'],
  ['생크 앞 턱', C('없음'), C('반경 0.675 mm'), C('미달'), '휠 경사면 길이 부족'],
  ['스핀들 부하 (%)', C('10 이하'), C('5 이하'), C('달성'), ''],
]);

const warnBox = (txt) => new Table({
  width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W],
  rows: [new TableRow({ children: [new TableCell({ width: { size: CONTENT_W, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, color: 'auto', fill: CREAM },
    borders: { top: { style: BorderStyle.SINGLE, size: 8, color: INK }, bottom: { style: BorderStyle.SINGLE, size: 8, color: INK }, left: { style: BorderStyle.SINGLE, size: 8, color: INK }, right: { style: BorderStyle.SINGLE, size: 8, color: INK } },
    margins: { top: 100, bottom: 100, left: 160, right: 160 },
    children: [new Paragraph({ children: [run('경고: ', { bold: true, size: TBL }), run(txt, { size: TBL })] })] })] })],
});

const children = [
  band,
  p([run('D3 초경 엔드밀 시험 공구 1개, ANCA GX7 원통연삭, 넥 지름 2 mm 한계 시험', { color: GRAY })], { spacing: { before: 120, after: 160 } }),
  info,
  h1('요약'),
  summary,
  caption('표 1. 시험 결과 요약'),
  t1,
  note('※ 부하는 기준 안이었으나 테이퍼 진입 때 소음이 있어 보류로 둠. 치핑은 현장 확인(한경준)'),
  note('※ 신뢰도 구분: 실측은 사내 직접 측정, 계산은 측정값으로 계산, 추정은 해석임'),

  h1('1. 서론'),
  h2('가. 시험 배경 및 목적'),
  item('1)', '테스트 1과 2에서 D3 엔드밀 넥을 2.85 mm 안팎으로 내는 조건을 확인함'),
  item('2)', '본 시험은 같은 휠과 장비로 넥을 어디까지 가늘게 낼 수 있는지 보는 한계 시험임. 넥 지름 2.000 mm를 목표로 하여 입력 보정, 스핀들 부하, 넥 끝 형상 자료를 모으는 것이 목적임'),
  h2('나. 시험 범위'),
  item('1)', '공구 1개, 6회 연삭. 넥 지름 2.000 mm는 사내 넥 기준(날지름의 0.95 ~ 0.975배) 밖이므로 시험품으로만 다룸'),
  item('2)', '진원도, 표면 거칠기 Ra, 넥 강성을 확인하는 절삭 사용 시험은 다루지 않음'),

  h1('2. 시험 방법'),
  h2('가. 시험 장비 및 공구'),
  caption('표 2. 시험 장비 및 공구'),
  t2,
  h2('나. 시험 조건'),
  caption('표 3. 공통 시험 조건'),
  t3,
  note('※ Vc = π × 125.102 × 3,500 ÷ 60,000 = 22.93 m/s. 사내 휠 원주속도 상한 25 m/s 이내'),
  note('※ X 끝 위치는 목표 L2 15 mm에 휠 경사면 길이 6.94 mm를 더한 값. 2026. 10. 21. 임시 적용한 관계임'),
  item('1)', '회차마다 섹션 하나만 켜고 연삭한 뒤 측정함. 바꾼 변수는 입력 지름이며 1회와 2회는 생크 쪽 테이퍼만 먼저 깎는 섹션임'),
  item('2)', '회차별 입력 지름과 정삭 여유, 이송은 3장 표 4에 함께 적음'),
  h2('다. 설비 상태'),
  item('1)', '넥 휠 드레싱은 보류한 상태로 시험함. 마지막 드레싱 시점과 시험 당일 휠 지름은 기록하지 않음'),
  item('2)', '스핀들 런아웃, 휠 밸런스, 쿨런트 농도, 예열은 측정하지 않음'),
  h2('라. 측정 방법'),
  item('1)', '넥 지름은 디지털 마이크로미터로 잼. 3 ~ 5회는 위치를 나누지 않고 1값을, 6회는 날장 진입과 목 중간, 테이퍼 진입 3곳을 잼'),
  item('2)', '측정 위치가 경계에서 몇 mm 떨어졌는지는 기록하지 않음. 진원도와 Ra는 장비가 정해지지 않아 측정하지 않음'),
  h2('마. 판정 기준'),
  item('1)', '넥 지름은 목표 2.000 mm보다 가늘면 불합격으로 함. 넥은 깎은 뒤 되돌릴 수 없기 때문임'),
  item('2)', '스핀들 부하는 10% 이하이고 이상음과 떨림, 탄 색이 없을 것. 넘으면 그 회차에서 멈춤'),
  item('3)', '넥 시작 위치는 날장 5.4 mm보다 안쪽이면 날을 깎은 것으로 보고 불합격으로 함'),
  item('4)', '시험 전에 넥 지름 상한은 정하지 않음. 유효장 L2와 턱은 판정 대신 5장 목표 달성도로 평가함'),

  h1('3. 시험 결과'),
  h2('가. 회차별 넥 지름'),
  caption('표 4. 회차별 입력값과 측정값'),
  t4,
  note('※ 1회와 2회 결과, 6회 정삭 여유와 이송은 컴퓨터2 기록에 없음'),
  item('1)', '3 ~ 5회 측정 L2는 13.93 ~ 13.98 mm로 회차 간 차이가 0.05 mm 이내임'),
  item('2)', '스핀들 부하는 3 ~ 5회 모두 5% 이하였음. 휠이 테이퍼 쪽에 들어갈 때 3%에서 5%로 오르며 소음이 남'),
  h2('나. 6회 뒤 넥 지름'),
  caption('표 5. 6회 뒤 위치별 넥 지름 (입력 1.920 mm, 목표 2.000 mm)'),
  t5,
  item('1)', '목 중간과 테이퍼 진입은 목표보다 0.010 ~ 0.027 mm 굵음'),
  item('2)', '날장 진입만 목 중간보다 0.155 mm 굵게 남음'),
  h2('다. 6회 뒤 형상'),
  caption('표 6. 6회 뒤 형상 측정값'),
  t6,
  note('※ 턱 높이 = (5.98 − 4.63) ÷ 2 = 0.675 mm'),
  item('1)', '넥 시작부 경계는 깨끗하고 머리 쪽 치핑은 없음. 현미경 0.7배 사진 2장으로 현장 확인(한경준)'),
  item('2)', '넥에서 테이퍼로 이어지는 부분은 둥글게 연결됨. 테이퍼 면에 원주 방향 줄무늬가 보임'),

  h1('4. 고찰'),
  h2('가. 입력값 보정'),
  caption('표 7. 측정값과 입력값의 차이'),
  t7,
  note('※ 명령 반경 절입 = (앞 회차 측정 지름 − 입력 지름) ÷ 2. 3회는 머리 D 2.970 mm 가정'),
  p('측정값은 입력값보다 0.07 ~ 0.11 mm 굵었다. 넥이 2.40 mm에서 2.08 mm로 가늘어져 굽힘 강성이 약 0.56배가 되었는데도 차이는 0.01 mm만 늘었다. 공구 처짐보다 휠 기준의 고정 오차가 큰 것으로 판단된다. 이 휠 상태에서는 입력 지름을 목표보다 약 0.08 mm 작게 넣으면 된다.'),
  p('3회 차이 +0.110 mm가 가장 컸다. 2회 입력 지름이 4.050 mm여서 기존 L2와 X 15 mm 사이에 남은 양을 3회가 한꺼번에 깎았기 때문으로 판단된다. 계산상 이 구간의 반경 절입은 약 0.69 mm이다(추정).'),
  h2('나. 날장 진입 쪽 지름'),
  p('날장 진입 2.165 mm는 목 중간보다 0.155 mm 굵다. 현장에서는 휠 원통부 모서리 마모로 보았다. 경계에 너무 가까운 곳을 쟀을 가능성도 남아 있다. 드레싱 뒤 경계에서 0.5 mm 이상 떨어진 곳을 다시 재면 두 원인을 나눌 수 있다.'),
  h2('다. 유효장 L2 위치'),
  p('끝 위치 X −21.94에서 L2는 13.95 mm여서 둘의 차이는 7.99 mm였다. 사전 입력에 쓴 6.94 mm보다 1.05 mm 크고 테스트 2의 8.105 mm와 가깝다. 휠 등록 폭 10.487 mm에서 원통부 2.8 mm를 뺀 7.69 mm와도 비슷하여 휠 등록 형상과 실제 형상의 차이에서 오는 것으로 추정된다. 공구 2개의 결과이므로 사내 기준으로 정하지 않는다.'),
  h2('라. 생크 앞 턱'),
  p('휠 12° 경사면 7.0 mm가 덮는 지름 상승은 2 × 7.0 × tan 12° = 2.976 mm이다. 넥 2.0 mm에서 출발하면 경사면 끝 지름은 약 4.98 mm로 생크 6 mm에 못 미친다. 턱 없이 낼 수 있는 넥 지름 하한은 6.000 − 2.976 = 3.02 mm이다(계산). 실측 테이퍼 끝 4.63 mm는 계산보다 0.35 mm 작아서 경사면 유효 길이가 약 6.1 mm이거나 각도가 약 10.5°일 수 있다. 턱 위치를 재지 않아 어느 쪽인지 정할 수 없다.'),
  h2('마. 스핀들 부하'),
  p('회차당 명령 반경 절입 0.15 ~ 0.225 mm와 이송 4.0 mm/min에서도 부하는 5% 이하였다. 시험 전에는 테스트 2 황삭 결과로 환산해 부하가 더 클 것으로 보았으나 실제보다 크게 잡은 것이다. 테스트 2는 황삭 대각선 진입과 공구 회전 50 rpm 조건이어서 그대로 비교할 수 없다.'),
  h2('바. 시험의 한계'),
  item('1)', '공구 1개의 결과이며 머리 D를 재지 않았음'),
  item('2)', '1회와 2회 결과, 6회 일부 조건, 측정 위치의 경계 거리, 턱 위치가 기록되지 않음'),
  item('3)', '진원도와 Ra, 절삭 사용 시험을 하지 않아 넥 강성의 사용 가능 여부는 알 수 없음. 강성은 Ø D 원봉의 약 0.21배(계산)'),
  item('4)', '사진 원본 파일을 보관하지 않음'),
  gap(),
  warnBox('회차당 명령 반경 절입 0.15 ~ 0.225 mm는 사내 실적 0.075 mm의 2 ~ 3배로 초경 고절입 경고 대상임. 공구 1개에서 부하 5% 이하였다는 결과만으로 같은 절입을 반복 적용하지 않음'),

  h1('5. 결론 및 향후 계획'),
  h2('가. 결론'),
  item('1)', 'D3 엔드밀 넥을 6회 연삭해 목 중간 2.01 mm, 테이퍼 진입 2.027 mm로 목표 2.000 mm에 도달함'),
  item('2)', '연삭 중 스핀들 부하는 5% 이하였고 머리 쪽 치핑은 없음'),
  item('3)', '현재 휠 상태에서 측정값은 입력값보다 0.07 ~ 0.11 mm 굵었음. 입력 지름은 목표보다 약 0.08 mm 작게 넣어야 함'),
  item('4)', '날장 진입 쪽 지름 +0.155 mm, L2 부족 1.05 mm, 생크 앞 턱 반경 0.675 mm가 남음'),
  item('5)', '공구 1개의 시험값이며 사내 넥 기준 밖 시험품이므로 양산에는 적용하지 않음'),
  h2('나. 목표 달성도'),
  caption('표 8. 목표 달성도'),
  t8,
  h2('다. 향후 계획 및 요청 사항'),
  item('1)', '넥 휠을 드레싱함. 드레싱 전에 휠 지름을 먼저 재고 드레싱 뒤 지름과 경사면 폭, Qualify 값을 다시 등록함'),
  item('2)', '테스트 5는 새 공구로 진행함. 끝 위치는 −(15 + 8.0) = −23.0 mm 안팎으로 잡고 3번째 회차에서 입력 보정을 다시 잼'),
  item('3)', '턱을 없애는 연장 섹션은 테스트 5에서 테이퍼 각을 잰 뒤 시험함. 돌출은 31 mm 이상이 필요함(계산)'),
  item('4)', '드레싱과 돌출이 함께 바뀌므로 테스트 4 보정값과 직접 비교하지 않음'),
  item('5)', '넥 지름 3.02 mm 미만에서 턱을 없애려면 경사면이 더 긴 휠이 필요함. 경사면 10 mm 휠이면 하한이 6.000 − 2 × 10 × tan 12° = 1.75 mm가 됨. 추가 발주 때 검토함'),

  h1('부록'),
  h2('가. 측정 원자료'),
  item('1)', '3 ~ 5회 현장 보고: 넥 지름 2.78, 2.4, 2.08 mm, L 13.93, 13.98, 13.95 mm, 부하 5% 이하'),
  item('2)', '6회 현장 보고: 날장 5.46 mm, L2 13.95 mm, 넥 지름 2.165, 2.01, 2.027 mm, 생크 5.98 mm, 테이퍼 끝 4.63 mm'),
  h2('나. 프로그램 및 사진 파일'),
  item('1)', '원본 프로그램은 GX7_AFCY_D3.8_S6_Test3.tom. 회차 파일은 GX7_AFCY_D3p8_S6_T4_1 ~ 6_20261103.tom 규칙으로 저장함(파일명 확인 필요)'),
  item('2)', '사진 2장, 현미경 0.7배, 원본 파일명 없음. 원본 보관 필요'),
  h2('다. 사내 기록 위치'),
  item('1)', '결정: decisions.md 2026. 11. 4. (1) 테스트 4 결과와 (2) 테스트 5 전 드레싱'),
  item('2)', '위키: cadcam/원통연삭-넥-시험-AFCY-D3-2026-10-20 §7-D, 기록표 reports/01_연삭조건/넥_원통연삭_시험연삭_기록표_v2.xlsx T8 ~ T13'),
  item('3)', '시험 원기록: 프로젝트 문서 23_ 가공 전 검수, 24_ 결과, 25_ 시험 종료 인계(컴퓨터2, 2026. 11. 3. 17:16)'),
  h2('라. 사진 자료'),
  p('해당 없음. 원본 미보관'),
  h2('마. 개정 이력'),
  table(widthsOf([20, 14, 46, 20]), [
    ['날짜', '판', '변경', '양산 적용'],
    ['2026. 11. 4.', C('1'), '최초 작성', C('미적용')],
  ]),
];

const doc = new Document({
  creator: '생산팀 한경준', title: TITLE_TXT,
  styles: { default: { document: { run: { font: KO, size: BODY, color: INK } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: KO, size: 34, bold: true, color: NAVY }, paragraph: { outlineLevel: 0, keepNext: true } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: KO, size: BODY, bold: true, color: INK }, paragraph: { outlineLevel: 1, keepNext: true } },
    ] },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 850, bottom: 850, left: MARGIN_LR, right: MARGIN_LR, header: 400, footer: 400 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 120 },
      children: [new ImageRun({ type: 'png', data: fs.readFileSync(LOGO), transformation: { width: 96, height: 40 }, altText: { title: 'COGOTOOL', description: 'COGOTOOL 로고', name: 'logo' } })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
      children: [
        new TextRun({ text: TITLE_TXT + ' 제1판', font: KO, size: 20, color: GRAY }),
        new TextRun({ text: '\tCOGOTOOL  ', font: LATIN, size: 20, color: GRAY }),
        new TextRun({ children: [PageNumber.CURRENT], font: LATIN, size: 20, color: GRAY }),
      ] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log('written', OUT); });
