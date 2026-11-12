# -*- coding: utf-8 -*-
"""2차: 바이너리·오피스·UTF-16 파일 내용 계층 스캔"""
import os, re, subprocess, zipfile, sys

REPO = os.environ.get('CNC_WIKI_ROOT') or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

SECRET = [
    ('GitHub PAT', re.compile(r'gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}')),
    ('Google API key', re.compile(r'AIza[0-9A-Za-z_\-]{35}')),
    ('Google OAuth secret', re.compile(r'GOCSPX-[A-Za-z0-9_\-]{20,}')),
    ('AWS key', re.compile(r'AKIA[0-9A-Z]{16}')),
    ('Slack token', re.compile(r'xox[baprs]-[0-9A-Za-z\-]{10,}')),
    ('Private key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('JWT', re.compile(r'eyJ[A-Za-z0-9_\-]{15,}\.eyJ[A-Za-z0-9_\-]{15,}\.')),
    ('conn string pwd', re.compile(r'(?:mssql|mysql|postgres(?:ql)?|mongodb)://[^:\s/@]+:[^@\s]{3,}@')),
    ('ODBC pwd', re.compile(r'(?i)(?:pwd|password)\s*=\s*[^\s;\'"<>]{4,}\s*;')),
    ('비밀번호 하드코딩', re.compile(r'(?i)(?:password|passwd|secret|token|api[_\-]?key|앱비밀번호|비밀번호)\s*[=:]\s*[\'"][^\'"\s${}<>]{8,}[\'"]')),
]
SAFE = re.compile(r'(?i)REDACTED|\*{3,}|placeholder|your[_\- ]?(?:token|key)|여기에|getenv|environ|\$\{')
CONF = re.compile(r'단가|금액|견적|정가|매출|원가|청구|입금|세금계산서|unit\s*price')

def scan(text, label, hits, conf):
    for i, line in enumerate(text.splitlines(), 1):
        line = line[:4000]
        for name, rx in SECRET:
            if rx.search(line) and not SAFE.search(line):
                sn = line.strip()[:150]
                hits.append((name, label, i, sn))
    m = CONF.findall(text)
    if m:
        from collections import Counter
        conf[label] = Counter(m).most_common(4)

def tracked(pat):
    r = subprocess.run(['git', '--no-optional-locks', 'ls-files'], cwd=REPO,
                       capture_output=True)
    return [p for p in r.stdout.decode('utf-8','replace').split('\n')
            if p and re.search(pat, p, re.I)]

hits, conf, errs = [], {}, []

# --- UTF-16 등 NUL 포함 텍스트 파일 ---
u16 = 0
for rel in tracked(r'\.(html|css|js|txt|md|json|csv)$'):
    full = os.path.join(REPO, rel)
    raw = open(full, 'rb').read()
    if b'\x00' not in raw[:8192]:
        continue
    u16 += 1
    for enc in ('utf-16', 'utf-16-le', 'utf-16-be', 'latin-1'):
        try:
            txt = raw.decode(enc)
            break
        except Exception:
            continue
    scan(txt, rel + ' [%s]' % enc, hits, conf)
print('■ NUL 포함 텍스트 파일 %d건 디코딩 후 스캔 완료' % u16)

# --- 오피스 파일 (zip 내부 XML) ---
off = 0
for rel in tracked(r'\.(xlsx|xlsm|docx|pptx|potx)$'):
    full = os.path.join(REPO, rel)
    try:
        with zipfile.ZipFile(full) as z:
            buf = []
            for info in z.infolist():
                if info.file_size > 12 * 1024 * 1024:
                    continue
                if not re.search(r'\.(xml|rels|txt)$', info.filename, re.I):
                    continue
                try:
                    buf.append(z.read(info).decode('utf-8', 'replace'))
                except Exception:
                    pass
            off += 1
            scan('\n'.join(buf), rel, hits, conf)
    except Exception as e:
        errs.append((rel, repr(e)[:80]))
print('■ 오피스 파일 %d건 내부 XML 스캔 완료 (실패 %d건)' % (off, len(errs)))

# --- exe / tom / 기타 바이너리: strings 방식 ---
binn = 0
for rel in tracked(r'\.(exe|tom|spec|jpg|png|url|vbs)$'):
    full = os.path.join(REPO, rel)
    try:
        raw = open(full, 'rb').read()
    except OSError as e:
        errs.append((rel, repr(e)[:80])); continue
    binn += 1
    tbl = bytes((c if 0x20 <= c <= 0x7e else 0x0a) for c in range(256))
    CH = 4 * 1024 * 1024
    for off_ in range(0, len(raw), CH):
        chunk = raw[off_:off_ + CH + 256]
        scan(chunk.translate(tbl).decode('ascii', 'replace'),
             rel + ' [strings@%dMB]' % (off_ // (1024 * 1024)), hits, {})
    del raw
print('■ 바이너리 %d건 strings 스캔 완료' % binn)
print()
print('=' * 70)
print('■ 시크릿 적출 %d건' % len(hits))
for name, label, i, sn in hits:
    print('  🔴 [%s] %s:%d' % (name, label, i))
    print('      %s' % sn)
print()
print('■ 대외비 키워드(단가·금액 등) 포함 파일 %d건 — 상위 25건' % len(conf))
for k, v in sorted(conf.items(), key=lambda x: -sum(c for _, c in x[1]))[:25]:
    print('   %-72s %s' % (k[:72], v))
if errs:
    print()
    print('■ 처리 실패 %d건' % len(errs))
    for e in errs:
        print('   ', e)
