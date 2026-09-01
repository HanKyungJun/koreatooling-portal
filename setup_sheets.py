import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# .env 로드 (python-dotenv 없으면 수동 파싱)
def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        for line in open(env_path, encoding='utf-8'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                os.environ.setdefault(k.strip(), v.strip())
_load_env()

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# SECURITY TODO:
# - client_secret*.json과 token_sheets.json은 Google OAuth 민감 파일입니다.
# - GitHub/Netlify/공유 폴더에 올리지 말고, 배포 전 .gitignore와 로컬 설정 분리를 확인하세요.
CREDS_FILE = os.environ.get(
    'GOOGLE_CREDS_FILE',
    'client_secret_469311829534-3jnh14mv6tqbu4g2lurvhmdrblc9vpst.apps.googleusercontent.com.json'
)  # 2026-06-12: umv75na9 OAuth 클라이언트 삭제 → 신규 클라이언트로 교체.
TOKEN_FILE  = 'token_sheets.json'
SCOPES      = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
]

def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)

def create_sheet():
    service = get_service()

    # ── 시트 생성 (탭 4개) ──────────────────────────────────────────────────
    spreadsheet = {
        'properties': {'title': '코리아툴링 폼 접수 관리'},
        'sheets': [
            {'properties': {'title': '재연마의뢰',  'index': 0}},
            {'properties': {'title': '불량신고',    'index': 1}},
            {'properties': {'title': '진행문의',    'index': 2}},
            {'properties': {'title': '소모품요청',  'index': 3}},
        ]
    }
    result = service.spreadsheets().create(
        body=spreadsheet, fields='spreadsheetId,spreadsheetUrl'
    ).execute()
    sheet_id  = result['spreadsheetId']
    sheet_url = result['spreadsheetUrl']

    # ── 헤더 설정 ──────────────────────────────────────────────────────────
    headers = {
        '재연마의뢰': ['접수일시','회사명','담당자','연락처','이메일','공구종류','재질','규격','수량','특이사항'],
        '불량신고':   ['접수일시','회사명','담당자','연락처','발생일자','공구명/규격','불량수량','불량증상','피삭재/환경','불량상세'],
        '진행문의':   ['접수일시','회사명','담당자','연락처','참고일자','문의내용'],
        '소모품요청': ['접수일시','요청자','부서','품목명','규격/사양','수량','희망납기','용도/사유','긴급여부'],
    }
    batch = [{'range': f'{name}!A1', 'values': [row]} for name, row in headers.items()]
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=sheet_id,
        body={'valueInputOption': 'RAW', 'data': batch}
    ).execute()

    # ── 실제 sheetId 조회 ──────────────────────────────────────────────────
    info = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    sheet_ids = [s['properties']['sheetId'] for s in info['sheets']]

    # ── 헤더 굵게 + 배경색 ────────────────────────────────────────────────
    fmt_requests = []
    for sid in sheet_ids:
        fmt_requests.append({
            'repeatCell': {
                'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.102, 'green': 0.227, 'blue': 0.420},
                        'textFormat': {'foregroundColor': {'red':1,'green':1,'blue':1}, 'bold': True},
                        'horizontalAlignment': 'CENTER',
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })
        fmt_requests.append({
            'updateSheetProperties': {
                'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 1}},
                'fields': 'gridProperties.frozenRowCount'
            }
        })
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id, body={'requests': fmt_requests}
    ).execute()

    print()
    print('=' * 55)
    print('  ✅ 구글 시트 생성 완료!')
    print('=' * 55)
    print(f'  URL : {sheet_url}')
    print(f'  ID  : {sheet_id}')
    print('=' * 55)
    print()
    print('  다음 단계: Apps Script에 아래 ID를 붙여넣으세요')
    print(f'  SHEET_ID = "{sheet_id}"')
    print()

if __name__ == '__main__':
    create_sheet()
