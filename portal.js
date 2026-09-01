/* =====================================================
   portal.js — 코리아툴링 포털 공통 유틸리티
   적용 페이지: defect / inquiry / request / supplies / field-record / dashboard
   최종 수정: 2026-06-15
   ===================================================== */

/* ── 상수 ──────────────────────────────────────────── */
var GAS_FORM_URL = 'https://script.google.com/macros/s/AKfycbzjgm7IhynT5CCQzX1f9M78HUN8cDwwmLj9xVNSV3lrF_TPkvPCmLFt9E7GwRYmRipA/exec';

/* ── GAS 폼 제출 공통 핸들러 ─────────────────────────
   대상: defect / inquiry / request / supplies
   조건: <form> + .submit-btn + #form-wrap + #success 가 존재할 때 자동 바인딩
   ───────────────────────────────────────────────── */
(function bindGasForm() {
  var form = document.querySelector('form[name]');
  if (!form) return;
  // GAS_FORM_URL 대신 페이지가 window.PAGE_GAS_URL 을 먼저 선언한 경우 그것을 사용
  var url = (typeof window.PAGE_GAS_URL !== 'undefined') ? window.PAGE_GAS_URL : GAS_FORM_URL;
  form.setAttribute('action', url);
  form.setAttribute('target', 'hidden-target');
  form.addEventListener('submit', function () {
    var btn = form.querySelector('.submit-btn');
    if (btn) { btn.disabled = true; btn.textContent = '제출 중...'; }
    setTimeout(function () {
      var wrap = document.getElementById('form-wrap');
      var ok   = document.getElementById('success');
      if (wrap) wrap.style.display = 'none';
      if (ok)   ok.style.display   = 'block';
    }, 800);
  });
})();

/* ── 직원 인증 오버레이 ──────────────────────────────
   조건: #auth-overlay 가 존재하는 페이지에서만 동작
   비밀번호: 1234  (sessionStorage 'kt_auth' 로 세션 유지)
   ───────────────────────────────────────────────── */
(function initAuth() {
  var overlay = document.getElementById('auth-overlay');
  if (!overlay) return;
  if (sessionStorage.getItem('kt_auth') === '1') {
    overlay.style.display = 'none';
    return;
  }
  var inp = document.getElementById('pass-input');
  if (inp) {
    inp.focus();
    inp.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') window.checkPass();
    });
  }
})();

function checkPass() {
  var inp = document.getElementById('pass-input');
  if (!inp) return;
  if (inp.value === '1234') {
    sessionStorage.setItem('kt_auth', '1');
    document.getElementById('auth-overlay').style.display = 'none';
  } else {
    var err = document.getElementById('pass-err');
    if (err) err.textContent = '비밀번호가 틀렸습니다.';
    inp.value = '';
    inp.focus();
  }
}

/* ── 퀵 네비 렌더링 ──────────────────────────────────
   사용법: <nav class="quick-nav" id="quick-nav"></nav> 추가 후 자동 렌더링
   현재 페이지는 .active 클래스로 표시
   ───────────────────────────────────────────────── */
(function renderQuickNav() {
  var nav = document.getElementById('quick-nav');
  if (!nav) return;
  var links = [
    { href: 'index.html',        label: '🏠 메인' },
    { href: 'request.html',      label: '📥 재연마 의뢰' },
    { href: 'defect.html',       label: '⚠️ 불량 신고' },
    { href: 'inquiry.html',      label: '📋 진행 문의' },
    { href: 'dashboard.html',    label: '📊 현황판' },
    { href: 'supplies.html',     label: '🛒 소모품' },
    { href: '절삭조건-검색.html', label: '🔍 조건 검색' },
    { href: 'field-record.html', label: '📝 현장 기록' },
  ];
  var current = location.pathname.split('/').pop() || 'index.html';
  nav.innerHTML = links.map(function (l) {
    var cls = (l.href === current) ? ' class="active"' : '';
    return '<a href="' + l.href + '"' + cls + '>' + l.label + '</a>';
  }).join('');
})();
