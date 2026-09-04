import sys, io, os, json, hashlib, subprocess, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import openpyxl, xlrd, requests
from datetime import datetime, date, timedelta

# 2026-07-07: 16:00 정기 실행만 30분+ 소요되는 병목 조사용 타임스탬프 로깅.
# run.log에 단계별 시각(HH:MM:SS)과 시작 시점부터의 누적 경과(+Ns)를 남겨
# 어느 단계(파싱/페이지생성/git add/commit/push)가 느려지는지 다음 16:00 실행에서 특정한다.
# 관련: wiki/_handoff/tasks.md "16:00 정기 실행만 30분+ 소요되는 원인 조사" (P1)
_START_TS = time.time()


def _log(msg):
    elapsed = time.time() - _START_TS
    print(f'[{datetime.now().strftime("%H:%M:%S")} +{elapsed:7.1f}s] {msg}')

# .env 파일 로드 (python-dotenv 설치된 경우. 없으면 시스템 환경변수 사용)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── 설정 ──────────────────────────────────────────────────────────────────────
# 2026-05-11 보안 정리: 하드코딩되어 있던 토큰·비밀번호를 환경변수로 분리.
# 값은 .env 파일 또는 시스템 환경변수에서 로드. (.env.example 참조)
# 관련: SECURITY_NOTES.md, wiki/_handoff/decisions.md 2026-05-11 항목
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USER  = os.getenv('GITHUB_USER', 'HanKyungJun')
GITHUB_REPO  = os.getenv('GITHUB_REPO', 'koreatooling-portal')
STAFF_PASS   = os.getenv('STAFF_PASS', '1234')  # 화면 보호용 임시 비밀번호 — 실제 인증·권한 아님
SHOW_STAFF   = os.getenv('SHOW_STAFF', 'True').lower() == 'true'

# 필수 환경변수 체크 (--local 모드가 아닐 때만 GitHub 토큰 필요)
if '--local' not in sys.argv and not GITHUB_TOKEN:
    raise SystemExit(
        "⚠️ GITHUB_TOKEN 환경변수가 필요합니다.\n"
        "   .env 파일을 만들어 GITHUB_TOKEN=... 형식으로 설정하세요.\n"
        "   템플릿: .env.example 참조.\n"
        "   GitHub 업로드 없이 로컬 파일만 생성하려면 --local 플래그를 사용하세요."
    )

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
COMP_DIR    = os.path.join(BASE_DIR, 'wiki', 'comparisons')
WORKLOG_DIR = os.path.join(BASE_DIR, 'raw', '출하현황')
DIST_DIR    = os.path.join(BASE_DIR, 'dist')

# ── 사내 전용 출력 (2026-09-04 신설) ──────────────────────────────────────────
#   공개(GitHub Pages)와 사내(LAN 공유폴더)를 분리하기 위한 두 번째 출력 경로.
#   LAN 안에 있다는 것 자체가 접근 통제이므로 별도 인증이 필요 없다.
#   ⚠️ 서버가 꺼져 있거나 권한이 없어도 전체 파이프라인은 계속 진행해야 한다.
#      (매일 16:00 자동 실행이 이 한 줄 때문에 멈추면 안 된다)
INTERNAL_DIR = os.getenv(
    'INTERNAL_DIR',
    r'\\192.168.0.252\ToolKorea\생산팀\4.AI 자료실\현황판')
INTERNAL_ENABLED = os.getenv('INTERNAL_ENABLED', 'True').lower() == 'true'

# 사내 전용 정적 자산(css/js/html). dist/ 에 두지 않는다 = GitHub Pages 로 안 나간다.
INTERNAL_ASSET_DIR = os.path.join(BASE_DIR, 'internal')

# 사내 전용 파일명. dist/ 나 루트로 내보내지 않는다(= GitHub Pages 로 안 나감).
INTERNAL_ONLY = {
    'dashboard.html', 'dashboard.css', 'dashboard.js',
    'field-record.html', 'field-record.css', 'field-record.js',
    'supplies.html',          # 2026-09-04 미사용 확인 — 생성 중단
}

YEARS = [2026, 2025, 2024, 2023, 2022]


# ── 파싱 ──────────────────────────────────────────────────────────────────────
def parse_shipping(filepath):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb['요약']
    months = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']
    customers = []
    for row in ws.iter_rows(min_row=3, values_only=True):
        if not row[1]:
            break
        monthly = [row[i + 2] or 0 for i in range(12)]
        customers.append({'name': row[1], 'monthly': monthly, 'total': sum(monthly)})
    customers.sort(key=lambda x: x['total'], reverse=True)
    return {'months': months, 'customers': customers}


def parse_worklog():
    today = datetime.now()
    year, month, day = today.year, today.month, today.day
    path = os.path.join(WORKLOG_DIR,
                        f'재연마 작업일지({year})',
                        f'재연마_월간생산일지 ({month}월).xls')
    if not os.path.exists(path):
        return None, None

    wb = xlrd.open_workbook(path)
    ws = wb.sheet_by_index(0)

    today_row = None
    fast_cum = gx7_cum = fast_t_cum = gx7_t_cum = work_days = 0

    for i in range(2, ws.nrows):
        row = ws.row_values(i)
        try:
            d = int(row[0])
        except (ValueError, TypeError):
            break
        fast_qty  = int(row[1] or 0)
        fast_time = int(row[3] or 0)
        gx7_qty   = int(row[7] or 0)
        gx7_time  = int(row[9] or 0)
        if d <= day:
            fast_cum   += fast_qty;  gx7_cum    += gx7_qty
            fast_t_cum += fast_time; gx7_t_cum  += gx7_time
            if fast_qty > 0 or gx7_qty > 0:
                work_days += 1
        if d == day:
            today_row = {'fast_qty': fast_qty, 'fast_time': fast_time,
                         'gx7_qty': gx7_qty,   'gx7_time': gx7_time}

    if today_row is None:
        today_row = {'fast_qty': 0, 'fast_time': 0, 'gx7_qty': 0, 'gx7_time': 0}

    return {
        'date':       today.strftime('%Y-%m-%d'),
        'fast':       {'qty': today_row['fast_qty'],  'time_sec': today_row['fast_time']},
        'gx7':        {'qty': today_row['gx7_qty'],   'time_sec': today_row['gx7_time']},
        'total':      {'qty': today_row['fast_qty'] + today_row['gx7_qty'],
                       'time_sec': today_row['fast_time'] + today_row['gx7_time']},
        'cumulative': {'fast': fast_cum, 'gx7': gx7_cum,
                       'total': fast_cum + gx7_cum, 'work_days': work_days},
    }, f'{year}-{month:02d}-{day:02d} 재연마_월간생산일지 ({month}월)'


# ── 공통 컴포넌트 ──────────────────────────────────────────────────────────────
# CSS는 dist/portal.css 에 분리됨 (2026-06-15)
# GAS URL / 폼 제출 / 인증 로직은 dist/portal.js 에 분리됨 (2026-06-15)

# 인증 오버레이 HTML — CSS 클래스는 portal.css 에 정의되어 있음
_AUTH_HTML = """<div id="auth-overlay" class="auth-overlay">
  <div class="auth-box">
    <div class="auth-icon">🔒</div>
    <h2>직원 전용</h2>
    <p class="auth-desc">비밀번호를 입력하세요.</p>
    <input id="pass-input" type="password" placeholder="비밀번호">
    <button class="auth-btn" onclick="checkPass()">확인</button>
    <div id="pass-err" class="auth-err"></div>
    <a href="index.html" class="auth-back">← 메인으로 돌아가기</a>
  </div>
</div>"""


def _form_page(page_title, form_name, icon, header_title, fields_html, success_msg, protected=False):
    # CSS → portal.css, 폼 제출 + 인증 → portal.js (2026-06-15 분리)
    auth_block = _AUTH_HTML if protected else ''
    return ('<!DOCTYPE html>\n<html lang="ko">\n<head>\n'
            '<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '<title>' + page_title + ' — 코리아툴링</title>\n'
            '<link rel="stylesheet" href="portal.css">\n'
            '</head>\n<body>\n'
            + auth_block + '\n'
            '<header>\n'
            '  <h1>' + icon + ' ' + header_title + '</h1>\n'
            '  <a href="index.html" class="back-link">← 메인으로</a>\n'
            '</header>\n'
            '<main>\n'
            '  <div id="form-wrap" class="card">\n'
            '    <div class="card-title">' + icon + ' ' + header_title + '</div>\n'
            '    <div class="card-sub">＊ 표시는 필수 입력 항목입니다.</div>\n'
            '    <form name="' + form_name + '" method="POST">\n'
            '      <input type="hidden" name="form-name" value="' + form_name + '">\n'
            + fields_html + '\n'
            '      <button type="submit" class="submit-btn">제출하기 →</button>\n'
            '    </form>\n'
            '  </div>\n'
            '  <div id="success" style="display:none" class="card">\n'
            '    <div class="success-box">\n'
            '      <div class="icon">✅</div>\n'
            '      <h2>제출이 완료되었습니다</h2>\n'
            '      <p>' + success_msg + '</p>\n'
            '      <a href="index.html" class="home-btn">메인으로 돌아가기</a>\n'
            '    </div>\n'
            '  </div>\n'
            '</main>\n'
            '<footer>© 2026 코리아툴링 | Korea Tooling Co., Ltd.</footer>\n'
            '<iframe name="hidden-target" style="display:none;"></iframe>\n'
            '<script src="portal.js"></script>\n'
            '</body>\n</html>')


# ── 포털 메인 ──────────────────────────────────────────────────────────────────
def build_portal_html(show_staff: bool = None):
    """포털 index. show_staff=False 면 직원 전용 구역이 통째로 빠진다.

    2026-09-04: 공개(GitHub Pages) / 사내(LAN) 분리를 위해 인자화.
      공개용 → show_staff=False   사내용 → show_staff=True
    """
    if show_staff is None:
        show_staff = SHOW_STAFF
    staff_section = ("""
  <button class="staff-toggle" onclick="showStaffAuth()">🔒 직원 전용</button>

  <!-- 비밀번호 모달 -->
  <div id="staff-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:100;display:none;align-items:center;justify-content:center;">
    <div style="background:white;border-radius:16px;padding:32px 28px;width:320px;max-width:90vw;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
      <div style="font-size:2rem;margin-bottom:10px;">🔒</div>
      <h2 style="color:#1A3A6B;font-size:1rem;margin-bottom:6px;">직원 전용</h2>
      <p style="color:#999;font-size:0.78rem;margin-bottom:18px;">비밀번호를 입력하세요.</p>
      <input id="staff-pass-input" type="password" placeholder="비밀번호"
        style="width:100%;padding:10px 14px;border:1.5px solid #ddd;border-radius:8px;font-size:0.95rem;margin-bottom:10px;outline:none;text-align:center;"
        onkeydown="if(event.key==='Enter') checkStaffPass()">
      <p id="staff-pass-error" style="color:#e53935;font-size:0.78rem;min-height:18px;margin-bottom:8px;"></p>
      <button onclick="checkStaffPass()"
        style="width:100%;padding:11px;background:#1A3A6B;color:white;border:none;border-radius:8px;font-size:0.9rem;font-weight:700;cursor:pointer;margin-bottom:8px;">
        확인
      </button>
      <button onclick="closeStaffModal()"
        style="width:100%;padding:9px;background:none;border:1px solid #ddd;border-radius:8px;font-size:0.85rem;color:#aaa;cursor:pointer;">
        취소
      </button>
    </div>
  </div>

  <div id="staff-section" style="display:none">
    <div class="sec-label" style="margin-top:16px">🔒 직원 전용 <span class="staff-badge">PASSWORD</span></div>
    <div class="grid">
      <a class="card staff" href="dashboard.html">
        <div class="card-icon">📊</div>
        <div class="card-title">재연마 현황판</div>
        <div class="card-desc">출하현황 및 일일 생산 실적을 확인합니다.</div>
      </a>
      <a class="card staff" href="field-record.html">
        <div class="card-icon">📝</div>
        <div class="card-title">현장 기록</div>
        <div class="card-desc">가공 테스트 결과 및 불량 현황을 현장에서 바로 기록합니다.</div>
      </a>
    </div>
  </div>
  <script>
  function showStaffAuth() {
    var modal = document.getElementById('staff-modal');
    modal.style.display = 'flex';
    setTimeout(function(){ document.getElementById('staff-pass-input').focus(); }, 50);
  }
  function closeStaffModal() {
    document.getElementById('staff-modal').style.display = 'none';
    document.getElementById('staff-pass-input').value = '';
    document.getElementById('staff-pass-error').textContent = '';
  }
  function checkStaffPass() {
    var val = document.getElementById('staff-pass-input').value;
    if (val === '""" + STAFF_PASS + """') {
      closeStaffModal();
      document.getElementById('staff-section').style.display = 'block';
      document.querySelector('.staff-toggle').style.display = 'none';
    } else {
      document.getElementById('staff-pass-error').textContent = '비밀번호가 올바르지 않습니다.';
      document.getElementById('staff-pass-input').value = '';
      document.getElementById('staff-pass-input').focus();
    }
  }
  </script>""") if show_staff else ''

    return """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>코리아툴링 생산팀 포털</title>
  <link rel="stylesheet" href="index.css">
</head>
<body>
<header>
  <div class="co-name">Korea Tooling Co., Ltd.</div>
  <h1>생산팀 포털</h1>
  <p>서비스를 선택해 주세요</p>
</header>
<main>
  <div class="sec-label">🌐 고객 서비스</div>
  <div class="grid">
    <a class="card" href="request.html">
      <div class="card-icon">🔧</div>
      <div class="card-title">재연마 의뢰 접수</div>
      <div class="card-desc">공구 재연마를 의뢰하고 수량·납기를 등록합니다.</div>
    </a>
    <a class="card" href="defect.html">
      <div class="card-icon">⚠️</div>
      <div class="card-title">공구 불량 신고</div>
      <div class="card-desc">불량 공구의 증상 및 발생 현황을 신고합니다.</div>
    </a>
    <a class="card" href="inquiry.html">
      <div class="card-icon">📋</div>
      <div class="card-title">작업 진행 문의</div>
      <div class="card-desc">의뢰한 공구의 진행 현황을 문의합니다.</div>
    </a>
    <a class="card" href="절삭조건-검색.html">
      <div class="card-icon">⚙️</div>
      <div class="card-title">절삭 조건 검색</div>
      <div class="card-desc">JJ · COGO 카탈로그 기준 절삭 조건을 검색합니다.</div>
    </a>
  </div>
""" + staff_section + """
</main>
<footer>© 2026 코리아툴링 생산팀 포털 | Korea Tooling Co., Ltd.</footer>
</body>
</html>"""


# ── 폼 페이지들 ────────────────────────────────────────────────────────────────
def build_request_html():
    fields = """
      <div class="row2">
        <div class="field">
          <label>회사명 <span class="req">＊</span></label>
          <input type="text" name="company" placeholder="예) 코리아툴링" required>
        </div>
        <div class="field">
          <label>담당자 <span class="req">＊</span></label>
          <input type="text" name="contact" placeholder="이름" required>
        </div>
      </div>
      <div class="row2">
        <div class="field">
          <label>연락처 <span class="req">＊</span></label>
          <input type="tel" name="phone" placeholder="010-0000-0000" required>
        </div>
        <div class="field">
          <label>이메일</label>
          <input type="email" name="email" placeholder="example@email.com">
        </div>
      </div>
      <div class="row2">
        <div class="field">
          <label>공구 종류 <span class="req">＊</span></label>
          <select name="tool_type" required>
            <option value="">선택하세요</option>
            <option>엔드밀</option>
            <option>드릴</option>
            <option>리머</option>
            <option>탭</option>
            <option>기타</option>
          </select>
        </div>
        <div class="field">
          <label>재질</label>
          <select name="material">
            <option value="">선택하세요</option>
            <option>초경</option>
            <option>HSS</option>
            <option>SKD</option>
            <option>기타</option>
          </select>
        </div>
      </div>
      <div class="field">
        <label>규격 / 수량 <span class="req">＊</span>
          <span style="font-weight:400;color:#aaa;font-size:0.75rem;margin-left:6px;">품종이 여러 개면 행 추가</span>
        </label>
        <div id="spec-rows">
          <div class="spec-row" style="display:grid;grid-template-columns:1fr 90px 32px;gap:8px;margin-bottom:8px;">
            <input type="text" name="spec[]" placeholder="규격 (예: Ø10 4날, R0.5)" required
              style="padding:10px 13px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:0.9rem;outline:none;">
            <input type="number" name="quantity[]" placeholder="수량" min="1" required
              style="padding:10px 13px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:0.9rem;outline:none;text-align:center;">
            <button type="button" onclick="removeRow(this)"
              style="background:#fff0f0;color:#e53935;border:1.5px solid #ffd0d0;border-radius:8px;font-size:1.1rem;cursor:pointer;display:none;">✕</button>
          </div>
        </div>
        <button type="button" onclick="addSpecRow()"
          style="margin-top:4px;padding:8px 16px;background:#f0f4ff;color:#1A3A6B;border:1.5px dashed #b0c4f0;border-radius:8px;font-size:0.82rem;font-weight:600;cursor:pointer;">
          + 규격 추가
        </button>
      </div>
      <div class="field">
        <label>특이사항 / 요청사항</label>
        <textarea name="notes" placeholder="재연마 특이사항, 요청사항을 입력해주세요."></textarea>
      </div>
      <div class="field">
        <label>도면 / 사진 첨부 <span style="font-weight:400;color:#aaa;font-size:0.75rem">(선택 · 최대 5MB)</span></label>
        <label class="file-drop" for="attach-input" id="file-drop-zone">
          <span id="file-drop-text">📎 클릭하거나 파일을 드래그하세요<br>
          <span style="font-size:0.75rem;color:#bbb">JPG · PNG · PDF · DWG · DXF</span></span>
        </label>
        <input type="file" id="attach-input" accept="image/*,.pdf,.dwg,.dxf" style="display:none">
        <input type="hidden" name="file-data" id="file-data">
        <input type="hidden" name="file-name" id="file-name">
        <input type="hidden" name="file-type" id="file-type">
      </div>"""
    return (_form_page(
        '재연마 의뢰 접수', 'request-form', '🔧', '재연마 의뢰 접수',
        fields,
        '담당자가 확인 후 연락드리겠습니다.<br>감사합니다.')
    + """<script>
function addSpecRow() {
  var container = document.getElementById('spec-rows');
  var row = document.createElement('div');
  row.className = 'spec-row';
  row.style.cssText = 'display:grid;grid-template-columns:1fr 90px 32px;gap:8px;margin-bottom:8px;';
  row.innerHTML = '<input type="text" name="spec[]" placeholder="규격 (예: Ø10 4날, R0.5)"'
    + ' style="padding:10px 13px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:0.9rem;outline:none;">'
    + '<input type="number" name="quantity[]" placeholder="수량" min="1"'
    + ' style="padding:10px 13px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:0.9rem;outline:none;text-align:center;">'
    + '<button type="button" onclick="removeRow(this)"'
    + ' style="background:#fff0f0;color:#e53935;border:1.5px solid #ffd0d0;border-radius:8px;font-size:1.1rem;cursor:pointer;">✕</button>';
  container.appendChild(row);
  updateRemoveButtons();
  row.querySelector('input').focus();
}
function removeRow(btn) {
  btn.closest('.spec-row').remove();
  updateRemoveButtons();
}
function updateRemoveButtons() {
  var rows = document.querySelectorAll('.spec-row');
  rows.forEach(function(r, i) {
    r.querySelector('button').style.display = rows.length > 1 ? '' : 'none';
  });
}

// ── 파일 첨부 ─────────────────────────────────────────────────────────────────
var dropZone = document.getElementById('file-drop-zone');
document.getElementById('attach-input').addEventListener('change', function(e) {
  handleAttach(e.target.files[0]);
});
dropZone.addEventListener('dragover', function(e) {
  e.preventDefault(); dropZone.style.borderColor = '#1A3A6B';
});
dropZone.addEventListener('dragleave', function() {
  dropZone.style.borderColor = '';
});
dropZone.addEventListener('drop', function(e) {
  e.preventDefault(); dropZone.style.borderColor = '';
  handleAttach(e.dataTransfer.files[0]);
});
function handleAttach(file) {
  if (!file) return;
  if (file.size > 5 * 1024 * 1024) {
    alert('파일 크기는 5MB 이하로 첨부해 주세요.');
    return;
  }
  var reader = new FileReader();
  reader.onload = function(ev) {
    document.getElementById('file-data').value = ev.target.result;
    document.getElementById('file-name').value = file.name;
    document.getElementById('file-type').value = file.type;
    document.getElementById('file-drop-text').innerHTML =
      '✅ ' + file.name + '<br><span style="font-size:0.75rem;color:#888">'
      + (file.size/1024).toFixed(0) + 'KB · 클릭해서 변경</span>';
    dropZone.classList.add('has-file');
  };
  reader.readAsDataURL(file);
}
</script>"""
    )


def build_defect_html():
    fields = """
      <div class="row2">
        <div class="field">
          <label>회사명 <span class="req">＊</span></label>
          <input type="text" name="company" placeholder="예) 코리아툴링" required>
        </div>
        <div class="field">
          <label>담당자 <span class="req">＊</span></label>
          <input type="text" name="contact" placeholder="이름" required>
        </div>
      </div>
      <div class="row2">
        <div class="field">
          <label>연락처 <span class="req">＊</span></label>
          <input type="tel" name="phone" placeholder="010-0000-0000" required>
        </div>
        <div class="field">
          <label>발생 일자 <span class="req">＊</span></label>
          <input type="date" name="defect_date" required>
        </div>
      </div>
      <div class="field">
        <label>공구명 / 규격 <span class="req">＊</span>
          <span style="font-weight:400;color:#aaa;font-size:0.75rem;margin-left:6px;">품종이 여러 개면 행 추가</span>
        </label>
        <div id="defect-rows">
          <div class="defect-row" style="display:grid;grid-template-columns:1fr 90px 32px;gap:8px;margin-bottom:8px;">
            <input type="text" name="tool_spec[]" placeholder="공구명/규격 (예: 초경 엔드밀 Ø10, 4날)" required
              style="padding:10px 13px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:0.9rem;outline:none;">
            <input type="number" name="defect_qty[]" placeholder="수량" min="1" required
              style="padding:10px 13px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:0.9rem;outline:none;text-align:center;">
            <button type="button" onclick="removeDefectRow(this)"
              style="background:#fff0f0;color:#e53935;border:1.5px solid #ffd0d0;border-radius:8px;font-size:1.1rem;cursor:pointer;display:none;">✕</button>
          </div>
        </div>
        <button type="button" onclick="addDefectRow()"
          style="margin-top:4px;padding:8px 16px;background:#f0f4ff;color:#1A3A6B;border:1.5px dashed #b0c4f0;border-radius:8px;font-size:0.82rem;font-weight:600;cursor:pointer;">
          + 규격 추가
        </button>
      </div>
      <div class="field">
        <label>불량 증상 <span class="req">＊</span></label>
        <div class="check-group">
          <label class="check-item"><input type="checkbox" name="symptom" value="치핑"> 치핑</label>
          <label class="check-item"><input type="checkbox" name="symptom" value="파손"> 파손</label>
          <label class="check-item"><input type="checkbox" name="symptom" value="치수불량"> 치수 불량</label>
          <label class="check-item"><input type="checkbox" name="symptom" value="코팅불량"> 코팅 불량</label>
          <label class="check-item"><input type="checkbox" name="symptom" value="수명단축"> 수명 단축</label>
          <label class="check-item"><input type="checkbox" name="symptom" value="기타"> 기타</label>
        </div>
      </div>
      <div class="field">
        <label>피삭재 / 사용 환경</label>
        <input type="text" name="workpiece" placeholder="예) SUS304, 건식">
      </div>
      <div class="field">
        <label>불량 상세 내용 <span class="req">＊</span></label>
        <textarea name="detail" placeholder="불량 발생 경위, 사용 조건(회전수/이송) 등 상세히 기재해주세요." required></textarea>
      </div>"""
    return (_form_page(
        '공구 불량 신고', 'defect-form', '⚠️', '공구 불량 신고',
        fields,
        '불량 내용을 접수하였습니다.<br>빠른 시일 내에 확인 후 연락드리겠습니다.')
    + """<script>
function addDefectRow() {
  var container = document.getElementById('defect-rows');
  var row = document.createElement('div');
  row.className = 'defect-row';
  row.style.cssText = 'display:grid;grid-template-columns:1fr 90px 32px;gap:8px;margin-bottom:8px;';
  row.innerHTML = '<input type="text" name="tool_spec[]" placeholder="공구명/규격 (예: 초경 엔드밀 Ø10, 4날)"'
    + ' style="padding:10px 13px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:0.9rem;outline:none;">'
    + '<input type="number" name="defect_qty[]" placeholder="수량" min="1"'
    + ' style="padding:10px 13px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:0.9rem;outline:none;text-align:center;">'
    + '<button type="button" onclick="removeDefectRow(this)"'
    + ' style="background:#fff0f0;color:#e53935;border:1.5px solid #ffd0d0;border-radius:8px;font-size:1.1rem;cursor:pointer;">✕</button>';
  container.appendChild(row);
  updateDefectButtons();
  row.querySelector('input').focus();
}
function removeDefectRow(btn) {
  btn.closest('.defect-row').remove();
  updateDefectButtons();
}
function updateDefectButtons() {
  var rows = document.querySelectorAll('.defect-row');
  rows.forEach(function(r) {
    r.querySelector('button').style.display = rows.length > 1 ? '' : 'none';
  });
}
</script>"""
    )


def build_inquiry_html():
    fields = """
      <div class="row2">
        <div class="field">
          <label>회사명 <span class="req">＊</span></label>
          <input type="text" name="company" placeholder="예) 코리아툴링" required>
        </div>
        <div class="field">
          <label>담당자 <span class="req">＊</span></label>
          <input type="text" name="contact" placeholder="이름" required>
        </div>
      </div>
      <div class="row2">
        <div class="field">
          <label>연락처 <span class="req">＊</span></label>
          <input type="tel" name="phone" placeholder="010-0000-0000" required>
        </div>
        <div class="field">
          <label>의뢰 납기 / 참고 일자</label>
          <input type="text" name="ref_date" placeholder="예) 2026-04-30">
        </div>
      </div>
      <div class="field">
        <label>문의 내용 <span class="req">＊</span></label>
        <textarea name="inquiry" placeholder="공구명·수량·납기 등 진행 현황을 문의할 내용을 입력해주세요." style="min-height:120px;" required></textarea>
      </div>"""
    return _form_page(
        '작업 진행 문의', 'inquiry-form', '📋', '작업 진행 문의',
        fields,
        '문의를 접수하였습니다.<br>담당자가 확인 후 신속히 연락드리겠습니다.')


def build_supplies_html():
    fields = """
      <div class="row2">
        <div class="field">
          <label>요청자 <span class="req">＊</span></label>
          <input type="text" name="requester" placeholder="이름" required>
        </div>
        <div class="field">
          <label>부서 <span class="req">＊</span></label>
          <select name="department" required>
            <option value="">선택하세요</option>
            <option>생산팀</option>
            <option>품질팀</option>
            <option>관리팀</option>
            <option>기타</option>
          </select>
        </div>
      </div>
      <div class="field">
        <label>품목명 <span class="req">＊</span></label>
        <input type="text" name="item_name" placeholder="예) 절삭유, 연마석, 측정기" required>
      </div>
      <div class="row2">
        <div class="field">
          <label>규격 / 사양</label>
          <input type="text" name="item_spec" placeholder="예) 100L, #120">
        </div>
        <div class="field">
          <label>수량 <span class="req">＊</span></label>
          <input type="number" name="quantity" placeholder="개/L/m" min="1" required>
        </div>
      </div>
      <div class="field">
        <label>희망 납기</label>
        <input type="date" name="due_date">
      </div>
      <div class="field">
        <label>용도 / 사유 <span class="req">＊</span></label>
        <textarea name="reason" placeholder="구매가 필요한 이유와 용도를 기재해주세요." required></textarea>
      </div>
      <div class="field">
        <label class="check-item" style="font-size:0.88rem;cursor:pointer;">
          <input type="checkbox" name="urgent" value="Y" style="width:auto;accent-color:#c0392b;">
          &nbsp;긴급 요청 (즉시 처리 필요)
        </label>
      </div>"""
    return _form_page(
        '소모품 구매 요청', 'supplies-form', '🛒', '소모품 구매 요청',
        fields,
        '구매 요청이 접수되었습니다.<br>확인 후 처리하겠습니다.',
        protected=True)


# ── 현황판 ─────────────────────────────────────────────────────────────────────
def build_dashboard_html(shippings, daily, worklog_date, generated_at, todo=None):
    shipping_js = ',\n'.join(
        f'  [{y}, {json.dumps(d, ensure_ascii=False)}]' for y, d in shippings
    )
    daily_json = json.dumps(daily, ensure_ascii=False)

    # ── 「오늘 할 일」 블록 (2026-09-04 신설) ─────────────────────────────────
    #   현 화면은 이미 끝난 숫자만 보여준다. 앞을 보는 숫자를 맨 위에 둔다.
    #   ERP 조회 실패 시 todo=None → 블록 자체를 그리지 않는다(빈 값 표시 안 함).
    if todo:
        rows = ''
        for it in todo['detail']:
            tag = ('<span style="color:#e53935;font-weight:700">지연</span>'
                   if it['late'] else
                   '<span style="color:#f57c00;font-weight:700">임박</span>')
            rows += (f"<tr><td>{tag}</td><td>{it['dlv']}</td>"
                     f"<td>{it['cust']}</td><td>{it['itm']}</td>"
                     f"<td style=\"text-align:right\">{it['rest']:,}</td></tr>")
        if not rows:
            rows = ('<tr><td colspan="5" style="text-align:center;color:#999;padding:14px">'
                    '납기 임박·지연 건 없음</td></tr>')

        todo_html = f'''
  <div class="section-title-row">
    <span class="section-title">오늘 할 일</span>
    <span class="section-date">ERP 수주 기준 · {todo['since']} 이후</span>
  </div>
  <div class="kpi-grid">
    <div class="kpi-card" style="border-left:4px solid #e53935">
      <div class="kpi-label">🔴 납기 지연 — 미출하</div>
      <div class="kpi-value">{todo['late_cases']}<span class="kpi-unit">건</span></div>
      <div class="kpi-sub">{todo['late_qty']:,}개</div>
    </div>
    <div class="kpi-card" style="border-left:4px solid #f57c00">
      <div class="kpi-label">🟡 납기 임박 (D-3 이내)</div>
      <div class="kpi-value">{todo['near_cases']}<span class="kpi-unit">건</span></div>
      <div class="kpi-sub">{todo['near_qty']:,}개</div>
    </div>
    <div class="kpi-card" style="border-left:4px solid #1A3A6B">
      <div class="kpi-label">📦 미출하 잔량 전체</div>
      <div class="kpi-value">{todo['open_qty']:,}<span class="kpi-unit">개</span></div>
      <div class="kpi-sub">{todo['open_cases']}건</div>
    </div>
  </div>
  <div class="section-card">
    <div class="chart-title">납기 임박·지연 상세 <span style="font-size:0.78rem;color:#aaa;font-weight:400">(납기 빠른 순, 최대 12건)</span></div>
    <div style="overflow-x:auto">
      <table class="form-table">
        <thead><tr><th>구분</th><th>납기</th><th>거래처</th><th>품목</th><th style="text-align:right">잔량</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>
'''
    else:
        todo_html = ''

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>재연마 현황판 — 코리아툴링</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <link rel="stylesheet" href="portal.css">
  <link rel="stylesheet" href="dashboard.css">
</head>
<body>

{_AUTH_HTML}

<header>
  <a href="index.html" class="back-link">← 포털</a>
  <div>
    <h1>📊 재연마 현황판</h1>
  </div>
  <div class="header-meta">
    <span>생성: {generated_at}</span>
  </div>
</header>

<main>
{todo_html}
  <div class="section-title-row">
    <span class="section-title">오늘 실적</span>
    <span class="section-date">📅 {worklog_date}</span>
  </div>
  <div class="kpi-grid" id="kpi-grid"></div>

  <div class="chart-card">
    <div class="chart-title">업체별 월간 출하현황</div>
    <div class="tab-bar" id="tab-bar"></div>
    <div id="tab-panels"></div>
  </div>

  <div class="section-card">
    <div class="chart-title">📋 접수현황 <span style="font-size:0.78rem;color:#aaa;font-weight:400">(최신순)</span></div>
    <div class="refresh-row">
      <button class="refresh-btn" onclick="loadSubmissions()">🔄 새로고침</button>
      <span class="refresh-info" id="refresh-info">—</span>
    </div>
    <div class="sub-tab-bar" id="form-tab-bar"></div>
    <div id="form-tab-panels"></div>
  </div>
</main>

<script src="portal.js"></script>
<script>
// ── 동적 데이터 (generate.py 주입) ───────────────────
var SHIPPINGS = [
{shipping_js}
];
var daily = {daily_json};
</script>
<script src="dashboard.js"></script>
</body>
</html>"""


# ── ERP 「오늘 할 일」 데이터 (2026-09-04 신설) ────────────────────────────────
def fetch_erp_todo(lookback_days: int = 120):
    """재연마 수주에서 미출하 잔량·납기 임박을 계산한다.

    사내 현황판 전용. 현재 화면은 「이미 끝난 숫자」만 보여주므로
    「앞으로 할 일」을 더한다.

    [신뢰도: 실측 검증] 2026-09-04 ERP(sdb100_jae_g10) 값을 엑셀 export 와 대조:
      엑셀 08-05~09-02  68행 / 1,164개   ERP 08-01~09-04  69행 / 1,174개
      차이 10개 = 09-03~09-04 신규 수주분과 정확히 일치. 소스 신뢰 가능.
      @f_so_bs 필터도 '01'(61건) + '10'(8건) = 69건 = 전체라 무해함을 확인.

    잔량 = so_qty - out_qty(미출하면 NaN → 0). 부분출하도 반영된다.

    ★ ERP 에 닿지 않아도(사무실 밖·서버 점검) 예외를 던지지 않는다.
      현황판 나머지와 GitHub 업로드는 그대로 진행되어야 한다.
    반환: dict 또는 None(조회 실패)
    """
    try:
        sys.path.insert(0, os.path.join(BASE_DIR, 'erp'))
        from trico_client import TricoClient
        import pandas as pd
    except Exception as e:
        _log(f'  ⚠️ ERP 모듈 로드 실패 — 「오늘 할 일」 생략: {type(e).__name__}: {e}')
        return None

    try:
        fr = (date.today() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
        df = TricoClient().수주(fr_dt=fr)
    except Exception as e:
        _log(f'  ⚠️ ERP 수주 조회 실패 — 「오늘 할 일」 생략: {str(e)[:120]}')
        _log('     (사무실 네트워크가 아니거나 ERP 점검 중일 수 있습니다)')
        return None

    if len(df) == 0:
        _log('  ⚠️ ERP 수주 0행 — 「오늘 할 일」 생략 (파라미터 확인 필요)')
        return None

    try:
        d = df.copy()
        d['so_q']  = pd.to_numeric(d['so_qty'],  errors='coerce').fillna(0)
        d['out_q'] = pd.to_numeric(d['out_qty'], errors='coerce').fillna(0)
        d['rest']  = (d['so_q'] - d['out_q']).clip(lower=0)
        d['dlv']   = pd.to_datetime(d['dlv_dt'], errors='coerce', utc=True) \
                       .dt.tz_convert('Asia/Seoul').dt.date

        open_rows = d[d['rest'] > 0]
        today     = date.today()
        d3        = today + timedelta(days=3)

        late  = open_rows[open_rows['dlv'].notna() & (open_rows['dlv'] <  today)]
        near  = open_rows[open_rows['dlv'].notna() &
                          (open_rows['dlv'] >= today) & (open_rows['dlv'] <= d3)]

        # 임박·지연 상세 (납기 빠른 순 12건)
        detail = []
        for _, r in open_rows[open_rows['dlv'].notna() &
                              (open_rows['dlv'] <= d3)].sort_values('dlv').head(12).iterrows():
            detail.append({
                'dlv':   str(r['dlv']),
                'cust':  str(r.get('cust_nm', '')),
                'itm':   str(r.get('itm_nm', ''))[:38],
                'rest':  int(r['rest']),
                'late':  bool(r['dlv'] < today),
            })

        return {
            'open_cases': int(open_rows['so_no'].nunique()),
            'open_qty':   int(open_rows['rest'].sum()),
            'late_cases': int(late['so_no'].nunique()),
            'late_qty':   int(late['rest'].sum()),
            'near_cases': int(near['so_no'].nunique()),
            'near_qty':   int(near['rest'].sum()),
            'detail':     detail,
            'since':      fr,
        }
    except Exception as e:
        _log(f'  ⚠️ 「오늘 할 일」 집계 실패: {type(e).__name__}: {e}')
        return None


# ── 사내 공유폴더 배포 ─────────────────────────────────────────────────────────
def publish_internal(pages: dict) -> bool:
    """생성된 페이지와 정적 파일을 사내 LAN 공유폴더에 한 벌 더 쓴다.

    2026-09-04 신설. 공개(GitHub Pages) / 사내(LAN) 분리의 사내 쪽.

    ★ 실패해도 예외를 밖으로 던지지 않는다.
      서버가 꺼져 있거나 네트워크가 끊겨도 GitHub 업로드와 일일보고는
      정상 진행되어야 한다. 실패는 로그로만 남긴다.
    """
    if not INTERNAL_ENABLED:
        _log('사내 배포: 비활성(INTERNAL_ENABLED=False) — 건너뜀')
        return False

    import shutil, glob
    try:
        os.makedirs(INTERNAL_DIR, exist_ok=True)
    except Exception as e:
        _log(f'  ⚠️ 사내 배포 실패 — 폴더 접근 불가: {type(e).__name__}: {e}')
        _log(f'     경로: {INTERNAL_DIR}')
        _log('     (공개 배포는 정상 진행합니다)')
        return False

    n_ok, n_fail = 0, 0
    try:
        # 생성된 HTML
        for fname, html in pages.items():
            try:
                with open(os.path.join(INTERNAL_DIR, fname), 'w', encoding='utf-8') as f:
                    f.write(html)
                n_ok += 1
            except Exception as e:
                n_fail += 1
                _log(f'  ⚠️ {fname} 쓰기 실패: {e}')

        # 정적 파일 — 공용(dist/) + 사내 전용(internal/)
        search_dirs = [DIST_DIR]
        if os.path.isdir(INTERNAL_ASSET_DIR):
            search_dirs.append(INTERNAL_ASSET_DIR)
        else:
            _log(f'  ⚠️ internal/ 폴더 없음 — 사내 전용 자산이 빠집니다: {INTERNAL_ASSET_DIR}')

        seen = set()
        for d in search_dirs:
          for ext in ('*.html', '*.css', '*.js'):
            for src in glob.glob(os.path.join(d, ext)):
                fname = os.path.basename(src)
                if fname in pages or fname in seen:
                    continue
                seen.add(fname)
                try:
                    shutil.copy2(src, os.path.join(INTERNAL_DIR, fname))
                    n_ok += 1
                except Exception as e:
                    n_fail += 1
                    _log(f'  ⚠️ {fname} 복사 실패: {e}')
    except Exception as e:
        _log(f'  ⚠️ 사내 배포 중 예외: {type(e).__name__}: {e}')
        return False

    # ★ 조용한 성공 방지 — 0건 성공을 정상으로 찍지 않는다.
    if n_ok == 0:
        _log(f'  🔴 사내 배포: 성공 0건 / 실패 {n_fail}건 — 실패로 판정')
        return False

    _log(f'  → 사내 배포 완료: {n_ok}개 파일'
         + (f' (실패 {n_fail}건)' if n_fail else ''))
    _log(f'     {INTERNAL_DIR}')
    return True


# ── GitHub Pages 업로드 ────────────────────────────────────────────────────────
# 2026-06-15: cwd를 DIST_DIR → BASE_DIR 로 변경
#   이유: 외부 CSS/JS 파일 분리 이후 루트에 portal.css, dashboard.css 등이 추가됨.
#   git add . 는 repo 루트 기준으로 실행해야 모든 파일이 포함됨.
def _mask_secret(s):
    """로그에 GITHUB_TOKEN 평문이 노출되지 않도록 마스킹.
    2026-07-07: 실제 push 실패 시 git이 원격 URL(토큰 포함)을 stderr에 그대로 반환하는
    사고가 발생해 run.log에 토큰 평문이 기록됨 — 재발 방지."""
    if not s or not GITHUB_TOKEN:
        return s
    return s.replace(GITHUB_TOKEN, '***REDACTED***')


def upload_to_github():
    git = 'git'
    env = os.environ.copy()
    # 2026-07-07: 16:00 병목 조사에서 실제 원인 확인 — 원격 URL에 토큰이 포함돼 있어도
    # Windows의 git-credential-manager가 개입해 인증을 시도하다 비대화형(Task Scheduler
    # S4U) 세션에서 프롬프트를 표시할 수 없어 17분+ 멈춘 뒤 "/dev/tty: No such device or
    # address" 오류로 실패하는 현상 확인(run.log 2026-07-07 14:21 블록). 아래 두 환경변수로
    # 자격증명 프롬프트 자체를 차단해 실패 시 즉시 오류로 반환되도록 함(더 이상 멈추지 않음).
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['GCM_INTERACTIVE'] = 'never'

    def run(cmd, cwd=BASE_DIR, timeout=60, label=None):
        t0 = time.time()
        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True,
                                    text=True, encoding='utf-8', errors='replace',
                                    env=env, timeout=timeout)
        except subprocess.TimeoutExpired:
            dt = time.time() - t0
            if label:
                _log(f'  [git] {label} — TIMEOUT ({dt:.1f}s)')
            return 1, '', f'[timeout] {" ".join(cmd)}'
        dt = time.time() - t0
        if label:
            _log(f'  [git] {label}: {dt:.1f}s (code={result.returncode})')
        return (result.returncode,
                _mask_secret(result.stdout.strip()),
                _mask_secret(result.stderr.strip()))

    # 원격 URL (토큰 포함) — 절대 그대로 로그에 출력하지 않음(_mask_secret 참조)
    remote = f'https://{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{GITHUB_REPO}.git'

    # git 설정
    run([git, 'config', 'user.email', 'hankyungjun@koreatooling.com'], label='config email')
    run([git, 'config', 'user.name',  GITHUB_USER], label='config name')

    # 원격 URL 갱신
    run([git, 'remote', 'set-url', 'origin', remote], label='remote set-url')

    # 변경사항 스테이징 — 생성된 정적 파일(HTML/CSS/JS)과 dist/ 폴더만 add.
    # 2026-06-30: git add . (루트 전체) → timeout 원인 확인.
    #   BASE_DIR = cnc-wiki 루트이므로 wiki/*.md, raw/ 등 대용량 파일까지 diff 대상이 됨.
    #   → 생성 파일만 명시적으로 add하여 push 크기를 최소화.
    t_add = time.time()
    import glob as _glob
    n_added = 0
    _add_fail = []
    for _pattern in ('*.html', '*.css', '*.js'):
        for _f in _glob.glob(os.path.join(BASE_DIR, _pattern)):
            _c, _o, _e = run([git, 'add', _f])
            if _c != 0:
                _add_fail.append(_e)
            n_added += 1
    _dist = os.path.join(BASE_DIR, 'dist')
    if os.path.isdir(_dist):
        _c, _o, _e = run([git, 'add', _dist])
        if _c != 0:
            _add_fail.append(_e)
        n_added += 1
    _log(f'  [git] add 단계 완료: {n_added}개 대상, 총 {time.time()-t_add:.1f}s')
    # 2026-08-28: .git/index.lock 잔존으로 add가 전부 실패했는데도 개별 run()이
    #   label 없이 호출돼 로그에 아무 흔적이 남지 않았고, 이어진 commit이 code=128로
    #   죽은 뒤 push가 code=0(보낼 것 없음)을 반환해 "✅ 업로드 완료"가 거짓으로
    #   기록됐다. add 실패를 명시적으로 남기고 즉시 중단한다.
    if _add_fail:
        _log(f'  ❌ git add 실패 {len(_add_fail)}건 — 첫 오류: {_add_fail[0][:200]}')
        if 'index.lock' in (_add_fail[0] or ''):
            _log('  → .git/index.lock 잔존. git 프로세스 종료 후 해당 파일을 삭제하세요.')
        return None

    # 커밋 (변경 없으면 스킵)
    msg = f'update: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    code, out, err = run([git, 'commit', '-m', msg], label='commit')
    # 2026-08-28: 커밋할 것이 없을 때 git이 내는 문구는 상황·로케일에 따라 다르다.
    #   ①'nothing to commit'(작업트리 깨끗) ②'no changes added to commit'(스테이징 안 된
    #   변경만 있음) ③한국어 로케일. daily_report.py가 이미 generate.py를 한 번 돌리므로
    #   배치 4단계의 두 번째 실행은 정상적으로 ②에 해당한다 — 실패가 아니다.
    _noop = ('nothing to commit', 'no changes added to commit',
             'nothing added to commit', '커밋할 사항 없음', '커밋할 변경 사항')
    if code != 0 and any(k in (out + err) for k in _noop):
        _log('  변경 없음 — 업로드 생략')
        return f'https://{GITHUB_USER}.github.io/{GITHUB_REPO}/'
    # '변경 없음'이 아닌 커밋 실패(예: index.lock → code=128)를 그대로 흘려보내면
    #   뒤이은 push가 code=0을 반환해 성공으로 오인된다. 여기서 끊는다.
    if code != 0:
        _log(f'  ❌ 커밋 실패 (code={code}): {(err or out)[:300]}')
        return None

    # 푸시 (파이썬 레벨 timeout 없음 — daily_report.py의 1800s가 상위 안전장치)
    code, out, err = run([git, 'push', 'origin', 'main'], timeout=None, label='push')
    if code != 0:
        _log(f'  ❌ 푸시 실패: {err}')
        return None

    url = f'https://{GITHUB_USER}.github.io/{GITHUB_REPO}/'
    _log(f'  ✅ 업로드 완료: {url}')
    return url


# ── 메인 ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--local', action='store_true', help='GitHub Pages 업로드 건너뜀')
    args = parser.parse_args()

    _log(f'generate.py 시작 '
         f'{"(로컬 전용)" if args.local else "(GitHub Pages 업로드 포함)"}')

    os.makedirs(DIST_DIR, exist_ok=True)

    # 1) 출하현황 파싱
    _t = time.time()
    _log('출하현황 파싱 중...')
    shippings = []
    for y in YEARS:
        path = os.path.join(COMP_DIR, f'출하현황_납품처별_월별분석_{y}.xlsx')
        if os.path.exists(path):
            data = parse_shipping(path)
            shippings.append((y, data))
            _log(f'  → {y}: 납품처 {len(data["customers"])}개사')
        else:
            _log(f'  → {y}: 파일 없음 (건너뜀)')
    _log(f'출하현황 파싱 완료 ({time.time()-_t:.1f}s)')

    # 2) 월간생산일지 파싱
    _t = time.time()
    _log('월간생산일지 파싱 중...')
    daily, worklog_file = parse_worklog()
    _log(f'  → {worklog_file or "파일 없음"} ({time.time()-_t:.1f}s)')

    # 2-B) ERP 「오늘 할 일」 (2026-09-04 신설) — 사내 현황판 전용
    #      실패해도 None 을 받아 블록만 빠진다. 나머지는 정상 진행.
    _t = time.time()
    _log('ERP 「오늘 할 일」 조회 중...')
    todo = fetch_erp_todo()
    if todo:
        _log(f'  → 미출하 {todo["open_cases"]}건 / {todo["open_qty"]:,}개 · '
             f'지연 {todo["late_cases"]}건 · 임박 {todo["near_cases"]}건 '
             f'({time.time()-_t:.1f}s)')
    else:
        _log(f'  → 생략 (블록 미표시) ({time.time()-_t:.1f}s)')

    worklog_date = daily['date'] if daily else '-'
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 3) 페이지 생성
    _t = time.time()
    # 2026-09-04 — 공개(GitHub Pages) / 사내(LAN 공유폴더) 분리
    #   공개: 거래처 정보가 없는 고객용 페이지만
    #   사내: 전부 (현황판은 거래처명·물량이 박히므로 절대 공개로 내보내지 않는다)
    #   ※ supplies.html 은 미사용 확인(한경준님, 2026-09-04)으로 생성 중단.
    #      build_supplies_html() 함수는 삭제하지 않고 남겨둔다.
    public_pages = {
        'index.html':     build_portal_html(show_staff=False),
        'request.html':   build_request_html(),
        'defect.html':    build_defect_html(),
        'inquiry.html':   build_inquiry_html(),
    }
    internal_pages = {
        'index.html':     build_portal_html(show_staff=True),
        'request.html':   public_pages['request.html'],
        'defect.html':    public_pages['defect.html'],
        'inquiry.html':   public_pages['inquiry.html'],
        'dashboard.html': build_dashboard_html(shippings, daily, worklog_date, generated_at, todo),
    }
    pages = public_pages   # 이하 공개 배포 경로는 기존 로직 그대로
    _log(f'페이지 생성 완료 — 공개 {len(public_pages)}개 / 사내 {len(internal_pages)}개 '
         f'({time.time()-_t:.1f}s)')

    _t = time.time()
    for fname, html in public_pages.items():
        for out_dir in (DIST_DIR, BASE_DIR):
            fpath = os.path.join(out_dir, fname)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(html)
        _log(f'  → 저장(공개): {fname} (dist/ + 루트)')
    _log(f'파일 저장 완료 ({time.time()-_t:.1f}s)')

    # 3-B) dist/ 정적 파일 → 루트 동기화 (generate가 생성하지 않는 파일)
    # HTML 뿐 아니라 CSS·JS 도 루트로 복사 (2026-06-15: 외부 파일 분리 대응)
    _t = time.time()
    import shutil, glob
    generated = set(pages.keys())
    for ext in ('*.html', '*.css', '*.js'):
        for src in glob.glob(os.path.join(DIST_DIR, ext)):
            fname = os.path.basename(src)
            if fname in INTERNAL_ONLY:      # 2026-09-04 사내 전용 — 공개로 내보내지 않음
                continue
            if fname not in generated:
                dst = os.path.join(BASE_DIR, fname)
                shutil.copy2(src, dst)
                _log(f'  → 정적 복사: {fname} (dist/ → 루트)')
    _log(f'정적 파일 동기화 완료 ({time.time()-_t:.1f}s)')

    # 3-C) 사내 공유폴더 배포 (2026-09-04 신설)
    _t = time.time()
    _log('사내 공유폴더 배포 중...')
    internal_ok = publish_internal(internal_pages)
    _log(f'사내 배포 단계 종료 ({time.time()-_t:.1f}s) — '
         f'{"성공" if internal_ok else "실패/건너뜀"}')

    # 4) GitHub Pages 업로드
    upload_ok = True
    if args.local:
        _log('완료. (GitHub 업로드 건너뜀)')
    else:
        _log('GitHub Pages 업로드 중...')
        _t = time.time()
        url = upload_to_github()
        _log(f'업로드 단계 종료 ({time.time()-_t:.1f}s)')
        if not url:
            upload_ok = False
            _log('⚠ 업로드 실패 — 로컬 파일만 생성됨')

    _log(f'완료. (전체 소요 {time.time()-_START_TS:.1f}s)')

    # 2026-07-07: 이전에는 업로드 실패해도 exit code가 항상 0이라 daily_report.py가
    # "GitHub Pages 업로드 완료"로 잘못 로그를 남겼음(returncode만 확인) — 실패를
    # 상위 프로세스에 정확히 전달하도록 exit code 구분.
    if not upload_ok:
        sys.exit(1)
