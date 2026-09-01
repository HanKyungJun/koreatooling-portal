#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
worklog.md 핸드오프 블록 -> 캘린더 아티팩트 CLAUDE_WORK 자동 업데이트
실행: python scripts/update_calendar_claude_work.py
동작:
  1. wiki/_handoff/worklog.md에서 날짜별 "- 한 일:" 섹션의 **볼드** 문구를 라벨 후보로 추출
  2. 아티팩트 CLAUDE_WORK에 아직 없는 날짜만 골라 자동 태깅 후 삽입 (최대 3개/일)
  3. 이미 사람이 채워둔 날짜는 절대 건드리지 않음 (수동 큐레이션 값 보존)
출력: weekly-calendar-overview\index.html CLAUDE_WORK 갱신
주의: 요약 품질은 worklog.md 작성 시 핵심 작업에 **볼드**를 붙이는 습관에 의존한다.
      볼드가 없으면 그 날짜는 자동 채움 대상에서 빠지므로, 세션 종료 worklog 작성 시
      "- 한 일:" 항목 제목에 **볼드**를 유지할 것.
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

BASE     = Path(__file__).resolve().parent.parent
WORKLOG  = BASE / 'wiki' / '_handoff' / 'worklog.md'
ARTIFACT = Path(r'C:\Users\TOOLKOREA\Documents\Claude\Artifacts\weekly-calendar-overview\index.html')
LOG      = BASE / 'wiki' / 'reports' / 'daily' / 'run.log'

MAX_TAGS_PER_DAY = 3
MAX_TAGS_PER_BLOCK = 2  # 같은 날 여러 세션이 있을 때 한 세션이 캡을 독식하지 않도록 제한

# (태그, 키워드 목록) 순서대로 먼저 매치되는 것을 채택. 빈 키워드 목록 = 기본값(fallback)
TAG_RULES = [
    ('cl-wiki',   ['위키', '페이지']),
    ('cl-data',   ['KPI', '데이터', '분석', 'Weibull']),
    ('cl-portal', ['포털', 'GitHub Pages', 'CSS', 'JS', 'GAS', 'dist']),
    ('cl-report', ['보고서', '회의록']),
    ('cl-auto',   ['자동화', 'OAuth', '알림', '스크립트']),
    ('cl-infra',  []),
]


def log(msg):
    print(msg)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass


def guess_tag(label: str) -> str:
    for tag, keywords in TAG_RULES:
        if keywords and any(kw in label for kw in keywords):
            return tag
    return 'cl-infra'


def parse_worklog(text: str) -> dict:
    """날짜별로 '- 한 일:' 섹션의 **볼드** 라벨을 수집"""
    blocks = re.split(r'(?m)^## ', text)[1:]
    by_date: dict[str, list[str]] = {}
    for block in blocks:
        head_line = block.split('\n', 1)[0]
        m = re.match(r'(\d{4}-\d{2}-\d{2})', head_line)
        if not m:
            continue
        date_key = m.group(1)
        work_m = re.search(
            r'한\s*일[:\*\s]*(.*?)(?=\n-\s*\*{0,2}\s*(?:결과|산출물|점검)|\Z)',
            block, re.S,
        )
        if not work_m:
            continue
        bolds = re.findall(r'\*\*(.+?)\*\*', work_m.group(1))
        bucket = by_date.setdefault(date_key, [])
        added_from_this_block = 0
        for b in bolds:
            if added_from_this_block >= MAX_TAGS_PER_BLOCK:
                break
            b = b.strip()
            if b and b not in bucket:
                bucket.append(b)
                added_from_this_block += 1
    return by_date


def main():
    if not WORKLOG.exists():
        log('[calendar-work] ERROR - worklog.md not found')
        sys.exit(1)
    if not ARTIFACT.exists():
        log('[calendar-work] ERROR - artifact not found')
        sys.exit(1)

    by_date = parse_worklog(WORKLOG.read_text(encoding='utf-8'))
    html = ARTIFACT.read_text(encoding='utf-8')

    m = re.search(r'const CLAUDE_WORK = \{(.*?)\n\};', html, re.S)
    if not m:
        log('[calendar-work] ERROR - CLAUDE_WORK marker not found')
        sys.exit(1)
    existing_dates = set(re.findall(r'"(\d{4}-\d{2}-\d{2})":', m.group(1)))

    new_lines = []
    added_dates = []
    for date_key in sorted(by_date):
        if date_key in existing_dates:
            continue
        labels = by_date[date_key][:MAX_TAGS_PER_DAY]
        if not labels:
            continue
        items = ','.join(
            '{t:"%s",l:"🤖 %s"}' % (guess_tag(l), l.replace('"', "'"))
            for l in labels
        )
        new_lines.append(f'  "{date_key}":[{items}],')
        added_dates.append(date_key)

    if not new_lines:
        log('[calendar-work] SKIP - no new dates')
        return

    marker = '};\n\nconst LEAVE_DAYS'
    if marker not in html:
        log('[calendar-work] ERROR - insertion marker not found')
        sys.exit(1)

    insertion = '\n'.join(new_lines) + '\n'
    updated = html.replace(marker, insertion + '};\n\nconst LEAVE_DAYS', 1)
    ARTIFACT.write_text(updated, encoding='utf-8')
    log(f'[calendar-work] OK - added {len(added_dates)} date(s): {", ".join(added_dates)}')


if __name__ == '__main__':
    main()
