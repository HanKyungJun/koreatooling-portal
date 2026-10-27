#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
일일보고 xlsx -> 캘린더 아티팩트 PROD 자동 업데이트
실행: python scripts/update_calendar_artifact.py [YYYY-MM-DD] [--artifact=경로]
      날짜 생략 시 오늘 날짜 사용 · --artifact 는 시험용(생략 시 실제 아티팩트)
출력: weekly-calendar-overview\index.html 업데이트 (Cowork Artifacts 폴더)

2026-10-27 수정 (원본: update_calendar_artifact.py.bak_20261027)
  - 10-23 부터 일일보고가 ERP 작업실적 기준(decisions 2026-10-23 (7))이라 「FAST GRIND / GX7 수량」 줄이 없다.
    옛 코드는 FG·GX7 을 None 으로 읽고 f-string 으로 그대로 써서 JS 에 `None` 이 들어갔고,
    `const PROD` 선언에서 ReferenceError → 캘린더 화면 전체가 멈췄다(10-23 16:00 회차).
  - 고친 것: ① ERP 보고서는 「합계  수량」 행에서 total 을 읽고 fg·gx7 = null, src="erp"
             ② PROD 줄은 json.dumps 로 쓴다 — 파이썬 None 이 JS 에 들어갈 수 없다
             ③ 가공시간은 H:MM:SS 만 남기고, 표준공수 추정값이면 "est":true 로 따로 표시
  - 엑셀 기준 보고서(~10-22)는 전과 같은 값·같은 형식으로 쓴다(total = fg + gx7).
"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import date
from pathlib import Path
import openpyxl

BASE      = Path(__file__).resolve().parent.parent
DAILY_DIR = BASE / 'wiki' / 'reports' / 'daily'
ARTIFACT  = Path(r'C:\Users\TOOLKOREA\Documents\Claude\Artifacts\weekly-calendar-overview\index.html')
LOG       = DAILY_DIR / 'run.log'
MARKER    = '};\n\nconst REPORT_START'
TIME_RE   = re.compile(r'(\d+):(\d{2}):(\d{2})')


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


def _int(v):
    return int(v) if v is not None else 0


def _hms(sec):
    sec = int(round(float(sec)))
    return f'{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}'


def parse_report(xlsx_path: Path) -> dict:
    """일일 요약 시트 → PROD 항목(dict). 엑셀 기준 / ERP 기준 보고서 둘 다 읽는다."""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb['일일 요약']
    fg = gx7 = nc_ok = nc_ng = total_row = None
    avg, time_str, est = 0.0, '0:00:00', False

    for row in ws.iter_rows(values_only=True):
        if not row or not row[0]:
            continue
        label = str(row[0])

        if 'FAST GRIND  수량' in label:
            fg = _int(row[1])
        elif 'GX7  수량' in label:
            gx7 = _int(row[1])
        elif label.startswith('NC 양품'):
            nc_ok = _int(row[1])
        elif label.startswith('NC 불량'):
            nc_ng = _int(row[1])
        elif '합계  수량' in label:
            total_row = row[1]
            avg = round(float(row[5]), 1) if row[5] is not None else 0.0
        elif '합계  가공시간' in label:
            note = str(row[8]) if len(row) > 8 and row[8] is not None else ''
            m = TIME_RE.search(note)
            if m:
                time_str = f'{int(m.group(1))}:{m.group(2)}:{m.group(3)}'
            elif row[1] is not None and isinstance(row[1], (int, float)):
                time_str = _hms(row[1])          # 비고 칸이 비었을 때 초 값으로
            est = ('추정' in label) or ('추정' in note)

    erp = (fg is None and gx7 is None) and (nc_ok is not None or nc_ng is not None)
    if erp:
        total = _int(total_row) if total_row is not None else (nc_ok or 0) + (nc_ng or 0)
        entry = {'fg': None, 'gx7': None, 'total': total, 'avg': avg, 'time': time_str, 'src': 'erp'}
    else:
        # 엑셀 기준: total 은 fg+gx7 직접 합산 (xlsx 합계 행 의존 제거 — 기존 방식 유지)
        entry = {'fg': fg or 0, 'gx7': gx7 or 0, 'total': (fg or 0) + (gx7 or 0), 'avg': avg, 'time': time_str}
    if est:
        entry['est'] = True
    return entry


def parse_xlsx(xlsx_path: Path):
    """옛 호출부 호환용 (fg, gx7, total, avg, time_str). ERP 보고서면 fg·gx7 = None."""
    e = parse_report(xlsx_path)
    return e['fg'], e['gx7'], e['total'], e['avg'], e['time']


def prod_line(date_key: str, entry: dict) -> str:
    """PROD 한 줄. json.dumps 라 None → null (JS 에 None 이 들어가지 않는다)."""
    body = json.dumps(entry, ensure_ascii=False, separators=(',', ':'))
    return f'  "{date_key}":{body},\n'


def update_artifact(date_key: str, entry: dict, artifact: Path = None) -> bool:
    artifact = artifact or ARTIFACT
    if not artifact.exists():
        log(f'[calendar] ERROR - artifact not found: {artifact}')
        return False

    html = artifact.read_text(encoding='utf-8')     # CRLF → \n 으로 읽힘
    new_entry = prod_line(date_key, entry)

    if new_entry in html:
        log(f'[calendar] SKIP - {date_key} already in PROD (same values)')
        return True
    # 날짜는 있지만 값이 다른 경우 → 기존 줄 삭제 후 재삽입 (부분 집계 후 최종값 갱신 대응)
    if f'"{date_key}":{{"fg":' in html:
        html = re.sub(rf'  "{date_key}":\{{[^\n]+\}},\n', '', html)
        log(f'[calendar] UPDATE - {date_key} values changed, overwriting')

    if MARKER not in html:
        log('[calendar] ERROR - PROD marker not found')
        return False

    updated = html.replace(MARKER, new_entry + MARKER, 1)

    # 안전장치: PROD 블록에 파이썬 None 이 남아 있으면 쓰지 않는다(화면 전체가 멈춤)
    s = updated.find('const PROD = {')
    block = updated[s:updated.find(MARKER, s)] if s >= 0 else ''
    if re.search(r':\s*None\b', block):
        log('[calendar] ERROR - PROD 에 None 이 있음 (JS 오류 원인) — 쓰지 않음. fix_calendar_erp_20261027.py 로 정리 필요')
        return False

    artifact.write_text(updated, encoding='utf-8', newline='\r\n')
    if entry.get('src') == 'erp':
        log(f'[calendar] OK - {date_key}: NC(ERP) total {entry["total"]}, {entry["time"]}'
            + (' (표준공수 추정)' if entry.get('est') else ''))
    else:
        log(f'[calendar] OK - {date_key}: FG {entry["fg"]}, GX7 {entry["gx7"]}, total {entry["total"]}, {entry["time"]}')
    return True


def main():
    args = sys.argv[1:]
    art_arg = [a for a in args if a.startswith('--artifact=')]
    artifact = Path(art_arg[0].split('=', 1)[1]) if art_arg else ARTIFACT
    pos = [a for a in args if not a.startswith('--')]

    date_key  = get_date_key(pos[0] if pos else None)
    xlsx_path = DAILY_DIR / f'{date_key}_일일보고.xlsx'

    if not xlsx_path.exists():
        log(f'[calendar] ERROR - report not found: {xlsx_path}')
        sys.exit(1)

    try:
        entry = parse_report(xlsx_path)
    except Exception as ex:
        log(f'[calendar] ERROR - xlsx parse failed: {ex}')
        sys.exit(1)

    success = update_artifact(date_key, entry, artifact)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
