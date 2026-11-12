// ============================================================
// cnc-wiki field-record.html → Google Sheets 연동 스크립트  [v2]
//
// v2 변경점 (2026-09-08): 공유 토큰 검증 추가
//   배포 URL 이 공개 저장소 이력에 남아 URL 만으로 누구나 시트에 쓸 수 있었다.
//   URL 을 바꾸는 것만으로는 또 새면 같은 문제가 되므로 토큰으로 막는다.
//
// 🔴 토큰은 이 파일에 적지 않는다 (이 저장소는 Public 이다).
//    Apps Script 콘솔 > 프로젝트 설정 > 스크립트 속성 에 등록한다:
//      속성 이름: SHARED_TOKEN     값: .env 의 FIELD_RECORD_TOKEN 과 동일한 값
//
// 🟢 스크립트 속성이 없으면 검증을 건너뛴다 → v1 과 동작이 같다.
//    덕분에 붙여넣기 순서에 관계없이 현장 화면이 죽지 않는다(점진 적용).
//
// 적용 순서 (권장)
//   ① .env 에 FIELD_RECORD_GAS_URL · FIELD_RECORD_TOKEN 등재 → `python generate.py`
//      (사내 전용 internal/field-record-config.js 가 생성돼 클라이언트가 토큰을 보내기 시작)
//   ② 이 파일 내용을 Apps Script 콘솔에 붙여넣기 → 스크립트 속성 SHARED_TOKEN 등록
//   ③ 배포 > **새 배포** > 웹 앱 (「배포 관리 > 편집 > 새 버전」은 URL 이 그대로다)
//        - 다음 사용자로 실행: 나(hzn2001@toolkorea.co.kr)
//        - 액세스 권한: 모든 사용자   ← 현장 화면이 익명 POST 하므로 필요
//   ④ 새 URL 을 .env 의 FIELD_RECORD_GAS_URL 에 반영 → `python generate.py`
//   ⑤ 🔴 **기존 배포를 아카이브** — 이 단계까지 해야 옛 URL 이 죽는다
//
// ⚠️ 저장소의 이 파일은 사본이다. 콘솔에 붙여넣지 않으면 아무 효과가 없다.
// ============================================================

var SHEET_ID     = '1FawxgBM132Xi_ourEGj3dlEQOxk9ZMDbO2O4De0AfHc';
var NOTIFY_EMAIL = 'hzn2001@toolkorea.co.kr';

// ── 헤더 정의 ──────────────────────────────────────────────
var TEST_HEADERS = [
  '저장시각', '날짜', '장비', '소재', '공구유형', '시리즈', '직경(mm)',
  '날수', '코팅', 'RPM', '이송(mm/min)', 'ap(mm)', 'ae(mm)', '깊이(mm)',
  '쿨런트', 'Ra(μm)', '수명(개)', '결과', '메모'
];

var DEFECT_HEADERS = [
  '저장시각', '날짜', '장비', '소재', '공구유형', '직경(mm)', '시리즈',
  '증상', '발생위치', '추정원인', '원인상세', '조치내용', '재발여부'
];

// ── CORS 허용 (OPTIONS 프리플라이트) ───────────────────────
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok' }))
    .setMimeType(ContentService.MimeType.JSON);
}

// ── 메인 핸들러 ────────────────────────────────────────────
function doPost(e) {
  try {
    var d  = e.parameter;

    // ── 공유 토큰 검증 (v2, 2026-09-08) ──────────────────────
    //   스크립트 속성 SHARED_TOKEN 이 설정된 경우에만 검증한다.
    //   미설정이면 v1 과 동일하게 통과 → 점진 적용이 가능하다.
    var expected = PropertiesService.getScriptProperties().getProperty('SHARED_TOKEN');
    if (expected && d['token'] !== expected) {
      return jsonResponse({ status: 'forbidden' });   // 시트에 쓰지 않고, 메일도 보내지 않는다
    }

    var ts = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm:ss');
    var ss = SpreadsheetApp.openById(SHEET_ID);
    var type = d['type'] || '';

    if (type === 'test') {
      var sheet = getOrCreateSheet(ss, '현장기록_테스트', TEST_HEADERS);
      sheet.appendRow([
        ts,
        d['date']      || '',
        d['machine']   || '',
        d['material']  || '',
        d['tool_type'] || '',
        d['series']    || '',
        d['diameter']  || '',
        d['flutes']    || '',
        d['coating']   || '',
        d['rpm']       || '',
        d['feed']      || '',
        d['ap']        || '',
        d['ae']        || '',
        d['depth']     || '',
        d['coolant']   || '',
        d['ra']        || '',
        d['tool_life'] || '',
        d['result']    || '',
        d['notes']     || ''
      ]);
      notifyEmail('가공 테스트 기록', d, ts);

    } else if (type === 'defect') {
      var sheet = getOrCreateSheet(ss, '현장기록_불량', DEFECT_HEADERS);
      sheet.appendRow([
        ts,
        d['date']       || '',
        d['machine']    || '',
        d['material']   || '',
        d['tool_type']  || '',
        d['diameter']   || '',
        d['series']     || '',
        d['symptom']    || '',
        d['location']   || '',
        d['cause']      || '',
        d['cause_note'] || '',
        d['action']     || '',
        d['recurring']  || ''
      ]);
      notifyEmail('불량 기록', d, ts);

    } else {
      return jsonResponse({ status: 'error', message: 'unknown type: ' + type });
    }

    return jsonResponse({ status: 'ok', ts: ts });

  } catch (err) {
    return jsonResponse({ status: 'error', message: err.message });
  }
}

// ── 시트 가져오기 (없으면 생성 + 헤더 설정) ────────────────
function getOrCreateSheet(ss, name, headers) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
    sheet.appendRow(headers);
    // 헤더 행 스타일
    var headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setBackground('#1a1a2e');
    headerRange.setFontColor('#ffffff');
    headerRange.setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

// ── 이메일 알림 ────────────────────────────────────────────
function notifyEmail(label, d, ts) {
  try {
    var subject = '[cnc-wiki] ' + label + ' - ' + ts;
    var body = label + '\n';
    body += '============================\n';
    body += '시각: ' + ts + '\n';
    Object.keys(d).forEach(function(k) {
      if (k === 'token') return;                 // v2: 토큰은 메일에 남기지 않는다
      if (d[k]) body += k + ': ' + d[k] + '\n';
    });
    body += '\n시트: https://docs.google.com/spreadsheets/d/' + SHEET_ID;
    MailApp.sendEmail({ to: NOTIFY_EMAIL, subject: subject, body: body });
  } catch (err) {
    Logger.log('Email error: ' + err.message);
  }
}

// ── JSON 응답 헬퍼 ─────────────────────────────────────────
function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
