"""
Gmail OAuth 토큰 발급 (최초 1회만 실행)
───────────────────────────────────
실행하면 브라우저가 열립니다.
hzn2001@toolkorea.co.kr 계정으로 로그인 후 권한 허용 → 자동으로 token_gmail.json 저장.
"""

from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES      = ["https://www.googleapis.com/auth/gmail.send"]
SECRET_FILE = Path(__file__).parent.parent / "client_secret_gmail.json"
TOKEN_FILE  = Path(__file__).parent / "token_gmail.json"

if TOKEN_FILE.exists():
    print(f"이미 토큰이 있습니다: {TOKEN_FILE}")
    print("재발급하려면 token_gmail.json 삭제 후 다시 실행하세요.")
else:
    flow = InstalledAppFlow.from_client_secrets_file(str(SECRET_FILE), SCOPES)
    creds = flow.run_local_server(port=0)

    # 토큰 저장
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    print(f"\n✅ 토큰 저장 완료: {TOKEN_FILE}")
    print("이제 daily_dlv_alert.py 를 실행하면 이메일이 발송됩니다.")
