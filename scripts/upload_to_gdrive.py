import sys, io, os, glob
from pathlib import Path

def _load_env():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDS_FILE = os.environ.get("GOOGLE_CREDS_FILE", "client_secret_469311829534-3jnh14mv6tqbu4g2lurvhmdrblc9vpst.apps.googleusercontent.com.json")
TOKEN_FILE  = os.environ.get("GOOGLE_TOKEN_FILE", "token.json")
FOLDER_NAME = 'cnc-wiki 분석자료'

# 업로드할 파일 목록
UPLOAD_FILES = [
    'wiki/comparisons/출하현황_납품처별_월별분석_2025.xlsx',
    'wiki/comparisons/2025_KPI_설비가동율_작업효율_양품율.xlsx',
    'wiki/comparisons/KPI_설비가동율_작업효율_양품율_2022-2025.xlsx',
]

MIME_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


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


def get_or_create_folder(service, folder_name):
    q = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=q, fields='files(id, name)').execute()
    folders = results.get('files', [])
    if folders:
        fid = folders[0]['id']
        print(f"  기존 폴더 사용: {folder_name} (id={fid})")
        return fid
    meta = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    folder = service.files().create(body=meta, fields='id').execute()
    fid = folder['id']
    print(f"  새 폴더 생성: {folder_name} (id={fid})")
    return fid


def upload_file(service, local_path, folder_id):
    name = os.path.basename(local_path)
    # 기존 동명 파일 삭제
    q = f"name='{name}' and '{folder_id}' in parents and trashed=false"
    existing = service.files().list(q=q, fields='files(id)').execute().get('files', [])
    for f in existing:
        service.files().delete(fileId=f['id']).execute()

    meta = {'name': name, 'parents': [folder_id]}
    media = MediaFileUpload(local_path, mimetype=MIME_XLSX, resumable=True)
    file = service.files().create(body=meta, media_body=media, fields='id, webViewLink').execute()
    return file.get('webViewLink', '')


if __name__ == '__main__':
    print("=== Google Drive 업로드 ===")
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    folder_id = get_or_create_folder(service, FOLDER_NAME)

    for fpath in UPLOAD_FILES:
        if not os.path.exists(fpath):
            print(f"  [건너뜀] 파일 없음: {fpath}")
            continue
        print(f"  업로드 중: {os.path.basename(fpath)} ...", end=' ', flush=True)
        link = upload_file(service, fpath, folder_id)
        print(f"완료")
        if link:
            print(f"    링크: {link}")

    print("\n모든 파일 업로드 완료!")
    print(f"Google Drive 폴더: https://drive.google.com/drive/folders/{folder_id}")
