# -*- coding: utf-8 -*-
"""tasks.md 줄이기 — 큰 항목의 원문을 tasks-archive.md 로 옮기고 tasks.md 에는 요약 카드만 남긴다.
2026-11-03 신설(2026-10-12 slim_tasks_20261012.py 를 일반화 · 매주 정리 제안에서 재사용).

  python scripts/slim_tasks.py                 드라이런 — 무엇을 옮기는지 목록만
  python scripts/slim_tasks.py --apply         적용 — 원본을 _to_delete/handoff_backup_YYYYMMDD/ 에 먼저 복사
  옵션: --min-kb 1.0 (이보다 큰 항목만) · --cap 180 (남기는 줄의 최대 글자 수) · --max-lines 6 (항목당 남기는 열린 줄 수)

남기는 것: 제목 줄 · 담당 · 관련 · 열린 ⬜ · 보류(⏸) 줄 — 길면 앞부분만 + 「…」. 원문 전체는 아카이브에 그대로.
지우는 것 없음: 모든 원문은 tasks-archive.md 「제목 — 이력 (날짜 이관)」 아래에 그대로 붙는다.
"""
import datetime, re, shutil, sys
from pathlib import Path

H = Path(__file__).resolve().parent.parent / 'wiki' / '_handoff'
P, A = H / 'tasks.md', H / 'tasks-archive.md'
args = sys.argv[1:]
APPLY = '--apply' in args
MIN_KB = float(args[args.index('--min-kb') + 1]) if '--min-kb' in args else 1.0
CAP = int(args[args.index('--cap') + 1]) if '--cap' in args else 180
MAXL = int(args[args.index('--max-lines') + 1]) if '--max-lines' in args else 6
TODAY = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d')
ITEM = re.compile(r'^- \[[ x]\] ')

s = P.read_text(encoding='utf-8-sig')
lines = s.split('\n')
items, i = [], 0
while i < len(lines):
    if ITEM.match(lines[i]):
        j = i + 1
        while j < len(lines) and not ITEM.match(lines[j]) and not lines[j].startswith('## '):
            j += 1
        while j > i + 1 and lines[j - 1].strip() == '':
            j -= 1
        items.append((i, j)); i = j
    else:
        i += 1


def size(a, b):
    return sum(len(x.encode()) + 1 for x in lines[a:b])


def cut(t):
    return t if len(t) <= CAP else t[:CAP].rstrip() + ' …(이력 참고)'


def active(l):
    t = l.strip()
    if t.startswith(('- 담당', '- 관련')):
        return True
    u = re.sub(r'~~.*?~~', '', t)
    return ('⬜' in u or '⏸' in u) and not t.startswith('- ~~')


def title(h):
    t = re.sub(r'\*\*', '', ITEM.sub('', h))
    return re.split(r' \(P\d', t)[0].strip()[:80]


out, arc, rep, last = [], [], [], 0
for a, b in items:
    if size(a, b) < MIN_KB * 1024:
        continue
    head, body = lines[a], lines[a + 1:b]
    keep = [cut(l) for l in body if active(l)]
    if len(keep) > MAXL:
        keep = keep[:MAXL] + [f'  - … 열린 줄 {len(keep) - MAXL}개 더 — 아카이브 이력 참고']
    t = title(head)
    link = f'  - 📦 원문 {len(body) + 1}줄 · {size(a, b) / 1024:.1f} KB → [[tasks-archive]] 「{t} — 이력 ({TODAY} 이관)」'
    card = [cut(head), link] + keep
    out += lines[last:a] + card
    arc += ['', f'### {t} — 이력 ({TODAY} 이관)', '', f'> `tasks.md` 에서 옮긴 원문 그대로({len(body) + 1}줄). 열린 줄은 tasks.md 카드에 남아 있다.', ''] + lines[a:b]
    rep.append((size(a, b) / 1024, sum(len(x.encode()) + 1 for x in card) / 1024, len(keep), t))
    last = b
out += lines[last:]
new = '\n'.join(out)

for r in rep:
    print('%5.1f → %4.1f KB  남김 %2d줄  %s' % r)
print(f'\n대상 {len(rep)}개 · tasks.md {len(s.encode()) / 1024:.0f} KB → {len(new.encode()) / 1024:.0f} KB')
if APPLY and rep:
    bk = H.parent.parent / '_to_delete' / f'handoff_backup_{TODAY.replace("-", "")}'
    bk.mkdir(parents=True, exist_ok=True)
    for f in (P, A):
        shutil.copy2(f, bk / (f.name + '.before_slim'))
    a_txt = A.read_text(encoding='utf-8-sig')
    sec = [f'## 활성 큐에서 이관 — 요약 카드 원문 ({TODAY})', ''] + arc + ['', '']
    k = a_txt.find('\n## ')  # 최신이 위 — 첫 「## 」 섹션 앞에 넣는다
    a_new = (a_txt[:k + 1] + '\n'.join(sec) + a_txt[k + 1:]) if k >= 0 else a_txt.rstrip('\n') + '\n\n' + '\n'.join(sec)
    A.write_text(a_new, encoding='utf-8-sig')
    P.write_text(new, encoding='utf-8-sig')
    print(f'적용 완료 · 백업 {bk.relative_to(H.parent.parent)}')
elif not APPLY:
    print('(드라이런 — 바꾼 것 없음. 적용은 --apply)')
