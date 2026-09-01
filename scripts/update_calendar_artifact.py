#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
일일보고 xlsx -> 캘린더 아티팩트 PROD 자동 업데이트
실행: python scripts/update_calendar_artifact.py [YYYY-MM-DD]
      날짜 생략 시 오늘 날짜 사용
출력: weekly-calendar-overview\index.html 업데이트 (Cowork Artifacts 폴더)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import date
from pathlib import Path
import openpyxl

BASE      = Path(__file__).resolve().parent.parent
DAILY_DIR = BASE / 'wiki' / 'reports' / 'daily'
ARTIFACT  = Path(r'C:\Users\TOOLKOREA\Documents\Claude\Artifacts\weekly-calendar-overview\index.html')
LOG       = DAILY_DIR / 'run.log'


def log(msg):
    print(msg)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass


def get_date_key(arg=None):
    if arg:
        return arg
    return date.today().strftime('%Y-%m-%d')


def parse_xlsx(xlsx_path: Path):
    """일일 요약 시트에서 FG/GX7/합계/월평균/가공시간 추출"""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb['일일 요약']
    fg = gx7 = total = avg = time_str = None

    for row in ws.iter_rows(values_only=True):
        if not row[0]:
            continue
        label = str(row[0])

        if 'FAST GRIND  수량' in label:
            fg = int(row[1]) if row[1] is not None else 0

        elif 'GX7  수량' in label:
            gx7 = int(row[1]) if row[1] is not None else 0

        elif '합계  수량' in label:
            # total은 fg+gx7 직접 합산으로 계산 (xlsx 합계 행 의존 제거)
            avg   = round(float(row[5]), 1) if row[5] is not None else 0.0

        elif '합계  가공시간' in label:
            time_str = str(row[8]) if row[8] is not None else '0:00:00'

    total = (fg or 0) + (gx7 or 0)
    return fg, gx7, total, avg, time_str


def update_artifact(date_key: str, fg: int, gx7: int, total: int, avg: float, time_str: str) -> bool:
    if not ARTIFACT.exists():
        log(f'[calendar] ERROR - artifact not found: {ARTIFACT}')
        return False

    html = ARTIFACT.read_text(encoding='utf-8')

    # PROD 형식("date":{"fg": 패턴)으로만 체크 - 캘린더 일정 섹션과 구분
    # 이미 있어도 수치가 다르면 덮어쓰기 (부분 집계 후 최종값으로 갱신 대응)
    existing_marker = f'"{date_key}":{{"fg":{fg},"gx7":{gx7},'
    if existing_marker in html:
        log(f'[calendar] SKIP - {date_key} already in PROD (same values)')
        return True
    # 날짜는 있지만 값이 다른 경우 → 기존 라인 삭제 후 재삽입
    if f'"{date_key}":{{"fg":' in html:
        import re
        html = re.sub(rf'  "{date_key}":\{{[^\n]+\}},\n', '', html)
        log(f'[calendar] UPDATE - {date_key} values changed, overwriting')

    # PROD 오브젝트 닫는 줄 바로 앞에 새 항목 삽입
    new_entry = f'  "{date_key}":{{"fg":{fg},"gx7":{gx7},"total":{total},"avg":{avg},"time":"{time_str}"}},\n'
    marker    = '};\n\nconst REPORT_START'

    if marker not in html:
        log('[calendar] ERROR - PROD marker not found')
        return False

    updated = html.replace(marker, new_entry + marker, 1)
    ARTIFACT.write_text(updated, encoding='utf-8')
    log(f'[calendar] OK - {date_key}: FG {fg}, GX7 {gx7}, total {total}, {time_str}')
    return True


def main():
    date_key  = get_date_key(sys.argv[1] if len(sys.argv) > 1 else None)
    xlsx_path = DAILY_DIR / f'{date_key}_일일보고.xlsx'

    if not xlsx_path.exists():
        log(f'[calendar] ERROR - report not found: {xlsx_path}')
        sys.exit(1)

    fg, gx7, total, avg, time_str = parse_xlsx(xlsx_path)

    if total is None:
        log('[calendar] ERROR - xlsx parse failed (no total)')
        sys.exit(1)

    success = update_artifact(date_key, fg, gx7, total, avg, time_str)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
