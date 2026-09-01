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
    var ts   = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm:ss');
    var ss   = SpreadsheetApp.openById(SHEET_ID);

    var sheetMap = {
      'request-form':  '재연마의뢰',
      'defect-form':   '불량신고',
      'inquiry-form':  '진행문의',
      'supplies-form': '소모품요청'
    };

    var sheetName = sheetMap[form];
    if (!sheetName) return ContentService.createTextOutput('unknown form: ' + form);

    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) return ContentService.createTextOutput('sheet not found: ' + sheetName);

    var fileUrl = '';
    if (form === 'request-form' && d['file-data'] && d['file-data'].indexOf(',') > -1) {
      fileUrl = saveFileToDrive(d['file-data'], d['file-name'] || 'attachment', ts);
    }

    sheet.appendRow(buildRow(form, d, darr, ts, fileUrl));
    sendEmail(form, d, darr, ts, fileUrl);

    return ContentService.createTextOutput('ok');

  } catch (err) {
    return ContentService.createTextOutput('error: ' + err.message);
  }
}

function saveFileToDrive(dataUrl, fileName, ts) {
  try {
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
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    return file.getUrl();
  } catch (err) {
    return 'file save error: ' + err.message;
  }
}

function sendEmail(form, d, darr, ts, fileUrl) {
  try {
    var labels = {
      'request-form':  'Regrinding Request',
      'defect-form':   'Defect Report',
      'inquiry-form':  'Progress Inquiry',
      'supplies-form': 'Supplies Request'
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
    'supplies-form': 'Supplies Request'
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
  return [ts, JSON.stringify(d)];
}
