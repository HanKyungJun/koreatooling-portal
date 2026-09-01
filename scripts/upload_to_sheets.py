#!/usr/bin/env python3
"""
재연마 일일보고 → Google Sheets 자동 업로드
실행: python scripts/upload_to_sheets.py [YYYY-MM-DD]

Google Sheets 구조:
  시트1 "오늘의 보고"  - 매일 덮어쓰기 (최신 데이터 항상 유지)
  시트2 "월별 누적"    - 날짜별 행 추가/갱신 (이력 누적)
"""
import sys, io, os, json, argparse
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# daily_report.py 의 데이터 추출 함수 재사용
sys.path.insert(0, str(Path(__file__).parent))
from daily_report import (
    find_xls, read_summary, read_detail,
    find_prev, calc_avg, sec_to_hms, _int
)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── .env 로드 ─────────────────────────────────────────────────────────────────
def _load_env():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

# ── 경로 / 설정 ────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
]

# .env의 GOOGLE_CREDS_FILE 우선, 없으면 glob으로 자동 탐색 (하위 호환)
_creds_env = os.environ.get("GOOGLE_CREDS_FILE")
if _creds_env:
    CREDS_FILE = str(BASE / _creds_env) if not os.path.isabs(_creds_env) else _creds_env
else:
    _found = list(BASE.glob('client_secret_*.json'))
    CREDS_FILE = str(_found[0]) if _found else "client_secret_미설정.json"

TOKEN_FILE    = os.environ.get("GOOGLE_TOKEN_FILE", str(BASE / 'token.json'))
SHEET_ID_FILE = str(BASE / 'sheets_id.json')
SHEET_TITLE  = '재연마 일일보고 (자동)'


# ── 인증 ───────────────────────────────────────────────────
def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            print("브라우저 인증이 필요합니다. 잠시 후 브라우저가 열립니다...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return creds


# ── 스프레드시트 생성 또는 재사용 ──────────────────────────
def get_or_create_spreadsheet(drive_svc, sheets_svc):
    # 저장된 ID 확인
    if os.path.exists(SHEET_ID_FILE):
        with open(SHEET_ID_FILE) as f:
            saved = json.load(f)
        sid = saved.get('spreadsheet_id', '')
        try:
            sheets_svc.spreadsheets().get(spreadsheetId=sid).execute()
            print(f"  기존 스프레드시트 사용 중 (id: {sid})")
            return sid
        except Exception:
            print("  저장된 ID가 유효하지 않음 → 새로 생성")

    # Drive에서 검색
    q = (f"name='{SHEET_TITLE}' and "
         f"mimeType='application/vnd.google-apps.spreadsheet' and trashed=false")
    results = drive_svc.files().list(q=q, fields='files(id)').execute()
    files   = results.get('files', [])
    if files:
        sid = files[0]['id']
        print(f"  Drive에서 발견 (id: {sid})")
    else:
        body = {
            'properties': {'title': SHEET_TITLE, 'locale': 'ko_KR'},
            'sheets': [
                {'properties': {'title': '오늘의 보고', 'sheetId': 0, 'index': 0}},
                {'properties': {'title': '월별 누적',   'sheetId': 1, 'index': 1}},
            ],
        }
        ss  = sheets_svc.spreadsheets().create(body=body, fields='spreadsheetId').execute()
        sid = ss['spreadsheetId']
        print(f"  새 스프레드시트 생성 (id: {sid})")

        # 공유 설정: 링크 있는 모든 사람이 볼 수 있음
        drive_svc.permissions().create(
            fileId=sid,
            body={'type': 'anyone', 'role': 'reader'},
        ).execute()
        print("  공유 설정 완료 (링크 공유 — 뷰어)")

    with open(SHEET_ID_FILE, 'w') as f:
        json.dump({'spreadsheet_id': sid}, f)
    return sid


def ensure_sheet(sheets_svc, sid, title):
    ss = sheets_svc.spreadsheets().get(spreadsheetId=sid).execute()
    names = [s['properties']['title'] for s in ss['sheets']]
    if title not in names:
        sheets_svc.spreadsheets().batchUpdate(
            spreadsheetId=sid,
            body={'requests': [{'addSheet': {'properties': {'title': title}}}]},
        ).execute()
        print(f"  시트 추가: {title}")


def write_values(sheets_svc, sid, sheet_title, values):
    sheets_svc.spreadsheets().values().clear(
        spreadsheetId=sid,
        range=f"'{sheet_title}'",
    ).execute()
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=sid,
        range=f"'{sheet_title}'!A1",
        valueInputOption='USER_ENTERED',
        body={'values': values},
    ).execute()


def apply_formats(sheets_svc, sid, sheet_id, requests):
    if requests:
        sheets_svc.spreadsheets().batchUpdate(
            spreadsheetId=sid,
            body={'requests': requests},
        ).execute()


def hex_to_rgb(h):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return {'red': r/255, 'green': g/255, 'blue': b/255}


def cell_fmt(sid, row, col, bold=False, bg=None, fg=None,
             font_size=10, halign='CENTER', sheet_id=0):
    fmt = {
        'textFormat': {
            'bold': bold,
            'fontSize': font_size,
            'foregroundColor': hex_to_rgb(fg) if fg else {'red':0,'green':0,'blue':0},
        },
        'horizontalAlignment': halign,
        'verticalAlignment': 'MIDDLE',
    }
    if bg:
        fmt['backgroundColor'] = hex_to_rgb(bg)
    return {
        'repeatCell': {
            'range': {
                'sheetId':          sheet_id,
                'startRowIndex':    row,
                'endRowIndex':      row + 1,
                'startColumnIndex': col,
                'endColumnIndex':   col + 1,
            },
            'cell': {'userEnteredFormat': fmt},
            'fields': ('userEnteredFormat(textFormat,horizontalAlignment,'
                       'verticalAlignment,backgroundColor)'),
        }
    }


def row_fmt(sid, row, ncols, bold=False, bg=None, fg=None,
            font_size=10, halign='CENTER', sheet_id=0):
    fmt = {
        'textFormat': {
            'bold': bold,
            'fontSize': font_size,
            'foregroundColor': hex_to_rgb(fg) if fg else {'red':0,'green':0,'blue':0},
        },
        'horizontalAlignment': halign,
        'verticalAlignment': 'MIDDLE',
    }
    if bg:
        fmt['backgroundColor'] = hex_to_rgb(bg)
    return {
        'repeatCell': {
            'range': {
                'sheetId':          sheet_id,
                'startRowIndex':    row,
                'endRowIndex':      row + 1,
                'startColumnIndex': 0,
                'endColumnIndex':   ncols,
            },
            'cell': {'userEnteredFormat': fmt},
            'fields': ('userEnteredFormat(textFormat,horizontalAlignment,'
                       'verticalAlignment,backgroundColor)'),
        }
    }


def merge(sheet_id, row, c1, c2):
    return {
        'mergeCells': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': row, 'endRowIndex': row + 1,
                'startColumnIndex': c1, 'endColumnIndex': c2,
            },
            'mergeType': 'MERGE_ALL',
        }
    }


# ── 시트1: 오늘의 보고 ─────────────────────────────────────
def build_today_sheet(target, td, prev, avg, detail, n_prev, n_work):
    y, m, d   = target.year, target.month, target.day
    date_str  = target.strftime('%Y년 %m월 %d일')
    prev_str  = f"{m}월 {int(prev['일'])}일" if prev else '없음'
    now_str   = datetime.now().strftime('%Y-%m-%d %H:%M')

    rows = []

    # 제목
    rows.append([f'재연마 일일생산 보고  —  {date_str}  (17:30 기준)'])
    rows.append([f'생성: {now_str}  |  전일: {prev_str}  |  월평균 기준: 이전 {n_prev}일  |  {m}월 누적 작업일: {n_work}일'])
    rows.append([])

    # 요약 헤더
    rows.append(['항목', '오늘', '전일', '전일대비(▲▼)', '전일대비(%)',
                 '월평균', '월평균대비(▲▼)', '월평균대비(%)', '비고'])

    KEYS = [
        ('FAST GRIND  수량 (개)',    'FG수량',  False),
        ('FAST GRIND  가공시간 (초)', 'FG시간', True),
        ('GX7  수량 (개)',           'GX수량',  False),
        ('GX7  가공시간 (초)',        'GX시간', True),
        ('합계  수량 (개)',           '합수량',  False),
        ('합계  가공시간 (초)',        '합시간', True),
        ('합계  금액',               '합금액',  False),
    ]
    for label, key, is_time in KEYS:
        tv = td.get(key, 0)
        pv = prev.get(key, 0) if prev else None
        av = avg.get(key, 0)

        d_prev  = (tv - pv)  if pv is not None else None
        d_avg   = tv - av
        # 비율: 문자열로 표기 (숫자+% 는 Sheets가 텍스트로 취급)
        p_prev  = f"{(d_prev/pv*100):+.1f}%" if (pv and pv != 0 and d_prev is not None) else ''
        p_avg   = f"{(d_avg/av*100):+.1f}%"  if av != 0 else ''
        note    = sec_to_hms(tv) if is_time else ''
        # 숫자 차이값은 raw 숫자로 넘겨야 Sheets가 오류 없이 표시
        d_prev_val = round(d_prev) if d_prev is not None else ''
        d_avg_val  = round(d_avg)

        rows.append([
            label, tv, pv if pv is not None else '',
            d_prev_val, p_prev,
            round(av, 1), d_avg_val, p_avg, note,
        ])

    rows.append([])

    # 월 누적
    rows.append([f'{m}월 누적 ({n_work}일 / {d}일 중 작업일)',
                 '', '', '', '', '', '', '', ''])
    rows.append([])
    rows.append([])

    # 작업 상세 — FAST GRIND
    rows.append(['■ FAST GRIND 작업 상세'])
    rows.append(['순서', '형상', '날수(F)', '날경(Ø)', '상크경(Ø)',
                 '코팅', '특이사항', '완료', '수량(개)', '시간합계(초)', '시간(H:M:S)'])
    if detail['fg']:
        for j in detail['fg']:
            rows.append([j['순서'], j['형상'], j['날수(F)'], j['날경(Ø)'],
                         j['상크경(Ø)'], j['코팅'], j['특이사항'], j['완료여부'],
                         j['수량'], j['시간합계'], sec_to_hms(j['시간합계'])])
        rows.append(['소계', '', '', '', '', '', '', '',
                     sum(j['수량'] for j in detail['fg']),
                     sum(j['시간합계'] for j in detail['fg']),
                     sec_to_hms(sum(j['시간합계'] for j in detail['fg']))])
    else:
        rows.append(['(작업 없음)'])

    rows.append([])

    # 작업 상세 — GX7
    rows.append(['■ GX7 작업 상세'])
    rows.append(['순서', '형상', '날수(F)', '날경(Ø)', '상크경(Ø)',
                 '코팅', '특이사항', '완료', '수량(개)', '시간합계(초)', '시간(H:M:S)'])
    if detail['gx']:
        for j in detail['gx']:
            rows.append([j['순서'], j['형상'], j['날수(F)'], j['날경(Ø)'],
                         j['상크경(Ø)'], j['코팅'], j['특이사항'], j['완료여부'],
                         j['수량'], j['시간합계'], sec_to_hms(j['시간합계'])])
        rows.append(['소계', '', '', '', '', '', '', '',
                     sum(j['수량'] for j in detail['gx']),
                     sum(j['시간합계'] for j in detail['gx']),
                     sec_to_hms(sum(j['시간합계'] for j in detail['gx']))])
    else:
        rows.append(['(작업 없음)'])

    return rows


# ── 시트2: 월별 누적 ───────────────────────────────────────
def build_monthly_rows(sheets_svc, sid, summary, y, m):
    sheet_title = f'{y}년 {m:02d}월'
    ensure_sheet(sheets_svc, sid, sheet_title)

    # 기존 데이터 읽기
    result = sheets_svc.spreadsheets().values().get(
        spreadsheetId=sid,
        range=f"'{sheet_title}'",
    ).execute()
    existing = result.get('values', [])

    HDR = ['날짜', 'FG수량', 'FG가공시간(초)', 'FG시간(H:M:S)',
           'GX수량', 'GX가공시간(초)', 'GX시간(H:M:S)',
           '합수량', '합가공시간(초)', '합시간(H:M:S)']

    # 날짜 → 행 매핑 (기존 데이터에서)
    date_map = {}
    for i, row in enumerate(existing):
        if i == 0:
            continue
        if row and row[0]:
            date_map[str(row[0])] = i

    # summary 의 모든 작업일로 행 구성
    new_rows = [HDR]
    for _, r in summary[summary['합수량'] > 0].iterrows():
        day = int(r['일'])
        dstr = f"{y}-{m:02d}-{day:02d}"
        new_rows.append([
            dstr,
            int(r['FG수량']),  int(r['FG시간']),  sec_to_hms(int(r['FG시간'])),
            int(r['GX수량']),  int(r['GX시간']),  sec_to_hms(int(r['GX시간'])),
            int(r['합수량']),  int(r['합시간']),   sec_to_hms(int(r['합시간'])),
        ])

    # 합계 행
    n = len(new_rows) - 1  # 데이터 행 수
    if n > 0:
        new_rows.append([
            f'합계 ({n}일)',
            f'=SUM(B2:B{n+1})', '', '',
            f'=SUM(E2:E{n+1})', '', '',
            f'=SUM(H2:H{n+1})', '', '',
        ])
        new_rows.append([
            f'일평균',
            f'=AVERAGE(B2:B{n+1})', '', '',
            f'=AVERAGE(E2:E{n+1})', '', '',
            f'=AVERAGE(H2:H{n+1})', '', '',
        ])

    write_values(sheets_svc, sid, sheet_title, new_rows)
    return sheet_title


# ── 메인 업로드 함수 ───────────────────────────────────────
def upload(target: datetime):
    y, m, d = target.year, target.month, target.day

    xls_path = find_xls(y, m)
    summary  = read_summary(xls_path)
    today_row = summary[summary['일'] == d]
    if today_row.empty:
        raise ValueError(f"{y}-{m:02d}-{d:02d} 데이터가 월간합계표에 없습니다.")

    td     = today_row.iloc[0].to_dict()
    prev   = find_prev(summary, d)
    avg    = calc_avg(summary, d)
    detail = read_detail(xls_path, d)
    n_prev = len(summary[(summary['일'] < d) & (summary['합수량'] > 0)])
    n_work = len(summary[(summary['일'] <= d) & (summary['합수량'] > 0)])

    print("Google 인증 확인 중...")
    creds       = get_credentials()
    drive_svc   = build('drive',  'v3', credentials=creds, cache_discovery=False)
    sheets_svc  = build('sheets', 'v4', credentials=creds, cache_discovery=False)

    print("스프레드시트 준비 중...")
    sid = get_or_create_spreadsheet(drive_svc, sheets_svc)

    # ── 시트1: 오늘의 보고 ────────────────────────────────
    print("  '오늘의 보고' 시트 업데이트 중...")
    ensure_sheet(sheets_svc, sid, '오늘의 보고')
    today_values = build_today_sheet(target, td, prev, avg, detail, n_prev, n_work)
    write_values(sheets_svc, sid, '오늘의 보고', today_values)

    # 기본 서식 (제목 굵게)
    ss_meta  = sheets_svc.spreadsheets().get(spreadsheetId=sid).execute()
    sheet_id = next(s['properties']['sheetId']
                    for s in ss_meta['sheets']
                    if s['properties']['title'] == '오늘의 보고')

    fmt_reqs = [
        row_fmt(sid, 0, 9, bold=True, bg='1F497D', fg='FFFFFF', font_size=12, sheet_id=sheet_id),
        row_fmt(sid, 3, 9, bold=True, bg='4472C4', fg='FFFFFF', sheet_id=sheet_id),
        # FAST GRIND 제목 행 (행 위치는 고정값으로)
    ]
    apply_formats(sheets_svc, sid, sheet_id, fmt_reqs)

    # ── 시트2: 월별 누적 ──────────────────────────────────
    print("  '월별 누적' 시트 업데이트 중...")
    monthly_title = build_monthly_rows(sheets_svc, sid, summary, y, m)

    url = f"https://docs.google.com/spreadsheets/d/{sid}/edit"
    print()
    print("=" * 55)
    print(f"  업로드 완료!")
    print(f"  URL: {url}")
    print("=" * 55)
    print()
    print("  이 URL을 북마크하거나 공유하면 어디서든 열람 가능합니다.")
    return url


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    parser = argparse.ArgumentParser(description='일일보고 Google Sheets 업로드')
    parser.add_argument('date', nargs='?', help='날짜 (YYYY-MM-DD). 생략 시 오늘')
    args = parser.parse_args()

    target = (datetime.strptime(args.date, '%Y-%m-%d')
              if args.date else datetime.now())

    try:
        upload(target)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
