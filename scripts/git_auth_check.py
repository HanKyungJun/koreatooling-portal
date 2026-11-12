#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""GitHub 인증 방식 바꾸기 전 확인 — 실제로 올리지 않는다(push --dry-run)    2026-10-30 Cowork

목적: generate.py 가 매 실행마다 토큰을 .git/config 의 origin 주소에 평문으로 써넣는 방식(tasks 「PAT 평문 상주」)을
      「origin 주소는 토큰 없이 · push 때만 인증 헤더를 명령에 실어 보내는」 방식으로 바꾸기 전에,
      새 방식으로 GitHub 쓰기 인증이 되는지 `git push --dry-run`(서버에 접속해 권한만 확인, 실제로 올리지 않음)으로 확인한다.

실행(PowerShell, cnc-wiki 폴더에서):
    python scripts\git_auth_check.py

바꾸는 것 없음 — .git/config · 원격 저장소 모두 그대로. 토큰은 화면에 찍지 않는다.
"""
import base64
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, '.env'))
except ImportError:
    pass

TOKEN = os.getenv('GITHUB_TOKEN', '')
USER = os.getenv('GITHUB_USER', 'HanKyungJun')
REPO = os.getenv('GITHUB_REPO', 'koreatooling-portal')
if not TOKEN:
    sys.exit('GITHUB_TOKEN 이 .env 에 없음 — 확인 중단')

auth = base64.b64encode(f'{USER}:{TOKEN}'.encode()).decode()
clean = f'https://github.com/{USER}/{REPO}.git'
env = os.environ.copy()
env['GIT_TERMINAL_PROMPT'] = '0'
env['GCM_INTERACTIVE'] = 'never'


def mask(s):
    return (s or '').replace(TOKEN, '***').replace(auth, '***')


def run(args, label):
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, timeout=60)
    out = mask((r.stdout or '').strip())
    err = mask((r.stderr or '').strip())
    first = out.splitlines()[0] if out else ''
    print(f'[{label}] code={r.returncode} {first[:60]}')
    if r.returncode != 0 and err:
        print('   ' + err[:300])
    return r.returncode


# ① 새 방식: 토큰 없는 주소 + 인증 헤더(이 명령에서만) · 자격 증명 관리자 끔 · --dry-run = 실제로 올리지 않음
c1 = run(['git', '-c', 'credential.helper=',
          '-c', f'http.https://github.com/.extraheader=AUTHORIZATION: basic {auth}',
          'push', '--dry-run', clean, 'main'], '새 방식(헤더) push 시험')
# ② 대조: 헤더 없이 — 쓰기 인증이 없으니 실패해야 정상(= ①이 헤더 덕분에 통과했다는 증거)
c2 = run(['git', '-c', 'credential.helper=', 'push', '--dry-run', clean, 'main'], '헤더 없이(대조, 실패가 정상)')
print()
if c1 == 0 and c2 != 0:
    print('판정: 새 방식으로 쓰기 인증 OK(헤더 없으면 실패 확인) — generate.py 를 바꿔도 된다.')
elif c1 == 0:
    print('판정: 새 방식 OK 이지만 헤더 없이도 통과 — 다른 저장 자격 증명이 쓰였을 수 있음. Cowork 에 결과를 붙여 주세요.')
else:
    print('판정: 새 방식 실패 — generate.py 는 바꾸지 않는다. 위 오류를 Cowork 에 붙여 주세요.')
