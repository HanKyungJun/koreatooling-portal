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
const ASOF = "자료 기준일 2026-10-22";
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
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.68, w: 12.1, h: 0.72, fontSize: 36, bold: true, color: C.text1, align: "left", valign: "middle", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 1.45, w: 12.1, h: 0.45, fontSize: 20, bold: true, color: C.accent1, align: "left", valign: "middle", margin: 0 }, text: "" } },
      { text: { text: "TOOLKOREA 생산팀, Claude AI 파일럿 2기", options: { x: 7.2, y: 7.0, w: 5.0, h: 0.3, fontSize: 11, color: C.accent3, align: "right", margin: 0 } } },
    ],
    slideNumber: { x: 12.3, y: 7.0, w: 0.45, h: 0.3, fontSize: 11, color: C.accent3, align: "right" },
  });

  const box = (s, name, x, y, w, h, fill, line) =>
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: line || fill, width: 0.75 }, objectName: name });
  const note = (s, t) => s.addText(t, { x: 0.6, y: 6.95, w: 6.5, h: 0.35, fontSize: 12, color: H.gray, margin: 0, isTextBox: true, objectName: "footnote" });
  const NAV = [["1 배경", 1.0], ["2 활용 현황 ①", 1.65], ["3 자동화 시스템 ②", 1.95], ["4 전후 비교 ③", 1.65], ["5 한계와 과제", 1.6]];
  const nav = (s, k) => {
    let x = 12.7 - NAV.reduce((a, n) => a + n[1], 0);
    NAV.forEach((n, i) => {
      const on = i === k;
      const o = { x, y: 0.22, w: n[1] - 0.08, h: 0.36, fontSize: 14, bold: on, color: on ? H.teal : H.gray, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "nav" + i };
      if (on) o.fill = { color: H.tealBg };
      s.addText(n[0], o);
      x += n[1];
    });
  };
  const head = (s, kicker, title, msg) => {
    if (typeof kicker === "number") nav(s, kicker); else if (kicker) s.addText(kicker, { placeholder: "kicker" });
    s.addText(title, { placeholder: "title" });
    if (msg) s.addText("▶ " + msg, { placeholder: "body" });
    s.addShape(pres.shapes.LINE, { x: 0.6, y: 1.98, w: 12.1, h: 0, line: { color: H.line, width: 1 }, objectName: "title-rule" });
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
  head(s, "", "목차");
  const toc = [
    ["1", "추진 배경", "도입 전 업무와 추진 방향", ""],
    ["2", "팀 내 Claude 활용 현황", "활용 영역과 현장 사례", "필수 ①"],
    ["3", "자동화 시스템 소개 및 시연", "구성, 실행 화면, 질의응답", "필수 ②"],
    ["4", "업무 적용 전후 비교", "일일보고와 항목별 전후 비교", "필수 ③"],
    ["5", "한계와 향후 과제", "운영하며 확인한 한계와 다음 과제", ""],
  ];
  toc.forEach((r, i) => {
    const y = 2.2 + i * 0.88;
    box(s, "toc" + i, 0.6, y, 12.1, 0.74, i % 2 ? H.white : H.bg, H.line);
    s.addText(r[0], { x: 0.85, y, w: 0.9, h: 0.74, fontSize: 24, bold: true, color: H.teal, valign: "middle", margin: 0, isTextBox: true, objectName: "toc" + i + "-n" });
    s.addText(r[1], { x: 1.8, y, w: 5.0, h: 0.74, fontSize: 20, bold: true, color: H.navy, valign: "middle", margin: 0, isTextBox: true, objectName: "toc" + i + "-t" });
    s.addText(r[2], { x: 6.8, y, w: 4.4, h: 0.74, fontSize: 16, color: H.gray, valign: "middle", margin: 0, isTextBox: true, objectName: "toc" + i + "-d" });
    if (r[3]) s.addText(r[3], { x: 11.3, y: y + 0.17, w: 1.2, h: 0.4, fontSize: 14, bold: true, color: H.teal, fill: { color: H.tealBg }, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "toc" + i + "-tag" });
  });
  s.addNotes("[0:15] 순서입니다. 공지된 필수 항목 세 가지는 2, 3, 4번에 담았고, 화면 오른쪽 위에 지금 어디인지 표시됩니다.");

  // ===== 3. 추진 배경 =====
  pres.addSection({ title: "01 추진 배경" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 추진 배경" });
  head(s, 0, "추진 배경", "일일보고 집계와 장비 투입 판단을 매일 손으로 처리");
  // v0.4: 장비 사진은 넣지 않음(한경준님 10-19) — 실제 자료 2종(가공비·금액 열 숨김 / 연락처·주소 흐림)
  s.addText("하루 1시트씩 손으로 입력하던 월간생산일지 엑셀", { x: 0.6, y: 2.15, w: 5.0, h: 0.32, fontSize: 13, bold: true, color: H.sub, margin: 0, isTextBox: true, objectName: "src0-cap" });
  s.addImage({ path: CAP + "monthly_log.png", x: 0.6, y: 2.5, w: 5.0, h: 5.0 * 438 / 1276, objectName: "src0-img", altText: "재연마 월간생산일지 엑셀 화면 (10-16 시트, 금액 열 숨김)" });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 2.5, w: 5.0, h: 5.0 * 438 / 1276, fill: { type: "none" }, line: { color: H.line, width: 0.75 }, objectName: "src0-frame" });
  s.addText("장비마다 따로 보관하던 수리 발주서 PDF", { x: 0.6, y: 4.42, w: 5.0, h: 0.32, fontSize: 13, bold: true, color: H.sub, margin: 0, isTextBox: true, objectName: "src1-cap" });
  s.addImage({ path: CAP + "repair_order.png", x: 0.6, y: 4.77, w: 3.8, h: 3.8 * 575 / 1150, objectName: "src1-img", altText: "장비 수리 발주서 PDF (연락처·주소 흐림 처리)" });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 4.77, w: 3.8, h: 3.8 * 575 / 1150, fill: { type: "none" }, line: { color: H.line, width: 0.75 }, objectName: "src1-frame" });
  box(s, "bg-asis", 5.9, 2.15, 6.8, 2.2, H.bg, H.line);
  s.addText("도입 전", { x: 6.15, y: 2.25, w: 6.3, h: 0.4, fontSize: 17, bold: true, color: H.sub, margin: 0, isTextBox: true, objectName: "asis-h" });
  s.addText([
    { text: "일일보고는 매일 엑셀로 손집계", options: { bullet: true, breakLine: true } },
    { text: "장비 투입 순서는 담당자 경험으로 결정", options: { bullet: true, breakLine: true } },
    { text: "조건을 바꾼 이유와 고장 처리 경위는 기록 없음", options: { bullet: true } },
  ], { x: 6.15, y: 2.7, w: 6.35, h: 1.55, fontSize: 17, color: H.ink, valign: "top", margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: "asis-t" });
  s.addShape(pres.shapes.DOWN_ARROW, { x: 9.05, y: 4.42, w: 0.5, h: 0.32, fill: { color: H.teal }, line: { color: H.teal }, objectName: "bg-arrow" });
  box(s, "bg-tobe", 5.9, 4.8, 6.8, 1.9, H.tealBg, H.line);
  s.addText("추진 방향", { x: 6.15, y: 4.9, w: 6.3, h: 0.4, fontSize: 17, bold: true, color: H.teal, margin: 0, isTextBox: true, objectName: "tobe-h" });
  s.addText([
    { text: "출처와 신뢰도를 붙여 사내 위키에 기록", options: { bullet: true, breakLine: true } },
    { text: "반복 집계는 업무 PC 예약 실행으로", options: { bullet: true, breakLine: true } },
    { text: "기존 값은 지우지 않고 이력으로 보존", options: { bullet: true } },
  ], { x: 6.15, y: 5.32, w: 6.35, h: 1.3, fontSize: 17, color: H.ink, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: "tobe-t" });
  note(s, "재연마 장비는 ANCA FastGrind와 GX7 2대");
  s.addNotes("[0:50] (왼쪽 자료를 가리키며) 생산팀은 ANCA 장비 두 대로 재연마를 합니다. 왼쪽이 실제 쓰던 월간생산일지와 수리 발주서입니다. 자료가 ERP, 엑셀, PDF, 사람 머릿속에 흩어져 있었고, 일일보고 집계와 투입 판단을 매일 손으로 했습니다. 그래서 세 방향으로 추진했습니다 — 한곳에 기록, 반복은 자동 실행, 판단 근거는 남긴다.");

  // ===== 5. 활용 영역 =====
  pres.addSection({ title: "① 활용 현황" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "① 활용 현황" });
  head(s, 1, "팀 내 활용 현황 (1/2)", "6개월 동안 재연마 기록 문서 147개 작성");
  const area = [
    ["지식 기록", "장비, 휠, 연삭 조건, 수리 이력 정리", "문서 147개와 수리 이력 17건"],
    ["보고 자동화", "매일 07:50과 16:00에 일일보고와 현황판 생성", "일일보고 136건"],
    ["현장 판단 보조", "ERP 수주 기준으로 장비별 투입 순서 작성", "09-28부터 쓰며 규칙 8번 수정"],
    ["데이터 검수", "단가표 대조, 작업일지 읽기, ERP 조회", "단가표 10,744건 대조"],
    ["설비 문서", "로더 고장 진단, 수리 검토보고, 증설 투자 검토", "F와 GX7 로더 정식 수리"],
  ];
  s.addTable([[TH("영역"), TH("내용"), TH("대표 사례")], ...area.map((r, i) => [TD(r[0], { bold: true, fill: { color: i % 2 ? H.white : H.bg } }), TD(r[1], { fill: { color: i % 2 ? H.white : H.bg } }), TD(r[2], { color: H.teal, bold: true, fill: { color: i % 2 ? H.white : H.bg } })])],
    { ...tableOpts(2.15, [2.1, 5.9, 4.1], [0.46, 0.62, 0.62, 0.62, 0.62, 0.62]), objectName: "area-table" });
  s.addText("판단 근거 기록 320여 건과 Python 자동화 스크립트 59개", { x: 0.6, y: 5.85, w: 12.1, h: 0.36, fontSize: 17, bold: true, color: H.navy, margin: 0, isTextBox: true, objectName: "area-etc" });
  s.addText("수치마다 출처 표기. 예: 휠 원주속도 18 ~ 22 m/s [제조사 기준] / 사내 실사용 2,600 ~ 3,000 rpm [실측]", { x: 0.6, y: 6.25, w: 12.1, h: 0.36, fontSize: 15, color: H.sub, margin: 0, isTextBox: true, objectName: "area-src" });
  note(s, "투입 목록과 단가표 검수는 2기에 새로 시작  |  " + ASOF);
  s.addNotes("[1:00] 첫 번째 필수 항목, 팀 내 활용 현황입니다. 6개월 동안 재연마 기록 문서 147개와, 무엇을 왜 바꿨는지 남긴 판단 근거 320여 건이 쌓였습니다. 표는 Claude를 쓰는 다섯 가지 일이고, 2기에 새로 맡긴 건 장비 투입 목록과 단가표 검수입니다. 수치에는 출처를 붙여서, 휠 원주속도는 제조사 기준 18에서 22 m/s, 사내 실사용은 실측 2,600에서 3,000 rpm으로 나눠 적습니다.");

  // ===== 5-1. 활용 사례 — 넥 원통연삭 시험 (v0.5 추가, 10-19 ~ 10-21) =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "① 활용 현황" });
  head(s, 1, "팀 내 활용 현황 (2/2) 현장 사례", "넥 원통연삭 두 번째 시험에서 넥 시작부 자국 해결");
  const steps = [
    ["10-19 ~ 20", "테스트 1 정삭만 4회 가공에서 넥 시작부 같은 자리 자국 반복"],
    ["10-20", "제조사 롱넥 31품목 치수로 넥 기준 dn = 0.96 × D 설정"],
    ["10-20 오후", "테스트 2 황삭을 대각선 진입으로 바꿔 자국 없앰"],
    ["10-21", "제조사 매뉴얼 원문으로 원인 확인 후 결과 보고서 작성"],
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
  const cr = [["넥 시작부 자국", "매번 같은 자리에 생김", "없음"], ["치수 판정", "합격", "보류 (0.01 mm 굵음)"]];
  s.addTable([[TH("항목", { fontSize: 15 }), TH("테스트 1 정삭만", { fontSize: 15 }), TH("테스트 2 황삭 대각선", { fontSize: 15 })],
    ...cr.map((r, i) => { const f = { fill: { color: i % 2 ? H.white : H.bg } }; return [TD(r[0], { bold: true, fontSize: 15, ...f }), TD(r[1], { fontSize: 15, color: H.gray, ...f }), TD(r[2], { fontSize: 15, bold: true, color: H.teal, ...f })]; })],
    { x: 6.5, y: 5.75, w: 6.2, colW: [1.6, 2.1, 2.5], rowH: [0.38, 0.38, 0.38], border: { type: "solid", pt: 0.75, color: H.line }, margin: [2, 6, 2, 6], fontFace: "맑은 고딕", objectName: "case-table" });
  note(s, "공구 1 ~ 2개 시험값으로 양산 미적용  |  " + ASOF2);
  s.addNotes("[0:50] 이번 달에 새로 쓴 사례입니다. 엔드밀 목 부분을 가늘게 깎는 원통연삭 조건을 잡는 시험인데, 사내 기준이 없었습니다. 장비 PC와 사무 PC를 하나의 프로젝트로 묶어 시험하면서, 제조사 롱넥 제품 31종의 치수로 넥 지름 기준을 잡았습니다. 첫 시험은 넥 시작부에 매번 같은 자리 자국이 남았는데, 제조사 매뉴얼에서 정삭은 항상 시작 쪽 한 곳에서 들어간다는 것을 확인하고 황삭 방식을 바꿔 두 번째 시험에서 자국을 없앴습니다. 아직 공구 두 개 결과라 양산에는 쓰지 않았습니다.");

  // ===== 7. 시스템 구성 =====
  pres.addSection({ title: "② 자동화 시스템" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "② 자동화 시스템" });
  head(s, 2, "자동화 시스템 (1/3) 구성", "기존 엑셀과 ERP를 그대로 읽어 업무 PC가 정해진 시각에 실행");
  const cols = [
    { x: 0.6, w: 3.4, h: "읽는 자료", items: ["ERP 수주와 A/S 조회", "월간생산일지 엑셀", "출하현황 엑셀"], fill: H.bg },
    { x: 4.75, w: 3.8, h: "업무 PC", items: ["예약 실행 07:50과 16:00", "Python 스크립트로 집계, 대조, 배정", "Claude가 스크립트 작성과 점검"], fill: H.tealBg },
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
  note(s, "업무 PC 1대에서 예약 작업 2개와 시작 프로그램 1개로 실행");
  s.addNotes("[0:50] 구성은 단순합니다. 새 시스템을 들인 게 아니라 원래 쓰던 ERP와 엑셀을 그대로 읽습니다. 업무 PC가 출근 로그온 때와 오후 4시에 스크립트를 돌려 일일보고, 현황판, 장비별 투입 목록을 만듭니다. Claude는 이 스크립트를 짜고 점검하고, 바뀐 내용을 기록하는 역할입니다.");

  // ===== 8. 실행 화면 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "② 자동화 시스템" });
  head(s, 2, "자동화 시스템 (2/3) 실행 화면", "PC를 켜면 일일보고, 현황판, 투입 목록 생성");
  const caps = [
    ["일일보고 엑셀", "16:00 속보값이며 확정치는 다음 날 「전일」 칸", "daily_crop.png", 980, 368],
    ["사내 현황판", "납기 지연과 임박, 미출하 잔량", "dashboard_crop.png", 1320, 1200],
    ["FG 장비 투입 목록", "납기순으로 같은 형상끼리 묶음", "queue_crop.png", 1090, 1170],
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
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "② 자동화 시스템" });
  head(s, 2, "자동화 시스템 (3/3) 질의응답", "기록에 없는 내용은 「확인 필요」로 표시");
  const qa = [
    ["장비 이력", "「GX7 로더는 왜 못 썼고, 언제 다시 썼나?」", ["08-13 외부 점검에서 실린더 이상 발견해 로더 사용 금지", "08-14 부품 발주 후 10-12 교체 수리 완료", "10-13 생산 재개 (고장 원인은 「확인 필요」)"], "근거: 수리 이력 페이지, 10월 생산일지(10-12 「수리 중」)"],
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
  s.addText("조건 답변은 iGrind 입력 전 검산용이며 확정은 현장 시험으로", { x: 0.8, y: 6.05, w: 11.7, h: 0.6, fontSize: 17, color: H.navy, valign: "middle", margin: 0, isTextBox: true, objectName: "qa-limit-t" });
  note(s, "10-19에 실제로 물은 질문과 답을 줄여 옮김");
  s.addNotes("[1:00] 두 가지 예시입니다. 장비 고장 경위를 날짜까지 기록에서 꺼내 답하고, 원인처럼 기록이 없는 건 확인 필요라고 답합니다. 연삭 조건은 계산 과정을 보여 줘서 검산할 수 있고, 사내 기준 범위와 같이 나옵니다. 다만 조건은 참고값이고, 확정은 현장 테스트로 합니다.");

  // ===== 6. 추진 경과 =====
  pres.addSection({ title: "③ 전후 비교" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "③ 전후 비교" });
  head(s, 3, "업무 적용 전후 비교 (1/2) 일일보고", "최근 20영업일 동안 20건 모두 자동 생성");
  const months = ["4월", "5월", "6월", "7월", "8월", "9월", "10월*"];
  s.addChart(pres.charts.BAR, [
    { name: "소급 또는 수동 생성 (6월 9일 일괄 등)", labels: months, values: [21, 19, 12, 0, 0, 0, 0] },
    { name: "매일 자동 생성 (6월 18일부터)", labels: months, values: [0, 0, 9, 22, 19, 20, 14] },
  ], {
    x: 0.6, y: 2.1, w: 7.5, h: 4.6, barDir: "col", barGrouping: "stacked", barGapWidthPct: 60,
    chartColors: [H.gray, H.teal],
    showValue: true, dataLabelPosition: "ctr", dataLabelFormatCode: "0;;;", dataLabelFontSize: 13, dataLabelColor: H.white, dataLabelFontFace: "+mn-lt",
    showTitle: true, title: "일일보고 월별 생성 건수 (단위: 건)", titleFontSize: 14, titleColor: H.navy, titleFontFace: "+mn-lt",
    showLegend: true, legendPos: "b", legendFontSize: 13, legendColor: H.ink, legendFontFace: "+mn-lt",
    catAxisLabelColor: H.ink, catAxisLabelFontSize: 14, catAxisLabelFontFace: "+mn-lt", catAxisLineShow: false,
    valAxisLabelColor: H.gray, valAxisLabelFontSize: 12, valAxisLabelFontFace: "+mn-lt", valAxisMaxVal: 25, valAxisMajorUnit: 5, valAxisLineShow: false,
    valGridLine: { color: H.line, size: 0.5 }, catGridLine: { style: "none" },
    objectName: "daily-chart",
  });
  box(s, "ba-panel", 8.4, 2.1, 4.3, 4.6, H.bg, H.line);
  [["적용 전", "담당자가 매일 엑셀로 손집계", H.gray], ["적용 후", "07:50과 16:00에 자동 생성되어 담당자는 확인만", H.teal], ["아낀 시간", "하루 15분 이하 [사내 경험값]", H.navy]].forEach((r, i) => {
    const y = 2.3 + i * 1.45;
    s.addText(r[0], { x: 8.65, y, w: 3.8, h: 0.36, fontSize: 15, bold: true, color: r[2], margin: 0, isTextBox: true, objectName: "ba" + i + "-h" });
    s.addText(r[1], { x: 8.65, y: y + 0.4, w: 3.8, h: 0.85, fontSize: 18, color: H.ink, valign: "top", margin: 0, isTextBox: true, objectName: "ba" + i + "-t" });
  });
  note(s, "파일 수정 시각 실측, *10월은 22일까지  |  " + ASOF);
  s.addNotes("[0:50] 세 번째 필수 항목, 전후 비교입니다. 먼저 일일보고입니다. 전에는 매일 엑셀로 손으로 집계했고, 지금은 아침 7시 50분과 오후 4시에 자동으로 만들어집니다. 회색은 6월 9일에 지난 분을 한꺼번에 만들거나 손으로 만든 것이고, 청록이 그날그날 자동으로 만든 것입니다. 10월 22일 기준 최근 20영업일은 20건 모두 생성됐습니다. 아낀 시간은 하루 15분 이하인데, 정식으로 잰 값이 아니라 경험값입니다.");

  // ===== 10. 전후 비교 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "③ 전후 비교" });
  head(s, 3, "업무 적용 전후 비교 (2/2)", "6개 항목 중 4개는 실측으로 확인");
  const ba = [
    ["일일보고 집계", "매일 수작업 집계", "자동 생성 18 / 18 영업일", "성적표 10-07", "실측"],
    ["집계와 판단 소요", "하루 15분 이하", "확인만 하여 월 5시간 이하 절약", "담당자 확인", "사내 경험값"],
    ["판단 근거 기록", "개인 기억과 메신저", "결정 기록 320여 건", "결정 기록", "실측"],
    ["장비 수리 이력", "PDF, 사진, 메일에 분산", "과거 12건과 올해 5건 정리", "수리 이력 페이지", "실측"],
    ["단가표 검수", "수작업 대조", "10,744건 자동 대조", "중간보고 09-14", "실측"],
    ["장비별 투입", "매일 경험으로 판단", "목록 자동 생성 (효과 측정 중)", "작업일지 셋업 분석", "판단 보류"],
  ];
  s.addTable([[TH("항목"), TH("적용 전"), TH("적용 후"), TH("근거"), TH("신뢰도", { align: "center" })],
    ...ba.map((r, i) => { const f = { fill: { color: i === 0 ? H.tealBg : (i % 2 ? H.white : H.bg) } }; return [TD(r[0], { bold: true, ...f }), TD(r[1], { color: H.gray, ...f }), TD(r[2], { bold: true, color: H.teal, ...f }), TD(r[3], { fontSize: 14, color: H.gray, ...f }), TD(r[4], { align: "center", fontSize: 14, ...f })]; })],
    { ...tableOpts(2.15, [2.4, 2.9, 3.6, 1.9, 1.3], [0.5, 0.66, 0.66, 0.66, 0.66, 0.66, 0.66]), objectName: "ba-table" });
  note(s, "주: 실측은 기록으로 센 값이고 사내 경험값은 담당자 확인값");
  s.addNotes("[1:10] 나머지 항목입니다. 결정 기록 320여 건, 수리 이력 17건, 단가표 1만여 건 대조는 실측으로 확인했습니다. 시간 절약은 경험값으로 따로 표시했습니다. 장비별 투입 목록은 효과를 재는 중인데, 도입 2주와 추석, 장비 수리가 섞여 아직 판단하지 않았습니다.");

  // ===== 11. 한계와 대응 =====
  pres.addSection({ title: "한계와 과제" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "한계와 과제" });
  head(s, 4, "한계와 향후 과제", "효과 없는 자동화 4건은 10-07에 중단");
  const lim = [
    ["효과 없는 자동화", "알림 메일 48통을 아무도 열지 않는 등 4건", "10-07에 4건 중단"],
    ["정상으로 찍힌 실패", "「정상 완료」로 남았지만 결과물이 없던 3건", "결과물이 있는지로 정상 여부 판정"],
    ["AI 계산 오류", "표준 인용 오류로 문서 19개 정정", "출처와 신뢰도를 붙이고 현장 시험 후 적용"],
    ["AI 문서 문체", "보고서와 발표 자료가 보고서답지 않다는 지적", "공식 양식과 논문을 대조해 작성 기준 마련"],
    ["담당자 1명", "만들고 고치는 사람이 1명", "작업 기록과 결정 근거를 문서로 남김"],
  ];
  s.addTable([[TH("구분"), TH("확인된 내용"), TH("대응")],
    ...lim.map((r, i) => { const f = { fill: { color: i % 2 ? H.white : H.bg } }; return [TD(r[0], { bold: true, fontSize: 14, ...f }), TD(r[1], { fontSize: 14, ...f }), TD(r[2], { color: H.teal, fontSize: 14, ...f })]; })],
    { ...tableOpts(3.2, [2.1, 5.2, 4.8], [0.4, 0.46, 0.46, 0.46, 0.46, 0.46]), objectName: "lim-table" });
  s.addText([{ text: "36", options: { fontSize: 44, bold: true, color: H.amber } }, { text: " %", options: { fontSize: 22, bold: true, color: H.amber } }],
    { x: 0.6, y: 2.1, w: 1.9, h: 0.9, valign: "middle", margin: 0, isTextBox: true, objectName: "cost-pct" });
  s.addText("4주간 결정 84건 중 30건이 자동화 수리와 운영 (10-07 1차 판정)", { x: 2.5, y: 2.1, w: 8.5, h: 0.36, fontSize: 16, bold: true, color: H.navy, margin: 0, isTextBox: true, objectName: "cost-h" });
  s.addChart(pres.charts.BAR, [
    { name: "자동화 수리와 운영", labels: ["결정 84건"], values: [30] },
    { name: "그 외 업무 판단", labels: ["결정 84건"], values: [54] },
  ], {
    x: 2.4, y: 2.4, w: 10.3, h: 0.74, barDir: "bar", barGrouping: "percentStacked", barGapWidthPct: 20,
    chartColors: [H.amber, H.line], showValue: true, dataLabelPosition: "ctr", dataLabelFontSize: 13, dataLabelColor: H.navy, dataLabelFontFace: "+mn-lt",
    showLegend: true, legendPos: "r", legendFontSize: 12, legendColor: H.ink, legendFontFace: "+mn-lt",
    catAxisHidden: true, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showTitle: false, objectName: "cost-chart",
  });
  box(s, "next", 0.6, 6.03, 12.1, 0.66, H.navy);
  s.addText("다음 과제: 11월 4일 자동화 2차 판정, 투입 목록 효과 재측정, 넥 원통연삭 테스트 3", { x: 0.85, y: 6.03, w: 11.7, h: 0.66, fontSize: 17, bold: true, color: H.white, valign: "middle", margin: 0, isTextBox: true, objectName: "next-t" });
  note(s, "다른 팀도 바로 쓸 수 있는 것: 엑셀 보고 집계, 자료 정리, 문서 조사");
  s.addNotes("[1:20] 마지막으로 한계입니다. 4주 동안 결정 84건 중 30건이 자동화를 고치는 일이었습니다. 그래서 자동화마다 성적표를 매겨, 알림 메일 48통을 아무도 안 읽은 것처럼 효과 없는 4건은 껐습니다. 정상으로 찍혔는데 결과물이 없던 경우가 있어 판정 기준을 바꿨고, AI 계산은 출처와 신뢰도를 붙여 현장에서 확인합니다. 다음은 11월 4일 자동화 2차 판정과 넥 원통연삭 세 번째 시험입니다. 엑셀 보고 집계나 자료 정리는 다른 팀도 바로 쓸 수 있습니다. 감사합니다.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
