const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/b975f8eb-8440-4783-8ac8-024b9f4448eb_d9575592-dd32-4ad8-8939-5359bb80f9d7/pptx/scripts/apply_theme.js");

const OUT = process.argv[2] || "deck_v02.pptx";
// 1기 발표(2026-07-14) 색·글꼴을 이어 쓴다
const H = { navy: "1F2A36", ink: "2C3E50", sub: "3A506B", gray: "6B7A88", line: "D9E2EC", bg: "F4F6F8", teal: "0E7C86", tealBg: "EAF4F5", amber: "E8930C", white: "FFFFFF" };
const THEME = {
  name: "TOOLKOREA 생산팀",
  headFontFace: "맑은 고딕",
  bodyFontFace: "맑은 고딕",
  colors: { dk1: H.navy, lt1: H.white, dk2: H.sub, lt2: H.bg, accent1: H.teal, accent2: H.ink, accent3: H.gray, accent4: H.amber, accent5: H.line, accent6: H.tealBg, hlink: H.teal, folHlink: H.sub },
};
const ASOF = "자료 기준일 2026-10-19";
const ASOF3 = "자료 기준일 2026-10-21";
const ASOF2 = "자료 기준일 2026-10-21";
const CAP = process.env.CAP_DIR || require("path").join(__dirname, "pilot_caps_20261019") + "/"; // 캡처 이미지 폴더
const CAP2 = process.env.CAP2_DIR || require("path").join(__dirname, "pilot_caps_20261021") + "/"; // v0.5 넥 시험 그림

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "Claude AI 활용 성과 — 파일럿 2기 (생산팀)";
  pres.author = "생산팀";
  const C = pres.SchemeColor;

  pres.defineSlideMaster({
    title: "COVER",
    background: { color: C.text1 },
    objects: [
      { placeholder: { options: { name: "kicker", type: "body", x: 0.8, y: 1.7, w: 9, h: 0.4, fontSize: 16, bold: true, color: C.accent5, charSpacing: 2, margin: 0 }, text: "" } },
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.2, w: 11.5, h: 1.0, fontSize: 40, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.35, w: 11.5, h: 0.6, fontSize: 20, color: C.accent5, align: "left", valign: "top", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    margin: [0.5, 0.6, 0.7, 0.6],
    objects: [
      { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.35, w: 9, h: 0.35, fontSize: 14, bold: true, color: C.accent1, margin: 0 }, text: "" } },
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.7, w: 12.1, h: 1.25, fontSize: 36, bold: true, color: C.text1, align: "left", valign: "top", lineSpacingMultiple: 0.95, margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 1.45, w: 12.1, h: 0.45, fontSize: 20, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } },
      { text: { text: "TOOLKOREA 생산팀, Claude AI 파일럿 2기", options: { x: 7.2, y: 7.0, w: 5.0, h: 0.3, fontSize: 11, color: C.accent3, align: "right", margin: 0 } } },
    ],
    slideNumber: { x: 12.3, y: 7.0, w: 0.45, h: 0.3, fontSize: 11, color: C.accent3, align: "right" },
  });

  const box = (s, name, x, y, w, h, fill, line) =>
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: line || fill, width: 0.75 }, objectName: name });
  const note = (s, t) => s.addText(t, { x: 0.6, y: 6.95, w: 6.5, h: 0.35, fontSize: 12, color: H.gray, margin: 0, isTextBox: true, objectName: "footnote" });
  const head = (s, kicker, title, msg) => {
    if (kicker) s.addText(kicker, { placeholder: "kicker" });
    s.addText(title, { placeholder: "title" });
    if (msg) s.addText(msg, { placeholder: "body" });
  };
  const TH = (t, o = {}) => ({ text: t, options: { bold: true, color: H.white, fill: { color: H.navy }, fontSize: 17, valign: "middle", ...o } });
  const TD = (t, o = {}) => ({ text: t, options: { color: H.navy, fontSize: 17, valign: "middle", ...o } });
  const tableOpts = (y, colW, rowH) => ({ x: 0.6, y, w: colW.reduce((a, b) => a + b, 0), colW, rowH, border: { type: "solid", pt: 0.75, color: H.line }, margin: [4, 8, 4, 8], fontFace: "맑은 고딕" });

  // ===== 1. 표지 =====
  pres.addSection({ title: "표지" });
  let s = pres.addSlide({ masterName: "COVER", sectionTitle: "표지" });
  s.addText("TOOLKOREA 생산팀    Claude AI 파일럿 2기 성과 발표", { placeholder: "kicker" });
  s.addText("재연마 현장 데이터의 정리와 업무 자동화", { placeholder: "title" });
  s.addText("2기(2026. 7 ~ 10) 생산팀 적용 결과", { placeholder: "body" });
  s.addShape(pres.shapes.LINE, { x: 0.8, y: 4.6, w: 11.7, h: 0, line: { color: H.sub, width: 0.75 }, objectName: "cover-rule" });
  s.addText([
    { text: "발표  ", options: { color: H.gray } }, { text: "2026. 11. 10 (화)", options: { color: H.white, breakLine: true } },
    { text: "발표자  ", options: { color: H.gray } }, { text: "생산팀 한경준", options: { color: H.white } },
  ], { x: 0.8, y: 4.85, w: 6, h: 0.9, fontSize: 18, margin: 0, valign: "top", isTextBox: true, objectName: "cover-meta" });
  s.addText("근거: 사내 지식 위키(cnc-wiki) 기록, 자동화 실행 로그  |  " + ASOF, { x: 0.8, y: 6.75, w: 11.7, h: 0.35, fontSize: 12, color: H.gray, margin: 0, isTextBox: true, objectName: "cover-src" });
  s.addNotes("[0:20] 생산팀 발표입니다. 2기 동안 재연마 현장의 흩어진 데이터를 정리하고, 매일 반복하던 보고 업무를 자동화한 결과를 말씀드리겠습니다.");

  // ===== 2. 목차 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "표지" });
  head(s, "목차", "발표 순서");
  const toc = [
    ["01", "추진 배경", "현황과 문제점, 추진 방향", ""],
    ["02", "팀 내 Claude 활용 현황", "핵심 수치, 활용 영역, 활용 사례, 추진 경과", "필수 ①"],
    ["03", "자동화 시스템 소개 및 시연", "시스템 구성, 실행 화면, 질의응답", "필수 ②"],
    ["04", "업무 적용 전후 비교", "정량 비교, 근거와 신뢰도", "필수 ③"],
    ["05", "한계와 향후 과제", "운영하며 확인한 한계, 대응, 다음 과제", ""],
  ];
  toc.forEach((r, i) => {
    const y = 2.2 + i * 0.88;
    box(s, "toc" + i, 0.6, y, 12.1, 0.74, i % 2 ? H.white : H.bg, H.line);
    s.addText(r[0], { x: 0.85, y, w: 0.9, h: 0.74, fontSize: 24, bold: true, color: H.teal, valign: "middle", margin: 0, isTextBox: true, objectName: "toc" + i + "-n" });
    s.addText(r[1], { x: 1.8, y, w: 5.0, h: 0.74, fontSize: 20, bold: true, color: H.navy, valign: "middle", margin: 0, isTextBox: true, objectName: "toc" + i + "-t" });
    s.addText(r[2], { x: 6.8, y, w: 4.4, h: 0.74, fontSize: 16, color: H.gray, valign: "middle", margin: 0, isTextBox: true, objectName: "toc" + i + "-d" });
    if (r[3]) s.addText(r[3], { x: 11.3, y: y + 0.17, w: 1.2, h: 0.4, fontSize: 14, bold: true, color: H.teal, fill: { color: H.tealBg }, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "toc" + i + "-tag" });
  });
  s.addNotes("[0:20] 순서입니다. 공지된 필수 항목 세 가지를 2·3·4장에 담았습니다.");

  // ===== 3. 추진 배경 =====
  pres.addSection({ title: "01 추진 배경" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 추진 배경" });
  head(s, "01  추진 배경", "매일 손으로 하던 일일보고 집계와 장비 투입 판단");
  // v0.4: 장비 사진은 넣지 않음(한경준님 10-19) — 실제 자료 2종(가공비·금액 열 숨김 / 연락처·주소 흐림)
  s.addText("월간생산일지 엑셀, 하루 1시트 수기 입력", { x: 0.6, y: 2.15, w: 5.0, h: 0.32, fontSize: 13, bold: true, color: H.sub, margin: 0, isTextBox: true, objectName: "src0-cap" });
  s.addImage({ path: CAP + "monthly_log.png", x: 0.6, y: 2.5, w: 5.0, h: 5.0 * 438 / 1276, objectName: "src0-img", altText: "재연마 월간생산일지 엑셀 화면 (10-16 시트, 금액 열 숨김)" });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 2.5, w: 5.0, h: 5.0 * 438 / 1276, fill: { type: "none" }, line: { color: H.line, width: 0.75 }, objectName: "src0-frame" });
  s.addText("수리 발주서 PDF, 장비마다 따로 보관", { x: 0.6, y: 4.42, w: 5.0, h: 0.32, fontSize: 13, bold: true, color: H.sub, margin: 0, isTextBox: true, objectName: "src1-cap" });
  s.addImage({ path: CAP + "repair_order.png", x: 0.6, y: 4.77, w: 3.8, h: 3.8 * 575 / 1150, objectName: "src1-img", altText: "장비 수리 발주서 PDF (연락처·주소 흐림 처리)" });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 4.77, w: 3.8, h: 3.8 * 575 / 1150, fill: { type: "none" }, line: { color: H.line, width: 0.75 }, objectName: "src1-frame" });
  box(s, "bg-asis", 5.9, 2.15, 6.8, 2.2, H.bg, H.line);
  s.addText("도입 전", { x: 6.15, y: 2.25, w: 6.3, h: 0.4, fontSize: 17, bold: true, color: H.sub, margin: 0, isTextBox: true, objectName: "asis-h" });
  s.addText([
    { text: "일일보고는 매일 엑셀로 손집계", options: { bullet: true, breakLine: true } },
    { text: "장비 투입 순서는 담당자 경험으로 결정", options: { bullet: true, breakLine: true } },
    { text: "조건을 바꾼 이유, 고장 처리 경위는 기록이 없음", options: { bullet: true } },
  ], { x: 6.15, y: 2.7, w: 6.35, h: 1.55, fontSize: 17, color: H.ink, valign: "top", margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: "asis-t" });
  s.addShape(pres.shapes.DOWN_ARROW, { x: 9.05, y: 4.42, w: 0.5, h: 0.32, fill: { color: H.teal }, line: { color: H.teal }, objectName: "bg-arrow" });
  box(s, "bg-tobe", 5.9, 4.8, 6.8, 1.9, H.tealBg, H.line);
  s.addText("추진 방향", { x: 6.15, y: 4.9, w: 6.3, h: 0.4, fontSize: 17, bold: true, color: H.teal, margin: 0, isTextBox: true, objectName: "tobe-h" });
  s.addText([
    { text: "출처와 신뢰도를 붙여 사내 위키에 기록", options: { bullet: true, breakLine: true } },
    { text: "반복 집계는 업무 PC 예약 실행으로", options: { bullet: true, breakLine: true } },
    { text: "기존 값은 지우지 않고 이력으로 보존", options: { bullet: true } },
  ], { x: 6.15, y: 5.32, w: 6.35, h: 1.3, fontSize: 17, color: H.ink, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: "tobe-t" });
  note(s, "생산팀 재연마 장비 2대, ANCA FastGrind와 GX7");
  s.addNotes("[0:50] (왼쪽 자료를 가리키며) 생산팀은 ANCA 장비 두 대로 재연마를 합니다. 왼쪽이 실제 쓰던 월간생산일지와 수리 발주서입니다. 자료가 ERP, 엑셀, PDF, 사람 머릿속에 흩어져 있었고, 일일보고 집계와 투입 판단을 매일 손으로 했습니다. 그래서 세 방향으로 추진했습니다 — 한곳에 기록, 반복은 자동 실행, 판단 근거는 남긴다.");

  // ===== 4. 활용 현황 — 핵심 수치 =====
  pres.addSection({ title: "02 활용 현황" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 활용 현황" });
  head(s, "02  팀 내 Claude 활용 현황  |  필수 ①", "6개월 동안 쌓은 재연마 기록 문서 138개");
  [["138", "개", "재연마 기록 문서", "장비, 휠, 연삭 조건, 수리 이력"], ["약 300", "건", "판단 근거 기록", "무엇을 왜 바꿨는지"]].forEach((k, i) => {
    const x = 0.6 + i * 6.15, w = 5.95;
    box(s, "kpi" + i, x, 2.2, w, 2.0, H.bg, H.line);
    s.addText([{ text: k[0], options: { fontSize: 50, bold: true, color: H.teal } }, { text: " " + k[1], options: { fontSize: 22, bold: true, color: H.navy } }],
      { x: x + 0.3, y: 2.35, w: 3.3, h: 1.7, valign: "middle", margin: 0, isTextBox: true, objectName: "kpi" + i + "-n" });
    s.addText([{ text: k[2], options: { fontSize: 22, bold: true, color: H.navy, breakLine: true } }, { text: k[3], options: { fontSize: 17, color: H.gray } }],
      { x: x + 3.6, y: 2.35, w: w - 3.8, h: 1.7, valign: "middle", margin: 0, isTextBox: true, objectName: "kpi" + i + "-l" });
  });
  s.addText("일일보고 133건, 단가표 대조 10,744건, 자동화 스크립트 55개", { x: 0.6, y: 4.4, w: 12.1, h: 0.45, fontSize: 17, color: H.sub, margin: 0, isTextBox: true, objectName: "kpi-etc" });
  box(s, "rule-box", 0.6, 5.05, 12.1, 1.7, H.white, H.line);
  s.addText("수치 표기 예", { x: 0.85, y: 5.15, w: 3.0, h: 0.4, fontSize: 16, bold: true, color: H.teal, margin: 0, isTextBox: true, objectName: "rule-h" });
  s.addText([
    { text: "휠 원주속도 18 ~ 22 m/s  [제조사 기준]", options: { bullet: true, breakLine: true } },
    { text: "사내 실사용 2,600 ~ 3,000 rpm  [실측]", options: { bullet: true, breakLine: true } },
    { text: "AI가 계산한 값은 [추정값]으로 적고 현장 시험 뒤 바꿈", options: { bullet: true } },
  ], { x: 0.85, y: 5.6, w: 11.6, h: 1.1, fontSize: 17, color: H.ink, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: "rule-t" });
  note(s, "근거: 위키 자동 집계, 결정 기록, 중간보고(09-14)  |  " + ASOF);
  s.addNotes("[0:50] 핵심 수치입니다. 위키 138페이지, 결정 기록 약 300건 — 왜 그렇게 했는지 나중에 찾을 수 있습니다. 일일보고 133건 — 6월 중순부터는 매일 자동 생성, 단가표 1만여 건 자동 대조. 원칙은 모든 수치에 신뢰도를 붙이고, AI 수치는 현장 검증 후에만 쓴다는 것입니다.");

  // ===== 5. 활용 영역 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 활용 현황" });
  head(s, "", "2기에 새로 맡긴 장비 투입 목록과 단가표 검수");
  const area = [
    ["지식 기록", "장비, 휠, 연삭 조건, 수리 이력 정리", "문서 138개, 수리 이력 17건"],
    ["보고 자동화", "일일보고 엑셀과 공유폴더 현황판, 매일 07:50과 16:00", "일일보고 133건"],
    ["현장 판단 보조", "ERP 수주에서 가공이 끝난 것을 빼고 장비별 투입 순서 작성", "09-28부터 사용, 규칙 8번 수정"],
    ["데이터 검수", "단가표 대조, 작업일지 읽기, ERP 조회", "단가표 10,744건 대조"],
    ["설비 문서", "로더 고장 진단, 수리 검토보고, 증설 투자 검토", "F, GX7 로더 정식 수리"],
  ];
  s.addTable([[TH("영역"), TH("내용"), TH("대표 사례")], ...area.map((r, i) => [TD(r[0], { bold: true, fill: { color: i % 2 ? H.white : H.bg } }), TD(r[1], { fill: { color: i % 2 ? H.white : H.bg } }), TD(r[2], { color: H.teal, bold: true, fill: { color: i % 2 ? H.white : H.bg } })])],
    { ...tableOpts(2.2, [2.1, 5.9, 4.1], [0.5, 0.8, 0.8, 0.8, 0.8, 0.8]), objectName: "area-table" });
  note(s, "현장 판단 보조와 데이터 검수는 2기에 새로 시작  |  " + ASOF);
  s.addNotes("[0:50] 활용 영역은 다섯 가지입니다. 2기에 새로 들어간 건 현장 판단 보조 — ERP 수주에서 이미 가공한 것을 빼고 장비별 투입 목록을 만드는 것 — 과 단가표·ERP 데이터 검수, 그리고 8월 로더 고장 때 진단부터 수리 검토보고까지 문서 작업입니다.");

  // ===== 5-1. 활용 사례 — 넥 원통연삭 시험 (v0.5 추가, 10-19 ~ 10-21) =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 활용 현황" });
  head(s, "", "두 번째 시험에서 없앤 넥 시작부 자국");
  const steps = [
    ["10-19 ~ 20", "테스트 1 정삭만 4회, 넥 시작부 같은 자리에 자국 반복"],
    ["10-20", "제조사 롱넥 31품목 치수로 넥 기준 dn = 0.96 × D 설정"],
    ["10-20 오후", "테스트 2 황삭을 대각선 진입으로 바꿔 자국 없앰"],
    ["10-21", "제조사 매뉴얼 원문으로 원인 확인, 결과 보고서 작성"],
  ];
  steps.forEach((r, i) => {
    const y = 2.15 + i * 1.15;
    box(s, "step" + i, 0.6, y, 5.6, 1.0, i % 2 ? H.white : H.bg, H.line);
    s.addText(r[0], { x: 0.75, y, w: 1.35, h: 1.0, fontSize: 16, bold: true, color: H.teal, valign: "middle", margin: 0, isTextBox: true, objectName: "step" + i + "-n" });
    s.addText(r[1], { x: 2.15, y: y + 0.05, w: 3.95, h: 0.9, fontSize: 17, color: H.ink, valign: "middle", margin: 0, isTextBox: true, objectName: "step" + i + "-t" });
  });
  s.addText("그림 1. 넥 지름 측정값과 허용 범위 (실측)", { x: 6.5, y: 2.15, w: 6.2, h: 0.32, fontSize: 13, bold: true, color: H.sub, margin: 0, isTextBox: true, objectName: "case-fig-cap" });
  s.addImage({ path: CAP2 + "neck_dn_compare.png", x: 6.5, y: 2.5, w: 6.2, h: 6.2 * 720 / 1440, objectName: "case-fig", altText: "테스트 1, 2 넥 지름 측정값과 허용 범위 그래프" });
  s.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 2.5, w: 6.2, h: 6.2 * 720 / 1440, fill: { type: "none" }, line: { color: H.line, width: 0.75 }, objectName: "case-fig-frame" });
  const cr = [["넥 시작부 자국", "매번 같은 자리에 생김", "없음"], ["치수 판정", "합격", "보류, 0.01 mm 굵음"]];
  s.addTable([[TH("항목", { fontSize: 15 }), TH("테스트 1 정삭만", { fontSize: 15 }), TH("테스트 2 황삭 대각선", { fontSize: 15 })],
    ...cr.map((r, i) => { const f = { fill: { color: i % 2 ? H.white : H.bg } }; return [TD(r[0], { bold: true, fontSize: 15, ...f }), TD(r[1], { fontSize: 15, color: H.gray, ...f }), TD(r[2], { fontSize: 15, bold: true, color: H.teal, ...f })]; })],
    { x: 6.5, y: 5.75, w: 6.2, colW: [1.6, 2.1, 2.5], rowH: [0.38, 0.38, 0.38], border: { type: "solid", pt: 0.75, color: H.line }, margin: [2, 6, 2, 6], fontFace: "맑은 고딕", objectName: "case-table" });
  note(s, "공구 1 ~ 2개 시험값, 양산 미적용  |  " + ASOF2);
  s.addNotes("[0:50] 이번 달에 새로 쓴 사례입니다. 엔드밀 목 부분을 가늘게 깎는 원통연삭 조건을 잡는 시험인데, 사내 기준이 없었습니다. 장비 PC와 사무 PC를 하나의 프로젝트로 묶어 시험하면서, 제조사 롱넥 제품 31종의 치수로 넥 지름 기준을 잡았습니다. 첫 시험은 넥 시작부에 매번 같은 자리 자국이 남았는데, 제조사 매뉴얼에서 정삭은 항상 시작 쪽 한 곳에서 들어간다는 것을 확인하고 황삭 방식을 바꿔 두 번째 시험에서 자국을 없앴습니다. 아직 공구 두 개 결과라 양산에는 쓰지 않았습니다.");

  // ===== 6. 추진 경과 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 활용 현황" });
  head(s, "", "최근 20영업일 동안 일일보고 20건 자동 생성");
  const months = ["4월", "5월", "6월", "7월", "8월", "9월", "10월*"];
  s.addChart(pres.charts.BAR, [
    { name: "소급 또는 수동 생성 (6월 9일 일괄 등)", labels: months, values: [21, 19, 12, 0, 0, 0, 0] },
    { name: "매일 자동 생성 (6월 18일부터)", labels: months, values: [0, 0, 9, 22, 19, 20, 11] },
  ], {
    x: 0.6, y: 2.1, w: 7.5, h: 4.6, barDir: "col", barGrouping: "stacked", barGapWidthPct: 60,
    chartColors: [H.gray, H.teal],
    showValue: true, dataLabelPosition: "ctr", dataLabelFormatCode: "0;;;", dataLabelFontSize: 13, dataLabelColor: H.white, dataLabelFontFace: "+mn-lt",
    showTitle: true, title: "일일보고 월별 생성 건수 (건)", titleFontSize: 14, titleColor: H.navy, titleFontFace: "+mn-lt",
    showLegend: true, legendPos: "b", legendFontSize: 13, legendColor: H.ink, legendFontFace: "+mn-lt",
    catAxisLabelColor: H.ink, catAxisLabelFontSize: 14, catAxisLabelFontFace: "+mn-lt", catAxisLineShow: false,
    valAxisLabelColor: H.gray, valAxisLabelFontSize: 12, valAxisLabelFontFace: "+mn-lt", valAxisMaxVal: 25, valAxisMajorUnit: 5, valAxisLineShow: false,
    valGridLine: { color: H.line, size: 0.5 }, catGridLine: { style: "none" },
    objectName: "daily-chart",
  });
  box(s, "tl-panel", 8.4, 2.1, 4.3, 4.6, H.bg, H.line);
  s.addText("추진 경과", { x: 8.65, y: 2.2, w: 3.8, h: 0.45, fontSize: 17, bold: true, color: H.navy, margin: 0, isTextBox: true, objectName: "tl-h" });
  const tl = [["4 ~ 6월, 1기", "위키 시작, 일일보고 자동화"], ["7월", "가공 테스트"], ["8월", "F, GX7 로더 고장"], ["9월", "ERP 연동, 투입 목록 시작"], ["10월", "자동화 1차 판정, 넥 원통연삭 시험"]];
  tl.forEach((r, i) => {
    const y = 2.75 + i * 0.77;
    s.addText(r[0], { x: 8.65, y, w: 3.8, h: 0.32, fontSize: 14, bold: true, color: i ? H.teal : H.gray, margin: 0, isTextBox: true, objectName: "tl" + i + "-m" });
    s.addText(r[1], { x: 8.65, y: y + 0.32, w: 3.8, h: 0.38, fontSize: 15, color: H.ink, margin: 0, isTextBox: true, objectName: "tl" + i + "-t" });
  });
  note(s, "파일 수정 시각 실측, *10월은 19일까지  |  " + ASOF);
  s.addNotes("[0:50] 그래프는 일일보고 파일 수입니다. 회색은 6월 9일에 지난 분을 한꺼번에 만들거나 손으로 다시 만든 것이고, 청록이 그날그날 자동으로 생성된 것입니다. 6월 18일부터는 그날그날 자동으로 만들어지고, 10월 19일 기준 최근 20영업일은 20건 모두 생성됐습니다. 오른쪽은 1기·2기 경과입니다 — 7월 가공 테스트, 8월 로더 고장 대응, 9월 ERP 연동과 투입 목록, 10월 효과 측정.");

  // ===== 7. 시스템 구성 =====
  pres.addSection({ title: "03 자동화 시스템" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 자동화 시스템" });
  head(s, "03  자동화 시스템 소개와 시연  |  필수 ②", "기존 엑셀과 ERP를 그대로 읽는 자동 실행 구조");
  const cols = [
    { x: 0.6, w: 3.4, h: "읽는 자료", items: ["ERP 수주, A/S 조회", "월간생산일지 엑셀", "출하현황 엑셀"], fill: H.bg },
    { x: 4.75, w: 3.8, h: "업무 PC", items: ["예약 실행 07:50, 16:00", "Python 스크립트로 집계, 대조, 배정", "Claude가 스크립트 작성과 점검"], fill: H.tealBg },
    { x: 9.3, w: 3.4, h: "만드는 것", items: ["일일보고 엑셀", "공유폴더 현황판", "장비별 투입 목록", "위키 문서와 결정 기록"], fill: H.bg },
  ];
  cols.forEach((c, ci) => {
    box(s, "col" + ci, c.x, 2.15, c.w, 4.5, c.fill, H.line);
    s.addText(c.h, { x: c.x + 0.2, y: 2.3, w: c.w - 0.4, h: 0.45, fontSize: 17, bold: true, color: ci === 1 ? H.teal : H.navy, margin: 0, isTextBox: true, objectName: "col" + ci + "-h" });
    c.items.forEach((t, j) => {
      const y = 2.95 + j * (ci === 2 ? 0.9 : 1.15);
      box(s, `col${ci}-i${j}`, c.x + 0.2, y, c.w - 0.4, ci === 2 ? 0.72 : 0.95, H.white, H.line);
      s.addText(t, { x: c.x + 0.35, y, w: c.w - 0.7, h: ci === 2 ? 0.72 : 0.95, fontSize: 17, color: H.ink, valign: "middle", margin: 0, isTextBox: true, objectName: `col${ci}-t${j}` });
    });
  });
  [4.08, 8.63].forEach((x, i) => s.addShape(pres.shapes.RIGHT_ARROW, { x, y: 4.1, w: 0.6, h: 0.6, fill: { color: H.teal }, line: { color: H.teal }, objectName: "flow-arrow" + i }));
  note(s, "업무 PC 1대에서 예약 작업 2개, 시작 프로그램 1개로 실행");
  s.addNotes("[0:50] 구성은 단순합니다. 새 시스템을 들인 게 아니라 원래 쓰던 ERP와 엑셀을 그대로 읽습니다. 업무 PC가 출근 로그온 때와 오후 4시에 스크립트를 돌려 일일보고, 현황판, 장비별 투입 목록을 만듭니다. Claude는 이 스크립트를 짜고 점검하고, 바뀐 내용을 기록하는 역할입니다.");

  // ===== 8. 실행 화면 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 자동화 시스템" });
  head(s, "", "PC를 켜면 만들어지는 일일보고, 현황판, 투입 목록");
  const caps = [
    ["일일보고 엑셀", "16:00 속보값, 확정치는 다음 날 「전일」 칸", "daily_crop.png", 980, 368],
    ["사내 현황판", "납기 지연과 임박, 미출하 잔량", "dashboard_crop.png", 1320, 1200],
    ["장비별 투입 목록, FG", "납기순, 같은 형상끼리 묶음", "queue_crop.png", 1090, 1170],
  ];
  caps.forEach((c, i) => {
    const x = 0.6 + i * 4.1, w = 3.9;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 2.15, w, h: 3.6, fill: { color: H.bg }, line: { color: H.line, width: 0.75 }, objectName: "cap" + i });
    { const bw = w - 0.2, bh = 3.4, r = c[3] / c[4]; let iw = bw, ih = bw / r; if (ih > bh) { ih = bh; iw = bh * r; }
      s.addImage({ path: CAP + c[2], x: x + (w - iw) / 2, y: 2.15 + (3.6 - ih) / 2, w: iw, h: ih, objectName: "cap" + i + "-img", altText: c[0] + " 화면 (거래처명은 A·B·C로 바꿈)" }); }
    s.addText([{ text: c[0], options: { bold: true, color: H.navy, fontSize: 17, breakLine: true } }, { text: c[1], options: { color: H.gray, fontSize: 14 } }],
      { x, y: 5.85, w, h: 0.85, valign: "top", margin: 0, isTextBox: true, objectName: "cap" + i + "-cap" });
  });
  note(s, "화면: 일일보고 10-16, 현황판 10-19, 거래처명 익명  |  " + ASOF);
  s.addNotes("[1:00] (화면을 짚으며) 왼쪽이 매일 자동으로 만들어지는 일일보고 — 16:00 시점 속보값이라 이후 입력분은 다음 날 「전일」 칸과 월 합계에서 확정됩니다 —, 가운데가 사내 현황판, 오른쪽이 장비별 투입 목록입니다. 투입 목록은 현장 의견을 받아 규칙을 여덟 번 고쳤습니다.");

  // ===== 9. 질의응답 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 자동화 시스템" });
  head(s, "", "기록에 있는 근거로만 답하는 질의응답");
  const qa = [
    ["장비 이력", "「GX7 로더는 왜 못 썼고, 언제 다시 썼나?」", ["08-13 외부 점검, 실린더 이상으로 로더 사용 금지", "08-14 부품 발주, 10-12 교체 수리 완료", "10-13 생산 재개, 고장 원인은 「확인 필요」"], "근거: 수리 이력 페이지, 10월 생산일지(10-12 「수리 중」)"],
    ["연삭 조건", "「Ø125 휠로 19 m/s를 내려면 몇 rpm?」", ["N = 60,000 × 19 ÷ (π × 125) ≈ 2,903 rpm", "사내 실사용 2,600 ~ 3,000 rpm 범위 안", "제조사 ANCA 적용 사례 18 ~ 22 m/s"], "근거: 휠 기준 페이지, 제조사 자료 3종, 사내 상한 25 m/s"],
  ];
  qa.forEach((q, i) => {
    const x = 0.6 + i * 6.15, w = 5.95;
    s.addText(q[0], { x, y: 2.15, w: 1.5, h: 0.36, fontSize: 14, bold: true, color: H.white, fill: { color: H.teal }, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "qa" + i + "-tag" });
    box(s, "qa" + i + "-q", x, 2.6, w, 0.85, H.navy);
    s.addText(q[1], { x: x + 0.2, y: 2.6, w: w - 0.4, h: 0.85, fontSize: 18, bold: true, color: H.white, valign: "middle", margin: 0, isTextBox: true, objectName: "qa" + i + "-qt" });
    box(s, "qa" + i + "-a", x, 3.55, w, 2.35, H.bg, H.line);
    s.addText(q[2].map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < q[2].length - 1 } })),
      { x: x + 0.2, y: 3.7, w: w - 0.4, h: 1.75, fontSize: 17, color: H.ink, valign: "top", margin: 0, paraSpaceAfter: 8, isTextBox: true, objectName: "qa" + i + "-at" });
    s.addText(q[3], { x: x + 0.2, y: 5.45, w: w - 0.4, h: 0.35, fontSize: 13, color: H.gray, margin: 0, isTextBox: true, objectName: "qa" + i + "-src" });
  });
  box(s, "qa-limit", 0.6, 6.05, 12.1, 0.6, H.tealBg, H.line);
  s.addText("조건 답변은 iGrind 입력 전 검산용, 확정은 현장 시험으로", { x: 0.8, y: 6.05, w: 11.7, h: 0.6, fontSize: 17, color: H.navy, valign: "middle", margin: 0, isTextBox: true, objectName: "qa-limit-t" });
  note(s, "10-19에 실제로 물은 질문과 답을 줄여 옮김");
  s.addNotes("[1:00] 두 가지 예시입니다. 장비 고장 경위를 날짜까지 기록에서 꺼내 답하고, 원인처럼 기록이 없는 건 확인 필요라고 답합니다. 연삭 조건은 계산 과정을 보여 줘서 검산할 수 있고, 사내 기준 범위와 같이 나옵니다. 다만 조건은 참고값이고, 확정은 현장 테스트로 합니다.");

  // ===== 10. 전후 비교 =====
  pres.addSection({ title: "04 전후 비교" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 전후 비교" });
  head(s, "04  업무 적용 전후 비교  |  필수 ③", "전후 비교 6개 항목 중 실측으로 확인된 4개");
  const ba = [
    ["일일보고 집계", "매일 수작업 집계", "자동 생성 18 / 18 영업일", "성적표 10-07", "실측"],
    ["집계와 판단 소요", "하루 15분 이하", "확인만, 월 5시간 이하 절약", "담당자 확인", "사내 경험값"],
    ["판단 근거 기록", "개인 기억, 메신저", "결정 기록 약 300건", "결정 기록", "실측"],
    ["장비 수리 이력", "PDF, 사진, 메일에 분산", "17건 정리, 과거 12건과 올해 5건", "수리 이력 페이지", "실측"],
    ["단가표 검수", "수작업 대조", "10,744건 자동 대조", "중간보고 09-14", "실측"],
    ["장비별 투입", "매일 경험으로 판단", "목록 자동 생성, 효과는 측정 중", "작업일지 셋업 분석", "판단 보류"],
  ];
  s.addTable([[TH("항목"), TH("적용 전"), TH("적용 후"), TH("근거"), TH("신뢰도", { align: "center" })],
    ...ba.map((r, i) => { const f = { fill: { color: i === 0 ? H.tealBg : (i % 2 ? H.white : H.bg) } }; return [TD(r[0], { bold: true, ...f }), TD(r[1], { color: H.gray, ...f }), TD(r[2], { bold: true, color: H.teal, ...f }), TD(r[3], { fontSize: 14, color: H.gray, ...f }), TD(r[4], { align: "center", fontSize: 14, ...f })]; })],
    { ...tableOpts(2.15, [2.4, 2.9, 3.6, 1.9, 1.3], [0.5, 0.66, 0.66, 0.66, 0.66, 0.66, 0.66]), objectName: "ba-table" });
  note(s, "투입 목록 효과는 도입 2주, 추석, 장비 수리가 섞여 판단 보류  |  " + ASOF);
  s.addNotes("[1:30] 전후 비교입니다. 일일보고는 4주 동안 하루도 빠지지 않고 자동 생성됐습니다. 절약 시간은 하루 15분 이하, 월 5시간 이하인데 정식으로 잰 값이 아니라 경험값이라고 표시했습니다. 결정 기록 약 300건, 수리 이력 17건, 단가표 1만여 건 대조는 실측입니다. 투입 목록은 셋업당 개수로 효과를 재는 도구까지 만들었지만, 기간이 짧고 추석과 장비 수리가 겹쳐 아직 효과라고 말하지 않겠습니다. (질문 대비: FG 7.5→6.7, GX7 3.6→4.9 합산 / 하루 평균 6.5→6.1)");

  // ===== 11. 한계와 대응 =====
  pres.addSection({ title: "05 한계와 과제" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "05 한계와 과제" });
  head(s, "05  한계와 향후 과제", "자동화 수리에 들어간 결정 84건 중 30건");
  const lim = [
    ["효과 없는 자동화", "알림 메일 48통을 아무도 열지 않는 등 4건", "10-07에 4건 중단"],
    ["정상으로 찍힌 실패", "「정상 완료」로 남았지만 결과물이 없던 3건", "결과물이 있는지로 정상 여부 판정"],
    ["AI 계산 오류", "표준 인용 오류로 문서 19개 정정", "출처와 신뢰도 표기, 현장 시험 후 적용"],
    ["AI 문서 문체", "보고서와 발표 자료가 보고서답지 않다는 지적", "공식 양식, 논문과 대조해 작성 기준 마련"],
    ["담당자 1명", "만들고 고치는 사람이 1명", "작업 기록과 결정 근거를 문서로 남김"],
  ];
  s.addTable([[TH("구분"), TH("확인된 내용"), TH("대응")],
    ...lim.map((r, i) => { const f = { fill: { color: i % 2 ? H.white : H.bg } }; return [TD(r[0], { bold: true, fontSize: 16, ...f }), TD(r[1], { fontSize: 16, ...f }), TD(r[2], { color: H.teal, fontSize: 16, ...f })]; })],
    { ...tableOpts(2.95, [2.1, 5.2, 4.8], [0.45, 0.58, 0.58, 0.58, 0.58, 0.58]), objectName: "lim-table" });
  s.addText([{ text: "36", options: { fontSize: 44, bold: true, color: H.amber } }, { text: " %", options: { fontSize: 22, bold: true, color: H.amber } }],
    { x: 0.6, y: 1.75, w: 1.9, h: 1.0, valign: "middle", margin: 0, isTextBox: true, objectName: "cost-pct" });
  s.addText("4주간 결정 84건 중 30건이 자동화 수리와 운영", { x: 2.5, y: 1.75, w: 8.5, h: 0.4, fontSize: 16, bold: true, color: H.navy, margin: 0, isTextBox: true, objectName: "cost-h" });
  s.addChart(pres.charts.BAR, [
    { name: "자동화 수리와 운영", labels: ["결정 84건"], values: [30] },
    { name: "그 외 업무 판단", labels: ["결정 84건"], values: [54] },
  ], {
    x: 2.4, y: 2.1, w: 10.3, h: 0.75, barDir: "bar", barGrouping: "percentStacked", barGapWidthPct: 20,
    chartColors: [H.amber, H.line], showValue: true, dataLabelPosition: "ctr", dataLabelFontSize: 13, dataLabelColor: H.navy, dataLabelFontFace: "+mn-lt",
    showLegend: true, legendPos: "r", legendFontSize: 12, legendColor: H.ink, legendFontFace: "+mn-lt",
    catAxisHidden: true, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showTitle: false, objectName: "cost-chart",
  });
  note(s, "자동화 효과 지표 1차 판정(10-07), 중간보고(09-14)  |  " + ASOF);
  s.addNotes("[1:20] 한계도 분명히 있습니다. 결정의 36%가 자동화를 고치는 일이었습니다. 그래서 자동화마다 성적표를 매겼고, 알림 메일 48통을 아무도 안 읽은 것처럼 효과 없는 4건은 껐습니다. 정상이라고 찍혔는데 결과물이 없던 경우도 있어서 판정 기준을 바꿨고, AI 수치는 출처와 신뢰도를 붙여 현장에서 확인합니다. AI가 쓴 보고서와 발표 자료가 보고서답지 않다는 지적도 받아서, 국가 연구개발 보고서와 논문 양식, 발표 연구 자료와 대조해 작성 기준을 만들었습니다. 1인 운용 리스크는 기록으로 대비하고 있습니다.");

  // ===== 12. 향후 과제 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "05 한계와 과제" });
  head(s, "", "새 기능보다 먼저 할 일은 11월 4일 2차 판정");
  const plan = [
    ["효과 재판정", "자동화 성적표 2차 판정", "11-04"],
    ["투입 목록 효과", "데이터가 쌓이면 셋업당 개수 다시 측정", "데이터 누적 후"],
    ["ERP 실적 연동", "ERP 상태코드를 해석해 생산 실적 지표로 전환", "명칭표 확보 시"],
    ["도면 작성 보조", "무료 2D CAD로 도면 초안 작성 시험", "시험 단계"],
    ["가공 조건 시험", "넥 원통연삭 테스트 3 후 같은 방식을 다른 품목에 적용", "11월"],
  ];
  s.addTable([[TH("과제"), TH("내용"), TH("시기", { align: "center" })],
    ...plan.map((r, i) => { const f = { fill: { color: i % 2 ? H.white : H.bg } }; return [TD(r[0], { bold: true, ...f }), TD(r[1], f), TD(r[2], { align: "center", color: H.teal, bold: true, ...f })]; })],
    { ...tableOpts(2.15, [2.6, 7.0, 2.5], [0.5, 0.64, 0.64, 0.64, 0.64, 0.64]), objectName: "plan-table" });
  box(s, "close", 0.6, 5.95, 12.1, 0.85, H.navy);
  s.addText("다른 팀에도 바로 쓸 수 있는 것: 엑셀 보고 집계, 자료 정리, 문서 조사", { x: 0.9, y: 5.95, w: 11.5, h: 0.85, fontSize: 20, bold: true, color: H.white, valign: "middle", margin: 0, isTextBox: true, objectName: "close-t" });
  
  s.addNotes("[0:40] 앞으로는 새 기능을 늘리기보다 지금 돌아가는 것의 효과를 확인하겠습니다. 11월 4일 성적표 2차 판정, 투입 목록 효과 재측정, ERP 실적 연동, CAD 도면 보조는 시험 중이고, 넥 원통연삭은 세 번째 시험 뒤 다른 품목에 넓히겠습니다. 엑셀 보고 집계나 자료 정리는 다른 팀도 바로 쓸 수 있습니다. 감사합니다.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
