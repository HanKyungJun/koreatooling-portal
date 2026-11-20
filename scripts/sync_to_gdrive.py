import sys, io, os, mimetypes
from pathlib import Path

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

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timezone

SCOPES    = ['https://www.googleapis.com/auth/drive.file']
CREDS_FILE = os.environ.get("GOOGLE_CREDS_FILE", "client_secret_469311829534-3jnh14mv6tqbu4g2lurvhmdrblc9vpst.apps.googleusercontent.com.json")
TOKEN_FILE = os.environ.get("GOOGLE_TOKEN_FILE", "token.json")
LOCAL_ROOT = 'wiki'
DRIVE_ROOT = 'cnc-wiki'

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


# ── 폴더 조회 / 생성 ──────────────────────────────────────────────────────────
def get_or_create_folder(service, name, parent_id=None):
    parent_q = f"and '{parent_id}' in parents" if parent_id else "and 'root' in parents"
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false {parent_q}"
    res = service.files().list(q=q, fields='files(id)').execute()
    folders = res.get('files', [])
    if folders:
        return folders[0]['id']
    meta = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        meta['parents'] = [parent_id]
    folder = service.files().create(body=meta, fields='id').execute()
    return folder['id']


# ── Drive 파일 목록 조회 (name → {id, modifiedTime}) ─────────────────────────
def get_drive_files(service, folder_id):
    # 2026-11-20: 목록을 끝까지 읽는다(전에는 첫 페이지 100개만 읽어, 100개 넘는 폴더의 나머지 파일을
    # 「Drive 에 없음」으로 보고 매번 새로 올림 → 같은 이름 파일이 쌓임). 같은 이름이 여럿이면 가장 최근 것.
    q = f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'"
    out, token = {}, None
    while True:
        res = service.files().list(q=q, pageSize=1000, pageToken=token,
                                   fields='nextPageToken, files(id, name, modifiedTime)').execute()
        for f in res.get('files', []):
            old = out.get(f['name'])
            if old is None or f['modifiedTime'] > old['modifiedTime']:
                out[f['name']] = f
        token = res.get('nextPageToken')
        if not token:
            return out


# ── 로컬 수정일자 → UTC datetime ──────────────────────────────────────────────
def local_mtime(path):
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts, tz=timezone.utc)


# ── Drive 수정일자 파싱 ───────────────────────────────────────────────────────
def drive_mtime(iso_str):
    return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))


# ── 파일 업로드 (신규 or 덮어쓰기) ───────────────────────────────────────────
def upload_file(service, local_path, name, folder_id, existing=None):
    mime, _ = mimetypes.guess_type(local_path)
    mime = mime or 'application/octet-stream'
    media = MediaFileUpload(local_path, mimetype=mime, resumable=True)

    if existing:
        service.files().update(
            fileId=existing['id'],
            media_body=media
        ).execute()
        return '업데이트'
    else:
        meta = {'name': name, 'parents': [folder_id]}
        service.files().create(body=meta, media_body=media, fields='id').execute()
        return '신규'


# ── 폴더 재귀 동기화 ──────────────────────────────────────────────────────────
def sync_folder(service, local_dir, drive_folder_id, stats, rel_base=''):
    drive_files = get_drive_files(service, drive_folder_id)

    for entry in sorted(os.scandir(local_dir), key=lambda e: e.name):
        rel_path = os.path.join(rel_base, entry.name) if rel_base else entry.name

        if entry.is_dir():
            sub_id = get_or_create_folder(service, entry.name, drive_folder_id)
            sync_folder(service, entry.path, sub_id, stats, rel_path)

        elif entry.is_file():
            # Excel 임시 잠금 파일 건너뜀
            if entry.name.startswith('~$'):
                stats['skipped'] += 1
                continue
            # 2026-11-20: 작업 백업(.bak_YYYYMMDD 등)은 PC 에만 둔다 — Drive 에 올리지 않음
            if '.bak_' in entry.name or entry.name.endswith('.bak'):
                stats['skipped'] += 1
                continue
            existing = drive_files.get(entry.name)
            need_upload = True

            if existing:
                l_mt = local_mtime(entry.path)
                d_mt = drive_mtime(existing['modifiedTime'])
                if l_mt <= d_mt:
                    need_upload = False

            if need_upload:
                action = upload_file(service, entry.path, entry.name, drive_folder_id, existing)
                print(f"  [{action}] {rel_path}")
                stats['uploaded'] += 1
            else:
                stats['skipped'] += 1


# ── erp/ 소스 백업 (2026-11-20 추가 — decisions 2026-11-20 (9)) ─────────────────
# erp/ 를 공개 저장소에서 추적 제외해 git 이력 · 원격 백업이 없어지므로, 소스만 Drive 에 올린다.
# build/ · dist/ · snapshot/ 등 산출물 · 조회 결과는 올리지 않는다(사용설명서만 예외).
ERP_LOCAL = 'erp'
ERP_DRIVE = 'cnc-wiki-erp'
ERP_EXT = {'.py', '.bat', '.spec', '.md', '.ps1'}  # .txt 는 조회 결과가 많아 빼고 requirements 만(아래)
ERP_EXTRA = [os.path.join('dist', '사용설명서.txt')]


def erp_source_files(base=ERP_LOCAL):
    """올릴 erp 소스 파일 목록(상대 경로). erp/ 바로 아래 소스 + ERP_EXTRA."""
    out = []
    if not os.path.isdir(base):
        return out
    for entry in sorted(os.scandir(base), key=lambda e: e.name):
        if entry.is_file() and (os.path.splitext(entry.name)[1].lower() in ERP_EXT
                                or entry.name.endswith('requirements.txt')) \
                and not entry.name.startswith('~$') and '.bak_' not in entry.name:
            out.append(entry.name)
    for rel in ERP_EXTRA:
        if os.path.isfile(os.path.join(base, rel)):
            out.append(rel)
    return out


def sync_erp_sources(service, stats):
    root_id = get_or_create_folder(service, ERP_DRIVE)
    folder_ids = {'': root_id}
    for rel in erp_source_files():
        sub = os.path.dirname(rel)
        if sub not in folder_ids:
            folder_ids[sub] = get_or_create_folder(service, sub, root_id)
        fid = folder_ids[sub]
        name = os.path.basename(rel)
        existing = get_drive_files(service, fid).get(name)
        path = os.path.join(ERP_LOCAL, rel)
        if existing and local_mtime(path) <= drive_mtime(existing['modifiedTime']):
            stats['skipped'] += 1
            continue
        action = upload_file(service, path, name, fid, existing)
        print(f"  [{action}] {ERP_LOCAL}/{rel}")
        stats['uploaded'] += 1
    return root_id


# ── 메인 ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=== Google Drive 동기화 ===")
    print(f"  로컬 경로 : {LOCAL_ROOT}/")
    print(f"  Drive 폴더: {DRIVE_ROOT}")
    print()

    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    root_id = get_or_create_folder(service, DRIVE_ROOT)
    print(f"  Drive 폴더 확인: {DRIVE_ROOT} (id={root_id})")
    print()

    stats = {'uploaded': 0, 'skipped': 0}
    sync_folder(service, LOCAL_ROOT, root_id, stats)

    # erp/ 소스 백업 — 실패해도 wiki 동기화 결과에는 영향 없음
    try:
        erp_stats = {'uploaded': 0, 'skipped': 0}
        sync_erp_sources(service, erp_stats)
        print(f"  [erp] 소스 백업 — 업로드 {erp_stats['uploaded']}개 / 건너뜀 {erp_stats['skipped']}개 (Drive {ERP_DRIVE})")
    except Exception as e:
        print(f"  [erp] 소스 백업 실패: {type(e).__name__}: {e}")
    print()
    print(f"  ✅ 동기화 완료 — 업로드 {stats['uploaded']}개 / 건너뜀 {stats['skipped']}개")
    print(f"  Google Drive: https://drive.google.com/drive/folders/{root_id}")
