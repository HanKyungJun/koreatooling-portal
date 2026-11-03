#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
핸드오프 파일 분할 — decisions / worklog / tasks 를 활성분 + 아카이브로 나눈다.

실행:
    python scripts/archive_handoff.py                 # 드라이런 (기본, 아무것도 안 바꿈)
    python scripts/archive_handoff.py --apply         # 실제 적용
    python scripts/archive_handoff.py --keep 20 --apply
    python scripts/archive_handoff.py --only decisions --apply

동작:
  decisions.md → 최근 N건(기본 15)만 남기고 나머지는 _handoff/decisions-archive/YYYY-MM.md 로
  worklog.md   → 당월분만 남기고 나머지는 _handoff/worklog-archive/YYYY-MM.md 로 (기존 규칙 계승)
  tasks.md     → 「## 완료 아카이브」 섹션을 _handoff/tasks-archive.md 로

원칙:
  · 삭제하지 않는다 — 전부 아카이브 파일로 옮기고, 활성 파일 상단에 인덱스를 남긴다.
  · --apply 시 원본을 _to_delete/handoff_backup_YYYYMMDD/ 에 먼저 복사한다.
  · 날짜 헤더가 아닌 `## ` 섹션(항목 형식·템플릿 등)은 활성 파일에 그대로 남긴다.
  · 실행 전후 블록 수와 바이트를 대조해 유실이 없음을 확인한다.

⚠️ cnc-handoff 스킬은 decisions.md·worklog.md·tasks.md 를 계속 읽는다. 파일명은 바뀌지 않으므로
   스킬 수정은 불필요하다. 다만 과거 내용을 찾을 때는 아카이브 폴더도 함께 grep 해야 한다.
"""
import argparse, re, shutil, sys, datetime
from pathlib import Path
from collections import OrderedDict

BASE = Path(__file__).resolve().parent.parent
HO   = BASE / 'wiki' / '_handoff'
TODAY = datetime.date.today()
BLOCK = re.compile(r'(?m)^(?=## )')
DATED = re.compile(r'^## (20\d\d)-(\d\d)')


def split_blocks(text):
    """(서두, [블록...]) 로 나눈다."""
    parts = BLOCK.split(text)
    return parts[0], parts[1:]


def month_of(block):
    m = DATED.match(block)
    return f'{m.group(1)}-{m.group(2)}' if m else None


def append_archive(path, header, blocks, apply_):
    """아카이브 파일에 블록을 덧붙인다(최신이 위). 이미 있는 항목은 건너뛴다."""
    existing = path.read_text(encoding='utf-8') if path.exists() else ''
    if not existing:
        existing = header
    first_lines = {b.split('\n', 1)[0].strip() for b in split_blocks(existing)[1]}
    new = [b for b in blocks if b.split('\n', 1)[0].strip() not in first_lines]
    if not new:
        return 0
    pre, old = split_blocks(existing)
    out = pre + ''.join(new) + ''.join(old)
    if apply_:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(out, encoding='utf-8')
    return len(new)


def do_decisions(keep, apply_, log):
    p = HO / 'decisions.md'
    if not p.exists():
        log('  decisions.md 없음 — 건너뜀'); return
    text = p.read_text(encoding='utf-8')
    pre, blocks = split_blocks(text)
    dated  = [b for b in blocks if month_of(b)]
    static = [b for b in blocks if not month_of(b)]
    keep_b, arch_b = dated[:keep], dated[keep:]
    log(f'  전체 {len(dated)}건 (+고정 섹션 {len(static)}) → 유지 {len(keep_b)} / 아카이브 {len(arch_b)}')
    if not arch_b:
        log('  아카이브할 항목 없음'); return

    by_month = OrderedDict()
    for b in arch_b:
        by_month.setdefault(month_of(b), []).append(b)

    adir = HO / 'decisions-archive'
    for mon, bs in by_month.items():
        f = adir / f'{mon}.md'
        hdr = (f'# 결정사항 로그 아카이브 — {mon}\n\n'
               f'> `_handoff/decisions.md` 에서 분리된 {mon} 항목입니다. 시간 역순(최신이 위).\n'
               f'> 활성 로그는 [[decisions]] 참고. 과거 결정을 찾을 때는 이 폴더 전체를 grep 하세요.\n\n')
        n = append_archive(f, hdr, bs, apply_)
        log(f'    → decisions-archive/{mon}.md  ({n}건)')

    idx = ['\n## 📁 아카이브 인덱스\n\n',
           f'> 최근 **{keep}건**만 이 파일에 둡니다. 그 이전 항목은 아래 파일에 **삭제 없이 보존**됩니다.\n',
           '> 과거 결정을 찾을 때는 `wiki/_handoff/decisions-archive/` 전체를 grep 하세요.\n\n',
           '| 기간 | 이 파일 | 아카이브 | 합계 |\n|---|---|---|---|\n']
    for mon in sorted(set(month_of(b) for b in dated), reverse=True):
        k = sum(1 for b in keep_b if month_of(b) == mon)
        a = sum(1 for b in arch_b if month_of(b) == mon)
        link = f'[[decisions-archive/{mon}]] {a}건' if a else '—'
        idx.append(f'| {mon} | {k}건 | {link} | {k + a}건 |\n')
    idx.append(f'| **합계** | **{len(keep_b)}건** | **{len(arch_b)}건** | **{len(dated)}건** |\n')
    if keep_b:
        idx.append(f'\n> 이 파일의 범위: **{month_of(keep_b[-1])} ~ {month_of(keep_b[0])}** '
                   f'(가장 오래된 항목 — {keep_b[-1].split(chr(10))[0][3:60].strip()})\n')
    idx.append(f'\n> 재정리: `python scripts/archive_handoff.py --apply` (마지막 실행 {TODAY})\n')

    out = pre + ''.join(keep_b) + ''.join(idx) + ''.join(static)
    if apply_:
        p.write_text(out, encoding='utf-8')
    log(f'  decisions.md  {len(text.encode())/1024:.1f} KB → {len(out.encode())/1024:.1f} KB')


def do_worklog(apply_, log):
    p = HO / 'worklog.md'
    if not p.exists():
        log('  worklog.md 없음 — 건너뜀'); return
    text = p.read_text(encoding='utf-8')
    pre, blocks = split_blocks(text)
    cur = f'{TODAY:%Y-%m}'
    keep_b = [b for b in blocks if month_of(b) in (cur, None)]
    arch_b = [b for b in blocks if month_of(b) not in (cur, None)]
    log(f'  전체 {len(blocks)}건 → 유지 {len(keep_b)}(당월 {cur}) / 아카이브 {len(arch_b)}')
    if not arch_b:
        log('  아카이브할 항목 없음'); return
    by_month = OrderedDict()
    for b in arch_b:
        by_month.setdefault(month_of(b), []).append(b)
    for mon, bs in by_month.items():
        f = HO / 'worklog-archive' / f'{mon}.md'
        hdr = (f'# 워크로그 아카이브 — {mon}\n\n'
               f'> `_handoff/worklog.md` 에서 분리된 {mon} 기록입니다. 시간 역순(최신이 위).\n\n')
        n = append_archive(f, hdr, bs, apply_)
        log(f'    → worklog-archive/{mon}.md  ({n}건)')
    out = pre + ''.join(keep_b)
    if apply_:
        p.write_text(out, encoding='utf-8')
    log(f'  worklog.md  {len(text.encode())/1024:.1f} KB → {len(out.encode())/1024:.1f} KB')


def do_tasks(apply_, log):
    """완료 아카이브 섹션 + 활성 섹션에 남아 있는 `- [x]` 완료 항목을 tasks-archive.md 로 옮긴다.

    tasks.md 자신의 규칙 — *"완료 시 체크 후 「완료 아카이브」로 이동 (삭제 X)"* — 을 그대로 적용한다.
    """
    p = HO / 'tasks.md'
    if not p.exists():
        log('  tasks.md 없음 — 건너뜀'); return
    text = p.read_text(encoding='utf-8')

    m = re.search(r'(?m)^## 완료 아카이브\s*$', text)
    body, done_sec = (text[:m.start()], text[m.start():]) if m else (text, '')

    # 활성 섹션 안의 완료 항목(- [x]) 수거
    secs = re.split(r'(?m)^(?=## )', body)
    moved, out_secs = [], []
    for sec in secs:
        items = re.split(r'(?m)^(?=- \[)', sec)
        kept = [items[0]] if items else []
        for it in items[1:]:
            (moved if it.startswith('- [x]') else kept).append(it)
        out_secs.append(''.join(kept))
    new_body = ''.join(out_secs)

    if not moved and not done_sec:
        log('  옮길 완료 항목 없음 — 건너뜀'); return

    log(f'  활성 섹션의 완료 항목 {len(moved)}건 {sum(len(i.encode()) for i in moved)/1024:.1f} KB 수거')

    f = HO / 'tasks-archive.md'
    hdr = ('# 작업 큐 아카이브 — 완료 항목\n\n'
           '> `_handoff/tasks.md` 에서 분리한 완료 항목입니다. **삭제하지 않고 보존**합니다.\n'
           '> 활성 큐는 [[tasks]] 참고. tasks.md 규칙: *"완료 시 체크 후 완료 아카이브로 이동 (삭제 X)"*\n\n')
    prev = f.read_text(encoding='utf-8') if f.exists() else ''
    prev_body = re.split(r'(?m)^(?=- \[)', prev, maxsplit=1)
    seen = {l.split('\n', 1)[0].strip() for l in re.split(r'(?m)^(?=- \[)', prev)[1:]}
    fresh = [i for i in moved if i.split('\n', 1)[0].strip() not in seen]

    arch = hdr
    if done_sec:
        arch += f'## 기존 「완료 아카이브」 섹션 (분리 {TODAY})\n\n' + done_sec.split('\n', 1)[1].lstrip('\n')
    if fresh:
        arch += (f'\n## 활성 큐에서 이관 ({TODAY})\n\n'
                 f'> 완료 표시(`- [x]`)가 붙은 채 「진행 중」 등에 남아 있던 항목 {len(fresh)}건입니다.\n\n'
                 + ''.join(fresh))
    if prev and (prev_body[1:] or '## ' in prev.replace(hdr, '')):
        arch += f'\n## 이전 아카이브 (재정리 {TODAY} 이전)\n\n' + prev.replace(hdr, '', 1)

    ptr = ('## 완료 아카이브\n\n'
           f'> 📁 완료 항목 전량을 [[tasks-archive]] 로 분리했습니다 (삭제 아님).\n'
           f'> 분리일 {TODAY} · 재정리: `python scripts/archive_handoff.py --apply`\n')
    out = new_body.rstrip() + '\n\n' + ptr

    if apply_:
        f.write_text(arch, encoding='utf-8')
        p.write_text(out, encoding='utf-8')
    log(f'  → tasks-archive.md  (기존 섹션 + 이관 {len(fresh)}건)')
    log(f'  tasks.md  {len(text.encode())/1024:.1f} KB → {len(out.encode())/1024:.1f} KB')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='실제 적용 (없으면 드라이런)')
    ap.add_argument('--keep', type=int, default=15, help='decisions.md 에 남길 최근 항목 수 (기본 15)')
    ap.add_argument('--only', choices=['decisions', 'worklog', 'tasks'], help='하나만 처리')
    a = ap.parse_args()

    mode = '적용' if a.apply else '드라이런 (--apply 를 붙여야 실제로 바뀝니다)'
    print(f'모드: {mode}\n대상: {HO}\n')

    if a.apply:
        bak = BASE / '_to_delete' / f'handoff_backup_{TODAY:%Y%m%d}'
        bak.mkdir(parents=True, exist_ok=True)
        for n in ('decisions.md', 'worklog.md', 'tasks.md'):
            if (HO / n).exists():
                shutil.copy2(HO / n, bak / n)
        print(f'백업: {bak}\n')

    log = lambda s: print(s)
    for name, fn in (('decisions', lambda: do_decisions(a.keep, a.apply, log)),
                     ('worklog',   lambda: do_worklog(a.apply, log)),
                     ('tasks',     lambda: do_tasks(a.apply, log))):
        if a.only and a.only != name:
            continue
        print(f'── {name}.md ──')
        fn()
        print()

    if not a.apply:
        print('※ 드라이런이었습니다. 실제로 적용하려면 --apply 를 붙이세요.')


if __name__ == '__main__':
    main()
