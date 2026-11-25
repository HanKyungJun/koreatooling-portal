// Korea Tooling - Form Submissions to Google Sheets + Email
// HTML form (iframe POST) -> Apps Script doPost -> Sheets + Drive + Email

var SHEET_ID      = '1FawxgBM132Xi_ourEGj3dlEQOxk9ZMDbO2O4De0AfHc';
var NOTIFY_EMAIL  = 'hzn2001@toolkorea.co.kr';
var UPLOAD_FOLDER = 'koreatooling-attachments';

function doPost(e) {
  try {
    var d    = e.parameter;
    var darr = e.parameters;
    var form = d['form-name'] || '';
    // 2026-10-30 스팸 거르기: 폼의 숨은 칸(hp_check)은 사람이 볼 수 없다. 값이 있으면 자동 입력 → 저장 · 메일 없이 'ok' 만 돌려준다.
    //   칸이 없는 옛 폼은 값이 비어 있으므로 그대로 접수된다(순서 상관없이 배포 가능).
    if (d['hp_check']) return ContentService.createTextOutput('ok');
    var ts   = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm:ss');
    var ss   = SpreadsheetApp.openById(SHEET_ID);

    var sheetMap = {
      'request-form':  '재연마의뢰',
      'defect-form':   '불량신고',
      'inquiry-form':  '진행문의',
      'supplies-form': '소모품요청',
      'estimate-form': '견적문의'
    };

    var sheetName = sheetMap[form];
    if (!sheetName) return ContentService.createTextOutput('unknown form: ' + form);

    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) return ContentService.createTextOutput('sheet not found: ' + sheetName);

    var fileUrl = '';
    if ((form === 'request-form' || form === 'estimate-form') && d['file-data'] && d['file-data'].indexOf(',') > -1) {
      // 2026-11-25 — 파일 저장이 실패하면 행 · 메일 없이 실패를 돌려준다(화면이 「접수 확인 안 됨」을 띄워 고객이 다시 보냄).
      //   예전에는 오류 문구를 파일 칸에 넣고 'ok' 를 돌려줘서, 고객은 첨부된 줄 알았지만 파일이 없었다.
      try {
        fileUrl = saveFileToDrive(d['file-data'], d['file-name'] || 'attachment', ts);
      } catch (fileErr) {
        Logger.log('File save error: ' + fileErr.message);
        return ContentService.createTextOutput('error: file');
      }
    }

    sheet.appendRow(buildRow(form, d, darr, ts, fileUrl));
    sendEmail(form, d, darr, ts, fileUrl);

    return ContentService.createTextOutput('ok');

  } catch (err) {
    return ContentService.createTextOutput('error: ' + err.message);
  }
}

// 2026-11-25 — 실패하면 예외를 던진다(doPost 가 받아 'error: file' 로 돌려줌). 예전에는 오류 문구를 URL 자리에 돌려줬다.
function saveFileToDrive(dataUrl, fileName, ts) {
  var parts  = dataUrl.split(',');
  var mime   = parts[0].replace('data:', '').replace(';base64', '');
  var base64 = parts[1];
  var blob   = Utilities.newBlob(Utilities.base64Decode(base64), mime, fileName);

  var folders = DriveApp.getFoldersByName(UPLOAD_FOLDER);
  var folder  = folders.hasNext() ? folders.next() : DriveApp.createFolder(UPLOAD_FOLDER);

  var dot  = fileName.lastIndexOf('.');
  var base = dot > -1 ? fileName.substring(0, dot) : fileName;
  var ext  = dot > -1 ? fileName.substring(dot) : '';
  blob.setName(base + '_' + ts.replace(/[: ]/g, '-') + ext);

  var file = folder.createFile(blob);
  // 2026-11-25 — 공유 범위: 「링크가 있는 누구나」 → 「회사 계정 + 링크」. 고객 도면이 링크만으로 밖에서 열리지 않게.
  //   회사 정책상 도메인 공유가 막혀 있으면 공유 없이(소유자만) 둔다 — 알림 메일 링크는 소유자 계정으로 열림.
  try {
  file.setSharing(DriveApp.Access.DOMAIN_WITH_LINK, DriveApp.Permission.VIEW);
  } catch (shareErr) {
  Logger.log('Share setting skipped (owner only): ' + shareErr.message);
  }
  return file.getUrl();
}

// 2026-11-25 — 한 번만 손으로 실행: 이미 받은 첨부의 「링크가 있는 누구나」 공유를 「회사 계정 + 링크」로 바꾼다.
//   편집기에서 이 함수를 골라 ▶ 실행 → 실행 로그에 바꾼 개수가 나온다. 파일을 지우거나 옮기지 않는다.
function restrictExistingAttachments() {
  var folders = DriveApp.getFoldersByName(UPLOAD_FOLDER);
  if (!folders.hasNext()) { Logger.log('folder not found: ' + UPLOAD_FOLDER); return; }
  var files = folders.next().getFiles();
  var changed = 0, skipped = 0, failed = 0;
  while (files.hasNext()) {
    var f = files.next();
    try {
      if (f.getSharingAccess() === DriveApp.Access.ANYONE_WITH_LINK || f.getSharingAccess() === DriveApp.Access.ANYONE) {
        f.setSharing(DriveApp.Access.DOMAIN_WITH_LINK, DriveApp.Permission.VIEW);
        changed++;
      } else {
        skipped++;
      }
    } catch (err) {
      failed++;
      Logger.log('fail: ' + f.getName() + ' — ' + err.message);
    }
  }
  Logger.log('changed ' + changed + ' · already limited ' + skipped + ' · failed ' + failed);
}

function sendEmail(form, d, darr, ts, fileUrl) {
  try {
    var labels = {
      'request-form':  'Regrinding Request',
      'defect-form':   'Defect Report',
      'inquiry-form':  'Progress Inquiry',
      'supplies-form': 'Supplies Request',
      'estimate-form': 'Estimate Inquiry'
    };
    var label   = labels[form] || form;
    var subject = '[KoreaTooling] ' + label + ' (' + ts + ')';
    var body    = buildEmailBody(form, d, darr, ts, fileUrl);
    MailApp.sendEmail({ to: NOTIFY_EMAIL, subject: subject, body: body });
  } catch (err) {
    Logger.log('Email error: ' + err.message);
  }
}

function buildEmailBody(form, d, darr, ts, fileUrl) {
  function val(key) { return d[key] || '-'; }
  function arr(key) {
    var v = darr[key];
    return v ? v.filter(function(x) { return x && x.trim(); }).join(', ') : '-';
  }

  var labels = {
    'request-form':  'Regrinding Request',
    'defect-form':   'Defect Report',
    'inquiry-form':  'Progress Inquiry',
    'supplies-form': 'Supplies Request',
    'estimate-form': 'Estimate Inquiry'
  };

  var body = '================================\n';
  body += 'KoreaTooling - ' + (labels[form] || form) + '\n';
  body += '================================\n';
  body += 'Time: ' + ts + '\n\n';

  if (form === 'request-form') {
    body += 'Company  : ' + val('company') + '\n';
    body += 'Contact  : ' + val('contact') + '\n';
    body += 'Phone    : ' + val('phone') + '\n';
    body += 'Email    : ' + val('email') + '\n';
    body += 'Tool Type: ' + val('tool_type') + '\n';
    body += 'Material : ' + val('material') + '\n';
    body += 'Spec     : ' + arr('spec[]') + '\n';
    body += 'Quantity : ' + arr('quantity[]') + '\n';
    body += 'Notes    : ' + val('notes') + '\n';
    if (fileUrl) { body += 'File     : ' + fileUrl + '\n'; }
  } else if (form === 'defect-form') {
    body += 'Company  : ' + val('company') + '\n';
    body += 'Contact  : ' + val('contact') + '\n';
    body += 'Phone    : ' + val('phone') + '\n';
    body += 'Date     : ' + val('defect_date') + '\n';
    body += 'Tool Spec: ' + arr('tool_spec[]') + '\n';
    body += 'Defect Qty: ' + arr('defect_qty[]') + '\n';
    body += 'Symptom  : ' + arr('symptom') + '\n';
    body += 'Workpiece: ' + val('workpiece') + '\n';
    body += 'Detail   : ' + val('detail') + '\n';
  } else if (form === 'inquiry-form') {
    body += 'Company  : ' + val('company') + '\n';
    body += 'Contact  : ' + val('contact') + '\n';
    body += 'Phone    : ' + val('phone') + '\n';
    body += 'Ref Date : ' + val('ref_date') + '\n';
    body += 'Inquiry  : ' + val('inquiry') + '\n';
  } else if (form === 'supplies-form') {
    body += 'Requester: ' + val('requester') + '\n';
    body += 'Dept     : ' + val('department') + '\n';
    body += 'Item     : ' + val('item_name') + '\n';
    body += 'Spec     : ' + val('item_spec') + '\n';
    body += 'Quantity : ' + val('quantity') + '\n';
    body += 'Due Date : ' + val('due_date') + '\n';
    body += 'Reason   : ' + val('reason') + '\n';
    body += 'Urgent   : ' + (d['urgent'] === 'Y' ? 'YES' : 'NO') + '\n';
  } else if (form === 'estimate-form') {
    body += 'Company  : ' + val('company') + '\n';
    body += 'Contact  : ' + val('contact') + '\n';
    body += 'Phone    : ' + val('phone') + '\n';
    body += 'Email    : ' + val('email') + '\n';
    body += 'Category : ' + val('category') + '\n';
    body += 'Material : ' + val('material') + '\n';
    body += 'Spec     : ' + arr('spec[]') + '\n';
    body += 'Quantity : ' + arr('quantity[]') + '\n';
    body += 'Due Date : ' + val('due_date') + '\n';
    body += 'Monthly Vol: ' + val('monthly_volume') + '\n';
    body += 'Notes    : ' + val('notes') + '\n';
    if (fileUrl) { body += 'File     : ' + fileUrl + '\n'; }
  }

  body += '\n--------------------------------\n';
  body += 'Google Sheet:\n';
  body += 'https://docs.google.com/spreadsheets/d/' + SHEET_ID + '\n';
  body += '--------------------------------\n';
  body += 'KoreaTooling Portal - Auto Notification';
  return body;
}

function buildRow(form, d, darr, ts, fileUrl) {
  function val(key) { return d[key] || ''; }
  function arr(key) {
    var v = darr[key];
    return v ? v.filter(function(x) { return x && x.trim(); }).join(' / ') : '';
  }

  if (form === 'request-form') {
    return [ts, val('company'), val('contact'), val('phone'), val('email'),
            val('tool_type'), val('material'),
            arr('spec[]'), arr('quantity[]'), val('notes'), fileUrl || ''];
  }
  if (form === 'defect-form') {
    return [ts, val('company'), val('contact'), val('phone'), val('defect_date'),
            arr('tool_spec[]'), arr('defect_qty[]'),
            arr('symptom'), val('workpiece'), val('detail')];
  }
  if (form === 'inquiry-form') {
    return [ts, val('company'), val('contact'), val('phone'),
            val('ref_date'), val('inquiry')];
  }
  if (form === 'supplies-form') {
    return [ts, val('requester'), val('department'), val('item_name'),
            val('item_spec'), val('quantity'), val('due_date'), val('reason'),
            val('urgent') === 'Y' ? 'urgent' : 'normal'];
  }
  if (form === 'estimate-form') {
    return [ts, val('company'), val('contact'), val('phone'), val('email'),
            val('category'), val('material'),
            arr('spec[]'), arr('quantity[]'), val('due_date'), val('monthly_volume'),
            val('notes'), fileUrl || ''];
  }
  return [ts, JSON.stringify(d)];
}
