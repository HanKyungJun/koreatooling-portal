#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""접수 시트에 「견적문의」 탭 만들기 (일회성)    2026-10-28 Cowork 신설

왜: 견적 문의 웹폼(estimate.html) → Apps Script(netlify_to_sheets.gs)는 「견적문의」 탭에 줄을 쓴다.
    그런데 setup_sheets.py 가 이 탭을 만들지 않아서, 탭이 없으면 Apps Script 가
    「sheet not found: 견적문의」로 멈추고 시트 · 메일 어디에도 남지 않는다(2026-10-28 코드 확인).

헤더 13칸 = netlify_to_sheets.gs buildRow('estimate-form') 순서 그대로.

사용 (cnc-wiki 폴더에서):
  python scripts\setup_estimate_tab.py           # 확인만(아무것도 안 바꿈)
  python scripts\setup_estimate_tab.py --apply   # 탭이 없으면 만들고 헤더를 넣는다
이미 탭이 있으면 헤더만 비교해서 보여 주고 아무것도 바꾸지 않는다.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TAB = '견적문의'
HEADERS = ['접수일시', '회사명', '담당자', '연락처', '이메일', '구분', '재질',
           '규격', '수량', '희망납기', '월예상수량', '참고사항', '첨부파일']


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    apply = '--apply' in sys.argv
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, '.env'))
    except Exception:
        pass
    sid = os.getenv('FORM_SHEET_ID', '').strip().strip('"')
    if not sid:
        print('FORM_SHEET_ID 가 .env 에 없습니다 — 중단'); return 1
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    tok = os.path.join(ROOT, 'token_sheets.json')
    creds = Credentials.from_authorized_user_file(tok, ['https://www.googleapis.com/auth/spreadsheets'])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(tok, 'w', encoding='utf-8') as f:
            f.write(creds.to_json())
    svc = build('sheets', 'v4', credentials=creds)
    meta = svc.spreadsheets().get(spreadsheetId=sid, fields='sheets.properties(title,index)').execute()
    titles = [s['properties']['title'] for s in meta['sheets']]
    print('지금 탭:', ' · '.join(titles))
    if TAB in titles:
        cur = svc.spreadsheets().values().get(spreadsheetId=sid, range=f'{TAB}!A1:Z1').execute().get('values', [[]])
        cur = cur[0] if cur else []
        print(f'「{TAB}」 탭이 이미 있습니다 — 바꾸지 않음')
        print('  지금 헤더:', cur)
        print('  기대 헤더:', HEADERS, '(같음)' if cur == HEADERS else '(다름 — 손으로 확인)')
        return 0
    if not apply:
        print(f'「{TAB}」 탭이 없습니다. 만들려면: python scripts\\setup_estimate_tab.py --apply')
        return 0
    svc.spreadsheets().batchUpdate(spreadsheetId=sid, body={'requests': [
        {'addSheet': {'properties': {'title': TAB, 'index': len(titles)}}}]}).execute()
    svc.spreadsheets().values().update(spreadsheetId=sid, range=f'{TAB}!A1',
                                       valueInputOption='RAW', body={'values': [HEADERS]}).execute()
    chk = svc.spreadsheets().values().get(spreadsheetId=sid, range=f'{TAB}!A1:Z1').execute().get('values', [[]])[0]
    print(f'「{TAB}」 탭 생성 · 헤더 {len(chk)}칸:', chk)
    print('다음: 웹폼에서 시험 제출 1건 → 시트에 줄이 생기는지 · 알림 메일이 오는지 확인')
    return 0


if __name__ == '__main__':
    sys.exit(main())
