#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
캘린더 사본(private_local\calendar\weekly-calendar-overview.html) → 구글 드라이브용 데이터 파일
실행: python scripts/export_calendar_data.py [--days=N]
출력: private_local\calendar\calendar_data.txt → 구글 드라이브 「cnc-wiki-auto/calendar_data.txt」 바로 올림
      (scripts/drive_upload.py · 16:30 전체 동기화와 무관 — 11-17 · 11-18 동기화 누락 실측)

2026-11-19 신규 (decisions 2026-11-19 (4)) — 새 PC 이전
  - 새 데스크톱 앱은 아티팩트를 앱 내부 폴더에 둬서 파이썬이 못 고치고, Claude 예약 실행에는
    아티팩트를 고치는 도구(update_artifact)가 없다(11-19 13:43 시험).
  - 그래서 「Weekly Calendar Overview」 아티팩트가 열릴 때 구글 드라이브의 이 파일을 직접 읽어
    PROD(일일보고 실적) · CLAUDE_WORK(Claude 작업)를 덮어쓴다.
  - 드라이브 읽기 도구는 파일을 마크다운처럼 바꿔(\[ \_ 이스케이프 · 이모지 깨짐) 돌려주므로
    JSON 을 UTF-8 → 16진수(0-9a-f)로 바꿔 CALDATABEGIN ~ CALDATAEND 사이에 넣는다.
  - 넣는 기간: private_local\calendar\artifact_base.txt 날짜(아티팩트 안 데이터를 마지막으로
    통째로 갱신한 날) 7일 전부터. 그 이전 값은 아티팩트 안에 이미 있다. 파일이 없으면 최근 62일.
    파일이 커지면(수개월 뒤) 대화 세션에서 아티팩트를 사본으로 한 번 갱신하고 이 날짜를 바꾼다.
  - 데이터가 그대로면 파일을 다시 쓰지 않는다(드라이브 재업로드 방지).
"""
import sys, io, re, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE     = Path(__file__).resolve().parent.parent
SRC      = Path(os.environ.get('CALENDAR_HTML') or
                BASE / 'private_local' / 'calendar' / 'weekly-calendar-overview.html')
OUT      = Path(os.environ.get('CALENDAR_DATA') or SRC.parent / 'calendar_data.txt')
MARK     = OUT.with_suffix('.uploaded')   # 마지막으로 올린 데이터의 sha
BASEFILE = SRC.parent / 'artifact_base.txt'
LOG      = BASE / 'wiki' / 'reports' / 'daily' / 'run.log'
KST      = timezone(timedelta(hours=9))

PROD_LINE = re.compile(r'^\s*"(\d{4}-\d{2}-\d{2})":(\{.*\}),?\s*$')
WORK_LINE = re.compile(r'^\s*"(\d{4}-\d{2}-\d{2})":\[(.*)\],?\s*$')
WORK_ITEM = re.compile(r'\{t:"((?:[^"\\]|\\.)*)",l:"((?:[^"\\]|\\.)*)"\}')


def log(msg):
    print(msg)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass


def block(html: str, start: str) -> list:
    """`const NAME = {` 부터 맨 앞 `};` 까지의 줄."""
    s = html.find(start)
    if s < 0:
        raise ValueError(f'{start!r} 없음')
    e = html.find('\n};', s)
    if e < 0:
        raise ValueError(f'{start!r} 끝 없음')
    return html[s:e].split('\n')[1:]


def parse(html: str, since: str):
    prod, work = {}, {}
    for line in block(html, 'const PROD = {'):
        m = PROD_LINE.match(line)
        if m and m.group(1) >= since:
            prod[m.group(1)] = json.loads(m.group(2))
    for line in block(html, 'const CLAUDE_WORK = {'):
        m = WORK_LINE.match(line)
        if m and m.group(1) >= since:
            items = [{'t': json.loads(f'"{t}"'), 'l': json.loads(f'"{l}"')}
                     for t, l in WORK_ITEM.findall(m.group(2))]
            if items:
                work[m.group(1)] = items
    return prod, work


def main():
    days = None
    for a in sys.argv[1:]:
        if a.startswith('--days='):
            days = int(a.split('=', 1)[1])
    if not SRC.exists():
        log(f'[calendar-data] ERROR - source not found: {SRC}')
        sys.exit(1)
    if days is not None:
        since = (date.today() - timedelta(days=days)).isoformat()
    elif BASEFILE.exists():
        base = date.fromisoformat(BASEFILE.read_text(encoding='utf-8').strip()[:10])
        since = (base - timedelta(days=7)).isoformat()
    else:
        since = (date.today() - timedelta(days=62)).isoformat()
    try:
        prod, work = parse(SRC.read_text(encoding='utf-8'), since)
    except Exception as ex:
        log(f'[calendar-data] ERROR - parse failed: {ex}')
        sys.exit(1)
    if any(v is None for p in prod.values() for k, v in p.items() if k == 'total'):
        log('[calendar-data] ERROR - PROD total 이 비어 있음 — 쓰지 않음')
        sys.exit(1)

    payload = {'prod': prod, 'work': work}
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    sha = f'sha={len(body)}:{hash_of(body)}'
    if OUT.exists() and sha in OUT.read_text(encoding='utf-8'):
        if MARK.exists() and MARK.read_text(encoding='utf-8').strip() == sha:
            log(f'[calendar-data] SKIP - no change ({len(prod)} prod / {len(work)} work days)')
            return
    else:
        now = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
        payload['generated'] = now
        hexs = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8').hex()
        lines = [hexs[i:i + 100] for i in range(0, len(hexs), 100)]
        text = ('cnc-wiki calendar data (Weekly Calendar Overview 아티팩트가 읽음 - 손으로 고치지 말 것)\n'
                f'generated {now} KST · since {since} · {sha}\n'
                'CALDATABEGIN\n' + '\n'.join(lines) + '\nCALDATAEND\n')
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding='utf-8')
        log(f'[calendar-data] OK - {len(prod)} prod / {len(work)} work days since {since} -> {OUT.name}')
    if '--no-upload' in sys.argv:
        return
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from drive_upload import upload_text
        action, fid = upload_text(OUT)
        MARK.write_text(sha, encoding='utf-8')
        log(f'[calendar-data] DRIVE {action} - cnc-wiki-auto/{OUT.name}')
    except Exception as ex:
        log(f'[calendar-data] ERROR - drive upload failed: {type(ex).__name__}: {ex}')


def hash_of(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]


if __name__ == '__main__':
    main()
