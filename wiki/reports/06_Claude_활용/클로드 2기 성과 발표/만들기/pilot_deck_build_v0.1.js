const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const tb = require("react-icons/tb");
const { applyTheme } = require("/root/.claude/skills/synced/b975f8eb-8440-4783-8ac8-024b9f4448eb_d9575592-dd32-4ad8-8939-5359bb80f9d7/pptx/scripts/apply_theme.js");

const OUT = process.argv[2] || "deck.pptx";
const HEX = { dk1: "1E252D", lt1: "FFFFFF", dk2: "4A5561", lt2: "EEF1F4", a1: "E8731A", a2: "2F6F8F", a3: "8A96A3", a4: "FBE3CF", a5: "DCE8EE", a6: "3C8D5A" };
const THEME = {
  name: "생산팀 파일럿",
  headFontFace: "맑은 고딕",
  bodyFontFace: "맑은 고딕",
  colors: { dk1: HEX.dk1, lt1: HEX.lt1, dk2: HEX.dk2, lt2: HEX.lt2, accent1: HEX.a1, accent2: HEX.a2, accent3: HEX.a3, accent4: HEX.a4, accent5: HEX.a5, accent6: HEX.a6, hlink: HEX.a2, folHlink: HEX.dk2 },
};

async function icon(name, hex, px = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(tb[name], { color: "#" + hex, size: px }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "재연마 현장에 Claude를 붙여 보니 — 생산팀";
  pres.author = "생산팀";
  const C = pres.SchemeColor;

  pres.defineSlideMaster({
    title: "COVER_DARK",
    background: { color: C.text1 },
    objects: [
      { placeholder: { options: { name: "kicker", type: "body", x: 0.8, y: 1.6, w: 9, h: 0.5, fontSize: 20, bold: true, color: C.accent1, margin: 0 }, text: "" } },
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.2, w: 9.2, h: 1.9, fontSize: 44, bold: true, color: C.background1, valign: "top", align: "left", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.3, w: 9, h: 1.0, fontSize: 20, color: C.accent5, valign: "top", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    margin: [0.5, 0.6, 0.6, 0.6],
    objects: [
      { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.35, w: 9, h: 0.4, fontSize: 16, bold: true, color: C.accent1, margin: 0 }, text: "" } },
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.75, w: 12.1, h: 0.8, fontSize: 36, bold: true, color: C.text1, valign: "middle", align: "left", margin: 0 }, text: "" } },
      { text: { text: "생산팀 · Claude AI 파일럿 2기", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontSize: 11, color: C.accent3, margin: 0 } } },
    ],
    slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 11, color: C.accent3, align: "right" },
  });

  const card = (s, name, x, y, w, h, fill) =>
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill }, objectName: name });
  const iconDot = async (s, name, ic, x, y, d, bg, fg) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { color: bg }, objectName: name + "-dot" });
    const p = d * 0.22;
    s.addImage({ data: await icon(ic, fg), x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p, objectName: name + "-icon" });
  };
  const capture = (s, name, x, y, w, h, label) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: HEX.a3, width: 1.25, dashType: "dash" }, objectName: name });
    s.addText([{ text: "캡처 자리", options: { bold: true, breakLine: true } }, { text: label }], { x, y, w, h, align: "center", valign: "middle", fontSize: 14, color: C.accent3, isTextBox: true, objectName: name + "-label" });
  };

  // ---------- 1. 표지 ----------
  pres.addSection({ title: "도입" });
  let s = pres.addSlide({ masterName: "COVER_DARK", sectionTitle: "도입" });
  s.addText("Claude AI 파일럿 2기 · 2차 발표", { placeholder: "kicker" });
  s.addText("재연마 현장에\nClaude를 붙여 보니", { placeholder: "title" });
  s.addText("흩어진 자료 정리 · 매일 반복 작업 자동화 · 물어보면 답하는 기록", { placeholder: "body" });
  s.addText("생산팀  |  2026-11-10", { x: 0.8, y: 6.2, w: 6, h: 0.4, fontSize: 18, color: C.background1, margin: 0, isTextBox: true, objectName: "cover-team" });
  s.addShape(pres.shapes.OVAL, { x: 9.9, y: 1.7, w: 2.7, h: 2.7, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: "cover-dot" });
  s.addImage({ data: await icon("TbTool", HEX.lt1), x: 10.5, y: 2.3, w: 1.5, h: 1.5, objectName: "cover-icon" });
  s.addNotes("[0:15] 생산팀 발표입니다. 재연마 현장 일에 Claude 를 붙여 본 지 반년 정도 됐고, 대단한 걸 만든 건 아니지만 매일 쓸 만하다는 걸 보여 드리겠습니다.");

  // ---------- 2. 업무와 이유 ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "도입" });
  s.addText("우리 업무", { placeholder: "kicker" });
  s.addText("자료는 흩어져 있고, 정리는 매일 사람이 했다", { placeholder: "title" });
  card(s, "work-card", 0.6, 1.85, 4.6, 4.1, HEX.dk1);
  s.addText([
    { text: "재연마", options: { fontSize: 28, bold: true, color: HEX.a1, breakLine: true } },
    { text: "쓰던 엔드밀·드릴을 다시 연삭해 수명을 늘리는 일", options: { fontSize: 18, color: HEX.lt1, breakLine: true } },
    { text: " ", options: { fontSize: 10, breakLine: true } },
    { text: "장비 2대", options: { fontSize: 18, bold: true, color: HEX.a5, breakLine: true } },
    { text: "FG — ANCA FastGrind", options: { fontSize: 18, color: HEX.lt1, breakLine: true } },
    { text: "GX7 — ANCA GX7", options: { fontSize: 18, color: HEX.lt1 } },
  ], { x: 0.95, y: 2.1, w: 4.0, h: 3.6, valign: "middle", margin: 0, isTextBox: true, objectName: "work-text" });

  const srcs = [
    ["TbFileInvoice", "수주", "ERP"],
    ["TbTable", "재연마 월간생산일지", "엑셀"],
    ["TbTruckDelivery", "출하현황", "엑셀"],
    ["TbBook", "장비 매뉴얼·수리 기록", "PDF·사진"],
    ["TbUser", "현장 노하우", "사람 머릿속"],
  ];
  for (let i = 0; i < srcs.length; i++) {
    const y = 1.9 + i * 0.8;
    await iconDot(s, "src" + i, srcs[i][0], 5.7, y, 0.6, HEX.lt2, HEX.a2);
    s.addText([
      { text: srcs[i][1], options: { bold: true, color: HEX.dk1 } },
      { text: "   " + srcs[i][2], options: { color: HEX.dk2 } },
    ], { x: 6.5, y, w: 6.2, h: 0.6, fontSize: 20, valign: "middle", margin: 0, isTextBox: true, objectName: "src" + i + "-text" });
  }
  card(s, "daily-card", 0.6, 6.15, 12.1, 0.7, HEX.a4);
  s.addText([
    { text: "매일 손으로: ", options: { bold: true } },
    { text: "일일보고 집계 + 「오늘 어느 장비에 뭘 먼저」 — 하루 15분 이하 (사내 경험값)" },
  ], { x: 0.85, y: 6.15, w: 11.7, h: 0.7, fontSize: 18, color: HEX.dk1, valign: "middle", margin: 0, isTextBox: true, objectName: "daily-text" });
  s.addNotes("[1:00] 생산팀은 재연마를 합니다. 장비는 ANCA 두 대. 수주는 ERP, 생산일지와 출하는 엑셀, 장비 자료는 PDF·사진, 노하우는 사람 머릿속에 흩어져 있었고, 매일 일일보고 집계와 투입 순서 판단을 손으로 했습니다. 하루 15분 이하 정도 — 정식으로 잰 값은 아니고 경험값입니다.");

  // ---------- 3. 활용 현황 ----------
  pres.addSection({ title: "① 활용 현황" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "① 활용 현황" });
  s.addText("필수 ① 팀 내 Claude 활용 현황", { placeholder: "kicker" });
  s.addText("반년 동안 쌓인 것", { placeholder: "title" });
  const stats = [
    ["138", "페이지", "생산팀 지식 위키", "장비·휠·연삭 조건·수리 이력"],
    ["300", "건", "결정 기록", "왜 그렇게 했는지 남김"],
    ["55", "개", "자동화 스크립트", "Python — 보고·집계·정리"],
    ["17", "건", "장비 수리 이력", "과거 12건 + 올해 5건"],
  ];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.1;
    card(s, "stat" + i, x, 1.9, 2.8, 3.0, HEX.lt2);
    s.addText([
      ...(i === 1 ? [{ text: "약 ", options: { fontSize: 20, bold: true, color: HEX.dk1 } }] : []),
      { text: stats[i][0], options: { fontSize: 54, bold: true, color: HEX.a1 } },
      { text: " " + stats[i][1], options: { fontSize: 20, bold: true, color: HEX.dk1 } },
    ], { x: x + 0.25, y: 2.1, w: 2.4, h: 1.1, valign: "bottom", margin: 0, isTextBox: true, objectName: "stat" + i + "-num" });
    s.addText([
      { text: stats[i][2], options: { fontSize: 20, bold: true, color: HEX.dk1, breakLine: true } },
      { text: stats[i][3], options: { fontSize: 15, color: HEX.dk2 } },
    ], { x: x + 0.25, y: 3.35, w: 2.4, h: 1.4, valign: "top", margin: 0, isTextBox: true, objectName: "stat" + i + "-label" });
  }
  await iconDot(s, "how", "TbFolderShare", 0.6, 5.35, 0.75, HEX.a2, HEX.lt1);
  s.addText([
    { text: "쓰는 방식  ", options: { bold: true, color: HEX.a2 } },
    { text: "업무 PC 폴더를 Claude 에 연결 → 파일 읽기·정리·스크립트 실행을 대화로 시킨다", options: { color: HEX.dk1 } },
  ], { x: 1.6, y: 5.35, w: 11.1, h: 0.75, fontSize: 20, valign: "middle", margin: 0, isTextBox: true, objectName: "how-text" });
  s.addText("숫자는 2026-10-16 기준 — 제출 전 다시 잰다", { x: 0.6, y: 6.4, w: 8, h: 0.35, fontSize: 13, color: HEX.a3, margin: 0, isTextBox: true, objectName: "stat-asof" });
  s.addNotes("[1:30] 4월부터 쓴 결과입니다. 위키 138페이지, 결정 기록 약 300건 — 이게 제일 쓸모 있습니다. 나중에 '왜 이렇게 했지?'를 찾을 수 있습니다. 자동화 스크립트 55개, 장비 수리 이력 17건 정리. 쓰는 방식은 업무 PC 폴더를 연결해 놓고 대화로 시키는 겁니다.");

  // ---------- 4. 자동화 소개 ----------
  pres.addSection({ title: "② 자동화·시연" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "② 자동화·시연" });
  s.addText("필수 ② 자동화 프로그램 소개", { placeholder: "kicker" });
  s.addText("출근하면 이미 만들어져 있다", { placeholder: "title" });
  const autos = [
    ["TbFileSpreadsheet", "일일보고 자동 생성", "매일 07:50 · 16:00 자동 실행\n누적 131개 (10-15)", "일일보고 엑셀 1장"],
    ["TbLayoutDashboard", "사내 현황판", "오늘 실적 · 업체별 출하\n· 접수현황 → 공유폴더", "현황판 첫 화면"],
    ["TbListCheck", "장비별 투입 목록", "수주 − 이미 깎은 것 →\nFG/GX7 배정 · 납기순", "투입 목록 FG/GX7"],
  ];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.1;
    await iconDot(s, "auto" + i, autos[i][0], x, 1.85, 0.7, HEX.a1, HEX.lt1);
    s.addText(autos[i][1], { x: x + 0.85, y: 1.85, w: 2.9, h: 0.7, fontSize: 22, bold: true, color: HEX.dk1, valign: "middle", margin: 0, isTextBox: true, objectName: "auto" + i + "-title" });
    s.addText(autos[i][2], { x, y: 2.7, w: 3.8, h: 0.95, fontSize: 17, color: HEX.dk2, valign: "top", margin: 0, isTextBox: true, objectName: "auto" + i + "-desc" });
    capture(s, "auto" + i + "-cap", x, 3.85, 3.8, 2.8, autos[i][3]);
  }
  s.addNotes("[2:00] 자동화 세 가지. 일일보고는 매일 아침 출근 로그온과 오후 4시에 PC 가 알아서 만듭니다 — 4월부터 131개. 현황판은 오늘 실적과 출하를 공유폴더에 올립니다. 투입 목록은 ERP 수주에서 이미 깎은 걸 빼고 장비별로 납기순 정리합니다. (화면 캡처로 설명)");

  // ---------- 5. 물어보면 답한다 ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "② 자동화·시연" });
  s.addText("필수 ② 시연", { placeholder: "kicker" });
  s.addText("물어보면 기록에서 꺼내 답한다", { placeholder: "title" });
  const qa = [
    ["장비 문제", "GX7 로더 사용 금지는\n왜였고 언제 풀렸어?", [
      "08-13 점검: 실린더 이상 → 사용 금지",
      "10-12 교체 → 10-13 해제 (약 2개월)",
      "고장 원인은 「확인 필요」로 남겨 둠",
    ]],
    ["연삭 조건", "Ø125 휠을 19 m/s 로\n쓰려면 RPM 은?", [
      "60,000 × 19 ÷ (π × 125) ≈ 2,903 rpm",
      "사내 실사용 2,600~3,000 rpm 안",
      "사내 상한 25 m/s = 3,820 rpm",
    ]],
  ];
  for (let i = 0; i < 2; i++) {
    const x = 0.6 + i * 6.2;
    s.addText(qa[i][0], { x, y: 1.8, w: 5.9, h: 0.4, fontSize: 16, bold: true, color: HEX.a2, margin: 0, isTextBox: true, objectName: "qa" + i + "-tag" });
    card(s, "qa" + i + "-q", x, 2.25, 5.9, 1.25, HEX.dk1);
    await iconDot(s, "qa" + i + "-qi", "TbMessageQuestion", x + 0.25, 2.5, 0.75, HEX.a1, HEX.lt1);
    s.addText(qa[i][1], { x: x + 1.2, y: 2.25, w: 4.5, h: 1.25, fontSize: 20, bold: true, color: HEX.lt1, valign: "middle", margin: 0, isTextBox: true, objectName: "qa" + i + "-qtext" });
    card(s, "qa" + i + "-a", x, 3.65, 5.9, 2.3, HEX.lt2);
    s.addText(qa[i][2].map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < 2, paraSpaceAfter: 10 } })),
      { x: x + 0.25, y: 3.85, w: 5.45, h: 1.9, fontSize: 19, color: HEX.dk1, valign: "top", margin: 0, isTextBox: true, objectName: "qa" + i + "-atext" });
  }
  card(s, "qa-rule", 0.6, 6.15, 12.1, 0.7, HEX.a4);
  s.addText([
    { text: "모르는 건 모른다고 · ", options: { bold: true } },
    { text: "조건은 참고값, 검증은 사람 (ANCA iGrind 입력 전 계산·검산까지)" },
  ], { x: 0.85, y: 6.15, w: 11.7, h: 0.7, fontSize: 18, color: HEX.dk1, valign: "middle", margin: 0, isTextBox: true, objectName: "qa-rule-text" });
  s.addNotes("[1:30] 질문 두 개 예시 (실제 화면 캡처로 교체 예정). 장비 고장 경위를 날짜까지 기록에서 꺼내 답하고, 원인처럼 모르는 건 모른다고 답합니다. 연삭 조건은 계산 과정이 보여서 검산할 수 있고, 사내 기준과 같이 나옵니다. 단 조건은 참고값이고 ANCA 공구 설계 프로그램 입력 전 검산까지만 씁니다.");

  // ---------- 6. 전후 비교 (A안) ----------
  pres.addSection({ title: "③ 전후 비교" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "③ 전후 비교" });
  s.addText("필수 ③ 업무 적용 전후 비교", { placeholder: "kicker" });
  s.addText("써 보기 전 · 써 본 후", { placeholder: "title" });
  card(s, "ba0", 0.6, 1.9, 5.9, 3.7, HEX.lt2);
  s.addText("일일보고 집계", { x: 0.95, y: 2.15, w: 5.2, h: 0.45, fontSize: 20, bold: true, color: HEX.dk2, margin: 0, isTextBox: true, objectName: "ba0-label" });
  s.addText("매일 손으로", { x: 0.95, y: 2.85, w: 2.4, h: 0.9, fontSize: 24, color: HEX.a3, valign: "middle", margin: 0, isTextBox: true, objectName: "ba0-before" });
  s.addImage({ data: await icon("TbArrowRight", HEX.a1), x: 3.25, y: 2.95, w: 0.7, h: 0.7, objectName: "ba0-arrow" });
  s.addText("자동", { x: 4.1, y: 2.75, w: 2.2, h: 1.1, fontSize: 54, bold: true, color: HEX.a1, valign: "middle", margin: 0, isTextBox: true, objectName: "ba0-after" });
  s.addText("18 / 18 영업일 빠짐없이 생성\n(10-07 기준 4주)", { x: 0.95, y: 4.2, w: 5.2, h: 1.1, fontSize: 17, color: HEX.dk2, valign: "top", margin: 0, isTextBox: true, objectName: "ba0-note" });
  card(s, "ba1", 6.8, 1.9, 5.9, 3.7, HEX.lt2);
  s.addText("아낀 시간", { x: 7.15, y: 2.15, w: 5.2, h: 0.45, fontSize: 20, bold: true, color: HEX.dk2, margin: 0, isTextBox: true, objectName: "ba1-label" });
  s.addText([
    { text: "하루 약 ", options: { fontSize: 24, color: HEX.dk1 } },
    { text: "15", options: { fontSize: 54, bold: true, color: HEX.a1 } },
    { text: " 분", options: { fontSize: 24, color: HEX.dk1 } },
  ], { x: 7.15, y: 2.75, w: 5.2, h: 1.1, valign: "middle", margin: 0, isTextBox: true, objectName: "ba1-num" });
  s.addText("월 5시간 안팎\n사내 경험값 — 정식 측정 아님", { x: 7.15, y: 4.2, w: 5.2, h: 1.1, fontSize: 17, color: HEX.dk2, valign: "top", margin: 0, isTextBox: true, objectName: "ba1-note" });
  await iconDot(s, "ba-meter", "TbRuler2", 0.6, 5.95, 0.7, HEX.a2, HEX.lt1);
  s.addText("장비별 투입 목록 효과는 작업일지로 「셋업당 개수」를 재는 도구까지 만들었고, 아직 2주라 효과는 단정하지 않는다", { x: 1.55, y: 5.85, w: 11.15, h: 0.9, fontSize: 18, color: HEX.dk1, valign: "middle", margin: 0, isTextBox: true, objectName: "ba-meter-text" });
  s.addNotes("[1:30] 전후 비교. 일일보고는 손 집계에서 자동으로 바뀌었고 4주 동안 하루도 안 빠졌습니다. 아낀 시간은 하루 15분 정도 — 경험값입니다. 투입 목록 효과는 셋업당 개수를 재는 도구까지 만들었는데, 도입 2주에 추석·장비 수리가 섞여 아직 효과라고 말하지 않겠습니다. (질문 대비: FG 7.5→6.7, GX7 3.6→4.9 합산 / 하루 평균은 6.5→6.1 — 소재 페이지 §6)");

  // ---------- 7. 써 보니 ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "③ 전후 비교" });
  s.addText("필수 ③ 써 보니", { placeholder: "kicker" });
  s.addText("쓸 만한 점과 한계", { placeholder: "title" });
  s.addText("쓸 만한 점", { x: 0.6, y: 1.8, w: 5.0, h: 0.5, fontSize: 22, bold: true, color: HEX.a6, margin: 0, isTextBox: true, objectName: "good-head" });
  const goods = ["흩어진 자료를 한곳에 정리", "매일 반복하는 집계·보고", "「왜 그렇게 했는지」 기록이 남는다"];
  for (let i = 0; i < 3; i++) {
    const y = 2.5 + i * 1.15;
    await iconDot(s, "good" + i, "TbCheck", 0.6, y, 0.65, HEX.a6, HEX.lt1);
    s.addText(goods[i], { x: 1.45, y, w: 4.3, h: 0.65, fontSize: 20, color: HEX.dk1, valign: "middle", margin: 0, isTextBox: true, objectName: "good" + i + "-text" });
  }
  s.addText("한계", { x: 6.3, y: 1.8, w: 5.0, h: 0.5, fontSize: 22, bold: true, color: HEX.a1, margin: 0, isTextBox: true, objectName: "limit-head" });
  const limits = [
    ["36%", "손이 간다 — 4주간 결정 84건 중 30건이 자동화 고치기·운영"],
    ["4개", "효과 없는 자동화는 껐다 — 예: 알림 메일 48통 아무도 안 읽음"],
    ["사람", "수치·조건은 AI 가 틀릴 수 있다 — 출처를 붙이고 현장 검증"],
  ];
  for (let i = 0; i < 3; i++) {
    const y = 2.4 + i * 1.45;
    card(s, "limit" + i, 6.3, y, 6.4, 1.25, HEX.lt2);
    s.addText(limits[i][0], { x: 6.5, y, w: 1.55, h: 1.25, fontSize: 32, bold: true, color: HEX.a1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "limit" + i + "-num" });
    s.addText(limits[i][1], { x: 8.15, y, w: 4.35, h: 1.25, fontSize: 16, color: HEX.dk1, valign: "middle", margin: 0, isTextBox: true, objectName: "limit" + i + "-text" });
  }
  s.addNotes("[1:30] 써 보니 정리·반복 작업에는 확실히 강합니다. 한계도 있습니다. 4주 동안 결정의 36%가 자동화를 고치고 돌보는 일이었습니다. 효과 없는 자동화는 성적표로 재서 4개를 껐습니다 — 예로 알림 메일 48통을 아무도 안 읽었습니다. 그리고 수치·조건은 AI 가 틀릴 수 있어서 출처를 붙이고 현장에서 확인합니다.");

  // ---------- 8. 마무리 ----------
  pres.addSection({ title: "마무리" });
  s = pres.addSlide({ masterName: "COVER_DARK", sectionTitle: "마무리" });
  s.addText("앞으로의 가능성", { placeholder: "kicker" });
  s.addText("대단한 건 아니어도,\n매일 쓸 만하다", { placeholder: "title" });
  s.addText([
    { text: "CAD — 무료 2D CAD 에 연결해 말로 도면 초안 (시험 중)", options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "다른 팀도 바로 — 엑셀 보고 자동화 · 흩어진 자료 정리 · 문서 조사", options: { bullet: true } },
  ], { placeholder: "body" });
  s.addText("감사합니다  |  생산팀", { x: 0.8, y: 6.2, w: 6, h: 0.4, fontSize: 18, color: C.background1, margin: 0, isTextBox: true, objectName: "end-team" });
  s.addShape(pres.shapes.OVAL, { x: 9.9, y: 1.7, w: 2.7, h: 2.7, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: "end-dot" });
  s.addImage({ data: await icon("TbRulerMeasure", HEX.lt1), x: 10.5, y: 2.3, w: 1.5, h: 1.5, objectName: "end-icon" });
  s.addNotes("[0:45] 앞으로는 CAD 도면 초안을 말로 그리는 걸 시험 중입니다 — 아직 '이런 것도 된다' 수준입니다. 엑셀 보고 자동화나 자료 정리는 다른 팀도 바로 쓸 수 있습니다. 대단한 건 아니어도 매일 쓸 만합니다. 감사합니다.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
