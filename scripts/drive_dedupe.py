# -*- coding: utf-8 -*-
"""Drive 중복 파일 정리 — sync_to_gdrive.py 가 올린 cnc-wiki · cnc-wiki-erp 폴더 안에서
같은 폴더 · 같은 이름 파일이 여러 개면 가장 최근 것(modifiedTime)만 남기고 나머지를 휴지통으로 보낸다.
.bak 파일(작업 백업)은 2026-11-20 부터 올리지 않으므로 함께 정리 대상으로 표시한다.

  python scripts/drive_dedupe.py            목록만 만든다(아무것도 안 바꿈) → outputs/drive_dedupe_YYYYMMDD.csv
  python scripts/drive_dedupe.py --apply    목록의 「정리」 행을 Drive 휴지통으로(30일 안에 복구 가능, 영구 삭제 아님)

이 앱이 올린 파일만 보인다(drive.file 권한). 사람이 직접 올린 파일은 보이지도 바뀌지도 않는다.
근거: worklog 2026-11-20 · 중복 원인 = 옛 get_drive_files 가 첫 100개만 읽음(같은 날 수정)
"""
import csv
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync_to_gdrive as s  # noqa: E402  (인증 · 폴더 함수 재사용)
from googleapiclient.discovery import build  # noqa: E402

KST = timezone(timedelta(hours=9))
ROOTS = [s.DRIVE_ROOT, s.ERP_DRIVE]
FOLDER = 'application/vnd.google-apps.folder'


def list_children(service, folder_id):
    q = f"'{folder_id}' in parents and trashed=false"
    out, token = [], None
    while True:
        res = service.files().list(q=q, pageSize=1000, pageToken=token,
                                   fields='nextPageToken, files(id, name, mimeType, modifiedTime, size, md5Checksum)').execute()
        out += res.get('files', [])
        token = res.get('nextPageToken')
        if not token:
            return out


def find_root(service, name):
    q = f"name='{name}' and mimeType='{FOLDER}' and trashed=false and 'root' in parents"
    files = service.files().list(q=q, fields='files(id)').execute().get('files', [])
    return files[0]['id'] if files else None


def plan(service, folder_id, path, rows):
    kids = list_children(service, folder_id)
    groups = {}
    for f in kids:
        if f['mimeType'] == FOLDER:
            plan(service, f['id'], f"{path}/{f['name']}", rows)
        else:
            groups.setdefault(f['name'], []).append(f)
    for name, fs in groups.items():
        fs.sort(key=lambda f: f['modifiedTime'], reverse=True)
        is_bak = '.bak_' in name or name.endswith('.bak')
        for i, f in enumerate(fs):
            if is_bak:
                act, why = '정리', '작업 백업(.bak) — 더 이상 올리지 않음'
            elif i == 0:
                act, why = '남김', '가장 최근' if len(fs) > 1 else '하나뿐'
            else:
                same = f.get('md5Checksum') and f.get('md5Checksum') == fs[0].get('md5Checksum')
                act, why = '정리', '중복 — 내용 같음' if same else '중복 — 옛 판(내용 다름)'
            if act == '정리' or len(fs) > 1:
                rows.append({'act': act, 'why': why, 'path': f'{path}/{name}', 'id': f['id'],
                             'modified_kst': s.drive_mtime(f['modifiedTime']).astimezone(KST).strftime('%Y-%m-%d %H:%M'),
                             'size': f.get('size', ''), 'copies': len(fs)})


def main():
    apply = '--apply' in sys.argv[1:]
    service = build('drive', 'v3', credentials=s.get_credentials())
    rows = []
    for name in ROOTS:
        rid = find_root(service, name)
        if rid:
            plan(service, rid, name, rows)
        else:
            print(f'  (폴더 없음: {name})')
    out = os.path.join('outputs', f"drive_dedupe_{datetime.now(KST):%Y%m%d}.csv")
    os.makedirs('outputs', exist_ok=True)
    with open(out, 'w', encoding='utf-8-sig', newline='') as fp:
        w = csv.DictWriter(fp, fieldnames=['act', 'why', 'path', 'id', 'modified_kst', 'size', 'copies'])
        w.writeheader()
        w.writerows(rows)
    todo = [r for r in rows if r['act'] == '정리']
    dup = sum(1 for r in todo if r['why'].startswith('중복'))
    diff = sum(1 for r in todo if '내용 다름' in r['why'])
    bak = len(todo) - dup
    print(f'  목록: {out}')
    print(f'  정리 대상 {len(todo)}개 — 중복 {dup}개(그중 내용 다른 옛 판 {diff}개) · .bak {bak}개')
    if not apply:
        print('  (목록만 만듦 — 아무것도 안 바꿈. 휴지통으로 보내려면 --apply)')
        return 0
    n = 0
    for r in todo:
        service.files().update(fileId=r['id'], body={'trashed': True}).execute()
        n += 1
    print(f'  휴지통으로 보냄: {n}개 (Drive 휴지통에서 30일 안에 복구 가능)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
