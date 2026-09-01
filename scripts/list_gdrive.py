import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timezone

# .env load
def _load_env():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDS_FILE = os.environ.get(
    "GOOGLE_CREDS_FILE",
    "client_secret_469311829534-3jnh14mv6tqbu4g2lurvhmdrblc9vpst.apps.googleusercontent.com.json",
)
TOKEN_FILE  = os.environ.get("GOOGLE_TOKEN_FILE", "token.json")
FOLDER_NAME = 'cnc-wiki'


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
    local = dt.astimezone()
    return local.strftime('%Y-%m-%d %H:%M')


def get_folder_id(service, folder_name):
    q = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    res = service.files().list(q=q, fields='files(id, name)').execute()
    folders = res.get('files', [])
    if not folders:
        print(f"  folder not found: {folder_name}")
        return None
    return folders[0]['id']


def list_files(service, folder_id):
    q = f"'{folder_id}' in parents and trashed=false"
    fields = 'files(id, name, size, modifiedTime, mimeType, webViewLink)'
    res = service.files().list(q=q, fields=fields, orderBy='modifiedTime desc').execute()
    return res.get('files', [])


if __name__ == '__main__':
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    folder_id = get_folder_id(service, FOLDER_NAME)
    if not folder_id:
        sys.exit(1)

    files = list_files(service, folder_id)

    print()
    print(f"  Google Drive -- {FOLDER_NAME}")
    print(f"  folder: https://drive.google.com/drive/folders/{folder_id}")
    print()

    if not files:
        print("  (no files)")
    else:
        col_name = max(len(f['name']) for f in files)
        col_name = max(col_name, 10)

        header = f"  {'name':<{col_name}}  {'size':>8}  {'modified':<16}  link"
        sep    = '  ' + '-' * (col_name + 2 + 8 + 2 + 16 + 2 + 40)
        print(header)
        print(sep)

        for f in files:
            name     = f.get('name', '')
            size     = fmt_size(f.get('size'))
            modified = fmt_date(f.get('modifiedTime'))
            link     = f.get('webViewLink', '-')
            print(f"  {name:<{col_name}}  {size:>8}  {modified:<16}  {link}")

        print(sep)
        print(f"  total: {len(files)} files")

    print()
