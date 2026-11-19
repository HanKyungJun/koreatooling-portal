#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
「주간 정리 제안」용 측정값 → 구글 드라이브 (Claude 예약 작업 「주간 정리 제안 v2」가 읽음)
실행: python scripts/export_weekly_metrics.py [--force] [--no-upload]
      금요일(KST)에만 동작 — 다른 요일은 바로 끝남(--force 로 시험)
출력: private_local\weekly_metrics\YYYY-MM-DD.txt → 드라이브 「cnc-wiki-auto/weekly_metrics.txt」

2026-11-19 신규 (decisions 2026-11-19 (5)) — 새 PC 이전
  - 새 PC 에서는 Claude 예약 실행이 PC 폴더를 못 읽고 명령도 못 돌린다(11-19 14:09 진단).
    옛 예약 프롬프트(CLAUDE.md §15-3)가 device_bash 로 재던 값을 16:00 배치가 대신 재서 올린다.
  - 🔴 읽기 · 드라이런만. slim_tasks.py · archive_handoff.py 는 --apply 없이, git 은 --no-optional-locks 읽기만.
  - 거래처 실명 검사(anonymize_public.py --check)는 종료 코드와 걸린 줄 수만 적는다(실명은 드라이브에 올리지 않음).
"""
import sys, io, os, re, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE    = Path(__file__).resolve().parent.parent
HANDOFF = BASE / 'wiki' / '_handoff'
OUTDIR  = BASE / 'private_local' / 'weekly_metrics'
LOG     = BASE / 'wiki' / 'reports' / 'daily' / 'run.log'
KST     = timezone(timedelta(hours=9))
ENV     = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')


def log(msg):
    print(msg)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass


def run(args, timeout=180):
    try:
        p = subprocess.run(args, cwd=BASE, capture_output=True, timeout=timeout, env=ENV)
        out = (p.stdout or b'').decode('utf-8', 'replace') + (p.stderr or b'').decode('utf-8', 'replace')
        return p.returncode, out
    except Exception as ex:
        return -1, f'{type(ex).__name__}: {ex}'


def kb(p: Path):
    return f'{p.stat().st_size / 1024:.1f} KB' if p.exists() else '없음'


def dir_mb(p: Path):
    if not p.exists():
        return '없음'
    total = 0
    for root, dirs, files in os.walk(p):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return f'{total / 1048576:.1f} MB'


def tail(text, n=15):
    lines = [l for l in text.splitlines() if l.strip()]
    return '\n'.join(lines[-n:]) if lines else '(출력 없음)'


def main():
    today = date.today()
    if today.weekday() != 4 and '--force' not in sys.argv:
        return
    d = today.isoformat()
    monday = (today - timedelta(days=today.weekday())).isoformat()
    now = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
    py = sys.executable
    out = [f'# 주간 정리 측정값 {d}', f'date: {d}', f'generated: {now} KST', '']

    out += ['## 1. 핸드오프 크기 (기준 tasks 40 · decisions 60 · worklog 30 KB)']
    for n in ('tasks.md', 'decisions.md', 'worklog.md', 'sources.md'):
        out.append(f'- {n}: {kb(HANDOFF / n)}')

    rc, o = run([py, 'scripts/slim_tasks.py'])
    out += ['', f'## 2. slim_tasks.py 드라이런 (rc={rc}, 끝 15줄)', tail(o)]
    rc, o = run([py, 'scripts/archive_handoff.py'])
    out += ['', f'## 3. archive_handoff.py 드라이런 (rc={rc}, 끝 15줄)', tail(o)]

    heads = []
    dec = HANDOFF / 'decisions.md'
    if dec.exists():
        for line in dec.read_text(encoding='utf-8-sig').splitlines():
            if line.startswith('## ') and monday <= line[3:13] <= d:
                heads.append(line)
    out += ['', f'## 4. 이번 주({monday} ~ {d}) decisions 제목 {len(heads)}건', *(heads or ['(없음)'])]

    rc, o = run(['git', '--no-optional-locks', '-c', 'core.quotepath=false', 'ls-files'], timeout=60)
    tracked = set(o.splitlines()) if rc == 0 else set()
    baks, baks_tracked = 0, 0
    for root, dirs, files in os.walk(BASE):
        rel_root = os.path.relpath(root, BASE).replace('\\', '/')
        if rel_root.startswith(('.git', '_to_delete')):
            dirs[:] = []
            continue
        for f in files:
            m = re.match(r'(.+)\.bak_', f)
            if m:
                baks += 1
                orig = (m.group(1) if rel_root == '.' else f'{rel_root}/{m.group(1)}')
                if orig in tracked:
                    baks_tracked += 1
    out += ['', '## 5. .bak 파일 (.git · _to_delete 제외)',
            f'- 전체 {baks}개 · 그중 원본이 git 추적 중 {baks_tracked}개' + ('' if rc == 0 else f' (git ls-files 실패 rc={rc})')]

    out += ['', '## 6. 폴더 크기 (기준 outputs 300 MB · _to_delete 500 MB)',
            f'- outputs/: {dir_mb(BASE / "outputs")}', f'- _to_delete/: {dir_mb(BASE / "_to_delete")}']

    rc, o = run([py, 'scripts/anonymize_public.py', '--check'], timeout=300)
    out += ['', '## 7. 거래처 실명 검사 (anonymize_public.py --check)',
            f'- 종료 코드 {rc} (0 = 실명 없음) · 출력 줄 수 {len(o.splitlines())} — 🔴 1 이면 대화 세션에서 --check 원문 확인',
            f'- 마지막 줄: {tail(o, 1)[:120] if rc == 0 else "(실명이 들어 있을 수 있어 생략)"}']

    tasks = HANDOFF / 'tasks.md'
    done_open, p01, p01_chars = [], [], 0
    if tasks.exists():
        for line in tasks.read_text(encoding='utf-8-sig').splitlines():
            if line.startswith('- [ ]') and re.search(r'✅|종결|완료|해소', line.split('—')[0] if '—' in line else line):
                done_open.append(line[:150])
            if line.startswith('- [ ]') and ('(P0,' in line or '(P1,' in line):
                p01.append(line)
                p01_chars += len(line)
    out += ['', f'## 8. 제목에 완료 표시가 있는데 [ ] 로 남은 항목 {len(done_open)}개', *(done_open or ['(없음)'])]

    wl = HANDOFF / 'worklog.md'
    top = ''
    if wl.exists():
        m = re.search(r'^## .*?(?=^## |\Z)', wl.read_text(encoding='utf-8-sig'), re.S | re.M)
        top = m.group(0) if m else ''
    dec3 = sum(len(h) for h in [l for l in (dec.read_text(encoding='utf-8-sig').splitlines() if dec.exists() else [])
                                  if l.startswith('## ')][:3])
    light = len(top) + p01_chars + dec3
    out += ['', '## 9. 가볍게 시작 읽는 양 (기준 3,000자)',
            f'- worklog 맨 위 블록 {len(top)} + P0 · P1 줄 {p01_chars}({len(p01)}줄) + decisions 제목 3줄 {dec3} = {light}자']
    out += ['', '## 10. 프로젝트 메모 목록 — PC 에서 못 잼(예약 실행이 project_memory_read 로 확인)', '', '## END']

    OUTDIR.mkdir(parents=True, exist_ok=True)
    path = OUTDIR / f'{d}.txt'
    path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    log(f'[weekly-metrics] OK - {d} -> {path.name}')
    if '--no-upload' in sys.argv:
        return
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from drive_upload import upload_text
        action, _ = upload_text(path, 'weekly_metrics.txt')
        log(f'[weekly-metrics] DRIVE {action} - cnc-wiki-auto/weekly_metrics.txt')
    except Exception as ex:
        log(f'[weekly-metrics] ERROR - drive upload failed: {type(ex).__name__}: {ex}')


if __name__ == '__main__':
    main()
