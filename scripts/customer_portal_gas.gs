// ============================================================
// 코리아툴링 거래처 발주·재고 조회 — Apps Script  [v1, 2026-10-08]
//   워크숍 범위 ③ · decisions.md 2026-10-08 (2)·(3)
//
// 흐름
//   PC(erp/customer_portal_export.py --upload) ──POST(업로드 토큰)──▶ doPost → 「data」 탭 통째로 교체
//   고객(order-status.html) ──POST {action:'view', code}──▶ doPost → 그 거래처 행만 JSON 으로 반환
//     (접속 코드가 주소창·접속 기록에 남지 않도록 GET 이 아니라 POST 본문으로 받는다)
//
// 🔴 이 저장소는 Public 이다. 시트 ID·토큰·접속 코드는 이 파일에 적지 않는다.
//    Apps Script 콘솔 > 프로젝트 설정 > 스크립트 속성 에 등록:
//      SHEET_ID      : 이 용도로 새로 만든 비공개 구글 시트의 ID (공유하지 않는다)
//      UPLOAD_TOKEN  : .env 의 CUSTOMER_PORTAL_UPLOAD_TOKEN 과 같은 값
//    🔴 둘 중 하나라도 없으면 업로드·조회 모두 거부한다(닫힌 기본값 — 현장기록 v2 와 다름).
//
// 시트 탭 (없으면 자동 생성)
//   codes      : 거래처코드 | 거래처명 | 접속코드 | 사용(Y/N) | 메모   ← 경준님이 직접 관리
//   data       : PC 업로드분 (손으로 고치지 않는다 — 다음 업로드 때 덮어써진다)
//   meta       : 마지막 업로드 시각 · 스냅샷 시각 · 행 수
//   access_log : 조회 기록 (시각 · 결과 · 거래처코드) — 접속 코드 원문은 남기지 않는다
//
// 배포: 배포 > 새 배포 > 웹 앱
//   - 다음 사용자로 실행: 나(hzn2001@toolkorea.co.kr)
//   - 액세스 권한: 모든 사용자   ← 고객이 로그인 없이 접속 코드로 조회하므로 필요
// ⚠️ 저장소의 이 파일은 사본이다. 콘솔에 붙여넣지 않으면 아무 효과가 없다.
// ============================================================

var CODE_HEADERS = ['거래처코드', '거래처명', '접속코드', '사용(Y/N)', '메모'];
var LOG_HEADERS  = ['시각', '결과', '거래처코드'];
var FAIL_LIMIT   = 30;    // 10분 동안 틀린 코드가 이만큼 넘으면 10분간 조회 중지
var FAIL_WINDOW  = 600;   // 초

function props_() { return PropertiesService.getScriptProperties(); }
function now_()   { return Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm:ss'); }
function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
function sheet_(ss, name, headers) {
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    if (headers) sh.appendRow(headers);
  }
  return sh;
}
function ss_() {
  var id = props_().getProperty('SHEET_ID');
  return id ? SpreadsheetApp.openById(id) : null;
}

// ── 업로드 (PC 전용) ───────────────────────────────────────
function doPost(e) {
  try {
    var expected = props_().getProperty('UPLOAD_TOKEN');
    var ss = ss_();
    if (!expected || !ss) return json_({ status: 'not_configured' });

    var p = JSON.parse(e.postData.contents);
    if (p.action === 'view') return view_(ss, p.code);
    if (p.token !== expected) return json_({ status: 'forbidden' });

    var cols = p.columns;
    var rows = (p.rows || []).map(function (r) {
      return cols.map(function (c) { return r[c] === undefined ? '' : r[c]; });
    });

    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      var data = sheet_(ss, 'data');
      data.clearContents();
      data.getRange(1, 1, 1, cols.length).setValues([cols]);
      if (rows.length) {
        data.getRange(2, 1, rows.length, cols.length).setNumberFormat('@').setValues(rows);
      }
      var meta = sheet_(ss, 'meta');
      meta.clearContents();
      meta.getRange(1, 1, 4, 2).setNumberFormat('@').setValues([   // '@' = 텍스트 — 시각이 날짜로 바뀌지 않게 (2026-10-08)
        ['uploaded_kst', p.uploaded_kst || now_()],
        ['snapshot_kst', p.snapshot_kst || ''],
        ['rows', rows.length],
        ['customers', JSON.stringify(p.customers || {})]
      ]);
      sheet_(ss, 'codes', CODE_HEADERS);   // 처음 한 번 탭을 만들어 둔다
    } finally {
      lock.releaseLock();
    }
    return json_({ status: 'ok', rows: rows.length });
  } catch (err) {
    return json_({ status: 'error', message: String(err).slice(0, 200) });
  }
}

// 주소만 열어 본 경우 — 데이터는 주지 않는다
function doGet(e) {
  return json_({ status: 'ok', service: 'customer-portal', note: 'POST only' });
}

// ── 조회 (고객) ───────────────────────────────────────────
function view_(ss, rawCode) {
  try {

    var cache = CacheService.getScriptCache();
    var fails = Number(cache.get('fails') || 0);
    if (fails >= FAIL_LIMIT) return json_({ status: 'busy' });

    var code = String(rawCode || '').trim().toUpperCase();
    var log = sheet_(ss, 'access_log', LOG_HEADERS);
    if (code.length < 8) return json_({ status: 'denied' });

    var codes = sheet_(ss, 'codes', CODE_HEADERS).getDataRange().getValues();
    var cust = null, custNm = '';
    for (var i = 1; i < codes.length; i++) {
      if (String(codes[i][2]).trim().toUpperCase() === code && String(codes[i][3]).trim().toUpperCase() === 'Y') {
        cust = String(codes[i][0]).trim();
        custNm = String(codes[i][1]).trim();
        break;
      }
    }
    if (!cust) {
      cache.put('fails', String(fails + 1), FAIL_WINDOW);
      log.appendRow([now_(), 'denied', '']);
      return json_({ status: 'denied' });   // 틀린 코드 · 사용 중지 코드를 구분하지 않는다
    }

    var vals = sheet_(ss, 'data').getDataRange().getValues();
    var head = vals[0], ci = head.indexOf('cust_cd'), out = [];
    for (var j = 1; j < vals.length; j++) {
      if (String(vals[j][ci]).trim() !== cust) continue;
      var o = {};
      for (var k = 0; k < head.length; k++) if (head[k] !== 'cust_cd') o[head[k]] = vals[j][k];
      out.push(o);
    }
    var meta = {};
    sheet_(ss, 'meta').getDataRange().getValues().forEach(function (r) { meta[r[0]] = r[1]; });
    log.appendRow([now_(), 'ok', cust]);
    return json_({ status: 'ok', customer: custNm, snapshot_kst: String(meta.snapshot_kst || ''),
                   uploaded_kst: String(meta.uploaded_kst || ''), rows: out });
  } catch (err) {
    return json_({ status: 'error' });
  }
}
