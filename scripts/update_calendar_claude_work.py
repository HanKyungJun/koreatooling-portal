#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
worklog.md 핸드오프 블록 -> 캘린더 아티팩트 CLAUDE_WORK 자동 업데이트
실행: python scripts/update_calendar_claude_work.py            (신규 날짜만 추가)
      python scripts/update_calendar_claude_work.py --repair   (+ 깨진 줄 재생성)
동작:
  1. wiki/_handoff/worklog.md에서 날짜별 "- 한 일:" 섹션의 작업 라벨을 추출
       1순위 항목 앞부분의 **볼드**(= 작업 제목)
       2순위 항목 머리말(구분자 —, →, · 앞까지)
  2. 아티팩트 CLAUDE_WORK에 아직 없는 날짜만 골라 자동 태깅 후 삽입 (최대 3개/일)
  3. 이미 사람이 채워둔 날짜는 절대 건드리지 않음 (수동 큐레이션 값 보존)
     단 --repair 를 주면, 라벨이 전부 '참조 파편'인 날짜만 골라 재생성한다.
출력: weekly-calendar-overview\index.html CLAUDE_WORK 갱신

[2026-09-30 수정] 볼드를 무조건 라벨로 쓰던 로직이 교차 참조까지 긁어오는 버그를 고쳤다.
  증상: 09-23~09-29 항목이 "(2)", "2026-09-29 (3)" 처럼 날짜·번호만 남음
  원인: worklog 본문의 `decisions **2026-09-29 (2)**`, `상세 블록 **(2)**` 같은
        참조 표기와, 문장 중간 강조(`**읽기 전용**`)를 작업 제목과 구분하지 못함
  대응: REF_CONTEXT(앞 문맥) · REF_ONLY(내용 자체) · BOLD_HEAD_WINDOW(위치) 3중 필터 +
        볼드가 없으면 항목 머리말로 폴백 → 볼드 습관에 대한 의존 제거
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

BASE     = Path(__file__).resolve().parent.parent
WORKLOG  = BASE / 'wiki' / '_handoff' / 'worklog.md'
# 2026-09-29 아카이브 분할 이후 옛 블록은 worklog-archive/YYYY-MM.md 로 이동한다.
# --repair 로 과거 날짜를 고치려면 아카이브까지 읽어야 한다.
WORKLOG_ARCHIVE = BASE / 'wiki' / '_handoff' / 'worklog-archive'


def read_all_worklogs() -> str:
    parts = []
    if WORKLOG.exists():
        parts.append(WORKLOG.read_text(encoding='utf-8'))
    if WORKLOG_ARCHIVE.is_dir():
        for p in sorted(WORKLOG_ARCHIVE.glob('*.md')):
            parts.append(p.read_text(encoding='utf-8'))
    return '\n'.join(parts)
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


# 볼드 바로 앞이 이 문구로 끝나면 '작업 제목'이 아니라 '교차 참조'다
#   예) decisions **2026-09-29 (2)** / 상세 블록 **(2)**
REF_CONTEXT = re.compile(r'(?:decisions(?:\.md)?|상세\s*블록|블록|참조|항목)\s*$')

# 그 자체로 참조 번호인 볼드 (작업 내용이 아님)
#   예) (2) / 2026-09-29 / 2026-09-29 (3) / 2026-09-29 · (3) · (5)
REF_ONLY = re.compile(
    r'^(?:\(\d+\)|\d{4}-\d{2}-\d{2}(?:\s*[·,]?\s*\(\d+\))*|[\d\s·,()#-]+)$'
)

MIN_LABEL_LEN = 5   # 이보다 짧으면 문장 파편으로 보고 버림
MAX_LABEL_LEN = 60  # 캘린더 셀 폭 고려


def clean_label(s: str) -> str:
    # 인라인 코드 제거. 뒤에 홀로 남는 조사(`price_audit.py` 가 → " 가 ")까지 함께 지운다.
    s = re.sub(r'`[^`]*`\s*(?:가|이|은|는|을|를|에서|에|의|로|으로|와|과)(?=\s)', ' ', s)
    s = re.sub(r'`[^`]*`', '', s)
    s = re.sub(r'\*\*|~~', '', s)          # 볼드·취소선 마커 제거
    # 코드 제거로 비거나 반쪽만 남은 괄호 정리 — "선행 작업( 가 …" 같은 잔해 방지
    s = re.sub(r'\(\s*[,·]?\s*\)', '', s)  # 빈 괄호
    s = re.sub(r'\(\s*(?=[가-힣]{1,2}\s)', '', s)   # 여는 괄호 + 조사만 남은 경우
    s = re.sub(r'\s+([,.)])', r'\1', s)
    s = re.sub(r'\s+', ' ', s).strip(' ·—→-')
    if s.count('(') != s.count(')'):       # 짝이 안 맞으면 괄호 전부 제거
        s = s.replace('(', '').replace(')', '')
    return s[:MAX_LABEL_LEN].strip()


def is_usable(s: str) -> bool:
    return bool(s) and len(s) >= MIN_LABEL_LEN and not REF_ONLY.match(s)


BOLD_HEAD_WINDOW = 30  # 볼드가 항목 앞부분에 있어야 '제목'으로 인정


def pick_label_from_item(item: str) -> str | None:
    """리스트 항목 1개에서 대표 라벨 1개를 고른다.
    1순위: 항목 앞부분(BOLD_HEAD_WINDOW 이내)에 있는, 참조가 아닌 볼드 → 작업 제목
    2순위: 항목 머리말 (구분자 —, →, · 앞까지)
    문장 중간의 강조 볼드(예: **읽기 전용**)는 제목이 아니므로 1순위에서 제외된다.
    """
    for m in re.finditer(r'\*\*(.+?)\*\*', item):
        if m.start() > BOLD_HEAD_WINDOW:
            break                           # 문장 중간 강조 → 제목 아님
        cand = clean_label(m.group(1))
        if REF_CONTEXT.search(item[:m.start()].rstrip()):
            continue                        # decisions/상세 블록 참조 → 건너뜀
        if is_usable(cand):
            return cand

    head = re.split(r'\s*(?:—|→|·\s)\s*', item, maxsplit=1)[0]
    head = clean_label(head)
    return head if is_usable(head) else None


def parse_worklog(text: str) -> dict:
    """날짜별로 '- 한 일:' 섹션에서 작업 라벨을 수집"""
    blocks = re.split(r'(?m)^## ', text)[1:]
    by_date: dict[str, list[str]] = {}
    for block in blocks:
        head_line = block.split('\n', 1)[0]
        m = re.match(r'(\d{4}-\d{2}-\d{2})', head_line)
        if not m:
            continue
        date_key = m.group(1)
        work_m = re.search(
            r'한\s*일[^:\n]*[:\*\s]*(.*?)(?=\n-\s*\*{0,2}\s*(?:결과|산출물|점검|보강|미완|다음|챗)|\Z)',
            block, re.S,
        )
        if not work_m:
            continue

        body = work_m.group(1)
        # 번호 목록(1. 2. …) 또는 하위 불릿(- , * )으로 항목 분리.
        # 분리가 안 되면(한 줄 서술형) 본문 전체를 항목 1개로 본다.
        items = [s for s in re.split(r'(?m)^\s*(?:\d+\.|[-*])\s+', body) if s.strip()]
        if not items:
            items = [body]

        bucket = by_date.setdefault(date_key, [])
        added_from_this_block = 0
        for item in items:
            if added_from_this_block >= MAX_TAGS_PER_BLOCK:
                break
            label = pick_label_from_item(item.strip())
            if label and label not in bucket:
                bucket.append(label)
                added_from_this_block += 1
    return by_date


def main():
    if not WORKLOG.exists():
        log('[calendar-work] ERROR - worklog.md not found')
        sys.exit(1)
    if not ARTIFACT.exists():
        log('[calendar-work] ERROR - artifact not found')
        sys.exit(1)

    repair = '--repair' in sys.argv

    by_date = parse_worklog(read_all_worklogs())
    html = ARTIFACT.read_text(encoding='utf-8')

    m = re.search(r'const CLAUDE_WORK = \{(.*?)\n\};', html, re.S)
    if not m:
        log('[calendar-work] ERROR - CLAUDE_WORK marker not found')
        sys.exit(1)
    existing_dates = set(re.findall(r'"(\d{4}-\d{2}-\d{2})":', m.group(1)))

    # --repair: 이미 들어간 줄 중 '참조 파편'만 담긴 날짜를 찾아 재생성한다.
    #   예) "2026-09-29":[{...l:"🤖 2026-09-29 (3)"},{...l:"🤖 2026-09-29"}]
    if repair:
        repaired = []
        for line_m in re.finditer(r'(?m)^  "(\d{4}-\d{2}-\d{2})":\[(.*?)\],$', m.group(1)):
            date_key, payload = line_m.group(1), line_m.group(2)
            labels = [clean_label(x) for x in re.findall(r'l:"🤖\s*(.*?)"', payload)]
            if not labels:
                continue
            bad = sum(1 for l in labels if not is_usable(l))
            if bad == 0:
                continue                      # 정상 줄은 건드리지 않음
            fresh = by_date.get(date_key, [])[:MAX_TAGS_PER_DAY]
            if not fresh:
                log(f'[calendar-work] REPAIR-SKIP {date_key} - worklog에서 대체 라벨을 못 찾음')
                continue
            items = ','.join(
                '{t:"%s",l:"🤖 %s"}' % (guess_tag(l), l.replace('"', "'"))
                for l in fresh
            )
            html = html.replace(line_m.group(0), f'  "{date_key}":[{items}],', 1)
            repaired.append(date_key)
        if repaired:
            ARTIFACT.write_text(html, encoding='utf-8')
            log(f'[calendar-work] REPAIR - fixed {len(repaired)} date(s): {", ".join(repaired)}')
            m = re.search(r'const CLAUDE_WORK = \{(.*?)\n\};', html, re.S)
        else:
            log('[calendar-work] REPAIR - nothing to fix')

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
