# -*- coding: utf-8 -*-
"""추적 파일 시크릿 전수 스캔 (내용 계층).
- 대조군(--selftest) 을 먼저 통과해야 본 스캔 결과를 신뢰한다.
"""
import os, re, subprocess, sys

REPO = os.environ.get('CNC_WIKI_ROOT') or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

PATTERNS = [
    ('GitHub PAT (classic)',      re.compile(r'ghp_[A-Za-z0-9]{36}')),
    ('GitHub PAT (fine-grained)', re.compile(r'github_pat_[A-Za-z0-9_]{40,}')),
    ('GitHub OAuth/App',          re.compile(r'gh[osur]_[A-Za-z0-9]{36}')),
    ('Google API key',            re.compile(r'AIza[0-9A-Za-z_\-]{35}')),
    ('Google OAuth client secret',re.compile(r'GOCSPX-[A-Za-z0-9_\-]{20,}')),
    ('AWS access key id',         re.compile(r'AKIA[0-9A-Z]{16}')),
    ('Slack token',               re.compile(r'xox[baprs]-[0-9A-Za-z\-]{10,}')),
    ('Private key block',         re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----')),
    ('JSON private_key field',    re.compile(r'"private_key"\s*:\s*"-----BEGIN')),
    ('JWT',                       re.compile(r'eyJ[A-Za-z0-9_\-]{15,}\.eyJ[A-Za-z0-9_\-]{15,}\.')),
    ('DB conn string w/ password',re.compile(r'(?:mssql|mysql|postgres(?:ql)?|mongodb(?:\+srv)?|redis)://[^:\s/@]+:[^@\s]{3,}@')),
    ('ODBC/ADO password',         re.compile(r'(?i)(?:pwd|password)\s*=\s*[^\s;\'"]{4,}\s*;')),
    ('Gmail app password (16자)', re.compile(r'(?i)(?:pass|pwd|password|비밀번호)\s*[=:]\s*[\'"]?[a-z]{16}[\'"]?(?![a-z])')),
    ('Gmail app password (4x4)',  re.compile(r'[\'"][a-z]{4}\s[a-z]{4}\s[a-z]{4}\s[a-z]{4}[\'"]')),
    ('일반 비밀번호 하드코딩',      re.compile(r'(?i)(?:password|passwd|pwd|secret|token|api[_\-]?key|apikey|access[_\-]?key|앱비밀번호|비밀번호)\s*[=:]\s*[\'"][^\'"\s${}]{8,}[\'"]')),
    ('Bearer 토큰 리터럴',         re.compile(r'(?i)bearer\s+[A-Za-z0-9\-_\.]{20,}')),
    # 2026-09-08 추가 — portal.js 의 GAS 배포 URL 이 기존 패턴에 걸리지 않았다.
    ('GAS 웹앱 배포 URL',          re.compile(r'AKfycb[A-Za-z0-9_\-]{20,}')),
    ('OpenAI/Anthropic 키',        re.compile(r'sk-(?:ant-)?[A-Za-z0-9\-_]{20,}')),
    ('Notion 토큰',                re.compile(r'\b(?:ntn_|secret_)[A-Za-z0-9]{30,}')),
    ('Kakao/Naver REST 키',        re.compile(r'(?i)(?:kakao|naver)[_\-]?(?:rest)?[_\-]?(?:api)?[_\-]?key\s*[=:]\s*[\'"][0-9a-f]{32}[\'"]')),
    ('서비스계정 client_email',     re.compile(r'"client_email"\s*:\s*"[^"]+@[^"]+\.iam\.gserviceaccount\.com"')),
    ('Twilio/SendGrid 키',         re.compile(r'\bSK[0-9a-f]{32}\b|\bSG\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}')),
]

# 오탐 억제 — 값이 실제 시크릿이 아닌 것이 명백한 경우
SAFE = [
    re.compile(r'(?i)(?:REDACTED|\*{3,}|xxx+|placeholder|your[_\- ]?(?:token|key|password)|여기에|입력하세요|예시|sample|dummy|changeme|<[^>]+>)'),
    re.compile(r'os\.getenv|os\.environ|getenv\(|\$\{|%\(|process\.env'),
]

def scan_text(text, label, out):
    for i, line in enumerate(text.splitlines(), 1):
        if len(line) > 4000:
            line = line[:4000]
        for name, rx in PATTERNS:
            m = rx.search(line)
            if not m:
                continue
            if any(s.search(line) for s in SAFE):
                continue
            snippet = line.strip()
            if len(snippet) > 160:
                snippet = snippet[:160] + '…'
            out.append((label, i, name, snippet))

def tracked_files():
    r = subprocess.run(['git', '--no-optional-locks', 'ls-files', '-z'],
                       cwd=REPO, capture_output=True)
    return [p for p in r.stdout.decode('utf-8', 'replace').split('\0') if p]

def is_probably_text(path):
    try:
        with open(path, 'rb') as f:
            chunk = f.read(8192)
    except OSError:
        return False
    if b'\x00' in chunk:
        return False
    return True

def main():
    if '--selftest' in sys.argv:
        # 대조군: 실제 시크릿 형태를 심어 스캐너가 잡는지 확인
        control = '\n'.join([
            'TOKEN = "ghp_' + 'A' * 36 + '"',
            'GOOGLE = "AIza' + 'B' * 35 + '"',
            'AWS_ID = "AKIA' + 'C' * 16 + '"',
            'SLACK = "xoxb-1234567890-abcdefghij"',
            'GOCSPX_TEST = "GOCSPX-' + 'd' * 24 + '"',
            '-----BEGIN RSA PRIVATE KEY-----',
            'CONN = "postgresql://erpuser:hunter2pass@192.168.0.252:5432/trico"',
            'ALERT_EMAIL_PASS = "abcdefghijklmnop"',
            'app_pw = "abcd efgh ijkl mnop"',
            'DB_PASSWORD = "Toolkorea!2026"',
            'headers = {"Authorization": "Bearer abcdefghijklmnopqrstuvwxyz012345"}',
            'ODBC = "Driver={SQL Server};Server=x;Uid=sa;Pwd=Secret123;"',
            'PAT2 = "github_pat_11ABCDE' + 'f' * 60 + '"',
            'OAUTH = "gho_' + 'E' * 36 + '"',
            '  "private_key": "-----BEGIN PRIVATE KEY-----MIIEvg",',
            'JWTV = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc"',
            'GAS = "https://script.google.com/macros/s/AKfycb' + 'g' * 40 + '/exec"',
            'OPENAI = "sk-ant-' + 'h' * 40 + '"',
            'NOTION = "ntn_' + 'i' * 40 + '"',
            'KAKAO_REST_KEY = "' + '0' * 32 + '"',
            '  "client_email": "svc@proj.iam.gserviceaccount.com",',
            'SENDGRID = "SG.' + 'j' * 24 + '.' + 'k' * 24 + '"',
        ])
        hits = []
        scan_text(control, '<대조군>', hits)
        names = sorted({h[2] for h in hits})
        print('대조군 심은 유형: 22종 / 검출 유형: %d종' % len(names))
        for n in names:
            print('  ✅', n)
        missed = [n for n, _ in PATTERNS if n not in names]
        print('미검출 패턴(대조군에 미포함이면 정상):')
        for n in missed:
            print('  -', n)
        # 오탐 대조군: 잡히면 안 되는 것들
        benign = '\n'.join([
            "GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')",
            'GITHUB_TOKEN=your_token_here',
            'password = "***REDACTED***"',
            'STAFF_PASS = os.getenv("STAFF_PASS", "1234")',
            'token: <여기에 토큰 입력>',
        ])
        fp = []
        scan_text(benign, '<오탐대조군>', fp)
        print('오탐 대조군 5줄 → 오탐 %d건 %s' % (len(fp), '✅' if not fp else '❌'))
        for f in fp:
            print('   ❌', f)
        return 0 if names and not fp else 1

    files = tracked_files()
    hits, text_n, bin_files, unreadable = [], 0, [], []
    for rel in files:
        full = os.path.join(REPO, rel)
        if not os.path.exists(full):
            unreadable.append(rel)
            continue
        if not is_probably_text(full):
            bin_files.append(rel)
            continue
        try:
            with open(full, encoding='utf-8', errors='replace') as f:
                text = f.read()
        except OSError:
            unreadable.append(rel)
            continue
        text_n += 1
        scan_text(text, rel, hits)

    print('=' * 70)
    print('추적 파일 %d건 / 텍스트 검사 %d건 / 바이너리 제외 %d건 / 읽기실패 %d건'
          % (len(files), text_n, len(bin_files), len(unreadable)))
    print('=' * 70)
    print('■ 내용 계층 적출 %d건' % len(hits))
    for label, ln, name, snippet in hits:
        print('  🔴 [%s] %s:%d' % (name, label, ln))
        print('      %s' % snippet)
    print()
    print('■ 내용 미검사(바이너리) %d건 — 확장자별' % len(bin_files))
    ext = {}
    for b in bin_files:
        ext[b.rsplit('.', 1)[-1].lower() if '.' in b else '(없음)'] = \
            ext.get(b.rsplit('.', 1)[-1].lower() if '.' in b else '(없음)', 0) + 1
    for k, v in sorted(ext.items(), key=lambda x: -x[1]):
        print('   %-10s %3d건' % (k, v))
    if unreadable:
        print()
        print('■ 읽기 실패 %d건' % len(unreadable))
        for u in unreadable[:20]:
            print('   ', u)
    return 0

sys.exit(main())
