"""재연마 정가 조회 — 해석 · 조회 로직 (Python 판, 2026-10-29 Cowork)

scripts/price_lookup_core.js(웹 위젯)와 같은 규칙을 Python 으로 옮긴 것. 데이터는 price_data.json
(scripts/price_lookup.py --export-json 결과 — 정가만, 할인율 · 거래처 단가 없음)을 읽는다.

    core = PriceCore('price_data.json')
    core.answer('10파이 2날 볼 고경도')  → {'query', 'q', 'rows': [{'name', 'status', 'price', 'src'}]}
    core.price_one(2, '드릴', 6.0, '초경', '밑날', '비코팅')

status 가 OK 가 아니면 price 는 None. 드릴은 정가표 구간 안만 금액(표 밖은 ERP 옛 정가가 남아 있어 「담당자 확인」).
"""
import json
import re

BLOCK_SHAPES = ['평', '볼', '코너', '라핑평', '라핑볼', '라핑코너', '리머']
SHAPES = [(r'라핑\s*(?:볼|ball)', '라핑볼'), (r'라핑\s*(?:코너|cr|레디우스|radius)', '라핑코너'),
          (r'라핑\s*(?:평|플랫|flat|스퀘어|square)?', '라핑평'),
          (r'테이퍼\s*드릴', '테이퍼드릴'), (r'테이퍼\s*(?:볼|ball)', '테이퍼볼'), (r'테이퍼\s*(?:코너|cr)', '테이퍼코너'),
          (r'테이퍼\s*(?:평|플랫|flat)?', '테이퍼평'), (r'스[탭텝]\s*드릴', '스탭드릴'),
          (r'리머|reamer', '리머'), (r'드릴|drill', '드릴'), (r'챔퍼|면취|chamfer', '챔퍼'), (r'카운터\s*보[어아]', '카운터보어'),
          (r'카운터\s*싱크', '카운터싱크'),
          (r'코너\s*r?|레디우스|radius|\bcr\b|코너알', '코너'), (r'볼|ball|\bbe\b', '볼'), (r'평|플랫|flat|스퀘어|square|\bfe\b', '평')]
PARTS = [(r'밑\s*(?:옆날|외경|골수리)', '밑옆날'), (r'밑날\s*\+\s*외경|밑날외경', '밑옆날'), (r'골\s*수리', '골수리'),
         (r'밑날|선단|바닥날|엔드날|end', '밑날'), (r'옆날|외경|side', '옆날')]
COATS = [(r'비\s*코팅|무\s*코팅|노\s*코팅|코팅\s*(?:없|안|x)|non[\s-]*coat', '비코팅'), (r'고경도', '고경도코팅'),
         (r'일반\s*코팅|일반|코팅', '일반코팅')]
MATS = [(r'초경|카바이드|carbide|초경합금', '초경'), (r'hss|하이스|고속도강|하이스피드', 'HSS')]
BW = {'한': 1, '두': 2, '세': 3, '네': 4, '다섯': 5, '여섯': 6}
COAT_LABEL = {'비코팅': '비코팅', '일반코팅': '일반 코팅', '고경도코팅': '고경도 코팅'}
MERGE_PART = ('밑골수리', '밑옆날', '밑골수리날')


def g(x):
    """JS String(+(+x).toFixed(4)) 와 같은 숫자 표기 — 6 → '6', 6.80 → '6.8'."""
    s = '%.4f' % float(x)
    return s.rstrip('0').rstrip('.') if '.' in s else s


def _cut(t, m):
    return t[:m.start()] + ' ' + t[m.end():]


def std_name(b, s, d, m, p, c):
    return f'{b}날/{s}/{g(d)}mm/{m}/{p}/{COAT_LABEL.get(c, c)}'


def key(nm):
    p = [s.strip() for s in str(nm).split('/')]
    if len(p) < 6:
        return re.sub(r'\s+', '', str(nm)).lower()
    dm = re.match(r'^([\d.]+)', p[2])
    dia = g(dm.group(1)) if dm else p[2].lower()
    shape = '라핑평' if p[1] == '라핑' else p[1]
    part = p[4].replace(' ', '')
    if part in MERGE_PART:
        part = '밑옆날'
    return '/'.join([re.sub(r'\s+', '', p[0]), shape, dia, p[3].lower(), part, p[5].replace(' ', '')]).lower()


class PriceCore:
    def __init__(self, path):
        with open(path, encoding='utf-8') as f:
            self.data = json.load(f)
        self.conflict = set(self.data.get('conflict', []))
        self.path = path

    # ── 해석 ─────────────────────────────────────────
    def parse(self, text):
        t = ' ' + re.sub('[ØΦφ]', 'ø', str(text)).lower() + ' '
        t = re.sub(r'([가-힣])(\d)', r'\1 \2', t)
        q, assumed = {}, []
        if str(text).count('/') >= 5:
            p = [s.strip() for s in str(text).split('/')]
            b, d = re.match(r'^(\d+)', p[0]), re.match(r'^([\d.]+)', p[2])
            if b and d:
                q.update(blade=int(b.group(1)), shape='라핑평' if p[1] == '라핑' else p[1], dia=float(d.group(1)),
                         mat='HSS' if p[3].lower() == 'hss' else p[3], part=p[4], coat=p[5].replace(' ', ''))
                return self._finish(q, assumed)
        m = re.search(r'(?<![\d.])(\d{1,2})\s*(?:날|f\b|flute|fl\b|낭)', t) or re.search(r'(한|두|세|네|다섯|여섯)\s*날', t)
        if m:
            q['blade'] = int(m.group(1)) if m.group(1).isdigit() else BW[m.group(1)]
            t = _cut(t, m)
        rr = re.search(r'\br\s*(\d+(?:\.\d+)?)', t)
        if rr:
            q['r'] = float(rr.group(1)); t = _cut(t, rr)
        m = (re.search(r'(?:ø|파이|phi|\bd)\s*(\d+(?:\.\d+)?)', t) or re.search(r'(\d+(?:\.\d+)?)\s*(?:mm|파이|ø|phi)', t)
             or re.search(r'(\d+(?:\.\d+)?)', t))
        if m:
            q['dia'] = float(m.group(1)); t = _cut(t, m)
        for s in self.data.get('extra_shapes', []):
            if s.lower() in t:
                q['shape'] = s; break
        for pats, k in ((SHAPES, 'shape'), (PARTS, 'part'), (COATS, 'coat'), (MATS, 'mat')):
            if k in q:
                continue
            for rx, v in pats:
                if re.search(rx, t):
                    q[k] = v; break
        if 'shape' not in q and q.get('r') is not None:
            q['shape'] = '코너'
        return self._finish(q, assumed)

    @staticmethod
    def _finish(q, assumed):
        if not q.get('mat'):
            q['mat'] = '초경'; assumed.append('재질 = 초경(입력 없음)')
        if not q.get('part'):
            q['part'] = '밑날'; assumed.append('가공부 = 밑날(입력 없음)')
        q['missing'] = [k for k in ('shape', 'dia') if q.get(k) is None]
        q['assumed'] = assumed
        return q

    # ── 조회 ─────────────────────────────────────────
    def _band(self, runs, d):
        st = self.data['step']
        for a, b, v in runs:
            if a - st + 1e-9 < d <= b + 1e-9:
                return v
        return None

    def calc(self, b, s, d, m, p, c):
        pk = '밑옆날' if p in MERGE_PART else p
        combos = self.data['combos']
        if s == '드릴':
            if pk != '밑날' or b != 2:
                return None
            r = combos.get('|'.join([m, '드릴', '밑날', c, '2']))
            return self._band(r, d) if r else None
        if s not in BLOCK_SHAPES:
            return None
        r = combos.get('|'.join([m, s, pk, c, '2' if b == 2 else '4']))
        return self._band(r, d) if r else None

    def nearest(self, k):
        p = k.split('/')
        if len(p) < 6:
            return ''
        d, c = float(p[2]), []
        for kk in self.data['registered']:
            qq = kk.split('/')
            if len(qq) >= 6 and qq[0] == p[0] and qq[1] == p[1] and qq[3:] == p[3:]:
                try:
                    c.append((abs(float(qq[2]) - d), float(qq[2])))
                except ValueError:
                    pass
        return ' · '.join('Ø' + g(x[1]) for x in sorted(c, key=lambda x: x[0])[:2])

    def price_one(self, b, s, d, m, p, c):
        name = std_name(b, s, d, m, p, c)
        k = key(name)
        calc = self.calc(b, s, d, m, p, c)
        reg = self.data['registered'].get(k)
        if s == '리머' and '고경도' in str(c):   # 2026-10-30: 정가표 리머 블록에 고경도 칸 없음(한경준님 「확인 필요」)
            return dict(name=name, status='확인 필요', price=None, src='리머 고경도 코팅은 정가표에 가격 칸 없음 — 담당자 확인')
        if k in self.conflict:
            return dict(name=name, status='확인 필요', price=None, src='사업장 파일끼리 등록 정가가 다름')
        if calc is not None and reg is not None and abs(calc - reg) > 0.5:
            return dict(name=name, status='확인 필요', price=None, src='정가표 계산값과 등록 정가가 다름')
        if calc is not None:
            return dict(name=name, status='OK', price=calc, src=self.data['sheet'] + (' · 등록 품목' if reg is not None else ' · 미등록 규격'))
        if reg is not None:
            if s == '드릴':   # 정가표 드릴 구간 밖(초경 20 mm 초과 · 밑날 외 등) — ERP 옛 정가 (한경준님 10-29: 20 초과 가격표 없음)
                return dict(name=name, status='확인 필요', price=None, src=f'정가표 드릴 구간 밖 — ERP 등록 정가 {reg:,.0f}원(옛 값일 수 있음)')
            return dict(name=name, status='OK', price=reg, src='등록 품목 정가')
        n = self.nearest(k)
        return dict(name=name, status='없음', price=None, src='정가표·등록 품목에 없음 — 담당자 확인' + (f' (가까운 등록 규격: {n})' if n else ''))

    def answer(self, text):
        q = self.parse(text)
        res = dict(query=text, q=q, rows=[])
        if q['missing']:
            return res
        bl = [q['blade']] if q.get('blade') else [2, 4]
        co = [q['coat']] if q.get('coat') else ['비코팅', '일반코팅', '고경도코팅']
        if not q.get('blade'):
            q['assumed'].append('날수 입력 없음 → 2날 · 4날(3날 이상 같은 값) 모두 표시')
        if not q.get('coat'):
            q['assumed'].append('코팅 입력 없음 → 세 가지 모두 표시')
        for b in bl:
            for c in co:
                res['rows'].append(self.price_one(b, q['shape'], q['dia'], q['mat'], q['part'], c))
        return res


if __name__ == '__main__':   # 명령줄 시험: python price_core.py price_data.json "10파이 2날 볼"
    import sys
    core = PriceCore(sys.argv[1])
    for text in sys.argv[2:]:
        r = core.answer(text)
        print(text, '→', r['q'].get('missing') or '', [(x['name'], x['status'], x['price']) for x in r['rows']])
