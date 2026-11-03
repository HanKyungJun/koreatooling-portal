// =========================================================
// 납기 현황 자동 알림 스크립트 v3
// 대상 시트: 재연마 수주현황
// 알림 기준: 매일 아침 전체 현황 요약
// 업데이트: 2026-06-11 — 실제 수주현황 열 구조에 맞게 재구성
// =========================================================

// ─── 설정값 (여기만 수정하세요) ───────────────────────────
var RECIPIENT_EMAIL = "여기에_본인_이메일@gmail.com";  // 수신 이메일
var CC_EMAIL        = "";                              // CC (없으면 빈칸)
var SHEET_NAME      = "재연마 수주현황";

// 열 인덱스 (0부터 시작, 실제 수주현황 파일 기준)
var COL_ORDER_NO  = 0;   // A: 수주번호
var COL_CUSTOMER  = 2;   // C: 납품처명
var COL_ITEM      = 9;   // J: 품목명
var COL_QTY       = 10;  // K: 수주량
var COL_STATUS    = 6;   // G: 진행상태
var COL_DEADLINE  = 7;   // H: 납기일자

var STATUS_DONE   = "완결";  // 이 상태는 알림에서 제외
// ────────────────────────────────────────────────────────


// ─────────────────────────────────────────
// 메인 함수: 매일 아침 납기 전체 현황 발송
// 트리거에 이 함수를 등록합니다 (매일 08:30)
// ─────────────────────────────────────────
function checkDeadlines() {
  var ss    = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    Logger.log("시트를 찾을 수 없음: " + SHEET_NAME);
    return;
  }

  var data  = sheet.getDataRange().getValues();
  var today = new Date();
  today.setHours(0, 0, 0, 0);

  var groups = { overdue: [], today: [], d3: [], d7: [], future: [] };
  var total  = 0;

  for (var i = 1; i < data.length; i++) {
    var row    = data[i];
    var status = String(row[COL_STATUS]).trim();
    if (!row[COL_ORDER_NO] || status === STATUS_DONE || status === "nan") continue;

    var deadlineRaw = row[COL_DEADLINE];
    if (!deadlineRaw) continue;

    var deadline = new Date(deadlineRaw);
    deadline.setHours(0, 0, 0, 0);
    var diff = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24));

    var item = {
      orderNo:  row[COL_ORDER_NO],
      customer: row[COL_CUSTOMER],
      item:     row[COL_ITEM],
      qty:      row[COL_QTY],
      deadline: Utilities.formatDate(deadline, "Asia/Seoul", "MM/dd"),
      diff:     diff,
      status:   status
    };

    total++;
    if      (diff < 0)  groups.overdue.push(item);
    else if (diff === 0) groups.today.push(item);
    else if (diff <= 3)  groups.d3.push(item);
    else if (diff <= 7)  groups.d7.push(item);
    else                 groups.future.push(item);
  }

  if (total === 0) {
    Logger.log("진행 중인 수주 건 없음 — 이메일 미발송");
    return;
  }

  sendEmail(groups, total, false);
  Logger.log("발송 완료: 총 " + total + "건 (초과:" + groups.overdue.length + " 오늘:" + groups.today.length + " D-3:" + groups.d3.length + ")");
}


// ─────────────────────────────────────────
// 테스트 함수: 지금 바로 전체 현황 발송
// ─────────────────────────────────────────
function testSendAll() {
  checkDeadlines();
  Logger.log("테스트 발송 실행 완료");
}


// ─────────────────────────────────────────
// 이메일 발송 함수
// ─────────────────────────────────────────
function sendEmail(groups, total, isTest) {
  var today    = new Date();
  var dateStr  = Utilities.formatDate(today, "Asia/Seoul", "yyyy년 MM월 dd일");
  var overdueCnt = groups.overdue.length;
  var urgentCnt  = groups.today.length + groups.d3.length;

  var flag = overdueCnt > 0 ? "⛔ 납기초과 있음"
           : urgentCnt  > 0 ? "⚠️ 긴급 있음"
           : "✅ 정상";

  var subject = "[납기알림] " + Utilities.formatDate(today, "Asia/Seoul", "MM/dd")
              + " " + flag + " — 진행중 " + total + "건";

  function buildTable(items, color) {
    if (items.length === 0) return "<p style='color:#999;font-size:12px'>해당 없음</p>";
    var rows = items.map(function(r) {
      var dLabel = r.diff < 0  ? "D+" + Math.abs(r.diff)
                 : r.diff === 0 ? "오늘"
                 : "D-" + r.diff;
      return "<tr>"
        + "<td style='padding:5px 10px;border-bottom:1px solid #eee;font-weight:700;color:" + color + "'>" + dLabel + "</td>"
        + "<td style='padding:5px 10px;border-bottom:1px solid #eee'>" + r.deadline + "</td>"
        + "<td style='padding:5px 10px;border-bottom:1px solid #eee'>" + r.customer + "</td>"
        + "<td style='padding:5px 10px;border-bottom:1px solid #eee;font-size:12px'>" + r.item + "</td>"
        + "<td style='padding:5px 10px;border-bottom:1px solid #eee;text-align:right'>" + r.qty + "개</td>"
        + "<td style='padding:5px 10px;border-bottom:1px solid #eee;color:#888'>" + r.status + "</td>"
        + "</tr>";
    }).join("");
    return "<table style='width:100%;border-collapse:collapse;font-size:13px'>"
      + "<tr style='background:#f5f5f5;font-size:11px;color:#666'>"
      + "<th style='padding:5px 10px;text-align:left'>D-Day</th>"
      + "<th style='padding:5px 10px;text-align:left'>납기</th>"
      + "<th style='padding:5px 10px;text-align:left'>납품처</th>"
      + "<th style='padding:5px 10px;text-align:left'>품목</th>"
      + "<th style='padding:5px 10px;text-align:right'>수량</th>"
      + "<th style='padding:5px 10px;text-align:left'>상태</th>"
      + "</tr>" + rows + "</table>";
  }

  function section(title, color, icon, items) {
    if (items.length === 0) return "";
    return "<div style='margin-bottom:18px'>"
      + "<h3 style='color:" + color + ";font-size:13px;margin:0 0 6px;border-left:4px solid " + color + ";padding-left:8px'>"
      + icon + " " + title + " (" + items.length + "건)</h3>"
      + buildTable(items, color)
      + "</div>";
  }

  var body = "<div style='font-family:\"Malgun Gothic\",Arial,sans-serif;font-size:14px;max-width:680px'>"
    + "<div style='background:#1A3A6B;padding:16px 20px;border-radius:8px 8px 0 0'>"
    + "<h2 style='color:#fff;margin:0;font-size:16px'>📦 납기 현황 알림</h2>"
    + "<p style='color:rgba(255,255,255,0.7);margin:4px 0 0;font-size:12px'>"
    + dateStr + " 기준 · 진행 중 " + total + "건"
    + (overdueCnt > 0 ? " &nbsp;<span style='background:#d32f2f;color:#fff;border-radius:10px;padding:1px 8px;font-size:11px'>" + overdueCnt + "건 초과</span>" : "")
    + (urgentCnt  > 0 ? " &nbsp;<span style='background:#f57c00;color:#fff;border-radius:10px;padding:1px 8px;font-size:11px'>" + urgentCnt + "건 긴급</span>" : "")
    + "</p></div>"
    + "<div style='padding:16px 20px;background:#fff;border:1px solid #e0e0e0;border-top:none'>"
    + section("⛔ 납기 초과", "#d32f2f", "⛔", groups.overdue)
    + section("🔴 오늘 납기", "#c62828", "🔴", groups.today)
    + section("🟠 D-3 이내",  "#f57c00", "🟠", groups.d3)
    + section("🟡 D-4 ~ D-7", "#f9a825", "🟡", groups.d7)
    + section("🟢 D-8 이상",  "#388e3c", "🟢", groups.future)
    + "</div>"
    + "<div style='background:#f5f5f5;padding:10px 20px;font-size:11px;color:#999;border-radius:0 0 8px 8px'>"
    + "시트: " + SHEET_NAME + " · 자동발송 (코리아툴링 생산팀)"
    + "</div></div>";

  var options = { htmlBody: body };
  if (CC_EMAIL && CC_EMAIL.trim() !== "") options.cc = CC_EMAIL;

  GmailApp.sendEmail(RECIPIENT_EMAIL, subject, "", options);
}
