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
const ASOF = "자료 기준일 2026-10-16";

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
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.7, w: 12.1, h: 0.7, fontSize: 36, bold: true, color: C.text1, align: "left", valign: "middle", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 1.45, w: 12.1, h: 0.45, fontSize: 20, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } },
      { text: { text: "TOOLKOREA 생산팀 · Claude AI 파일럿 2기", options: { x: 7.2, y: 7.0, w: 5.0, h: 0.3, fontSize: 11, color: C.accent3, align: "right", margin: 0 } } },
    ],
    slideNumber: { x: 12.3, y: 7.0, w: 0.45, h: 0.3, fontSize: 11, color: C.accent3, align: "right" },
  });

  const box = (s, name, x, y, w, h, fill, line) =>
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: line || fill, width: 0.75 }, objectName: name });
  const note = (s, t) => s.addText(t, { x: 0.6, y: 6.95, w: 6.5, h: 0.35, fontSize: 11, color: H.gray, margin: 0, isTextBox: true, objectName: "footnote" });
  const head = (s, kicker, title, msg) => {
    s.addText(kicker, { placeholder: "kicker" });
    s.addText(title, { placeholder: "title" });
    if (msg) s.addText(msg, { placeholder: "body" });
  };
  const TH = (t, o = {}) => ({ text: t, options: { bold: true, color: H.white, fill: { color: H.navy }, fontSize: 17, valign: "middle", ...o } });
  const TD = (t, o = {}) => ({ text: t, options: { color: H.navy, fontSize: 17, valign: "middle", ...o } });
  const tableOpts = (y, colW, rowH) => ({ x: 0.6, y, w: colW.reduce((a, b) => a + b, 0), colW, rowH, border: { type: "solid", pt: 0.75, color: H.line }, margin: [4, 8, 4, 8], fontFace: "맑은 고딕" });

  // ===== 1. 표지 =====
  pres.addSection({ title: "표지" });
  let s = pres.addSlide({ masterName: "COVER", sectionTitle: "표지" });
  s.addText("TOOLKOREA 생산팀  ·  Claude AI 파일럿 2기 성과 발표", { placeholder: "kicker" });
  s.addText("재연마 현장 데이터의 정리와 업무 자동화", { placeholder: "title" });
  s.addText("지식 기록 · 보고 자동화 · 현장 판단 보조 — 2기(2026. 7 ~ 10) 적용 결과", { placeholder: "body" });
  s.addShape(pres.shapes.LINE, { x: 0.8, y: 4.6, w: 11.7, h: 0, line: { color: H.sub, width: 0.75 }, objectName: "cover-rule" });
  s.addText([
    { text: "발표  ", options: { color: H.gray } }, { text: "2026. 11. 10 (화)", options: { color: H.white, breakLine: true } },
    { text: "발표자  ", options: { color: H.gray } }, { text: "생산팀 한경준", options: { color: H.white } },
  ], { x: 0.8, y: 4.85, w: 6, h: 0.9, fontSize: 18, margin: 0, valign: "top", isTextBox: true, objectName: "cover-meta" });
  s.addText("근거: 사내 지식 위키(cnc-wiki) 기록 · 자동화 실행 로그  |  " + ASOF, { x: 0.8, y: 6.75, w: 11.7, h: 0.35, fontSize: 12, color: H.gray, margin: 0, isTextBox: true, objectName: "cover-src" });
  s.addNotes("[0:20] 생산팀 발표입니다. 2기 동안 재연마 현장의 흩어진 데이터를 정리하고, 매일 반복하던 보고 업무를 자동화한 결과를 말씀드리겠습니다.");

  // ===== 2. 목차 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "표지" });
  head(s, "CONTENTS", "발표 순서", "공지된 필수 3항목(①②③)을 4개 장에 나눠 담았습니다");
  const toc = [
    ["01", "추진 배경", "현황과 문제점, 추진 방향", ""],
    ["02", "팀 내 Claude 활용 현황", "핵심 수치 · 활용 영역 · 추진 경과", "필수 ①"],
    ["03", "자동화 시스템 소개 및 시연", "시스템 구성 · 실행 화면 · 질의응답", "필수 ②"],
    ["04", "업무 적용 전후 비교", "정량 비교 · 근거와 신뢰도", "필수 ③"],
    ["05", "한계와 향후 과제", "운영하며 확인한 한계 · 대응 · 다음 과제", ""],
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
  head(s, "01  추진 배경", "현황과 문제점", "재연마 업무의 자료는 다섯 곳에 흩어져 있었고, 집계와 판단은 매일 사람이 했습니다");
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 2.15, w: 5.0, h: 3.55, fill: { color: H.bg }, line: { color: H.gray, width: 1, dashType: "dash" }, objectName: "photo-main" });
  s.addText("사진 삽입\nANCA 장비 (FG · GX7)", { x: 0.6, y: 2.15, w: 5.0, h: 3.55, fontSize: 15, color: H.gray, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "photo-main-ph" });
  [0, 1].forEach((k) => {
    const x = 0.6 + k * 2.55;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 5.85, w: 2.45, h: 0.85, fill: { color: H.bg }, line: { color: H.gray, width: 1, dashType: "dash" }, objectName: "photo-sub" + k });
    s.addText(k ? "캡처: 수리 기록 PDF" : "캡처: 월간생산일지 엑셀", { x, y: 5.85, w: 2.45, h: 0.85, fontSize: 12, color: H.gray, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "photo-sub" + k + "-ph" });
  });
  box(s, "bg-asis", 5.9, 2.15, 6.8, 2.2, H.bg, H.line);
  s.addText("현황 (도입 전)", { x: 6.15, y: 2.25, w: 6.3, h: 0.4, fontSize: 17, bold: true, color: H.sub, margin: 0, isTextBox: true, objectName: "asis-h" });
  s.addText([
    { text: "자료 분산 — ERP · 엑셀 2종 · PDF · 개인 노하우", options: { bullet: true, breakLine: true } },
    { text: "일일보고 집계 · 투입 판단을 매일 수작업", options: { bullet: true, breakLine: true } },
    { text: "조건·고장 처리의 근거가 기록으로 남지 않음", options: { bullet: true } },
  ], { x: 6.15, y: 2.7, w: 6.35, h: 1.55, fontSize: 17, color: H.ink, valign: "top", margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: "asis-t" });
  s.addShape(pres.shapes.DOWN_ARROW, { x: 9.05, y: 4.42, w: 0.5, h: 0.32, fill: { color: H.teal }, line: { color: H.teal }, objectName: "bg-arrow" });
  box(s, "bg-tobe", 5.9, 4.8, 6.8, 1.9, H.tealBg, H.line);
  s.addText("추진 방향", { x: 6.15, y: 4.9, w: 6.3, h: 0.4, fontSize: 17, bold: true, color: H.teal, margin: 0, isTextBox: true, objectName: "tobe-h" });
  s.addText([
    { text: "한곳에 기록 — 출처·신뢰도와 함께 사내 위키로", options: { bullet: true, breakLine: true } },
    { text: "반복은 자동 실행 — 업무 PC 예약 실행", options: { bullet: true, breakLine: true } },
    { text: "판단 근거 보존 — 기존 값은 지우지 않고 이력으로", options: { bullet: true } },
  ], { x: 6.15, y: 5.32, w: 6.35, h: 1.3, fontSize: 17, color: H.ink, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: "tobe-t" });
  note(s, "생산팀 재연마 — 장비 2대(ANCA FastGrind · ANCA GX7)  |  " + ASOF);
  s.addNotes("[0:50] (장비 사진을 가리키며) 생산팀은 ANCA 장비 두 대로 재연마를 합니다. 자료가 ERP, 엑셀, PDF, 사람 머릿속에 흩어져 있었고, 일일보고 집계와 투입 판단을 매일 손으로 했습니다. 그래서 세 방향으로 추진했습니다 — 한곳에 기록, 반복은 자동 실행, 판단 근거는 남긴다.");

  // ===== 4. 활용 현황 — 핵심 수치 =====
  pres.addSection({ title: "02 활용 현황" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 활용 현황" });
  head(s, "02  팀 내 Claude 활용 현황  |  필수 ①", "핵심 수치", "생산팀 계정 1개로, 업무 PC 폴더를 연결해 대화로 정리·분석·자동화를 진행했습니다");
  const kpi = [
    ["138", "페이지", "지식 위키", "장비 · 휠 · 연삭 조건 · 수리"],
    ["약 300", "건", "결정 기록", "근거 · 대안 · 영향"],
    ["132", "건", "일일보고 생성", "6월부터 매일 자동"],
    ["10,744", "건", "단가표 자동 대조", "재연마 단가표 검수"],
    ["55", "개", "자동화 스크립트", "Python"],
  ];
  kpi.forEach((k, i) => {
    const x = 0.6 + i * 2.46, w = 2.26;
    box(s, "kpi" + i, x, 2.2, w, 2.6, H.bg, H.line);
    s.addText([{ text: k[0], options: { fontSize: 34, bold: true, color: H.teal } }, { text: " " + k[1], options: { fontSize: 15, bold: true, color: H.navy } }],
      { x: x + 0.1, y: 2.4, w: w - 0.2, h: 0.95, align: "center", valign: "bottom", margin: 0, isTextBox: true, objectName: "kpi" + i + "-n" });
    s.addText([{ text: k[2], options: { fontSize: 18, bold: true, color: H.navy, breakLine: true } }, { text: k[3], options: { fontSize: 14, color: H.gray } }],
      { x: x + 0.1, y: 3.55, w: w - 0.2, h: 1.0, align: "center", valign: "top", margin: 0, isTextBox: true, objectName: "kpi" + i + "-l" });
  });
  box(s, "rule-box", 0.6, 5.15, 12.1, 1.5, H.white, H.line);
  s.addText("운영 원칙", { x: 0.85, y: 5.3, w: 2.0, h: 0.4, fontSize: 16, bold: true, color: H.teal, margin: 0, isTextBox: true, objectName: "rule-h" });
  s.addText([
    { text: "모든 수치에 단위와 신뢰도 표기 (제조사 기준 / 실측 검증 / 사내 경험값 / 추정값)", options: { bullet: true, breakLine: true } },
    { text: "AI 가 낸 수치·조건은 참고값 — 현장 검증 후 적용, 기존 값은 지우지 않고 이력으로 보존", options: { bullet: true } },
  ], { x: 0.85, y: 5.7, w: 11.6, h: 0.85, fontSize: 17, color: H.ink, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: "rule-t" });
  note(s, "근거: 위키 자동 집계 · 결정 기록 · 중간보고(09-14)  |  " + ASOF);
  s.addNotes("[0:50] 핵심 수치입니다. 위키 138페이지, 결정 기록 약 300건 — 왜 그렇게 했는지 나중에 찾을 수 있습니다. 일일보고 132건 — 6월부터는 매일 자동 생성, 단가표 1만여 건 자동 대조. 원칙은 모든 수치에 신뢰도를 붙이고, AI 수치는 현장 검증 후에만 쓴다는 것입니다.");

  // ===== 5. 활용 영역 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 활용 현황" });
  head(s, "02  팀 내 Claude 활용 현황  |  필수 ①", "활용 영역", "기록 · 자동화 · 판단 보조 · 검수 · 문서 작성 다섯 영역에 쓰고 있습니다");
  const area = [
    ["지식 기록", "장비·휠·연삭 조건·수리 이력 정리, 결정마다 근거 기록", "위키 138페이지 · 수리 이력 17건"],
    ["보고 자동화", "일일보고 엑셀 생성, 사내 현황판 배포 (매일 07:50 · 16:00)", "일일보고 132건 (6월~ 매일 자동)"],
    ["현장 판단 보조", "ERP 수주 − 가공 완료분 → 장비별 투입 목록 (납기순 · 형상 묶음)", "09-28 가동 · 규칙 보강 7회"],
    ["데이터 검수", "단가표 대조, 작업일지 파싱, ERP 조회 연동", "단가표 10,744건 · ERP 5개 화면"],
    ["설비 대응 문서", "로더 고장 진단 · 수리 검토보고 · 증설 투자 검토", "F · GX7 로더 진단 → 정식 수리"],
  ];
  s.addTable([[TH("영역"), TH("내용"), TH("대표 사례")], ...area.map((r, i) => [TD(r[0], { bold: true, fill: { color: i % 2 ? H.white : H.bg } }), TD(r[1], { fill: { color: i % 2 ? H.white : H.bg } }), TD(r[2], { color: H.teal, bold: true, fill: { color: i % 2 ? H.white : H.bg } })])],
    { ...tableOpts(2.2, [2.1, 5.9, 4.1], [0.5, 0.8, 0.8, 0.8, 0.8, 0.8]), objectName: "area-table" });
  note(s, "현장 판단 보조·데이터 검수는 2기에 새로 시작한 영역  |  " + ASOF);
  s.addNotes("[0:50] 활용 영역은 다섯 가지입니다. 2기에 새로 들어간 건 현장 판단 보조 — ERP 수주에서 이미 가공한 것을 빼고 장비별 투입 목록을 만드는 것 — 과 단가표·ERP 데이터 검수, 그리고 8월 로더 고장 때 진단부터 수리 검토보고까지 문서 작업입니다.");

  // ===== 6. 추진 경과 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 활용 현황" });
  head(s, "02  팀 내 Claude 활용 현황  |  필수 ①", "추진 경과", "6월부터 일일보고가 매일 자동으로 만들어지고 있습니다 — 그 이전 분은 일괄 소급 생성");
  const months = ["4월", "5월", "6월", "7월", "8월", "9월", "10월*"];
  s.addChart(pres.charts.BAR, [
    { name: "소급 생성 (6-09 일괄)", labels: months, values: [21, 19, 5, 0, 0, 0, 0] },
    { name: "매일 자동 생성", labels: months, values: [0, 0, 16, 22, 19, 20, 10] },
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
  const tl = [["1기 · 4~6월", "기록 체계 구축 · 일일보고 자동화"], ["7월", "가공 테스트 · 보고서 양식"], ["8월", "F · GX7 로더 고장 대응"], ["9월", "ERP 연동 · 투입 목록 가동"], ["10월", "효과 측정 · 효과 없는 자동화 중단"]];
  tl.forEach((r, i) => {
    const y = 2.75 + i * 0.77;
    s.addText(r[0], { x: 8.65, y, w: 3.8, h: 0.32, fontSize: 14, bold: true, color: i ? H.teal : H.gray, margin: 0, isTextBox: true, objectName: "tl" + i + "-m" });
    s.addText(r[1], { x: 8.65, y: y + 0.32, w: 3.8, h: 0.38, fontSize: 15, color: H.ink, margin: 0, isTextBox: true, objectName: "tl" + i + "-t" });
  });
  note(s, "파일 실측 · *10월은 16일까지 · 8월 11건 재생성 포함  |  " + ASOF);
  s.addNotes("[0:50] 그래프는 일일보고 파일 수입니다. 회색은 6월 9일에 지난 분을 한꺼번에 만든 것이고, 청록이 그날그날 자동으로 생성된 것입니다. 6월부터는 매달 영업일 수만큼 빠짐없이 쌓이고 있습니다. 오른쪽은 1기·2기 경과입니다 — 7월 가공 테스트, 8월 로더 고장 대응, 9월 ERP 연동과 투입 목록, 10월 효과 측정.");

  // ===== 7. 시스템 구성 =====
  pres.addSection({ title: "03 자동화 시스템" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 자동화 시스템" });
  head(s, "03  자동화 시스템 소개  |  필수 ②", "시스템 구성", "기존 자료를 그대로 읽어, 업무 PC 가 정해진 시각에 결과물을 만들어 배포합니다");
  const cols = [
    { x: 0.6, w: 3.4, h: "입력 — 기존 자료", items: ["ERP 수주 · A/S 조회", "월간생산일지 (엑셀)", "출하현황 (엑셀)"], fill: H.bg },
    { x: 4.75, w: 3.8, h: "처리 — 업무 PC", items: ["예약 실행 — 07:50 · 16:00", "Python 스크립트 — 집계 · 대조 · 배정", "Claude — 스크립트 작성 · 점검 · 기록"], fill: H.tealBg },
    { x: 9.3, w: 3.4, h: "출력 — 결과물", items: ["일일보고 엑셀", "사내 현황판 (공유폴더)", "장비별 투입 목록", "지식 위키 · 결정 기록"], fill: H.bg },
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
  note(s, "새 시스템을 들이지 않고, 기존 엑셀·ERP 를 그대로 읽는 방식  |  " + ASOF);
  s.addNotes("[0:50] 구성은 단순합니다. 새 시스템을 들인 게 아니라 원래 쓰던 ERP와 엑셀을 그대로 읽습니다. 업무 PC가 출근 로그온 때와 오후 4시에 스크립트를 돌려 일일보고, 현황판, 장비별 투입 목록을 만듭니다. Claude는 이 스크립트를 짜고 점검하고, 바뀐 내용을 기록하는 역할입니다.");

  // ===== 8. 실행 화면 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 자동화 시스템" });
  head(s, "03  자동화 시스템 시연  |  필수 ②", "실행 화면", "출근하면 일일보고·현황판·투입 목록이 이미 만들어져 있습니다");
  const caps = [
    ["일일보고 엑셀", "전일 장비별 실적 · 매일 자동 생성"],
    ["사내 현황판", "오늘 실적 · 업체별 출하 · 접수 현황"],
    ["장비별 투입 목록", "FG / GX7 배정 · 납기순 · 형상 묶음"],
  ];
  caps.forEach((c, i) => {
    const x = 0.6 + i * 4.1, w = 3.9;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 2.15, w, h: 3.6, fill: { color: H.bg }, line: { color: H.gray, width: 1, dashType: "dash" }, objectName: "cap" + i });
    s.addText("화면 캡처 삽입", { x, y: 2.15, w, h: 3.6, fontSize: 14, color: H.gray, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "cap" + i + "-ph" });
    s.addText([{ text: c[0], options: { bold: true, color: H.navy, fontSize: 17, breakLine: true } }, { text: c[1], options: { color: H.gray, fontSize: 14 } }],
      { x, y: 5.85, w, h: 0.85, valign: "top", margin: 0, isTextBox: true, objectName: "cap" + i + "-cap" });
  });
  note(s, "일일보고 4주 18/18 영업일 생성(10-07 성적표)  |  " + ASOF);
  s.addNotes("[1:00] (화면을 짚으며) 왼쪽이 매일 자동으로 만들어지는 일일보고, 가운데가 사내 현황판, 오른쪽이 장비별 투입 목록입니다. 투입 목록은 현장 의견을 받아 규칙을 일곱 번 고쳤습니다.");

  // ===== 9. 질의응답 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 자동화 시스템" });
  head(s, "03  자동화 시스템 시연  |  필수 ②", "기록 기반 질의응답", "쌓아 둔 기록에서 근거와 함께 답하고, 확인되지 않은 것은 「확인 필요」로 답합니다");
  const qa = [
    ["장비 이력", "GX7 로더 사용 금지는 왜였고, 언제 풀렸나?", ["08-13 외부 점검 — 실린더 이상 → 사용 금지", "08-14 발주 → 10-12 교체 → 10-13 해제", "고장 원인 — 「확인 필요」 (기록 없음)"], "근거: 수리 이력 페이지"],
    ["연삭 조건", "Ø125 휠, 원주속도 19 m/s 면 RPM 은?", ["N = 60,000 × 19 ÷ (π × 125) ≈ 2,903 rpm", "사내 실사용 2,600 ~ 3,000 rpm 범위 안", "사내 운용 상한 25 m/s = 3,820 rpm"], "근거: 휠 기준 페이지 · Norton 카탈로그"],
  ];
  qa.forEach((q, i) => {
    const x = 0.6 + i * 6.15, w = 5.95;
    s.addText(q[0], { x, y: 2.15, w: 1.5, h: 0.36, fontSize: 13, bold: true, color: H.white, fill: { color: H.teal }, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "qa" + i + "-tag" });
    box(s, "qa" + i + "-q", x, 2.6, w, 0.85, H.navy);
    s.addText("Q.  " + q[1], { x: x + 0.2, y: 2.6, w: w - 0.4, h: 0.85, fontSize: 18, bold: true, color: H.white, valign: "middle", margin: 0, isTextBox: true, objectName: "qa" + i + "-qt" });
    box(s, "qa" + i + "-a", x, 3.55, w, 2.35, H.bg, H.line);
    s.addText(q[2].map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < q[2].length - 1 } })),
      { x: x + 0.2, y: 3.7, w: w - 0.4, h: 1.75, fontSize: 17, color: H.ink, valign: "top", margin: 0, paraSpaceAfter: 8, isTextBox: true, objectName: "qa" + i + "-at" });
    s.addText(q[3], { x: x + 0.2, y: 5.45, w: w - 0.4, h: 0.35, fontSize: 12, color: H.gray, margin: 0, isTextBox: true, objectName: "qa" + i + "-src" });
  });
  box(s, "qa-limit", 0.6, 6.05, 12.1, 0.6, H.tealBg, H.line);
  s.addText("조건은 참고값 — ANCA 공구 설계 프로그램(iGrind) 입력 전 계산·검산까지만 쓰고, 확정은 현장 테스트로 합니다", { x: 0.8, y: 6.05, w: 11.7, h: 0.6, fontSize: 17, color: H.navy, valign: "middle", margin: 0, isTextBox: true, objectName: "qa-limit-t" });
  note(s, "실제 질의 화면 캡처로 교체 예정  |  " + ASOF);
  s.addNotes("[1:00] 두 가지 예시입니다. 장비 고장 경위를 날짜까지 기록에서 꺼내 답하고, 원인처럼 기록이 없는 건 확인 필요라고 답합니다. 연삭 조건은 계산 과정을 보여 줘서 검산할 수 있고, 사내 기준 범위와 같이 나옵니다. 다만 조건은 참고값이고, 확정은 현장 테스트로 합니다.");

  // ===== 10. 전후 비교 =====
  pres.addSection({ title: "04 전후 비교" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 전후 비교" });
  head(s, "04  업무 적용 전후 비교  |  필수 ③", "적용 전후 비교", "반복 집계는 자동으로 바뀌었고, 판단 근거가 기록으로 남기 시작했습니다");
  const ba = [
    ["일일보고 집계", "매일 수작업 집계", "자동 생성 18 / 18 영업일", "성적표 10-07", "실측"],
    ["집계·판단 소요", "하루 약 15분", "확인만 — 월 약 5시간 절약", "담당자 확인", "사내 경험값"],
    ["판단 근거 기록", "개인 기억 · 메신저", "결정 기록 약 300건", "decisions 기록", "실측"],
    ["장비 수리 이력", "PDF · 사진 · 메일에 분산", "17건 정리 (과거 12 + 올해 5)", "수리 이력 페이지", "실측"],
    ["단가표 검수", "수작업 대조", "10,744건 자동 대조", "중간보고 09-14", "실측"],
    ["장비별 투입", "매일 경험으로 판단", "목록 자동 생성 · 효과는 측정 중", "작업일지 셋업 분석", "판단 보류"],
  ];
  s.addTable([[TH("항목"), TH("적용 전"), TH("적용 후"), TH("근거"), TH("신뢰도", { align: "center" })],
    ...ba.map((r, i) => { const f = { fill: { color: i === 0 ? H.tealBg : (i % 2 ? H.white : H.bg) } }; return [TD(r[0], { bold: true, ...f }), TD(r[1], { color: H.gray, ...f }), TD(r[2], { bold: true, color: H.teal, ...f }), TD(r[3], { fontSize: 14, color: H.gray, ...f }), TD(r[4], { align: "center", fontSize: 14, ...f })]; })],
    { ...tableOpts(2.15, [2.4, 2.9, 3.6, 1.9, 1.3], [0.5, 0.66, 0.66, 0.66, 0.66, 0.66, 0.66]), objectName: "ba-table" });
  note(s, "투입 목록 효과는 도입 2주·추석·장비 수리가 섞여 판단 보류  |  " + ASOF);
  s.addNotes("[1:30] 전후 비교입니다. 일일보고는 4주 동안 하루도 빠지지 않고 자동 생성됐습니다. 절약 시간은 하루 15분, 월 5시간 정도인데 정식으로 잰 값이 아니라 경험값이라고 표시했습니다. 결정 기록 약 300건, 수리 이력 17건, 단가표 1만여 건 대조는 실측입니다. 투입 목록은 셋업당 개수로 효과를 재는 도구까지 만들었지만, 기간이 짧고 추석과 장비 수리가 겹쳐 아직 효과라고 말하지 않겠습니다. (질문 대비: FG 7.5→6.7, GX7 3.6→4.9 합산 / 하루 평균 6.5→6.1)");

  // ===== 11. 한계와 대응 =====
  pres.addSection({ title: "05 한계와 과제" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "05 한계와 과제" });
  head(s, "05  한계와 향후 과제", "운영하며 확인한 한계와 대응", "자동화는 만드는 것보다 유지가 더 들었고, 그래서 성적표로 효과를 재고 정리했습니다");
  const lim = [
    ["효과 없는 자동화", "알림 메일 48통 전부 미열람 등 효과 없는 4건", "10-07 중단 — 만든 것도 쓰이지 않으면 끈다"],
    ["조용한 실패", "「정상 완료」로 기록됐으나 산출물이 없던 3건", "종료 코드 대신 산출물 존재로 정상 판정"],
    ["수치 신뢰성", "AI 계산·인용이 실제와 다를 수 있음 (표준 인용 정정 19문서)", "출처·신뢰도 4단계 표기, 현장 검증 후 적용"],
    ["1인 운용", "만들고 고치는 사람이 1명", "작업 기록·결정 근거를 문서로 남겨 인수 가능하게"],
  ];
  s.addTable([[TH("구분"), TH("확인된 내용"), TH("대응")],
    ...lim.map((r, i) => { const f = { fill: { color: i % 2 ? H.white : H.bg } }; return [TD(r[0], { bold: true, ...f }), TD(r[1], f), TD(r[2], { color: H.teal, ...f })]; })],
    { ...tableOpts(3.35, [2.3, 5.0, 4.8], [0.5, 0.68, 0.68, 0.68, 0.68]), objectName: "lim-table" });
  s.addText([{ text: "36", options: { fontSize: 44, bold: true, color: H.amber } }, { text: " %", options: { fontSize: 22, bold: true, color: H.amber } }],
    { x: 0.6, y: 2.1, w: 1.9, h: 1.0, valign: "middle", margin: 0, isTextBox: true, objectName: "cost-pct" });
  s.addText("유지 비용 — 4주간 결정 84건 중 30건이 자동화 수리·운영", { x: 2.5, y: 2.1, w: 6.5, h: 0.4, fontSize: 16, bold: true, color: H.navy, margin: 0, isTextBox: true, objectName: "cost-h" });
  s.addChart(pres.charts.BAR, [
    { name: "자동화 수리·운영", labels: ["결정 84건"], values: [30] },
    { name: "그 외 업무 판단", labels: ["결정 84건"], values: [54] },
  ], {
    x: 2.4, y: 2.45, w: 10.3, h: 0.75, barDir: "bar", barGrouping: "percentStacked", barGapWidthPct: 20,
    chartColors: [H.amber, H.line], showValue: true, dataLabelPosition: "ctr", dataLabelFontSize: 13, dataLabelColor: H.navy, dataLabelFontFace: "+mn-lt",
    showLegend: true, legendPos: "r", legendFontSize: 12, legendColor: H.ink, legendFontFace: "+mn-lt",
    catAxisHidden: true, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showTitle: false, objectName: "cost-chart",
  });
  note(s, "자동화 효과 지표 1차 판정(10-07) · 중간보고(09-14)  |  " + ASOF);
  s.addNotes("[1:10] 한계도 분명히 있습니다. 결정의 36%가 자동화를 고치는 일이었습니다. 그래서 자동화마다 성적표를 매겼고, 알림 메일 48통을 아무도 안 읽은 것처럼 효과 없는 4건은 껐습니다. 정상이라고 찍혔는데 결과물이 없던 경우도 있어서 판정 기준을 바꿨고, AI 수치는 출처와 신뢰도를 붙여 현장에서 확인합니다. 1인 운용 리스크는 기록으로 대비하고 있습니다.");

  // ===== 12. 향후 과제 =====
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "05 한계와 과제" });
  head(s, "05  한계와 향후 과제", "향후 과제", "새 기능을 늘리기보다, 지금 돌아가는 것의 효과를 확인하고 넓힙니다");
  const plan = [
    ["효과 재판정", "자동화 성적표 2차 판정", "11-04"],
    ["투입 목록 효과", "운영 데이터 누적 후 셋업당 개수 재측정", "데이터 누적 후"],
    ["ERP 실적 연동", "ERP 상태코드 해석 → 생산 실적 지표로 전환", "명칭표 확보 시"],
    ["도면 작성 보조", "무료 2D CAD 연결 — 말로 도면 초안 (시험 중)", "시험 단계"],
  ];
  s.addTable([[TH("과제"), TH("내용"), TH("시기", { align: "center" })],
    ...plan.map((r, i) => { const f = { fill: { color: i % 2 ? H.white : H.bg } }; return [TD(r[0], { bold: true, ...f }), TD(r[1], f), TD(r[2], { align: "center", color: H.teal, bold: true, ...f })]; })],
    { ...tableOpts(2.15, [2.6, 7.0, 2.5], [0.5, 0.7, 0.7, 0.7, 0.7]), objectName: "plan-table" });
  box(s, "close", 0.6, 5.65, 12.1, 1.0, H.navy);
  s.addText("AI 는 답을 대신 주는 도구가 아니라, 현장 기록을 쌓고 검증하는 협업자입니다", { x: 0.9, y: 5.65, w: 11.5, h: 1.0, fontSize: 20, bold: true, color: H.white, valign: "middle", margin: 0, isTextBox: true, objectName: "close-t" });
  note(s, "다른 팀 적용 가능: 엑셀 보고 집계 · 자료 정리 · 문서 조사  |  " + ASOF);
  s.addNotes("[0:40] 앞으로는 새 기능을 늘리기보다 지금 돌아가는 것의 효과를 확인하겠습니다. 11월 4일 성적표 2차 판정, 투입 목록 효과 재측정, ERP 실적 연동, 그리고 CAD 도면 보조는 시험 중입니다. 엑셀 보고 집계나 자료 정리는 다른 팀도 바로 쓸 수 있습니다. 감사합니다.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
