// ============================================================
// cnc-wiki field-record.html → Google Sheets 연동 스크립트
// 배포 방법: Apps Script > 배포 > 새 배포 > 웹 앱
//   - 다음 사용자로 실행: 나(hzn2001@toolkorea.co.kr)
//   - 액세스 권한: 모든 사용자
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
