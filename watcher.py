import sys, io, os, time, subprocess, threading
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 감시할 폴더
WATCH_DIRS = [
    os.path.join(BASE_DIR, 'wiki', 'comparisons'),   # 출하현황 분석 파일
    os.path.join(BASE_DIR, 'raw', '출하현황'),         # 재연마 월간생산일지
]

# 디바운스 타이머 (연속 이벤트 묶기)
_timer = None
_DEBOUNCE = 3.0  # 마지막 이벤트 후 3초 대기


def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}', flush=True)


def run_generate():
    log('로컬 현황판 갱신 중...')
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, 'generate.py'), '--local'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    for line in result.stdout.splitlines():
        print(f'  {line}', flush=True)
    if result.returncode != 0:
        log(f'❌ 오류 발생:\n{result.stderr[:300]}')


def schedule_generate():
    global _timer
    if _timer:
        _timer.cancel()
    _timer = threading.Timer(_DEBOUNCE, run_generate)
    _timer.start()


class XlsxHandler(FileSystemEventHandler):
    def on_modified(self, event):
        self._handle(event.src_path)

    def on_created(self, event):
        self._handle(event.src_path)

    def on_moved(self, event):
        # Excel 저장 시 임시파일 → 원본으로 rename하는 방식 감지
        self._handle(event.dest_path)

    def _handle(self, path):
        name = os.path.basename(path)
        # 엑셀 임시파일 무시
        if name.startswith('~$') or name.startswith('.~'):
            return
        if not (name.endswith('.xlsx') or name.endswith('.xls')):
            return
        log(f'변경 감지: {name}')
        schedule_generate()


if __name__ == '__main__':
    log('파일 감시 시작')
    for d in WATCH_DIRS:
        log(f'  → {d}')

    handler  = XlsxHandler()
    observer = Observer()
    for d in WATCH_DIRS:
        observer.schedule(handler, d, recursive=True)

    observer.start()
    log('저장(Ctrl+S) 감지 시 GitHub Pages 자동 업로드됩니다. 종료: Ctrl+C')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    log('종료.')
