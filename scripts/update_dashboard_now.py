# -*- coding: utf-8 -*-
"""현황판 지금 업데이트 — 바탕화면 「현황판 업데이트.bat」 이 부른다 (2026-11-10 신설, Cowork)

16:00 자동 실행(daily_and_upload.bat 5단계)과 같은 `python generate.py` 를 손으로 한 번 돌린다.
사내 현황판(공유폴더) · GitHub 포털을 갱신하고, generate.py 가 하는 자동 커밋 · push 도 같이 일어난다.

막는 것
  - 15:55 ~ 16:15 KST: 16:00 자동 실행과 겹치면 파일 잠금 오류가 난 전례가 있어(2026-10-14 step5) 실행하지 않는다
  - generate.py 가 이미 돌고 있으면 실행하지 않는다
기록
  - 출력은 화면에 보이면서 wiki/reports/daily/generate.log 에도 이어 붙인다(자동 실행과 같은 파일)
  - wiki/reports/daily/run.log 에 [manual-generate-start] · [manual-generate-end] rc= 두 줄
"""
import os, subprocess, sys
from datetime import datetime, timedelta, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY = os.path.join(BASE, 'wiki', 'reports', 'daily')
KST = timezone(timedelta(hours=9))


def now():
    return datetime.now(KST)


def running_generate():
    """generate.py 를 돌리는 다른 python 이 있으면 개수. 확인 못 하면 None."""
    if os.name != 'nt':
        return None
    cmd = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' -and "
           "$_.CommandLine -match 'generate\\.py' } | Measure-Object | ForEach-Object { $_.Count }")
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', cmd],
                           capture_output=True, text=True, timeout=30)
        return int((r.stdout or '0').strip() or 0)
    except Exception:
        return None


def mark(line):
    try:
        with open(os.path.join(DAILY, 'run.log'), 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except OSError:
        pass


def main():
    t = now()
    print(f'현황판 업데이트 — {t:%Y-%m-%d %H:%M} KST\n')
    hm = t.hour * 60 + t.minute
    if 15 * 60 + 55 <= hm <= 16 * 60 + 15:
        print('⏸ 지금은 16:00 자동 실행 시간대(15:55 ~ 16:15)입니다. 자동 실행이 현황판을 갱신하니 16:15 뒤에 다시 눌러 주세요.')
        return 2
    n = running_generate()
    if n:
        print(f'⏸ 현황판 생성이 이미 돌고 있습니다({n}개). 1 ~ 2분 뒤에 다시 눌러 주세요.')
        return 3
    if n is None:
        print('(실행 중 확인을 못 했습니다 — 그대로 진행합니다)\n')

    mark(f'[manual-generate-start] {t:%Y-%m-%d %H:%M} KST')
    out = []
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    with open(os.path.join(DAILY, 'generate.log'), 'a', encoding='utf-8') as log:
        log.write(f'[manual-run] {t:%Y-%m-%d %H:%M} KST — 현황판 업데이트 버튼\n')
        p = subprocess.Popen([sys.executable, 'generate.py'], cwd=BASE, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding='utf-8', errors='replace')
        for line in p.stdout:
            print(line, end='')
            log.write(line)
            out.append(line)
        rc = p.wait()
    mark(f'[manual-generate-end] {now():%Y-%m-%d %H:%M} KST rc={rc}')

    text = ''.join(out)
    internal = '사내 배포 완료' in text
    portal = '업로드 완료' in text
    print('\n' + '=' * 50)
    if rc == 0 and internal and portal:
        print(f'✅ 현황판 업데이트 완료 ({now():%H:%M}) — 사내 현황판 · 포털 모두 갱신')
        print('   브라우저에서 새로고침(Ctrl + F5) 하면 보입니다.')
        return 0
    print(f'⚠️ 끝났지만 확인이 필요합니다 — 종료 코드 {rc} · 사내 현황판 {"✅" if internal else "❌"} · 포털 {"✅" if portal else "❌"}')
    for line in out:
        if any(k in line for k in ('❌', '실패', '오류', 'Error', 'Traceback')):
            print('   ' + line.rstrip())
    print('   전체 로그: wiki\\reports\\daily\\generate.log (맨 아래 [manual-run] 부분) — Cowork 에 「현황판 버튼 오류」라고 알려 주세요')
    return 1


if __name__ == '__main__':
    sys.exit(main())
