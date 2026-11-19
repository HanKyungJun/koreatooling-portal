#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
이카운트 일일업무일지 초안 「재료」 → 구글 드라이브 (Claude 예약 작업 「업무일지 초안」이 읽음)
실행: python scripts/export_worklog_material.py [YYYY-MM-DD] [--no-upload]
출력: private_local\worklog_material\YYYY-MM-DD.txt → 드라이브 「cnc-wiki-auto/worklog_material.txt」

2026-11-19 신규 (decisions 2026-11-19 (5)) — 새 PC 이전
  - 새 PC 에서는 Claude 예약 실행이 PC 폴더를 못 읽는다(연결 폴더 0개 · device_bash 없음 — 11-19 14:09 진단).
    그래서 16:00 배치가 재료만 모아 드라이브에 올리고, 예약 작업은 드라이브의 이 파일 하나만 읽어 초안을 쓴다.
  - 재료: ① ANCA 수량 = 오늘 일일보고 xlsx 「일일 요약」 「합계  수량」 오늘 값(16:00 전 생성이거나 없으면
    erp/snapshot/pw_nc_<월>-01_<오늘>.csv 의 오늘 ok + bad, 둘 다 없으면 「확인 필요」)
    ② worklog.md 오늘 블록 원문 ③ decisions.md 오늘 제목 ④ wiki/_private/업무일지_연장근무.md 「## 목록」 원문
  - 금액 · 단가는 넣지 않는다(ERP 스냅샷은 수량 열만 읽음).
"""
import sys, io, re, csv, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE    = Path(__file__).resolve().parent.parent
DAILY   = BASE / 'wiki' / 'reports' / 'daily'
HANDOFF = BASE / 'wiki' / '_handoff'
OT_FILE = BASE / 'wiki' / '_private' / '업무일지_연장근무.md'
SNAP    = BASE / 'erp' / 'snapshot'
OUTDIR  = BASE / 'private_local' / 'worklog_material'
LOG     = DAILY / 'run.log'
KST     = timezone(timedelta(hours=9))


def log(msg):
    print(msg)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass


def anca_count(d: str):
    x = DAILY / f'{d}_일일보고.xlsx'
    if x.exists():
        try:
            import openpyxl
            ws = openpyxl.load_workbook(x, data_only=True, read_only=True)['일일 요약']
            title, total = None, None
            for row in ws.iter_rows(values_only=True):
                a = row[0] if row else None
                if title is None and isinstance(a, str):
                    title = a
                if isinstance(a, str) and a.startswith('합계') and '수량' in a:
                    total = row[1]
                    break
            m = re.search(r'\((\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}) 생성', title or '')
            if total is not None and m and (m.group(1) > d or int(m.group(2)) >= 16):
                return f'{int(total)}', f'일일보고 xlsx ({m.group(1)} {m.group(2)}:{m.group(3)} 생성)'
        except Exception as ex:
            log(f'[worklog-material] WARN - xlsx read failed: {ex}')
    snap = SNAP / f'pw_nc_{d[:8]}01_{d}.csv'
    if snap.exists():
        try:
            n = 0
            with open(snap, encoding='utf-8-sig', newline='') as f:
                for r in csv.DictReader(f):
                    if str(r.get('work_dt', ''))[:10] == d:
                        n += int(float(r.get('ok') or 0)) + int(float(r.get('bad') or 0))
            return f'{n}', f'ERP 스냅샷 {snap.name}'
        except Exception as ex:
            log(f'[worklog-material] WARN - snapshot read failed: {ex}')
    return '확인 필요', '일일보고 · 스냅샷 없음'


def blocks(text: str, d: str):
    """`## YYYY-MM-DD` 로 시작하는 오늘 블록 원문들."""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith('## '):
            if cur is not None:
                out.append('\n'.join(cur).rstrip())
            cur = [line] if line[3:13] == d else None
        elif cur is not None:
            cur.append(line)
    if cur is not None:
        out.append('\n'.join(cur).rstrip())
    return out


def ot_list():
    if not OT_FILE.exists():
        return None
    lines, on = [], False
    for line in OT_FILE.read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            on = line.strip() == '## 목록'
            continue
        if on:
            lines.append(line)
    return '\n'.join(lines).strip('\n')


def main():
    pos = [a for a in sys.argv[1:] if not a.startswith('--')]
    d = pos[0] if pos else date.today().isoformat()
    now = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
    n, src = anca_count(d)
    wl = blocks((HANDOFF / 'worklog.md').read_text(encoding='utf-8-sig'), d) if (HANDOFF / 'worklog.md').exists() else []
    dec = [b.splitlines()[0] for b in blocks((HANDOFF / 'decisions.md').read_text(encoding='utf-8-sig'), d)] \
        if (HANDOFF / 'decisions.md').exists() else []
    ot = ot_list()
    parts = [
        f'# 업무일지 재료 {d}',
        f'date: {d}',
        f'generated: {now} KST',
        '',
        '## ANCA',
        f'count: {n}',
        f'source: {src}',
        '',
        f'## worklog 오늘 블록 ({len(wl)}개)',
        *(wl or ['(없음)']),
        '',
        f'## decisions 오늘 제목 ({len(dec)}개)',
        *(dec or ['(없음)']),
        '',
        '## 연장근무 목록',
        ot if ot is not None else '(파일 없음)',
        '',
        '## END',
    ]
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / f'{d}.txt'
    out.write_text('\n'.join(parts) + '\n', encoding='utf-8')
    log(f'[worklog-material] OK - {d}: ANCA {n} ({src}) · worklog {len(wl)} · decisions {len(dec)} -> {out.name}')
    if '--no-upload' in sys.argv:
        return
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from drive_upload import upload_text
        action, _ = upload_text(out, 'worklog_material.txt')
        log(f'[worklog-material] DRIVE {action} - cnc-wiki-auto/worklog_material.txt')
    except Exception as ex:
        log(f'[worklog-material] ERROR - drive upload failed: {type(ex).__name__}: {ex}')


if __name__ == '__main__':
    main()
