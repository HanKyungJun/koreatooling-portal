#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""재연마 견적 판정 검수 문항 세트 만들기    2026-10-30 Cowork

신규 쇼핑몰 · ERP 개발사가 「우리 규칙과 같은 답을 내는지」 확인할 기준표.
규칙: wiki/standards/재연마-견적-판정-명세.md
  - 시트 「검수 문항」: 사람이 읽는 대표 문항(분류별) — 입력 → 기대 결과(품목명 · 상태 · 정가)
  - 시트 「여러 줄 견적」: quote_price 규칙(코팅 확인 · 합계)
  - 시트 「전체 구간 경계」: 정가표 블록마다 구간 상한 · 상한+0.05 mm 자동 문항(기계 대조용)
  - 같은 내용 JSON(개발사 자동 시험용) + 그때의 price_data.json
기대값 = Python 기준 엔진(price_lookup.py). 같은 데이터로 웹 엔진(price_lookup_core.js, node)을 돌려 대조한 결과도 적는다.

실행: python scripts\price_acceptance_cases.py [출력 폴더]   (기본 outputs\price_acceptance_YYYYMMDD\)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import openpyxl  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402
from openpyxl.utils import get_column_letter as L  # noqa: E402

import price_lookup as pl  # noqa: E402
import quote_price as qp  # noqa: E402

today = datetime.now().strftime('%Y%m%d')
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'outputs', f'price_acceptance_{today}')
os.makedirs(out, exist_ok=True)
lk = pl.Lookup()

# ── 대표 문항(분류, 입력, 비고) ─────────────────────────────
C = []


def add(cat, q, note=''):
    C.append((cat, q, note))


for q in ['10파이 2날 평 비코팅', '6 4날 볼 일반코팅', 'Ø12 2날 코너 R1 고경도', '8 4날 라핑 평 비코팅', '10 2날 라핑 볼 일반코팅',
          '12 4날 라핑 코너 고경도', '4날 리머 10파이 HSS 비코팅', '2날 드릴 6 초경 비코팅', '하이스 드릴 41mm 2날 비코팅']:
    add('A 기본(형상별)', q)
for q, n in [('2날 평 6 비코팅', '구간 상한 = 6이하에 포함'), ('2날 평 6.05 비코팅', '다음 구간'), ('2날 평 10 비코팅', ''),
             ('2날 평 10.05 비코팅', ''), ('2날 드릴 20 초경 비코팅', '초경 드릴 마지막 구간'),
             ('2날 드릴 20.05 초경 비코팅', '초경 드릴 표 밖'), ('2날 드릴 50 HSS 비코팅', 'HSS 드릴 마지막 구간'),
             ('2날 드릴 50.5 HSS 비코팅', 'HSS 드릴 표 밖'), ('4날 평 30 비코팅', ''), ('4날 평 30.5 비코팅', '구간 라벨 사이 빈틈 여부'),
             ('4날 리머 32 HSS 비코팅', 'HSS 리머 32이하'), ('4날 리머 32.5 HSS 비코팅', 'HSS 리머 「32이하」 · 「33이상」 사이')]:
    add('B 직경 경계', q, n)
add('C 기본값 가정', '10파이 2날 볼 고경도', '재질 · 부위 입력 없음 → 초경 · 밑날')
add('C 기본값 가정', '10 2날 평 하이스 비코팅', '재질 HSS · 부위 입력 없음')
add('D 코팅 미입력', '10파이 2날 볼', '코팅 3종 모두')
add('D 코팅 미입력', 'D6 4날 평 밑옆날', '')
add('E 날수 미입력', '10파이 볼 고경도', '2날 · 3날 이상 모두')
add('E 날수 미입력', '하이스 드릴 10mm 비코팅', '드릴 3날 이상은 표 밖')
for q, n in [('4날 리머 10파이 HSS 고경도', '리머 고경도 = 확인 필요(decisions 2026-10-30 (3))'), ('4날 리머 10파이 초경 고경도', ''),
             ('초경 드릴 22mm 2날 비코팅', '드릴 표 밖 · ERP 옛 정가 있음'), ('4날 초경 드릴 10파이 비코팅', '3날 이상 드릴'),
             ('2날 드릴 16 HSS 고경도', 'HSS 드릴 고경도 — 정가표 값 보관 중, ERP Ø16 정가 빈칸')]:
    add('F 확인 필요', q, n)
for k in sorted(lk.conflict)[:2]:
    add('F 확인 필요', k, '사업장끼리 등록 정가 다름')
mm = []
for k, (pr, nm, code) in sorted(lk.master.items()):
    p = k.split('/')
    if len(p) >= 6 and p[1] in ('평', '볼', '코너', '라핑평', '라핑볼', '라핑코너') and p[5] in ('비코팅', '일반코팅', '고경도코팅'):
        try:
            r = lk.answer(nm)['rows']
        except Exception:
            continue
        if len(r) == 1 and r[0]['status'] == '확인 필요' and '등록 정가' in (r[0].get('note') or ''):
            mm.append(nm)
    if len(mm) >= 3:
        break
for nm in mm:
    add('F 확인 필요', nm, '정가표 계산 ≠ ERP 등록 정가')
add('G 없음', '2날 평 70 비코팅', '정가표 · 등록 품목 모두 없음')
add('G 없음', '2날 드릴 22 초경 고경도', '')
add('H 정보 부족', '10파이 2날 고경도', '형상 없음')
add('H 정보 부족', '2날 볼 고경도', '직경 없음')
for q, n in [('하이스 볼 두날 8파이 무코팅', '하이스 · 두날 · 무코팅'), ('φ10 4F 평 코팅', 'φ · F · 「코팅」 = 일반'),
             ('D10 2날 스퀘어 노코팅', 'D · 스퀘어 · 노코팅'), ('10mm 2날 코너알 밑날+외경 고경도', '코너알 · 밑날+외경')]:
    add('I 문장 해석', q, n)
for q in ['2날/볼/10mm/초경/밑날/고경도 코팅', '4날/라핑평/12.5mm/HSS/밑날/일반 코팅']:
    add('J 품목명 6칸', q, '표준 품목명 그대로')
for q in ['2날 챔퍼 6 초경 비코팅', '2날 테이퍼 볼 6 초경 비코팅']:
    add('K 블록 없는 형상', q, 'ERP 등록 정가 또는 없음')
for q, n in [('10 2날 평 옆날 비코팅', '전장 없음 → 기본 금액 + 할증 안내'), ('10 2날 평 옆날 비코팅 L100', 'L = 100 정확히 → 할증 없음(초과 기준)'),
             ('10 2날 평 옆날 비코팅 L100.5', '100 초과 → 초경 ×1.2'), ('10 2날 평 옆날 비코팅 전장 150', '150 정확히 → Long ×1.2'),
             ('10 2날 평 옆날 비코팅 전장 151', '150 초과 → 초경 ×1.5'), ('10 2날 평 옆날 비코팅 전장 100 초과', '버튼 「100 mm 초과」 문구'),
             ('12 4날 라핑 평 밑옆날 비코팅 L130', '초경 라핑 ×1.5'), ('8 2날 볼 HSS 옆날 일반코팅 전장 150 초과', 'HSS ×2'),
             ('10 2날 평 비코팅 L120', '밑날 작업 → 할증 없음'), ('2날 드릴 10 초경 비코팅 L160', '드릴 → 할증 없음')]:
    add('L 전장 할증', q, n + ' — decisions 2026-10-30 (10) · (11)')


def py_rows(q):
    res = lk.answer(q)
    if res['missing']:
        return [dict(name='', status='정보 부족', price=None, note='미입력: ' + ', '.join(res['missing']))], res['assumed']
    return ([dict(name=r['name'], status=r['status'], price=r['price'] if r['status'] == 'OK' else None, note=r.get('note', ''))
             for r in res['rows']], res['assumed'])


cases = []
for i, (cat, q, note) in enumerate(C, 1):
    rows, asm = py_rows(q)
    cases.append(dict(no=i, cat=cat, input=q, note=note, assumed=asm, expect=rows))

# ── 전체 구간 경계(기계 대조용) ─────────────────────────────
data_path = os.path.join(out, 'price_data.json')
pl.export_json(lk, data_path)
D = json.load(open(data_path, encoding='utf-8'))
edge = []
for key, runs in sorted(D['combos'].items()):
    mat, shape, part, coat, b = key.split('|')
    for a, hi, v in runs:
        for d in (hi, round(hi + D['step'], 2)):
            r = lk.price_one(2 if b == '2' else 4, shape, d, mat, part, coat)
            edge.append(dict(key=key, dia=d, name=r['name'], status=r['status'], price=r['price'] if r['status'] == 'OK' else None))

# ── 여러 줄 견적 ────────────────────────────────────────────
HD = ['접수일시', '회사명', '담당자', '연락처', '이메일', '구분', '재질', '규격', '수량']
QC = [('재연마', '초경', 'Ø10 2날 볼 고경도 / 6 4날 평 일반코팅 밑옆날', '5 / 3', '모두 OK → 합계'),
      ('재연마', '초경', 'Ø10 2날 볼 고경도 / 6 4날 평', '5 / 3', '2줄 코팅 확인 → 일부 합계'),
      ('재연마', '초경', 'Ø10 2날 볼 / 2날 드릴 22', '2 / 1', '코팅 확인 + 드릴 표 밖'),
      ('재연마', 'SKD', 'Ø10 2날 평', '3', '재질 SKD → 대상 아님'),
      ('신품 구매', '초경', 'Ø10 2날 평', '3', '구분 신품 → 계산 안 함'),
      ('재연마', '초경', 'Ø10 2날 평 비코팅 / 8 4날 볼 고경도', '5', '규격 · 수량 줄 수 다름')]
quotes = []
for cat, mat, spec, qty, note in QC:
    r = qp.quote_row(lk, HD, ['', '', '', '', '', cat, mat, spec, qty])
    quotes.append(dict(category=cat, material=mat, spec=spec, qty=qty, note=note, applicable=r['applicable'],
                       lines=[dict(spec=x['spec'], qty=x['qty'], status=x['status'], price=x['price'] if x['status'] == 'OK' else None,
                                   subtotal=x['subtotal'], note=x['note']) for x in r['lines']],
                       total=r['total'], complete=r['complete'], reason=r.get('reason', '')))

# ── 웹 엔진(JS) 대조 ────────────────────────────────────────
js_res, js_note = {}, ''
node = shutil.which('node')
if node:
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, 'q.json'), 'w', encoding='utf-8') as f:
        json.dump([c['input'] for c in cases], f, ensure_ascii=False)
    runner = ("global.window=global;const fs=require('fs');window.PRICE_DATA=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));"
              "eval(fs.readFileSync(process.argv[3],'utf8'));const qs=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));"
              "const o={};for(const q of qs){const r=window.PriceLookup.answer(q);"
              "o[q]=r.q.missing.length?[['','정보 부족',null]]:r.rows.map(x=>[x.name,x.status,x.status==='OK'?x.price:null]);}"
              "process.stdout.write(JSON.stringify(o));")
    with open(os.path.join(tmp, 'run.js'), 'w', encoding='utf-8') as f:
        f.write(runner)
    try:
        p = subprocess.run([node, os.path.join(tmp, 'run.js'), data_path, os.path.join(HERE, 'price_lookup_core.js'),
                            os.path.join(tmp, 'q.json')], capture_output=True, text=True, encoding='utf-8', timeout=120)
        js_res = json.loads(p.stdout) if p.returncode == 0 else {}
        js_note = '' if p.returncode == 0 else (p.stderr or '')[:200]
    except Exception as e:
        js_note = f'{type(e).__name__}: {e}'
else:
    js_note = 'node 없음 — 웹 엔진 대조 생략'
same = diff = 0
for c in cases:
    j = js_res.get(c['input'])
    if j is None:
        c['js'] = '대조 안 함'
        continue
    pyv = [[r['name'], r['status'], r['price']] for r in c['expect']]
    ok = len(j) == len(pyv) and all(a[1] == b[1] and (a[2] or 0) == (b[2] or 0) and a[0].replace(' ', '') == b[0].replace(' ', '')
                                    for a, b in zip(j, pyv))
    c['js'] = '같음' if ok else '다름: ' + json.dumps(j, ensure_ascii=False)[:200]
    same += ok
    diff += (not ok)

# ── 저장 ────────────────────────────────────────────────────
meta = dict(made=datetime.now().strftime('%Y-%m-%d %H:%M'), pricelist=os.path.basename(lk.pl_path), sheet=lk.pl.name, master=lk.master_src,
            rule='wiki/standards/재연마-견적-판정-명세.md',
            js_check=f'웹 엔진 대조 같음 {same} · 다름 {diff}' + (f' ({js_note})' if js_note else ''))
with open(os.path.join(out, '재연마견적_검수문항.json'), 'w', encoding='utf-8') as f:
    json.dump(dict(meta=meta, cases=cases, edges=edge, quotes=quotes), f, ensure_ascii=False, indent=1)

H = Font(bold=True, color='FFFFFF')
HF = PatternFill('solid', fgColor='1F497D')
W = Alignment(wrap_text=True, vertical='top')


def head_row(ws, head):
    ws.append(head)
    for c in ws[ws.max_row]:
        c.font = H
        c.fill = HF
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)


def widths(ws, ws_w):
    for i, w in enumerate(ws_w, 1):
        ws.column_dimensions[L(i)].width = w


wb = openpyxl.Workbook()
ws = wb.active
ws.title = '검수 문항'
ws.append(['재연마 견적 판정 — 검수 문항 세트'])
ws['A1'].font = Font(bold=True, size=14)
ws.append([f"기준: {meta['pricelist']} 「{meta['sheet']}」 · {meta['master']} · 만든 시각 {meta['made']} · 규칙 {meta['rule']} · {meta['js_check']}"])
ws.append(['정가는 공표 정가(할인 전, 개당). 「OK」 줄만 금액이 있어야 정상이고, 그 밖 상태는 금액 없이 「담당자 확인」으로 보여야 한다.'])
ws.append([])
head_row(ws, ['번호', '분류', '입력', '기대 품목명', '기대 상태', '기대 정가 (원)', '비고 · 가정', '웹 엔진 대조'])
start = ws.max_row
for c in cases:
    for k, r in enumerate(c['expect']):
        nt = ' · '.join(x for x in [c['note']] + c['assumed'] if x)
        ws.append([c['no'] if k == 0 else '', c['cat'] if k == 0 else '', c['input'] if k == 0 else '', r['name'], r['status'], r['price'],
                   nt if k == 0 else '', c['js'] if k == 0 else ''])
widths(ws, [6, 16, 34, 40, 11, 13, 44, 12])
for row in ws.iter_rows(min_row=start + 1):
    for c in row:
        c.alignment = W
    if isinstance(row[5].value, (int, float)):
        row[5].number_format = '#,##0'
ws.freeze_panes = ws.cell(start + 1, 1)

ws2 = wb.create_sheet('여러 줄 견적')
head_row(ws2, ['번호', '구분', '재질', '규격(「 / 」로 줄 구분)', '수량', '줄 상태', '줄 정가 (원)', '줄 소계 (원)', '합계 (원)', '완결', '비고'])
for i, q in enumerate(quotes, 1):
    ws2.append([i, q['category'], q['material'], q['spec'], q['qty'],
                ' | '.join(x['status'] for x in q['lines']) or ('계산 안 함 — ' + q['reason']),
                ' | '.join(f"{x['price']:,.0f}" if x['price'] else '-' for x in q['lines']),
                ' | '.join(f"{x['subtotal']:,.0f}" if x['subtotal'] else '-' for x in q['lines']),
                q['total'], '예' if q['complete'] else '아니오(일부 합계)', q['note']])
widths(ws2, [6, 10, 8, 40, 10, 30, 20, 20, 12, 16, 30])
for row in ws2.iter_rows(min_row=2):
    for c in row:
        c.alignment = W
    if isinstance(row[8].value, (int, float)):
        row[8].number_format = '#,##0'

ws3 = wb.create_sheet('전체 구간 경계')
head_row(ws3, ['블록(재질|형상|부위|코팅|날수)', '직경 (mm)', '품목명', '상태', '정가 (원)'])
for e in edge:
    ws3.append([e['key'], e['dia'], e['name'], e['status'], e['price']])
widths(ws3, [40, 10, 40, 11, 12])
for row in ws3.iter_rows(min_row=2):
    if isinstance(row[4].value, (int, float)):
        row[4].number_format = '#,##0'
ws3.freeze_panes = 'A2'

xl = os.path.join(out, f'재연마견적_검수문항_{today}.xlsx')
wb.save(xl)
print(f'저장: {xl}')
print(f'  대표 문항 {len(cases)}건 · 구간 경계 {len(edge)}줄 · 여러 줄 견적 {len(quotes)}건 · {meta["js_check"]}')
