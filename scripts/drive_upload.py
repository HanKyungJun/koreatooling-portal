#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
작은 텍스트 파일 하나를 구글 드라이브에 바로 올린다 (16:30 전체 동기화를 기다리지 않음).
쓰는 곳: scripts/export_calendar_data.py · scripts/export_worklog_material.py

2026-11-19 신규 (decisions 2026-11-19 (4) · (5)) — 새 PC 이전
  - 16:30 「cnc-wiki Drive 동기화」는 로그가 없고 11-17 은 중간에 멈춘 흔적 · 11-18 은 올린 파일 0
    (드라이브 수정 시각 실측) → 캘린더 · 업무일지 재료는 그 동기화에 기대지 않고 여기서 바로 올린다.
  - 토큰은 sync_to_gdrive.py 와 같은 token.json(drive.file 범위). 🔴 갱신이 안 되면 브라우저 로그인
    (InstalledAppFlow)을 띄우지 않고 실패만 돌려준다 — 숨김 배치(16:00)가 멈추지 않게.
  - 네트워크 대기는 60초까지(socket 기본 시간 제한).
  - 드라이브 위치: 내 드라이브 / cnc-wiki-auto / <파일 이름>. 같은 이름이 있으면 그 파일을 덮어쓴다(ID 유지).
"""
import os, socket
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DRIVE_FOLDER = 'cnc-wiki-auto'
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def _env(key, default):
    v = os.environ.get(key)
    if v:
        return v
    env = BASE / '.env'
    if env.exists():
        for line in env.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, val = line.partition('=')
                if k.strip() == key:
                    return val.strip()
    return default


def _service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    token = BASE / _env('GOOGLE_TOKEN_FILE', 'token.json')
    if not token.exists():
        raise RuntimeError(f'token 없음: {token.name}')
    creds = Credentials.from_authorized_user_file(str(token), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token.write_text(creds.to_json(), encoding='utf-8')
        else:
            raise RuntimeError('token 갱신 불가 — scripts/sync_to_gdrive.py 를 손으로 한 번 실행해 다시 로그인')
    return build('drive', 'v3', credentials=creds, cache_discovery=False)


def upload_text(local_path, name=None):
    """local_path 파일을 드라이브 cnc-wiki-auto/<name> 에 올린다. 돌려주는 값: ('신규'|'업데이트', fileId)"""
    from googleapiclient.http import MediaFileUpload
    old = socket.getdefaulttimeout()
    socket.setdefaulttimeout(60)
    try:
        svc = _service()
        name = name or Path(local_path).name
        q = (f"name='{DRIVE_FOLDER}' and mimeType='application/vnd.google-apps.folder' "
             "and 'root' in parents and trashed=false")
        found = svc.files().list(q=q, fields='files(id)', pageSize=10).execute().get('files', [])
        if found:
            folder = found[0]['id']
        else:
            folder = svc.files().create(body={'name': DRIVE_FOLDER,
                                              'mimeType': 'application/vnd.google-apps.folder'},
                                        fields='id').execute()['id']
        q = f"name='{name}' and '{folder}' in parents and trashed=false"
        files = svc.files().list(q=q, fields='files(id, modifiedTime)', orderBy='modifiedTime desc',
                                 pageSize=10).execute().get('files', [])
        media = MediaFileUpload(str(local_path), mimetype='text/plain', resumable=False)
        if files:
            svc.files().update(fileId=files[0]['id'], media_body=media).execute()
            return '업데이트', files[0]['id']
        f = svc.files().create(body={'name': name, 'parents': [folder]}, media_body=media,
                               fields='id').execute()
        return '신규', f['id']
    finally:
        socket.setdefaulttimeout(old)
