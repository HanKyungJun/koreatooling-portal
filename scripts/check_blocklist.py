# -*- coding: utf-8 -*-
"""공개 저장소 차단어 검사 — 사내 서버 주소 · IP 처럼 거래처 실명 대조표에 없는 값을 커밋 전에 막는다.

차단어 목록은 공개 저장소 밖 `private_local/public_blocklist.txt` 에 둔다(한 줄에 하나, # 주석).
이 파일에는 차단어를 적지 않는다(적으면 이 파일이 곧 노출이 된다).

  python scripts/check_blocklist.py --staged   커밋할 파일(스테이징된 내용)만 검사 — pre-commit 훅이 부름
  python scripts/check_blocklist.py --all      추적 파일 + 새 파일(.gitignore 제외) 전체 검사

차단어가 나오면 종료 코드 1. 목록 파일이 없으면 경고만 하고 0(목록 없는 PC 에서 커밋이 막히지 않게).
근거: decisions 2026-11-20 (6)
"""
import io
import subprocess
import sys
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LIST = BASE / 'private_local' / 'public_blocklist.txt'
OFFICE = {'.docx', '.xlsx', '.pptx'}
SKIP = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.exe', '.zip', '.step', '.stp', '.sc', '.dxf', '.ico', '.woff', '.woff2'}


def git(*args):
    r = subprocess.run(['git', '--no-optional-locks', '-C', str(BASE), *args],
                       capture_output=True, timeout=120)
    if r.returncode != 0:
        raise SystemExit(f'[blocklist] git {args[0]} 실패: {r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout


def load_words():
    if not LIST.exists():
        print(f'[blocklist] 경고: 차단어 목록 없음({LIST.relative_to(BASE)}) — 검사 건너뜀')
        return []
    words = []
    for line in LIST.read_text(encoding='utf-8-sig').splitlines():
        w = line.strip()
        if w and not w.startswith('#'):
            words.append(w.lower())
    return words


def texts(name, data):
    """파일 내용을 (위치, 글) 목록으로. 오피스 파일은 안쪽 xml 을 본다."""
    ext = Path(name).suffix.lower()
    if ext in SKIP:
        return []
    if ext in OFFICE:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                return [(n, z.read(n).decode('utf-8', 'ignore')) for n in z.namelist() if n.endswith('.xml')]
        except zipfile.BadZipFile:
            return []
    if b'\x00' in data[:4096]:
        return []
    return [('', data.decode('utf-8', 'ignore'))]


def scan(items, words):
    hits = 0
    for name, data in items:
        for part, s in texts(name, data):
            low = s.lower()
            for w in words:
                if w in low:
                    for no, line in enumerate(s.splitlines(), 1):
                        if w in line.lower():
                            where = f'{name}{"#" + part if part else ""}:{no}'
                            print(f'  {where}  차단어 {words.index(w) + 1}번')
                            hits += 1
                            break
    return hits


def staged_items():
    names = git('diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z').decode('utf-8').split('\0')
    for n in filter(None, names):
        yield n, git('show', f':{n}')


def all_items():
    names = git('ls-files', '--cached', '--others', '--exclude-standard', '-z').decode('utf-8').split('\0')
    for n in filter(None, names):
        p = BASE / n
        if p.is_file():
            yield n, p.read_bytes()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--staged'
    if mode not in ('--staged', '--all'):
        raise SystemExit(__doc__)
    words = load_words()
    if not words:
        return 0
    hits = scan(staged_items() if mode == '--staged' else all_items(), words)
    if hits:
        print(f'[blocklist] 공개하면 안 되는 값 {hits}곳 — 위 파일에서 지운 뒤 다시 커밋하세요')
        return 1
    print(f'[blocklist] 차단어 {len(words)}개 — 0곳')
    return 0


if __name__ == '__main__':
    sys.exit(main())
