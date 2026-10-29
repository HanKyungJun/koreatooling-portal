/* 재연마 예상 정가 위젯 — 시험판 (2026-10-29 Cowork)
 * 붙이는 법(페이지 아무 곳):
 *   <div id="kt-price-widget" data-inquiry-url="estimate.html"></div>
 *   <script src="price-data.js"></script>      ← 정가 데이터(scripts/price_lookup.py --export-web 로 생성)
 *   <script src="price-lookup.js"></script>    ← 해석 · 조회 로직(PriceLookup)
 *   <script src="price-widget.js"></script>    ← 이 파일(화면)
 * 원칙: 정가만 보여 준다(할인율 · 거래처 단가 없음). 상태가 OK 가 아닌 줄은 금액 대신 「담당자 확인」.
 */
(function () {
  'use strict';
  var PL = window.PriceLookup, DATA = window.PRICE_DATA;
  var CSS = '' +
    '.ktpw{--ktpw-acc:#1f5fbf;--ktpw-ink:#1d2330;--ktpw-sub:#5d6675;--ktpw-line:#dfe3ea;--ktpw-bg:#fff;--ktpw-soft:#f4f6f9;' +
    'font-family:"Malgun Gothic","맑은 고딕",system-ui,sans-serif;color:var(--ktpw-ink);background:var(--ktpw-bg);border:1px solid var(--ktpw-line);' +
    'border-radius:12px;padding:18px;max-width:720px;box-sizing:border-box;font-size:15px;line-height:1.5}' +
    '.ktpw *{box-sizing:border-box}.ktpw h3{margin:0 0 4px;font-size:19px}.ktpw .ktpw-lead{margin:0 0 12px;color:var(--ktpw-sub);font-size:13px}' +
    '.ktpw-tabs{display:flex;gap:6px;margin-bottom:12px}.ktpw-tab{flex:1;border:1px solid var(--ktpw-line);background:var(--ktpw-soft);border-radius:8px;padding:8px;cursor:pointer;font:inherit;font-size:14px;color:var(--ktpw-sub)}' +
    '.ktpw-tab[aria-selected="true"]{background:var(--ktpw-acc);border-color:var(--ktpw-acc);color:#fff}' +
    '.ktpw-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.ktpw label{display:block;font-size:12px;color:var(--ktpw-sub);margin-bottom:2px}' +
    '.ktpw select,.ktpw input{width:100%;font:inherit;font-size:15px;padding:9px 10px;border:1px solid #b9c1ce;border-radius:8px;background:#fff;color:inherit}' +
    '.ktpw-row{display:flex;gap:8px}.ktpw-row input{flex:1;min-width:0}' +
    '.ktpw-btn{border:0;border-radius:8px;background:var(--ktpw-acc);color:#fff;font:inherit;font-size:15px;padding:10px 18px;cursor:pointer;white-space:nowrap}' +
    '.ktpw-go{margin-top:10px;width:100%}.ktpw-ex{margin-top:8px;display:flex;flex-wrap:wrap;gap:6px}' +
    '.ktpw-chip{font-size:12px;padding:4px 10px;border:1px solid var(--ktpw-line);border-radius:14px;background:var(--ktpw-soft);cursor:pointer;color:var(--ktpw-sub)}' +
    '.ktpw-out{margin-top:14px}.ktpw-parsed{font-size:12px;color:var(--ktpw-sub);margin-bottom:6px}' +
    '.ktpw-ask{color:#b25b00;font-size:14px}.ktpw-note{font-size:12px;color:#b25b00}' +
    '.ktpw table{width:100%;border-collapse:collapse}.ktpw th,.ktpw td{padding:8px 6px;border-bottom:1px solid var(--ktpw-line);text-align:left;font-size:14px}' +
    '.ktpw th{font-size:12px;color:var(--ktpw-sub);font-weight:600}.ktpw td.ktpw-p{text-align:right;font-weight:700;white-space:nowrap}' +
    '.ktpw td.ktpw-na{text-align:right;color:var(--ktpw-sub);font-size:13px;white-space:nowrap}' +
    '.ktpw-foot{margin-top:12px;font-size:12px;color:var(--ktpw-sub)}.ktpw-cta{display:inline-block;margin-top:10px;text-decoration:none}' +
    '@media (max-width:560px){.ktpw-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.ktpw th,.ktpw td{font-size:13px;padding:7px 4px}}';

  var SHAPES = [['평', '평(스퀘어) 엔드밀'], ['볼', '볼 엔드밀'], ['코너', '코너R 엔드밀'], ['라핑평', '라핑 평'], ['라핑볼', '라핑 볼'],
    ['라핑코너', '라핑 코너R'], ['리머', '리머'], ['드릴', '드릴']];
  var PARTS = [['밑날', '밑날'], ['밑옆날', '밑날 + 옆날(외경)'], ['옆날', '옆날(외경)'], ['골수리', '골수리']];
  var COATS = [['비코팅', '비코팅'], ['일반코팅', '일반 코팅'], ['고경도코팅', '고경도 코팅']];

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function opts(list, sel) { return list.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === sel ? ' selected' : '') + '>' + o[1] + '</option>'; }).join(''); }
  function won(v) { return Number(v).toLocaleString('ko-KR') + '원'; }

  function mount(root) {
    if (!PL || !DATA) { root.textContent = '정가 데이터를 불러오지 못했습니다.'; return; }
    var inq = root.getAttribute('data-inquiry-url') || '';
    root.className += ' ktpw';
    root.innerHTML =
      '<h3>재연마 예상 정가 조회</h3>' +
      '<p class="ktpw-lead">정가표 기준 <b>정가</b>입니다. 실제 금액은 거래 조건에 따라 달라지며 담당자가 확인해 드립니다.</p>' +
      '<div class="ktpw-tabs" role="tablist"><button class="ktpw-tab" role="tab" aria-selected="true" data-m="pick">항목 선택</button>' +
      '<button class="ktpw-tab" role="tab" aria-selected="false" data-m="text">문장으로 입력</button></div>' +
      '<div data-pane="pick"><div class="ktpw-grid">' +
      '<div><label>재질</label><select data-f="mat"><option value="초경">초경</option><option value="HSS">HSS(하이스)</option></select></div>' +
      '<div><label>형상</label><select data-f="shape">' + opts(SHAPES, '평') + '</select></div>' +
      '<div><label>날 수</label><select data-f="blade">' + [1, 2, 3, 4, 5, 6].map(function (n) { return '<option value="' + n + '"' + (n === 2 ? ' selected' : '') + '>' + n + '날</option>'; }).join('') + '</select></div>' +
      '<div><label>날경 Ø (mm)</label><input data-f="dia" type="number" inputmode="decimal" min="0.5" max="60" step="0.1" placeholder="예) 10"></div>' +
      '<div><label>작업 부위</label><select data-f="part">' + opts(PARTS, '밑날') + '</select></div>' +
      '<div><label>코팅</label><select data-f="coat">' + opts(COATS, '비코팅') + '</select></div>' +
      '</div><button class="ktpw-btn ktpw-go" data-act="pick">예상 정가 보기</button></div>' +
      '<div data-pane="text" hidden><div class="ktpw-row"><input data-f="q" placeholder="예) 10파이 2날 볼 고경도"><button class="ktpw-btn" data-act="text">조회</button></div>' +
      '<div class="ktpw-ex">' + ['10파이 2날 볼 고경도', 'D6 4날 평 밑옆날 일반코팅', '드릴 6.8 HSS 비코팅 2날', '하이스 라핑 볼 16mm 두날 코팅'].map(function (e) { return '<span class="ktpw-chip">' + esc(e) + '</span>'; }).join('') + '</div></div>' +
      '<div class="ktpw-out" aria-live="polite"></div>' +
      '<div class="ktpw-foot">기준: 재연마 정가표 ' + esc(String(DATA.sheet || '').replace(/^정가표/, '')) + ' · 할인 적용 전 정가 · 표에 없는 규격 · 특수 가공은 담당자 확인</div>';
    var $ = function (s) { return root.querySelector(s); };
    var out = $('.ktpw-out');
    function field(n) { return root.querySelector('[data-f="' + n + '"]'); }

    function show(rows, q) {
      var h = '';
      if (q) {
        var lab = { blade: '날수', shape: '형상', dia: '날경', mat: '재질', part: '작업 부위', coat: '코팅' };
        h += '<div class="ktpw-parsed">이렇게 이해했어요: ' + Object.keys(lab).map(function (k) {
          var v = q[k]; if (v == null) return lab[k] + ' —';
          return lab[k] + ' <b>' + esc(k === 'dia' ? 'Ø' + PL.g(v) + ' mm' : k === 'blade' ? v + '날' : k === 'coat' ? PL.COAT_LABEL[v] : v) + '</b>';
        }).join(' · ') + '</div>';
        if (q.missing && q.missing.length) {
          out.innerHTML = h + '<div class="ktpw-ask">' + q.missing.map(function (m) { return { shape: '형상(평 · 볼 · 코너 · 라핑 · 드릴 …)', dia: '날경(mm)' }[m]; }).join(', ') + '을(를) 함께 입력해 주세요.</div>';
          return;
        }
        (q.assumed || []).forEach(function (a) { h += '<div class="ktpw-note">※ ' + esc(a) + '</div>'; });
      }
      h += '<table><tr><th>규격</th><th style="text-align:right">예상 정가</th></tr>';
      var anyAsk = false;
      rows.forEach(function (r) {
        // 드릴은 정가표(26.10) 구간 안만 금액 표시 — 표 밖(초경 20 mm 초과 · 밑날 외 등)은 ERP 옛 정가가 남아 있어 「담당자 확인」(한경준님 10-29: 20 초과 가격표 없음)
        var ok = r.status === 'OK' && r.price != null && !(/\/드릴\//.test(r.name) && r.src === '등록 품목 정가');
        if (!ok) anyAsk = true;
        h += '<tr><td>' + esc(r.name) + '</td>' + (ok ? '<td class="ktpw-p">' + won(r.price) + '</td>' : '<td class="ktpw-na">담당자 확인</td>') + '</tr>';
      });
      h += '</table>';
      if (inq) {
        var spec = rows.map(function (r) { return r.name; }).join(', ');
        h += '<a class="ktpw-btn ktpw-cta" href="' + esc(inq) + (inq.indexOf('?') < 0 ? '?' : '&') + 'spec=' + encodeURIComponent(spec) + '">이 규격으로 견적 문의</a>';
      }
      if (anyAsk) h += '<div class="ktpw-note" style="margin-top:6px">「담당자 확인」 규격은 정가표에 없거나 확인이 필요한 규격입니다.</div>';
      out.innerHTML = h;
    }

    function runPick() {
      var d = parseFloat(field('dia').value);
      if (!(d > 0)) { out.innerHTML = '<div class="ktpw-ask">날경(mm)을 입력해 주세요.</div>'; field('dia').focus(); return; }
      var r = PL.priceOne(+field('blade').value, field('shape').value, d, field('mat').value, field('part').value, field('coat').value);
      show([r], null);
    }
    function runText() {
      var v = field('q').value.trim(); if (!v) return;
      var res = PL.answer(v); show(res.rows, res.q);
    }
    root.addEventListener('click', function (e) {
      var t = e.target;
      if (t.classList.contains('ktpw-tab')) {
        root.querySelectorAll('.ktpw-tab').forEach(function (b) { b.setAttribute('aria-selected', b === t ? 'true' : 'false'); });
        root.querySelectorAll('[data-pane]').forEach(function (p) { p.hidden = p.getAttribute('data-pane') !== t.getAttribute('data-m'); });
        out.innerHTML = '';
      } else if (t.getAttribute('data-act') === 'pick') runPick();
      else if (t.getAttribute('data-act') === 'text') runText();
      else if (t.classList.contains('ktpw-chip')) { field('q').value = t.textContent; runText(); }
    });
    root.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter') return;
      if (e.target === field('q')) runText(); else if (e.target === field('dia')) runPick();
    });
    field('shape').addEventListener('change', function () { if (this.value === '드릴') { field('blade').value = '2'; field('part').value = '밑날'; } });
  }

  function init() {
    if (!document.getElementById('ktpw-style')) { var st = document.createElement('style'); st.id = 'ktpw-style'; st.textContent = CSS; document.head.appendChild(st); }
    document.querySelectorAll('#kt-price-widget, [data-kt-price-widget]').forEach(mount);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
