/* =====================================================
   dashboard.js — 재연마 현황판 전용 스크립트
   의존성: Chart.js (CDN), portal.js, inline SHIPPINGS/daily 변수
   최종 수정: 2026-06-15
   ===================================================== */

// ── 상수 ─────────────────────────────────────────────
var COLORS = [
  '#1A3A6B','#34a853','#fbbc04','#ea4335',
  '#9c27b0','#00acc1','#ff7043','#43a047',
  '#8d6e63','#546e7a','#bdbdbd'
];
var TOP_N = 10;

// ── KPI 렌더링 ────────────────────────────────────────
(function renderKPI() {
  var grid = document.getElementById('kpi-grid');
  if (!daily) { grid.innerHTML = '<div style="color:#aaa;padding:20px">생산일지 데이터 없음</div>'; return; }
  function secToHM(sec) {
    if (!sec) return '-';
    var h = Math.floor(sec/3600), m = Math.round((sec%3600)/60);
    return h > 0 ? h+'h '+m+'m' : m+'m';
  }
  var cards = [
    { cls:'',      label:'FAST GRIND — 오늘 수량', value: daily.fast.qty,  unit:'개', sub:'가동: '+secToHM(daily.fast.time_sec) },
    { cls:'gx7',   label:'GX7 — 오늘 수량',        value: daily.gx7.qty,   unit:'개', sub:'가동: '+secToHM(daily.gx7.time_sec) },
    { cls:'total', label:'합계 — 오늘 수량',        value: daily.total.qty, unit:'개', sub:'가동: '+secToHM(daily.total.time_sec) },
    { cls:'cum',   label:'월 누계 ('+daily.cumulative.work_days+'일 실적)',
       value: daily.cumulative.total, unit:'개',
       sub:'FAST '+daily.cumulative.fast.toLocaleString()+' / GX7 '+daily.cumulative.gx7.toLocaleString() },
  ];
  grid.innerHTML = cards.map(function(c) {
    return '<div class="kpi-card '+c.cls+'">'
      +'<div class="kpi-label">'+c.label+'</div>'
      +'<div class="kpi-value">'+c.value+'<span class="kpi-unit">'+c.unit+'</span></div>'
      +(c.sub ? '<div class="kpi-sub">'+c.sub+'</div>' : '')
      +'</div>';
  }).join('');
})();

// ── 차트 + 테이블 렌더링 ──────────────────────────────
function renderSection(data, canvasId, subId, tableId) {
  var months = data.months, customers = data.customers;
  var top    = customers.slice(0, TOP_N);
  var others = customers.slice(TOP_N);

  var datasets = top.map(function(c, i) {
    return { label: c.name, data: c.monthly, backgroundColor: COLORS[i % COLORS.length],
             stack:'stack', borderWidth:0, borderRadius:2 };
  });
  if (others.length > 0) {
    var om = months.map(function(_, mi) {
      return others.reduce(function(s,c){ return s+(c.monthly[mi]||0); }, 0);
    });
    datasets.push({ label:'기타 ('+others.length+'개사)', data:om,
      backgroundColor: COLORS[COLORS.length-1], stack:'stack', borderWidth:0, borderRadius:2 });
  }

  var monthTotals = months.map(function(_, mi) {
    return customers.reduce(function(s,c){ return s+(c.monthly[mi]||0); }, 0);
  });
  var grandTotal = monthTotals.reduce(function(a,b){ return a+b; }, 0);
  document.getElementById(subId).textContent =
    '연간 합계 '+grandTotal.toLocaleString()+'개 | 납품처 '+customers.length+'개사';

  new Chart(document.getElementById(canvasId).getContext('2d'), {
    type:'bar',
    data:{ labels:months, datasets:datasets },
    options:{
      responsive:true, maintainAspectRatio:false,
      interaction:{ mode:'index', intersect:false },
      plugins:{
        legend:{ position:'bottom', labels:{ font:{size:11}, padding:10, boxWidth:12 } },
        tooltip:{ callbacks:{ footer:function(items) {
          return '월합계: '+monthTotals[items[0].dataIndex].toLocaleString()+'개';
        }}}
      },
      scales:{
        x:{ stacked:true, grid:{display:false} },
        y:{ stacked:true, beginAtZero:true,
            ticks:{ callback:function(v){ return v.toLocaleString(); } },
            grid:{ color:'#f0f0f0' } },
      },
    },
  });

  var rankCls = function(i){ return i===0?'gold':i===1?'silver':i===2?'bronze':''; };
  var colMax  = months.map(function(_, mi) {
    return Math.max.apply(null, top.map(function(c){ return c.monthly[mi]||0; }));
  });
  document.querySelector('#'+tableId+' thead tr').innerHTML =
    '<th>순위</th><th>납품처</th>' +
    months.map(function(m){ return '<th>'+m+'</th>'; }).join('') +
    '<th>연간합계</th>';

  var rows = top.map(function(c, i) {
    var cells = c.monthly.map(function(val, mi) {
      var cls = val===0 ? 'zero' : val===colMax[mi] ? 'hi' : '';
      return '<td class="'+cls+'">'+(val===0 ? '-' : val.toLocaleString())+'</td>';
    }).join('');
    return '<tr><td><span class="rank-badge '+rankCls(i)+'">'+(i+1)+'</span></td>'
      +'<td title="'+c.name+'">'+c.name+'</td>'+cells
      +'<td><strong>'+c.total.toLocaleString()+'</strong></td></tr>';
  });
  if (others.length > 0) {
    var om2 = months.map(function(_,mi) {
      return others.reduce(function(s,c){ return s+(c.monthly[mi]||0); }, 0);
    });
    var ot = om2.reduce(function(a,b){ return a+b; }, 0);
    rows.push('<tr><td><span class="rank-badge" style="background:#eee;color:#999">기타</span></td>'
      +'<td>'+others.length+'개사 합산</td>'
      +om2.map(function(v){ return '<td class="'+(v===0?'zero':'')+'">'+(v===0?'-':v.toLocaleString())+'</td>'; }).join('')
      +'<td><strong>'+ot.toLocaleString()+'</strong></td></tr>');
  }
  var tcells = monthTotals.map(function(v){ return '<td>'+v.toLocaleString()+'</td>'; }).join('');
  rows.push('<tr><td colspan="2">합계</td>'+tcells+'<td>'+grandTotal.toLocaleString()+'</td></tr>');
  document.querySelector('#'+tableId+' tbody').innerHTML = rows.join('');
}

// ── 연도 탭 초기화 ────────────────────────────────────
var tabBar    = document.getElementById('tab-bar');
var tabPanels = document.getElementById('tab-panels');

SHIPPINGS.forEach(function(item, idx) {
  var year = item[0], data = item[1];
  var panelId = 'tab'+year;

  var btn = document.createElement('button');
  btn.className = 'tab-btn' + (idx===0 ? ' active' : '');
  btn.textContent = year+'년';
  btn.onclick = function(){ switchTab(panelId, btn); };
  tabBar.appendChild(btn);

  var panel = document.createElement('div');
  panel.className = 'tab-panel' + (idx===0 ? ' active' : '');
  panel.id = panelId;
  panel.innerHTML =
    '<div class="chart-sub" id="chart-sub-'+year+'"></div>'
    +'<div class="chart-wrap"><canvas id="chart'+year+'"></canvas></div>'
    +'<div class="table-wrap"><table id="table'+year+'"><thead><tr></tr></thead><tbody></tbody></table></div>';
  tabPanels.appendChild(panel);

  renderSection(data, 'chart'+year, 'chart-sub-'+year, 'table'+year);
});

function switchTab(panelId, btn) {
  document.querySelectorAll('.tab-panel').forEach(function(p){ p.classList.remove('active'); });
  document.querySelectorAll('.tab-btn').forEach(function(b){ b.classList.remove('active'); });
  document.getElementById(panelId).classList.add('active');
  btn.classList.add('active');
}

// ── 접수현황 탭 ───────────────────────────────────────
var formTabNames = ['재연마의뢰','불량신고','진행문의','소모품요청'];
var formTabIcons = ['🔧','⚠️','💬','📦'];
var activeFormTab = 0;

(function initFormTabs() {
  var bar    = document.getElementById('form-tab-bar');
  var panels = document.getElementById('form-tab-panels');
  formTabNames.forEach(function(name, i) {
    var btn = document.createElement('button');
    btn.className = 'sub-tab-btn' + (i===0 ? ' active' : '');
    btn.id = 'ftab-btn-'+i;
    btn.innerHTML = formTabIcons[i]+' '+name+' <span class="badge" id="ftab-cnt-'+i+'">—</span>';
    btn.onclick = (function(idx){ return function(){ switchFormTab(idx); }; })(i);
    bar.appendChild(btn);

    var panel = document.createElement('div');
    panel.className = 'sub-tab-panel' + (i===0 ? ' active' : '');
    panel.id = 'ftab-panel-'+i;
    panel.innerHTML = '<div class="no-data">불러오는 중...</div>';
    panels.appendChild(panel);
  });
  loadSubmissions();
  setInterval(loadSubmissions, 30000);
})();

function switchFormTab(idx) {
  activeFormTab = idx;
  document.querySelectorAll('.sub-tab-btn').forEach(function(b,i){
    b.classList.toggle('active', i===idx);
  });
  document.querySelectorAll('.sub-tab-panel').forEach(function(p,i){
    p.classList.toggle('active', i===idx);
  });
}

function loadSubmissions() {
  fetch('/api/form-submissions')
    .then(function(r){ return r.json(); })
    .then(function(res) {
      if (!res.ok) {
        document.getElementById('refresh-info').textContent = '오류: ' + res.error;
        return;
      }
      document.getElementById('refresh-info').textContent =
        '최종 갱신: ' + res.fetched_at + ' (30초 자동갱신)';
      formTabNames.forEach(function(name, i) {
        var tab = res.data[name];
        if (!tab) return;
        var cnt = tab.rows ? tab.rows.length : 0;
        document.getElementById('ftab-cnt-'+i).textContent = cnt;
        renderFormTable(i, tab.headers, tab.rows);
      });
    })
    .catch(function() {
      document.getElementById('refresh-info').textContent = '서버 연결 필요 (Flask 실행 중이어야 합니다)';
    });
}

function renderFormTable(idx, headers, rows) {
  var panel = document.getElementById('ftab-panel-'+idx);
  if (!rows || rows.length === 0) {
    panel.innerHTML = '<div class="no-data">접수 내역이 없습니다</div>';
    return;
  }
  var html = '<div style="overflow-x:auto"><table class="form-table"><thead><tr>';
  headers.forEach(function(h) { html += '<th>'+h+'</th>'; });
  html += '</tr></thead><tbody>';
  rows.forEach(function(row) {
    html += '<tr>';
    headers.forEach(function(_, ci) {
      var v = row[ci] || '';
      html += '<td title="'+v+'">'+v+'</td>';
    });
    html += '</tr>';
  });
  html += '</tbody></table></div>';
  panel.innerHTML = html;
}
