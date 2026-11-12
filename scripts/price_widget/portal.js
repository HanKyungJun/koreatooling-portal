/* =====================================================
   portal.js — 코리아툴링 포털 공통 유틸리티
   적용 페이지: defect / inquiry / request / supplies / field-record / dashboard
   최종 수정: 2026-06-15 · 2026-10-30 시험판(price_widget) — 제출 성공 판정
   ===================================================== */

/* ── 상수 ──────────────────────────────────────────── */
// 2026-10-02: 공개폼 프로젝트(코리아툴링 공개폼) 배포로 교체 — 옛 AKfycbzjgm7I… 는 계정에서 프로젝트를 찾지 못함
var GAS_FORM_URL = 'https://script.google.com/macros/s/AKfycbyXK6wvfA8pLepD9RHqtdNa5P6aMC6ktK3UYgVIciXwh2rPDFbanI9KOZCMi8UGLjNA1g/exec';

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
  /* 2026-10-30 시험판: 전송이 실패해도 0.8 초 뒤 「접수되었습니다」가 뜨던 문제 수정.
     fetch(no-cors)로 보내고 서버 응답이 왔을 때만 완료 화면을 띄운다. 연결 실패 · 45 초 무응답이면 오류 안내(첨부 5 MB 를 Drive 에 올리는 시간 고려).
     보내는 형식은 예전 iframe 제출과 같은 application/x-www-form-urlencoded(GAS doPost 의 e.parameter(s) 그대로).
     한계: no-cors 라 서버가 「ok」 를 돌려줬는지까지는 못 본다 — 연결 · 응답 여부만 판단. fetch 가 없는 옛 브라우저는 예전 방식. */
  var btn0 = form.querySelector('.submit-btn');
  var label0 = btn0 ? btn0.textContent : '';
  function showErr(msg) {
    var box = form.querySelector('.submit-err');
    if (!box) {
      box = document.createElement('div');
      box.className = 'submit-err';
      box.setAttribute('role', 'alert');
      box.style.cssText = 'margin:10px 0 0;padding:10px 12px;border:1.5px solid #ffd0d0;background:#fff5f5;color:#c62828;border-radius:8px;font-size:0.85rem;line-height:1.5';
      if (btn0 && btn0.parentNode) btn0.parentNode.insertBefore(box, btn0.nextSibling); else form.appendChild(box);
    }
    box.textContent = msg;
    box.style.display = msg ? 'block' : 'none';
  }
  function done() {
    var wrap = document.getElementById('form-wrap');
    var ok   = document.getElementById('success');
    if (wrap) wrap.style.display = 'none';
    if (ok)   ok.style.display   = 'block';
  }
  form.addEventListener('submit', function (e) {
    if (btn0) { btn0.disabled = true; btn0.textContent = '제출 중...'; }
    showErr('');
    if (!window.fetch || !window.URLSearchParams || !window.FormData) {   // 옛 브라우저 — 예전 방식(iframe 제출)
      setTimeout(done, 800);
      return;
    }
    e.preventDefault();
    var body = new URLSearchParams();
    new FormData(form).forEach(function (v, k) { if (typeof v === 'string') body.append(k, v); });
    var ctrl = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 45000);
    fetch(url, { method: 'POST', mode: 'no-cors', body: body, signal: ctrl ? ctrl.signal : undefined })
      .then(function () { clearTimeout(timer); done(); })
      .catch(function () {
        clearTimeout(timer);
        if (btn0) { btn0.disabled = false; btn0.textContent = label0; }
        showErr('전송하지 못했습니다. 인터넷 연결을 확인하고 다시 눌러 주세요. 계속 안 되면 전화로 문의해 주세요. 입력하신 내용은 그대로 남아 있습니다.');
      });
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
