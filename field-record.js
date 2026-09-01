/* =====================================================
   field-record.js — 현장 기록 페이지 전용 스크립트
   최종 수정: 2026-06-15
   ===================================================== */

// ── GAS 배포 URL ─────────────────────────────────────
var GAS_URL = 'https://script.google.com/macros/s/AKfycbzO00KKfNHFcmMRPGLZcaYb95JiYbqqMZbMgyhdCIuq77VLSHZI0Bx1JVYBoxfVrM88Sw/exec';

// ── 오늘 날짜 자동 세팅 ──────────────────────────────
(function () {
  var today = new Date().toLocaleDateString('en-CA'); // YYYY-MM-DD
  document.getElementById('test-date').value   = today;
  document.getElementById('defect-date').value = today;
})();

// ── 탭 전환 ─────────────────────────────────────────
function switchTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(function (p) { p.classList.remove('active'); });
  document.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
  document.getElementById('panel-' + name).classList.add('active');
  btn.classList.add('active');
}

// ── 재연마 의뢰 버튼 URL 생성 ────────────────────────
var _lastTestData   = {};
var _lastDefectData = {};

function buildRequestUrl(data) {
  var p = new URLSearchParams();
  if (data.tool_type) p.set('tool_type', data.tool_type);
  if (data.series)    p.set('series',    data.series);
  if (data.diameter)  p.set('diameter',  data.diameter);
  return 'request.html?' + p.toString();
}

// ── 폼 리셋 ─────────────────────────────────────────
function resetForm(type) {
  document.getElementById(type + '-form').reset();
  var today = new Date().toLocaleDateString('en-CA');
  document.getElementById(type + '-date').value = today;
  document.getElementById(type + '-form-wrap').style.display   = 'block';
  document.getElementById(type + '-success').style.display = 'none';
}

// ── 체크박스 값 수집 헬퍼 ────────────────────────────
function getCheckedValues(form, name) {
  return Array.from(form.querySelectorAll('input[name="' + name + '"]:checked'))
    .map(function (cb) { return cb.value; }).join(', ');
}

// ── 가공 테스트 제출 ─────────────────────────────────
document.getElementById('test-form').addEventListener('submit', function (e) {
  e.preventDefault();
  var btn = document.getElementById('test-submit-btn');
  btn.disabled = true; btn.textContent = '저장 중...';

  var fd   = new FormData(this);
  var data = { type: 'test' };
  fd.forEach(function (v, k) { data[k] = v; });
  _lastTestData = data;

  submitData(data, function () {
    document.getElementById('test-request-btn').href     = buildRequestUrl(_lastTestData);
    document.getElementById('test-form-wrap').style.display  = 'none';
    document.getElementById('test-success').style.display    = 'block';
    btn.disabled = false; btn.textContent = '기록 저장';
  });
});

// ── 불량 기록 제출 ───────────────────────────────────
document.getElementById('defect-form').addEventListener('submit', function (e) {
  e.preventDefault();
  var form = this;
  var btn  = document.getElementById('defect-submit-btn');

  var symptoms = getCheckedValues(form, 'symptom');
  if (!symptoms) { alert('불량 증상을 하나 이상 선택해 주세요.'); return; }

  btn.disabled = true; btn.textContent = '저장 중...';

  var fd   = new FormData(form);
  var data = { type: 'defect', symptom: symptoms };
  fd.forEach(function (v, k) { if (k !== 'symptom') data[k] = v; });
  _lastDefectData = data;

  submitData(data, function () {
    document.getElementById('defect-request-btn').href        = buildRequestUrl(_lastDefectData);
    document.getElementById('defect-form-wrap').style.display = 'none';
    document.getElementById('defect-success').style.display   = 'block';
    btn.disabled = false; btn.textContent = '불량 기록 저장';
  });
});

// ── 공통 전송 함수 ───────────────────────────────────
function submitData(data, onSuccess) {
  var params = new URLSearchParams(data).toString();
  fetch(GAS_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params
  }).then(function () {
    saveLocal(data);
    onSuccess();
  }).catch(function () {
    // 네트워크 오류 시 로컬 저장만
    saveLocal(data);
    onSuccess();
  });
}

// ── 로컬 저장 (오프라인 백업) ────────────────────────
function saveLocal(data) {
  var key     = data.type === 'test' ? 'cnc_test_records' : 'cnc_defect_records';
  var records = JSON.parse(localStorage.getItem(key) || '[]');
  data._saved_at = new Date().toISOString();
  records.unshift(data);
  if (records.length > 200) records = records.slice(0, 200);
  localStorage.setItem(key, JSON.stringify(records));
}

// ── 하단 퀵 네비 현재 페이지 표시 ───────────────────
(function () {
  var cur = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.qn-btn').forEach(function (a) {
    if (a.getAttribute('href') === cur) a.classList.add('qn-active');
  });
  document.body.style.paddingBottom = '64px';
})();
