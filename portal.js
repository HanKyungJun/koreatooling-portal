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
   2026-09-08 보안 조치 — 게이트 로직을 이 파일에서 제거했다.
   이유: portal.js 는 공개 저장소·GitHub Pages 로 그대로 나가므로
         비밀번호를 여기 두면 소스 보기로 즉시 노출된다.
   현재: 게이트는 사내 전용 `portal-auth.js` 가 담당한다.
         이 파일은 generate.py 가 .env 의 STAFF_PASS 로 빌드 시 생성하며
         사내 공유폴더에만 배포된다(공개 배포 경로에 존재하지 않음).
   ───────────────────────────────────────────────── */

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
