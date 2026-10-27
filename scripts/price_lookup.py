#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""재연마 정가 조회 (price_lookup) — 말로 한 품목 → 표준 품목명 → 정가    2026-10-27 Cowork 신설

대표님 지시(2026-10-27, 한경준님 전달): 고객이 묻거나 전표를 입력할 때 단가표 기반으로 금액을 자동 응답.
1단계 = 조회 엔진 + 사내 시연 화면. **정가만** 보여 준다(할인율 · 사업장 단가 · ERP 가격은 쓰지 않음).

정가의 근거 (위에서부터)
  ① 정가표 계산 — raw/단가표/ 최신 「정가표(YY.MM)」 시트. 판독 로직은 price_audit.Blocks.expect 를 그대로 쓴다
     (판독 규칙: wiki/standards/재연마-정가표-읽는법.md). 정가표는 대외비가 아니다(CLAUDE.md §4-1).
  ② 등록 품목 정가 — 정가표 블록이 없는 형상(챔퍼 · 테이퍼 · 원통연삭 등)은 등록 정가를 쓴다.
     2026-10-27 부터 **ERP 「품목정보조회」 내려받기 파일**(raw/단가표/YYMMDD/*_품목정보조회_*.xlsx — 품목코드 · 품목명 · 정가 열만)을
     먼저 읽고, 없으면 9월 단가 검수 _완료 파일(28열 정가)을 읽는다. 할인율 · 단가 · 마진 열은 읽지 않는다.
  ③ 두 값이 다르거나, 사업장 파일끼리 정가가 다르면 「확인 필요」로 답한다 — 고객에게 내보내지 않는다.

사용:
  python scripts\price_lookup.py "10파이 2날 볼 고경도"
  python scripts\price_lookup.py "D6 4날 평 초경 밑옆날 일반코팅"
  python scripts\price_lookup.py --test            # 내장 시험 문장 전부
  python scripts\price_lookup.py --export-json out.json   # 시연 화면용 정가 데이터(정가만)
정가표 원본은 읽기만 한다(수정 금지 — 2026-09-02 한경준님 지시).
"""
import argparse, collections, glob, json, os, re, sys, warnings

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
warnings.filterwarnings('ignore', category=UserWarning)
import openpyxl
import price_audit as pa

PRICE_DIR = os.path.join(ROOT, 'raw', '단가표')
COL_NAME, COL_CODE, COL_PRICE = 3, 2, 28     # 1-based, 품목일괄등록 시트 (정가 열만)

# ── 입력 해석 사전 ───────────────────────────────────────────────
SHAPES = [   # (정규식, 표준 형상) — 위에서부터 먼저 맞는 것
    (r'라핑\s*(?:볼|ball)', '라핑볼'), (r'라핑\s*(?:코너|cr|레디우스|radius)', '라핑코너'),
    (r'라핑\s*(?:평|플랫|flat|스퀘어|square)?', '라핑평'),
    (r'테이퍼\s*드릴', '테이퍼드릴'), (r'테이퍼\s*(?:볼|ball)', '테이퍼볼'), (r'테이퍼\s*(?:코너|cr)', '테이퍼코너'),
    (r'테이퍼\s*(?:평|플랫|flat)?', '테이퍼평'), (r'스[탭텝]\s*드릴', '스탭드릴'),
    (r'리머|reamer', '리머'), (r'드릴|drill', '드릴'), (r'챔퍼|면취|chamfer', '챔퍼'),
    (r'카운터\s*보[어아]', '카운터보어'), (r'카운터\s*싱크', '카운터싱크'),
    (r'코너\s*r?|레디우스|radius|\bcr\b|코너알', '코너'), (r'볼|ball|\bbe\b', '볼'),
    (r'평|플랫|flat|스퀘어|square|\bfe\b', '평'),
]
PARTS = [(r'밑\s*(?:옆날|외경|골수리)', '밑옆날'), (r'밑날\s*\+\s*외경|밑날외경', '밑옆날'),
         (r'골\s*수리', '골수리'), (r'밑날|선단|바닥날|엔드날|end', '밑날'), (r'옆날|외경|side', '옆날')]
COATS = [(r'비\s*코팅|무\s*코팅|노\s*코팅|코팅\s*(?:없|안|x)|non[\s-]*coat', '비코팅'),
         (r'고경도', '고경도코팅'), (r'일반\s*코팅|일반|코팅', '일반코팅')]
MATS = [(r'초경|카바이드|carbide|초경합금', '초경'), (r'hss|하이스|고속도강|하이스피드', 'HSS')]
EXTRA_SHAPES = []   # 등록 품목에만 있는 형상(날붙이초경 · 역R · 볼재생 …) — Lookup 이 채운다. 긴 것부터 먼저 본다
BLADE_WORD = {'한': 1, '두': 2, '세': 3, '네': 4, '다섯': 5, '여섯': 6}
COAT_LABEL = {'비코팅': '비코팅', '일반코팅': '일반 코팅', '고경도코팅': '고경도 코팅'}


def parse_query(text):
    """자유 입력 → dict(blade, shape, dia, mat, part, coat) + missing · assumed 목록."""
    t = ' ' + str(text).lower().replace('Ø', 'ø').replace('φ', 'ø').replace('Φ', 'ø') + ' '
    t = re.sub(r'([가-힣])(\d)', r'\1 \2', t)
    q = {}
    # 이미 표준 품목명(슬래시 6필드)이면 그대로
    if t.count('/') >= 5:
        p = pa.parse_name(text.strip())
        if p:
            q = dict(blade=p['blade'], shape=p['shape'], dia=p['dia'], mat=p['mat'].upper() if p['mat'].lower() == 'hss' else p['mat'],
                     part=p['part'], coat=p['coat'])
            return _finish(q, [])
    # 날수
    m = re.search(r'(?<![\d.])(\d{1,2})\s*(?:날|f\b|flute|fl\b|낭)', t) or re.search(r'(한|두|세|네|다섯|여섯)\s*날', t)
    if m:
        q['blade'] = int(m.group(1)) if m.group(1).isdigit() else BLADE_WORD[m.group(1)]
        t = t[:m.start()] + ' ' + t[m.end():]
    # 코너 R 값(형상 힌트로만 — 정가표는 R 값을 구분하지 않는다)
    rr = re.search(r'\br\s*(\d+(?:\.\d+)?)', t)
    if rr:
        q['r'] = float(rr.group(1)); t = t[:rr.start()] + ' ' + t[rr.end():]
    # 직경: 단위 · 기호가 붙은 숫자 우선, 없으면 남은 첫 숫자
    m = (re.search(r'(?:ø|파이|phi|\bd)\s*(\d+(?:\.\d+)?)', t) or re.search(r'(\d+(?:\.\d+)?)\s*(?:mm|파이|ø|phi)', t)
         or re.search(r'(\d+(?:\.\d+)?)', t))
    if m:
        q['dia'] = float(m.group(1)); t = t[:m.start()] + ' ' + t[m.end():]
    for s in EXTRA_SHAPES:
        if s.lower() in t:
            q['shape'] = s; break
    for pats, key in ((SHAPES, 'shape'), (PARTS, 'part'), (COATS, 'coat'), (MATS, 'mat')):
        if key in q:
            continue
        for pat, val in pats:
            if re.search(pat, t):
                q[key] = val; break
    if 'shape' not in q and 'r' in q:
        q['shape'] = '코너'
    return _finish(q, [])


def _finish(q, assumed):
    if 'mat' not in q:
        q['mat'] = '초경'; assumed.append('재질 = 초경(입력 없음)')
    if 'part' not in q:
        q['part'] = '밑날'; assumed.append('가공부 = 밑날(입력 없음)')
    missing = [k for k in ('shape', 'dia') if k not in q]
    q['missing'], q['assumed'] = missing, assumed
    return q


def std_name(blade, shape, dia, mat, part, coat):
    d = f'{dia:g}'
    return f'{blade}날/{shape}/{d}mm/{mat}/{part}/{COAT_LABEL.get(coat, coat)}'


def _key(nm):
    """품목명 비교 키 — 공백 제거 · 소문자 · mm 대소문자 · 라핑=라핑평 · 직경 숫자 정규화."""
    p = [x.strip() for x in str(nm).split('/')]
    if len(p) < 6:
        return re.sub(r'\s+', '', str(nm)).lower()
    m = re.match(r'^([\d.]+)', p[2])
    dia = f'{float(m.group(1)):g}' if m else p[2].lower()
    shape = '라핑평' if p[1] == '라핑' else p[1]
    part = p[4].replace(' ', '')
    if part in ('밑골수리', '밑옆날', '밑골수리날'):
        part = '밑옆날'
    return '/'.join([re.sub(r'\s+', '', p[0]), shape, dia, p[3].lower(), part, p[5].replace(' ', '')]).lower()


class Lookup:
    def __init__(self, price_dir=PRICE_DIR):
        pl_path = sorted(glob.glob(os.path.join(price_dir, '*정가표*.xlsx')))
        pl_path = [p for p in pl_path if not os.path.basename(p).startswith('~$')]
        if not pl_path:
            sys.exit(f'정가표 파일 없음: {price_dir}')
        self.pl_path = pl_path[-1]
        self.pl = pa.PriceList(self.pl_path)
        self.blocks = pa.Blocks(self.pl)
        self._patch_coat_alias()
        self.drill = self._drill_bands()
        self.master, self.conflict, self.master_files = {}, {}, []
        self._load_master(price_dir)

    def _patch_coat_alias(self):
        """블록 그룹 라벨이 「비코팅 / 코팅 / 고경도 코팅」 인 블록은 「코팅」 이 일반 코팅이다.
        price_audit.alias_groups 는 코팅 그룹이 둘 이상이면 「코팅」 에 일반 별칭을 붙이지 않아
        일반코팅 조회가 None 이 된다(예: 초경 FLAT E/M 밑옆날 4날 Ø6 — 2026-10-27 발견).
        여기서만 별칭을 더한다(price_audit 는 고치지 않음)."""
        self.alias_patched = 0
        for key, blk in self.blocks.v.items():
            if not blk or not isinstance(blk, tuple) or len(blk) != 2 or not isinstance(blk[1], dict):
                continue
            cols = blk[1]
            if '코팅' in cols and not any(k in cols for k in ('일반', '일반코팅', '일반 코팅')):
                for a in ('일반', '일반코팅', '일반 코팅'):
                    cols[a] = cols['코팅']
                self.alias_patched += 1
        for key, blk in self.blocks.h.items():
            if not blk or len(blk) != 2 or not isinstance(blk[1], dict):
                continue
            rows = blk[1]
            for n in ('2', '4'):
                if ('코팅' + n) in rows and ('일반' + n) not in rows:
                    rows['일반' + n] = rows['코팅' + n]; self.alias_patched += 1

    def _drill_bands(self):
        """「드릴/면취/NC 스포팅」 블록 — 날경 「a - b」 구간 × (비코팅, 코팅). 표 주석 「HSS/초경 동일가격」.
        고경도 코팅 = 「코팅」 열(등록 품목 고경도 드릴 10 / 10 일치, 2026-10-27 실측). 날수 구분 없음."""
        pos = self.pl.find(r'^드릴/면취/NC 스포팅$')
        if not pos:
            return []
        tr, tc = pos
        out, r = [], tr + 2
        while r <= self.pl.ws.max_row:
            got = False
            for c0 in (tc, tc + 3):
                m = re.match(r'^\s*([\d.]+)\s*-\s*([\d.]+)\s*$', str(self.pl.ws.cell(r, c0).value or ''))
                if m:
                    got = True
                    nc, co = self.pl.ws.cell(r, c0 + 1).value, self.pl.ws.cell(r, c0 + 2).value
                    out.append((float(m.group(1)), float(m.group(2)),
                                nc if isinstance(nc, (int, float)) else None, co if isinstance(co, (int, float)) else None))
            if not got:
                break
            r += 1
        return sorted(out)

    def drill_price(self, dia, coat):
        for a, b, nc, co in self.drill:
            if a - 0.05 - 1e-9 <= dia <= b + 1e-9:     # 구간 사이(예: 4.0 ~ 4.1)는 아래 구간 끝 + 0.05 까지 그 구간
                return nc if coat == '비코팅' else co
        return None

    def _load_master(self, price_dir):
        # ① ERP 품목정보조회 내려받기(가장 최근 폴더) — 열: 1 품목코드 · 2 품목명 · 6 정가 (2026-10-27 실측 머리글)
        erp = sorted(glob.glob(os.path.join(price_dir, '*', '*_품목정보조회_*.xlsx')))
        erp = [f for f in erp if not os.path.basename(f).startswith('~$')]
        if erp:
            last = os.path.dirname(erp[-1])
            files = [(f, 0, 1, 2, 6) for f in erp if os.path.dirname(f) == last]
            self.master_src = 'ERP 품목정보조회 ' + os.path.basename(last)
        else:   # ② 9월 단가 검수 _완료 파일 — 품목일괄등록 시트 3 품목명 · 2 코드 · 28 정가
            dirs = sorted(d for d in glob.glob(os.path.join(price_dir, '*단가 검수*')) if os.path.isdir(d))
            files = [(f, '품목일괄등록', COL_CODE, COL_NAME, COL_PRICE) for f in sorted(glob.glob(os.path.join(dirs[-1], '*_완료.xlsx')))] if dirs else []
            self.master_src = '단가 검수 _완료 파일'
        vals = collections.defaultdict(set); names = {}
        for f, sh, cc, cn, cp in files:
            if os.path.basename(f).startswith('~$'):
                continue
            self.master_files.append(os.path.basename(f))
            wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
            ws = wb.worksheets[sh] if isinstance(sh, int) else wb[sh]
            for r in ws.iter_rows(min_row=3, values_only=True):
                if not r or len(r) < cp or not r[cn - 1]:
                    continue
                try:
                    pr = float(r[cp - 1])
                except (TypeError, ValueError):
                    continue
                if pr <= 0:
                    continue
                k = _key(r[cn - 1]); vals[k].add(pr); names.setdefault(k, (str(r[cn - 1]).strip(), r[cc - 1]))
        std = {'평', '볼', '코너', '라핑평', '라핑볼', '라핑코너', '라핑', '리머', '드릴', '챔퍼', '테이퍼드릴', '테이퍼평', '테이퍼볼', '테이퍼코너',
               '스탭드릴', '카운터보어', '카운터싱크'}
        extra = {k.split('/')[1] for k in vals if k.count('/') >= 5} - std
        EXTRA_SHAPES[:] = sorted((s for s in extra if len(s) >= 2 and not re.search(r'\d', s)), key=len, reverse=True)
        for k, v in vals.items():
            if len(v) == 1:
                self.master[k] = (next(iter(v)),) + names[k]
            else:
                self.conflict[k] = sorted(v)

    def price_one(self, blade, shape, dia, mat, part, coat):
        """한 품목의 정가 판정 → dict(price, source, status, name, note)."""
        name = std_name(blade, shape, dia, mat, part, coat)
        k = _key(name)
        calc = None
        if shape == '드릴' and part == '밑날' and blade == 2 and coat != '고경도코팅':   # 고경도 드릴은 ERP 가 코팅 × 약 1.07(10-27 확인) → 등록 정가   # 3날 · 4날 초경 드릴은 블록과 다름(등록 정가 14건 불일치, 2026-10-27) → 등록 정가
            calc = self.drill_price(dia, coat)
        elif shape in ('평', '볼', '코너', '라핑평', '라핑볼', '라핑코너', '리머'):
            try:
                calc = self.blocks.expect(mat=mat, shape=shape, part=part, coat=coat, blade=blade, dia=dia)
            except Exception:
                calc = None
        reg = self.master.get(k)
        out = dict(name=name, price=None, source='', status='', note='', code=reg[2] if reg else None)
        if k in self.conflict:
            out.update(status='확인 필요', note='사업장 파일끼리 등록 정가가 다름', price=calc)
            out['source'] = '정가표 계산(참고)' if calc else ''
            return out
        if calc is not None and reg and abs(calc - reg[0]) > 0.5:
            out.update(status='확인 필요', note='정가표 계산값과 등록 정가가 다름', price=calc, source='정가표 계산(참고)')
            return out
        if calc is not None:
            out.update(price=calc, source=f'{self.pl.name}' + (' · 등록 품목 일치' if reg else ' · 미등록 규격'), status='OK')
            return out
        if reg:
            out.update(price=reg[0], source='등록 품목 정가(정가표 블록 없는 형상)', status='OK')
            return out
        near = self.nearest(k)
        out.update(status='없음', note='정가표 블록도, 등록 품목도 없음 — 담당자 확인' + (f' (가까운 등록 규격: {near})' if near else ''))
        return out

    def nearest(self, k, n=2):
        """같은 날수 · 형상 · 재질 · 가공부 · 코팅의 등록 품목 중 직경이 가까운 것(정가는 안 보임 — 규격만)."""
        p = k.split('/')
        if len(p) < 6:
            return ''
        try:
            d = float(p[2])
        except ValueError:
            return ''
        cand = []
        for kk in self.master:
            q = kk.split('/')
            if len(q) >= 6 and q[:2] == p[:2] and q[3:] == p[3:]:
                try:
                    cand.append((abs(float(q[2]) - d), float(q[2])))
                except ValueError:
                    pass
        return ' · '.join(f'Ø{x:g}' for _, x in sorted(cand)[:n])

    def answer(self, text):
        q = parse_query(text)
        res = dict(query=text, parsed={k: q.get(k) for k in ('blade', 'shape', 'dia', 'mat', 'part', 'coat', 'r')},
                   assumed=q['assumed'], missing=q['missing'], rows=[])
        if q['missing']:
            return res
        blades = [q['blade']] if q.get('blade') else [2, 4]
        coats = [q['coat']] if q.get('coat') else ['비코팅', '일반코팅', '고경도코팅']
        if not q.get('blade'):
            res['assumed'].append('날수 입력 없음 → 2날 · 4날(3날 이상 같은 값) 모두 표시')
        if not q.get('coat'):
            res['assumed'].append('코팅 입력 없음 → 비코팅 · 일반 · 고경도 모두 표시')
        for b in blades:
            for c in coats:
                res['rows'].append(self.price_one(b, q['shape'], q['dia'], q['mat'], q['part'], c))
        return res


def fmt(res):
    lines = [f"입력: {res['query']}"]
    p = res['parsed']
    if res['missing']:
        miss = ' · '.join({'shape': '형상(평/볼/코너/라핑…)', 'dia': '직경(mm)'}[m] for m in res['missing'])
        lines.append(f'  ❓ {miss} 을(를) 알려 주세요.')
        return '\n'.join(lines)
    for a in res['assumed']:
        lines.append(f'  ※ {a}')
    for r in res['rows']:
        pr = f"{r['price']:,.0f}원" if r['price'] else '-'
        tag = {'OK': '', '확인 필요': ' ⚠️ 확인 필요', '없음': ' ❓ 없음'}.get(r['status'], '')
        lines.append(f"  {r['name']:<40} 정가 {pr:>10}{tag}  [{r['source'] or r['note']}]" + (f" ({r['note']})" if r['note'] and r['source'] else ''))
    return '\n'.join(lines)


TESTS = ['10파이 2날 볼 고경도', 'D6 4날 평 초경 밑옆날 일반코팅', '2날/라핑평/12.5mm/HSS/밑날/일반 코팅',
         'ø8 코너 R0.5 2F 비코팅', '하이스 라핑 볼 16mm 두날 코팅', '3날 평 10mm', '드릴 6.8 HSS 비코팅 2날', '볼 엔드밀 얼마?']


def export_json(lk, path, step=0.05, dmax=60.0):
    """시연 화면용 데이터 — 정가만. ① 정가표 계산 구간표 ② 블록 없는 형상의 등록 품목 정가 ③ 확인 필요 키."""
    combos, n = {}, int(round(dmax / step))
    for mat in ('초경', 'HSS'):
        for shape in ('평', '볼', '코너', '라핑평', '라핑볼', '라핑코너', '리머'):
            for part in ('밑날', '밑옆날', '골수리', '옆날'):
                for coat in ('비코팅', '일반코팅', '고경도코팅'):
                    for blade in (2, 4):
                        runs, last = [], None
                        for i in range(1, n + 1):
                            d = round(i * step, 3)
                            try:
                                v = lk.blocks.expect(mat=mat, shape=shape, part=part, coat=coat, blade=blade, dia=d)
                            except Exception:
                                v = None
                            if runs and v == last:
                                runs[-1][1] = d
                            else:
                                runs.append([d, d, v]); last = v
                        runs = [r for r in runs if r[2] is not None]
                        if runs:
                            combos['|'.join([mat, shape, part, coat, str(blade)])] = runs
    for mat in ('초경', 'HSS'):          # 2날 드릴 — 「드릴/면취/NC 스포팅」 블록
        for coat in ('비코팅', '일반코팅'):
            runs, last = [], None
            for i in range(1, n + 1):
                d = round(i * step, 3)
                v = lk.drill_price(d, coat)
                if runs and v == last:
                    runs[-1][1] = d
                else:
                    runs.append([d, d, v]); last = v
            runs = [r for r in runs if r[2] is not None]
            if runs:
                combos['|'.join([mat, '드릴', '밑날', coat, '2'])] = runs
    reg, mismatch = {}, []
    for k, (pr, nm, code) in lk.master.items():
        p = k.split('/')
        sh = p[1] if len(p) >= 6 else ''
        reg[k] = pr
        if len(p) >= 6 and sh in ('평', '볼', '코너', '라핑평', '라핑볼', '라핑코너', '리머', '드릴'):
            try:
                b, d = int(re.match(r'\d+', p[0]).group()), float(p[2])
            except Exception:
                continue
            mat = 'HSS' if p[3] == 'hss' else p[3]
            if p[5] in ('비코팅', '일반코팅', '고경도코팅') and p[4] in ('밑날', '밑옆날', '골수리', '옆날'):
                if lk.price_one(b, sh, d, mat, p[4], p[5])['status'] == '확인 필요':
                    mismatch.append(k)
    out = dict(made=pa.now_kst().strftime('%Y-%m-%d %H:%M KST'), pricelist=os.path.basename(lk.pl_path), sheet=lk.pl.name, master_src=lk.master_src,
               step=step, combos=combos, registered=reg, conflict=sorted(lk.conflict), mismatch=sorted(mismatch),
               extra_shapes=EXTRA_SHAPES,
               note='정가만 · 할인율/사업장 단가 없음 · 실제 견적은 담당자 확인')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    return out


def main():
    ap = argparse.ArgumentParser(description='재연마 정가 조회')
    ap.add_argument('query', nargs='*')
    ap.add_argument('--test', action='store_true')
    ap.add_argument('--json', action='store_true', help='결과를 JSON 으로')
    ap.add_argument('--export-json', default=None)
    ap.add_argument('--export-html', default=None, help='사내 시연 화면(정가 데이터 내장 HTML 한 파일)')
    ap.add_argument('--force', action='store_true', help='정가표 블록을 못 찾아도 내보내기(공개 웹은 기본 거부)')
    ap.add_argument('--export-web', default=None, help='공개 웹용 price-data.js · price-lookup.js 를 이 폴더에 쓴다(예: dist)')
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    lk = Lookup()
    if lk.blocks.missing:   # 🔴 조용한 성공 방지 — 정가표 블록 제목이 바뀌면 그 형상은 정가표 계산이 빠진다
        print(f"⚠️ 정가표에서 못 찾은 블록 {len(lk.blocks.missing)}개: " + ' · '.join(lk.blocks.missing))
        print(f"   정가표: {os.path.basename(lk.pl_path)} (수정 {pa.datetime.datetime.fromtimestamp(os.path.getmtime(lk.pl_path), pa.KST):%Y-%m-%d %H:%M} KST)")
        if a.export_web and not a.force:
            print('   공개 웹 내보내기를 멈춥니다 — 정가표 확인 뒤 다시 실행하거나 --force')
            return 2
    if a.export_web:
        # 공개 웹(견적 문의 페이지)용 — 정가만. 2026-10-27 한경준님 「정가는 공개해도 됨」(decisions 2026-10-27 (10))
        import tempfile, shutil
        tmp = os.path.join(tempfile.gettempdir(), 'price_data_web.json')
        o = export_json(lk, tmp)
        os.makedirs(a.export_web, exist_ok=True)
        with open(os.path.join(a.export_web, 'price-data.js'), 'w', encoding='utf-8') as f:
            f.write('/* 재연마 공표 정가 데이터 — scripts/price_lookup.py --export-web 로 생성. 직접 고치지 말 것 */\n')
            f.write('window.PRICE_DATA=' + open(tmp, encoding='utf-8').read() + ';\n')
        shutil.copyfile(os.path.join(HERE, 'price_lookup_core.js'), os.path.join(a.export_web, 'price-lookup.js'))
        print(f"공개 웹 파일 저장: {a.export_web}/price-data.js · price-lookup.js · 구간표 {len(o['combos'])}조합 · 등록 품목 {len(o['registered'])}개")
        return 0
    if a.export_html:
        import tempfile
        tmp = os.path.join(tempfile.gettempdir(), 'price_data_tmp.json')
        o = export_json(lk, tmp)
        tpl = open(os.path.join(HERE, 'price_lookup_web.html'), encoding='utf-8').read()
        core = open(os.path.join(HERE, 'price_lookup_core.js'), encoding='utf-8').read()
        data = open(tmp, encoding='utf-8').read().replace('</', '<\\/')
        assert tpl.count('/*__DATA__*/null') == 1 and tpl.count('/*__CORE__*/') == 1
        with open(a.export_html, 'w', encoding='utf-8') as f:
            f.write(tpl.replace('/*__DATA__*/null', data).replace('/*__CORE__*/', core.replace('</', '<\\/')))
        print(f"시연 화면 저장: {a.export_html} · 구간표 {len(o['combos'])}조합 · 등록 품목 {len(o['registered'])}개 · 확인 필요 {len(o['conflict']) + len(o['mismatch'])}개")
        return 0
    if a.export_json:
        o = export_json(lk, a.export_json)
        print(f"정가 데이터 저장: {a.export_json} · 구간표 {len(o['combos'])}조합 · 등록 품목 {len(o['registered'])}개 · 확인 필요 {len(o['conflict']) + len(o['mismatch'])}개")
        return 0
    qs = TESTS if a.test else [' '.join(a.query)] if a.query else []
    if not qs:
        ap.print_help(); return 1
    print(f'정가표: {os.path.basename(lk.pl_path)} [{lk.pl.name}] · 등록 정가 출처 {lk.master_src} · 등록 품목 {len(lk.master):,}개(사업장 정가 다름 {len(lk.conflict)}개) · 파일 {", ".join(lk.master_files)}')
    for q in qs:
        r = lk.answer(q)
        print(json.dumps(r, ensure_ascii=False, default=str) if a.json else fmt(r))
    return 0


if __name__ == '__main__':
    sys.exit(main())
