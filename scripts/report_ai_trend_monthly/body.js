// AI 공작기계 동향 월간 보고 — 본문 (양식 D 월간판, 2026-11-18 Cowork)
// 데이터: 환경 변수 TREND_DATA = 해당 월 month.json, TREND_DIR = 해당 월 폴더(search_log.csv, fig/)
// 누적 목록: 이 폴더의 items_master.csv (삭제 없이 추가만, 상태 변경은 상태이력 열에 덧붙임)
// 문체: 사내 보고서 개조식 (standards/보고서-작성-규칙 §5), doc_style_check 기준 넘은 항목 0
const fs = require('fs');
const path = require('path');
const { ExternalHyperlink, TextRun: TR } = require('docx');

const readCsv = (f) => {
  if (!fs.existsSync(f)) return [];
  const rows = []; let row = [], cur = '', q = false; const s = fs.readFileSync(f, 'utf8').replace(/^﻿/, '');
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (q) { if (c === '"' && s[i + 1] === '"') { cur += '"'; i++; } else if (c === '"') q = false; else cur += c; }
    else if (c === '"') q = true; else if (c === ',') { row.push(cur); cur = ''; } else if (c === '\n') { row.push(cur.replace(/\r$/, '')); rows.push(row); row = []; cur = ''; } else cur += c;
  }
  if (cur || row.length) { row.push(cur); rows.push(row); }
  const head = rows.shift() || []; return rows.filter((r) => r.length > 1).map((r) => Object.fromEntries(head.map((h, i) => [h, r[i] || ''])));
};
const clean = (t) => String(t).replace(/\s·\s/g, ', ').replace(/\s[—–]\s/g, ', ').replace(/→/g, ', ');
const refStr = (a) => (a || []).map((n) => `[${n}]`).join('');
const CLS = { A: 'A 감시, 보정', B: 'B 프로그래밍', C: 'C 상담', D: 'D 자율 장비' };
const ym = (s) => { const [y, m] = s.split('-').map(Number); return y * 12 + m - 1; };

module.exports = (H) => {
  const { img, run, p, item, h1, h2, caption, note, gap, table, W, warnBox, refParas, CONTENT_W, NAVY, LAV, SMALL, AlignmentType, Table, TableRow, Paragraph, TextRun, WidthType, bandCell, DOC_TITLE, LATIN, KO, TITLE } = H;
  const M = require(process.env.TREND_DATA);
  const DIR = process.env.TREND_DIR;
  const master = readCsv(path.join(__dirname, 'items_master.csv'));
  const end = ym(M.month), win = master.filter((r) => r['발표월'] && /^\d{4}-\d{2}$/.test(r['발표월']) && ym(r['발표월']) <= end && ym(r['발표월']) > end - 12);
  const cnt = (f) => win.filter(f).length;
  const [Y, Mo] = M.month.split('-');
  const label = `${Y}. ${Number(Mo)}.`;

  const bandW = [CONTENT_W - 2700, 2700];
  const band = new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: bandW, rows: [new TableRow({ children: [
    bandCell(bandW[0], [new Paragraph({ children: [new TextRun({ text: DOC_TITLE, font: KO, size: 34, bold: true, color: 'FFFFFF' })] })], { top: 90, bottom: 90, left: 220, right: 100 }),
    bandCell(bandW[1], [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: 'MONTHLY AI TREND', font: LATIN, size: 24, bold: true, italics: true, color: 'FFFFFF' })] })], { top: 90, bottom: 90, left: 100, right: 220 }),
  ] })] });
  const lab = (t) => ({ t, fill: LAV, bold: true });
  const infoW = [1500, CONTENT_W / 2 - 1500, 1500, CONTENT_W / 2 - 1500];
  const info = table(infoW, [
    [lab('과제명'), '머시닝센터 AI 업계 동향 월간 추적', lab('문서번호'), `AI공작기계_월간동향_${Y}${Mo}`],
    [lab('보고일'), M.report_date, lab('자료 기간'), `${label} 1. ~ 말일 발표`],
    [lab('작성'), 'Claude Cowork 예약 작업', lab('검토'), '생산팀 한경준'],
    [lab('목적'), '업계 동향 공유, 도입 검토 전 단계', lab('판'), M.edition || '제1판'],
    [lab('대상'), '머시닝센터 중심, CNC 장치와 CAM 포함, 연삭기는 짧게', lab('지역'), '한국, 일본, 중국, 대만, 유럽, 미국'],
  ], false);
  const nv = (t) => ({ t, fill: NAVY, bold: true, color: 'FFFFFF', align: AlignmentType.CENTER });
  const summary = table([1300, CONTENT_W - 1300], [[nv('결론'), clean(M.summary.결론)], [nv('근거'), clean(M.summary.근거)], [nv('요청'), clean(M.summary.요청)]], false);

  const wN = W(2.6, 0.7, 0.8, 3.6, 1.0, 0.8, 0.7, 0.9);
  const tNew = M.new_items.length ? table(wN, [
    ['업체와 이름', '분류', '지역', '하는 일', '상태', '구분', '확인 수', '출처'],
    ...M.new_items.map((r) => [`${r.업체}\n${r.이름}`, { t: r.분류, align: AlignmentType.CENTER }, r.지역, clean(r.하는일), r.상태, r.구분, { t: String(r.확인수), align: AlignmentType.CENTER }, refStr(r.refs)]),
  ], true, 20) : p('이번 달에는 범위에 맞는 새 발표를 찾지 못함. 검색 기록은 부록 가항');
  const tChg = M.changed.length ? table(W(3, 2, 2, 3), [
    ['항목', '이전 상태', '지금 상태', '근거'],
    ...M.changed.map((r) => [clean(r.항목), r.이전, r.지금, `${clean(r.근거 || '')}${refStr(r.refs)}`]),
  ], true, SMALL) : p('이번 달 상태가 바뀐 항목 없음');
  const tCross = table(W(3, 1.4, 1.4, 1.4, 1.4, 1.4), [
    ['분류', '판매 중', '개발', '시연', '컨셉', '계'],
    ...['A', 'B', 'C', 'D'].map((c) => [CLS[c], ...['판매 중', '개발', '시연', '컨셉'].map((s) => ({ t: String(cnt((r) => r['분류'] === c && r['상태'] === s)), align: AlignmentType.CENTER })), { t: String(cnt((r) => r['분류'] === c)), align: AlignmentType.CENTER, bold: true }]),
    [{ t: '계', bold: true }, ...['판매 중', '개발', '시연', '컨셉'].map((s) => ({ t: String(cnt((r) => r['상태'] === s)), align: AlignmentType.CENTER, bold: true })), { t: String(win.length), align: AlignmentType.CENTER, bold: true }],
  ], true, SMALL);
  const tCond = table(W(4.5, 1.5, 4), [
    ['판단이 바뀔 조건', '이번 달', '근거'],
    ...M.conditions.map((r) => [clean(r.조건), r.해당, clean(r.근거)]),
  ], true, SMALL);
  const SEARCH = readCsv(path.join(DIR, 'search_log.csv'));
  const tSearch = table(W(0.7, 1.1, 0.8, 4.3, 0.7, 0.7, 2.6), [
    ['번호', '언어', '지역', '검색어', '결과', '채택', '메모'],
    ...SEARCH.map((s) => [{ t: s.no, align: AlignmentType.CENTER }, s.lang, s.region, clean(s.query), { t: s.returned, align: AlignmentType.CENTER }, { t: s.adopted, align: AlignmentType.CENTER }, clean(s.note)]),
    [{ t: '계', bold: true, span: 4 }, { t: String(SEARCH.reduce((a, s) => a + Number(s.returned || 0), 0)), align: AlignmentType.CENTER, bold: true }, { t: String(SEARCH.reduce((a, s) => a + Number(s.adopted || 0), 0)), align: AlignmentType.CENTER, bold: true }, ''],
  ], true, 18);
  const tEx = (rows, h) => (rows && rows.length ? table(W(4, 6), [h, ...rows.map((r) => [clean(r[0]), clean(r[1])])], true, SMALL) : p('없음'));
  const tRev = table(W(1.2, 2, 6.8), [['판', '날짜', '내용'], ...(M.revisions || [[M.edition || '제1판', M.report_date, '월간 예약 작업으로 작성']]).map((r) => r.map(clean))], true, SMALL);
  const media = (M.media || []).map(([t, u], i) => new Paragraph({ indent: { left: 560, hanging: 560 }, spacing: { after: 50, line: 280 },
    children: [run(`${i + 1}) `, { size: SMALL }), run(`${clean(t)} `, { size: SMALL }), new ExternalHyperlink({ link: u, children: [new TR({ text: u, font: LATIN, size: 18, color: '1F4E9A', underline: {} })] })] }));

  return [
    band, gap(), info,
    h1('요약'), summary,
    note('※ 구분 「추정」은 기사로만 확인한 제조사 주장, 「제조사」는 제조사 원문 확인. 상태와 분류 기준은 연간 보고 제1판 표 1과 같음'),
    h1(`1. ${label} 새 발표`),
    caption(`표 1. ${label} 새 발표 ${M.new_items.length}건`), tNew,
    ...(media.length ? [p('운용 모습을 볼 수 있는 영상과 사진은 아래와 같다. 시연은 전시 데모라 성능 검증이 아니다.'), ...media] : []),
    h1('2. 상태가 바뀐 항목'),
    caption('표 2. 상태 변경'), tChg,
    h1('3. 최근 12개월 누적'),
    caption('그림 1. 분류별 건수와 상태'), img('fig1_class_status.png', 16, '그림 1 분류별 건수와 상태'),
    caption('그림 2. 발표 연월별 건수'), img('fig3_month.png', 16, '그림 2 발표 연월별 건수'),
    caption('표 3. 분류와 상태별 건수'), tCross,
    note(`※ 최근 12개월 발표 ${win.length}건을 셈. 누적 목록: scripts/report_ai_trend_monthly/items_master.csv`),
    h1('4. 시사점'),
    ...M.implications.map((t, i) => item(`${i + 1})`, clean(t))),
    caption('표 4. 판단이 바뀔 조건 점검'), tCond,
    h1('5. 다음 달 확인할 것'),
    ...M.next.map((t, i) => item(`${i + 1})`, clean(t))),
    gap(),
    warnBox('주의: ', '이 보고의 수치와 일정은 업체 발표를 모은 것이며 장비 도입이나 조건 적용의 근거로 쓰지 않음. 도입을 검토할 때는 제조사 시연과 사양서로 다시 확인함'),
    h1('참고 문헌'),
    ...refParas(),
    h1('부록'),
    h2('가. 검색 기록'), caption(`표 5. 검색 기록, ${M.report_date} KST`), tSearch,
    note('※ 결과는 검색 화면에 나온 건수, 채택은 그중 출처로 쓴 건수임'),
    h2('나. 제외한 자료'), caption('표 6. 조사했으나 제외한 자료'), tEx(M.excluded, ['자료', '뺀 이유']),
    h2('다. 읽지 못한 자료'), caption('표 7. 읽지 못한 자료'), tEx(M.unread, ['자료', '못 읽은 이유와 대신 확인한 것']),
    h2('라. 개정 이력'), caption('표 8. 개정 이력'), tRev,
  ];
};
