/* =====================================================
   portal.js — 코리아툴링 포털 공통 유틸리티
   적용 페이지: request / defect / inquiry / estimate (공개 폼) · supplies(생성 중단)
   최종 수정: 2026-11-25 — 제출 결과를 서버 응답('ok')으로 확인한 뒤에만 「접수」 표시
   ===================================================== */

/* ── 상수 ──────────────────────────────────────────── */
// 2026-10-02: 공개폼 프로젝트(코리아툴링 공개폼) 배포로 교체 — 옛 AKfycbzjgm7I… 는 계정에서 프로젝트를 찾지 못함
var GAS_FORM_URL = 'https://script.google.com/macros/s/AKfycbyXK6wvfA8pLepD9RHqtdNa5P6aMC6ktK3UYgVIciXwh2rPDFbanI9KOZCMi8UGLjNA1g/exec';

/* ── GAS 폼 제출 공통 핸들러 ─────────────────────────
   대상: request / defect / inquiry / estimate
   조건: <form> + .submit-btn + #form-wrap + #success 가 존재할 때 자동 바인딩
   ───────────────────────────────────────────────── */
(function bindGasForm() {
  var form = document.querySelector('form[name]');
  if (!form) return;
  var url = (typeof window.PAGE_GAS_URL !== 'undefined') ? window.PAGE_GAS_URL : GAS_FORM_URL;
  form.setAttribute('action', url);            // 스크립트가 막힌 경우에도 기존 방식(숨은 iframe)으로 전송되게 남겨 둔다
  form.setAttribute('target', 'hidden-target');

  var btn   = form.querySelector('.submit-btn');
  var label = btn ? btn.textContent : '';
  var errBox = document.createElement('div');  // 실패 안내 — 폼 내용은 그대로 두고 다시 누르게 한다
  errBox.className = 'submit-error';
  errBox.setAttribute('role', 'alert');
  errBox.style.display = 'none';
  if (btn) btn.parentNode.insertBefore(errBox, btn);

  function showDone() {
    var wrap = document.getElementById('form-wrap');
    var ok   = document.getElementById('success');
    if (wrap) wrap.style.display = 'none';
    if (ok)   ok.style.display   = 'block';
  }
  function showFail() {
    if (btn) { btn.disabled = false; btn.textContent = label; }
    errBox.textContent = '접수가 확인되지 않았습니다. 입력하신 내용은 그대로 있으니 잠시 후 다시 눌러 주세요.';
    errBox.style.display = 'block';
  }

  form.addEventListener('submit', function (ev) {
    errBox.style.display = 'none';
    if (btn) { btn.disabled = true; btn.textContent = '제출 중...'; }
    // 2026-11-25 — 0.8초 뒤 무조건 「접수」 표시하던 것을 서버 응답('ok')을 확인한 뒤에만 표시하도록 바꿈
    if (!window.fetch || !window.URLSearchParams || !window.FormData) {
      // 아주 옛 브라우저: 숨은 iframe 이 응답을 받았을 때 표시(응답 내용은 못 읽음)
      var frame = document.querySelector('iframe[name="hidden-target"]');
      if (frame) frame.addEventListener('load', showDone, { once: true });
      return;                                  // 기본 전송(iframe POST) 진행
    }
    ev.preventDefault();
    var ctrl  = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 30000);   // 30 s 넘으면 실패 안내
    fetch(url, { method: 'POST', body: new URLSearchParams(new FormData(form)), signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) { return r.text(); })
      .then(function (t) { clearTimeout(timer); if (t.trim() === 'ok') showDone(); else showFail(); })
      .catch(function () { clearTimeout(timer); showFail(); });
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
    { href: 'about.html',        label: '🏭 회사 소개' },
    { href: 'request.html',      label: '📥 재연마 의뢰' },
    { href: 'estimate.html',     label: '💰 견적 문의' },
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
