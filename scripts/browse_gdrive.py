import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timezone

# ── .env 로드 (python-dotenv 없으면 수동 파싱) ──────────────────────────────
def _load_env():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

SCOPES     = ['https://www.googleapis.com/auth/drive.readonly']
CREDS_FILE = os.environ.get(
    "GOOGLE_CREDS_FILE",
    "client_secret_469311829534-3jnh14mv6tqbu4g2lurvhmdrblc9vpst.apps.googleusercontent.com.json",
)
TOKEN_FILE = os.environ.get("GOOGLE_TOKEN_READONLY_FILE", "token_readonly.json")


# ── 인증 ──────────────────────────────────────────────────────────────────────
def get_credentials():
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
    return creds


# ── 유틸 ──────────────────────────────────────────────────────────────────────
def fmt_size(size_bytes):
    if size_bytes is None:
        return '-'
    size = int(size_bytes)
    if size >= 1024 * 1024:
        return f'{size / 1024 / 1024:.1f} MB'
    elif size >= 1024:
        return f'{size / 1024:.1f} KB'
    return f'{size} B'


def fmt_date(iso_str):
    if not iso_str:
        return '-'
    dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
    return dt.astimezone().strftime('%Y-%m-%d %H:%M')


# ── 폴더 검색 ─────────────────────────────────────────────────────────────────
def find_folders(service, name):
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    res = service.files().list(q=q, fields='files(id, name, parents)').execute()
    return res.get('files', [])


# ── 폴더 내 파일 목록 ─────────────────────────────────────────────────────────
def list_folder(service, folder_id, indent=0):
    q = f"'{folder_id}' in parents and trashed=false"
    fields = 'files(id, name, size, mimeType, modifiedTime, webViewLink)'
    res = service.files().list(q=q, fields=fields, orderBy='folder,name').execute()
    items = res.get('files', [])

    pad = '  ' * indent
    for item in items:
        is_folder = item['mimeType'] == 'application/vnd.google-apps.folder'
        icon = '📁' if is_folder else '📄'
        size = '' if is_folder else f"  {fmt_size(item.get('size')):>8}"
        date = fmt_date(item.get('modifiedTime'))
        print(f"{pad}{icon} {item['name']}{size}  {date}")

        if is_folder:
            list_folder(service, item['id'], indent + 1)

    return len(items)


# ── 메인 ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    # 검색할 폴더명 입력
    if len(sys.argv) > 1:
        folder_name = ' '.join(sys.argv[1:])
    else:
        print('조회할 폴더명을 입력하세요: ', end='')
        folder_name = input().strip()

    print()
    folders = find_folders(service, folder_name)

    if not folders:
        print(f'  ❌ 폴더를 찾을 수 없습니다: {folder_name}')
        sys.exit(1)

    for folder in folders:
        fid = folder['id']
        print(f'📁 {folder["name"]}')
        print(f'   https://drive.google.com/drive/folders/{fid}')
        print()
        count = list_folder(service, fid, indent=1)
        print()
        print(f'   총 {count}개 항목')
        print()
