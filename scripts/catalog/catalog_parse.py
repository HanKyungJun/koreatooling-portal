# -*- coding: utf-8 -*-
r"""쪽별 글자 위치(JSON) → 품번 행(JSON)    2026-10-28 Cowork 신설
사용: python scripts\catalog\catalog_parse.py outputs\_cat_jj raw\Catalog\JJ.cache.json outputs\_jj_all.json
COGO 는 먼저 PowerShell 에서 $env:CAT_MODE="COGO" (제목 위치 · 두 줄 머리글 · 「샹크」 · 인쇄 쪽 번호 차이 대응)
판독 규칙: 머리글(날경 · 날장 · 전장 · 생크 …) x 위치로 열을 나누고, 품번(숫자+영문 대문자로 시작)을 줄 기준으로 삼는다.
"""
import json, glob, re, sys, os, csv, collections
CODE = re.compile(r'^(?=.*[A-Z])(?=.*\d)[0-9A-Z][0-9A-Z\-\.]{2,}$')
TITLE = re.compile(r'(엔드밀|드릴|커터|탭|버$|인서트|리머|밀$|공구|홀더|척|센터|바$|카운터|면취|스포팅|쓰레드|챔퍼)')
KO = re.compile(r'[가-힣]')
MODE = os.environ.get('CAT_MODE', 'JJ')   # JJ | COGO (2026-10-28 — COGO 는 제목이 왼쪽, 머리글이 두 줄 · 「샹크」)
SYM = {'D', 'L1', 'L2', 'L3', 'L', 'd', 'R×D', 'RxD', 'D×R', 'DxR', 'D1', 'θ', 'Ls', 'l6', 'dk', 'd1', 'd2', 'R', 'Thread', 'Pitch', 'C'}   # 머리글 기호 줄
HDR_EXCL = {'품목', '코드', '품목코드', '단위', '단위/'}

def rows_of(W, tol=2.5):
    W = sorted(W, key=lambda w: (w[3], w[1]))
    rows = []
    for w in W:
        if rows and abs(rows[-1][0] - w[3]) <= tol:
            rows[-1][1].append(w)
        else:
            rows.append([w[3], [w]])
    return [(t, sorted(r, key=lambda w: w[1])) for t, r in rows]

def cx(w): return (w[1] + w[2]) / 2
def cy(w): return (w[3] + w[4]) / 2

def parse_page(idx, W, cache_text, state):
    W = [w for w in W if w[1] < 560 and w[2] > 40 and '(cid:' not in w[0]]   # 오른쪽 세로 시리즈 글자 · 깨진 글꼴 제외
    W2 = []
    for w in W:   # 「New2SCCBN」 처럼 붙어 나온 토큰 → New 표시 + 품번
        m = re.match(r'^(New|NEW)(\d?[A-Z][A-Z0-9\-]+)$', w[0])
        if m:
            cut = w[1] + (w[2] - w[1]) * 3 / len(w[0])
            W2.append(['New', w[1], cut - 1, w[3], w[4]]); W2.append([m.group(2), cut + 14, w[2], w[3], w[4]])
        else:
            W2.append(w)
    # 한 글자씩 끊겨 나온 한글 머리글(「샹 크」 「날 경」) → 붙인다
    W2 = sorted(W2, key=lambda w: (round(w[3]), w[1]))
    M = []
    for w in W2:
        if M and abs(M[-1][3] - w[3]) < 1 and KO.fullmatch(w[0][:1] or ' ') and KO.search(M[-1][0][-1:]) and -1.5 <= w[1] - M[-1][2] < 2.5 and (len(w[0]) == 1 or len(M[-1][0]) == 1):
            M[-1] = [M[-1][0] + w[0], M[-1][1], w[2], M[-1][3], max(M[-1][4], w[4])]
        else:
            M.append(list(w))
    for w in M:   # 「전장(Overall」 「샹크(Shank」 처럼 영문이 붙은 한글 머리글
        if KO.match(w[0][:1] or ' ') and '(' in w[0]:
            w[0] = w[0].split('(')[0]
    W = [[('생크' if w[0] == '샹크' else w[0])] + list(w[1:]) for w in M]
    NEW = [w for w in W if w[0] in ('New', 'NEW')]            # 품번 앞 「New」 표시 — 품번 판독에서 빼고 신제품 표시로만 쓴다
    W = [w for w in W if w[0] not in ('New', 'NEW')]
    rows = rows_of(W)
    out = []
    icon = sorted(set(w[0] for w in W if re.fullmatch(r'(?i)AlCrN|TiSiN(-S)?|AlTiN|TiAlN|DLC|R-?TAC|Diamond|Uncoated|Non-?coated|HR|nACo|TiN', w[0]) and w[3] < 300 and w[1] > 200))
    foot = [w for w in W if re.search(r'COGOTOOL|TOOLS|jjtools', w[0], re.I)]
    pn = [w[0] for w in W if re.fullmatch(r'\d{1,3}', w[0]) and any(abs(f[3] - w[3]) < 4 and abs(f[1] - w[1]) < 140 for f in foot)]
    pp = int(pn[0]) if pn else idx + 1   # 인쇄된 쪽 번호(없으면 PDF 쪽)
    # series from cache text
    state['series'] = state.get('labels', {}).get(idx, '')
    # titles on page
    titles = []
    for i, (t, r) in enumerate(rows):
        txt = ' '.join(w[0] for w in r)
        if r[0][0] != '•' and '•' not in txt and KO.search(txt) and TITLE.search(txt) and len(txt) < 60 and r[0][1] > 120 and t < 800 and not txt.endswith('니다.'):
            en = ''
            for j in range(i - 1, max(-1, i - 4), -1):
                tt = ' '.join(w[0] for w in rows[j][1])
                if re.search(r'[A-Za-z]{3,}', tt) and not KO.search(tt) and rows[j][1][0][1] > 120 and len(rows[j][1]) >= 3 and 8 <= t - rows[j][0] <= 30 and rows[j][1][0][0] != '•':
                    en = tt; break
            if en:   # 제품명 = 바로 위(8~30 pt)에 영문 제품명 줄이 있는 한글 줄만 (설명 문장 줄바꿈 제외)
                titles.append((t, txt, en))
    if MODE == 'COGO':   # COGO: 한글 제품명이 왼쪽(x≈43)에 있고 영문 · 일문 제품명이 위에 떨어져 있다
        titles = []
        for i, (t, r) in enumerate(rows):
            r = [w for w in r if w[1] < 300]   # 오른쪽 공차표 글자가 같은 줄에 섞이지 않게
            if not r: continue
            txt = ' '.join(w[0] for w in r)
            if (r[0][1] < 80 and '•' not in txt and KO.search(txt) and TITLE.search(txt) and len(txt) < 40 and not txt.endswith('니다.')
                    and not re.search(r'[,()]|HRC|HRc|계열|이상|이하', txt) and re.match(r'^(\d|초경|하이스|HSS|[가-힣A-Z])', txt)):
                if titles and t - titles[-1][0] < 60:
                    continue
                en = ''
                for j in range(i - 1, -1, -1):
                    tt = ' '.join(w[0] for w in rows[j][1] if w[1] < 300)
                    if t - rows[j][0] > 160: break
                    if rows[j][1][0][1] < 80 and '•' not in tt and re.search(r'Flute|End ?mill|Drill|Cutter|Thread|Insert|Reamer', tt, re.I) and not re.search(r'[ぁ-ん一-龯]', tt):
                        en = tt   # 가장 위쪽 영문 제품명
                titles.append((t, txt, en))
    headers = [(t, r) for t, r in rows if (any(w[0] == '날경' for w in r) or (any(w[0] == '생크' for w in r) and any(w[0] == '전장' for w in r))) and sum(1 for w in r if KO.search(w[0])) >= 3 and r[0][0] != '•' and '•' not in [w[0] for w in r]]
    if MODE == 'COGO':
        HK = {'날경', '날장', '생크', '유효장', '각도', '면취량', '선단경', '홈길이'}
        cand = [t for t, r in rows if any(w[0] == '전장' for w in r) and any(w[0] in HK for w in r) and r[0][0] != '•']
        clusters = []
        for t in cand:   # 왼쪽 · 오른쪽 표 머리글이 1~2 pt 어긋나 두 줄로 잡히는 것 → 하나로
            if clusters and t - clusters[-1][-1] <= 6: clusters[-1].append(t)
            else: clusters.append([t])
        hx = []
        for c in clusters:   # 「날경 · 각도」 가 반 줄 위나 아래에 따로 있는 머리글 → ±9 pt 를 합친다 · 영문 괄호 · 품목코드 제외
            ext = [w for w in W if c[0] - 9 <= w[3] <= c[-1] + 9 and KO.search(w[0]) and w[0] not in HDR_EXCL and not w[0].startswith('(')]
            ext = [[re.sub(r'\(.*$', '', w[0])] + list(w[1:]) for w in ext]
            hx.append((max(w[3] for w in ext) - 7, sorted(ext, key=lambda w: w[1])))
        headers = hx
        # 머리글 없이 이어지는 쪽(표만 계속) → 앞 쪽 마지막 머리글 열 위치를 그대로 쓴다
        anc = [w[3] for w in W if re.match(r'^\d[A-Z]{2,}[A-Z0-9]*$', w[0]) and w[1] < 120 and w[3] > 80]
        if anc and state.get('last_hdr') and (not headers or min(anc) < headers[0][0]):
            headers.insert(0, (min(anc) - 16, [[x[0], x[1], x[2], min(anc) - 16, min(anc) - 9] for x in state['last_hdr']]))
        if headers: state['last_hdr'] = headers[-1][1]
    STOP = [t for t, r in rows if re.search(r'RPM|Work Material|Hardness|절삭조건|Cutting Condition', ' '.join(w[0] for w in r))]
    for hi, (ht, hr) in enumerate(headers):
        # product meta: last title above header
        tl = [x for x in titles if x[0] < ht]
        if tl:
            state['title'], state['en'], state['title_top'] = tl[-1][1], tl[-1][2], tl[-1][0]
            # bullets between title and header
            btxt = ' '.join(' '.join(w[0] for w in r) for t, r in rows if tl[-1][0] < t < ht)
            hrc = re.findall(r'HR[cC]\s*\d{2}\s*[~\-]\s*\d{2}|HR[cC]\d{2}\s*[~\-]\s*\d{2}', btxt)
            state['hrc'] = ' / '.join(sorted(set(h.replace(' ', '') for h in hrc)))
            ko_b = [s.strip() for s in re.split(r'•', btxt) if KO.search(s)]
            state['bullets'] = ' | '.join(ko_b)[:400]
        # groups split by 날경
        cols = [(w[0], cx(w), w) for w in hr]
        first = cols[0][0]
        starts = [i for i, c in enumerate(cols) if c[0] == first]
        groups = []
        for gi, s in enumerate(starts):
            e = starts[gi + 1] if gi + 1 < len(starts) else len(cols)
            groups.append(cols[s:e])
        nht = headers[hi + 1][0] if hi + 1 < len(headers) else 9999
        nt = [x[0] for x in titles if x[0] > ht]
        stp = [t for t in STOP if t > ht]
        ybot = min(nht, nt[0] if nt else 9999, stp[0] if stp else 9999)
        for gi, g in enumerate(groups):
            d_x = g[0][2][1]   # 첫 머리글(날경 · 피치규격 · 나사 …) 왼쪽 끝
            left = (groups[gi - 1][-1][2][2] + 5) if gi > 0 else 0
            right = max(g[-1][2][2] + 15, groups[gi + 1][0][2][1] - 125) if gi + 1 < len(groups) else 9999
            order_r = d_x - 22
            region = [w for w in W if ht + 15 < w[3] < ybot and left <= w[1] < right]
            anchors = [w for w in region if w[1] < order_r and CODE.match(w[0]) and not any(o[1] < w[1] - 1 and abs(o[3] - w[3]) < 3 and o[1] >= left for o in region if o[1] < order_r and o is not w)]
            a_top = min([a[3] for a in anchors], default=ybot)
            # 품번이 두 개(비코팅 · 코팅 등)인 표 — 품번 칸 위 소제목
            sub = [w for w in W if ht < w[3] < a_top - 2 and left <= w[1] < order_r and (KO.search(w[0]) or 'oated' in w[0])]
            sub = [w for w in sub if w[0] not in ('Order', 'Number')]
            # 표 안 소제목(예: 「외부 급유형 (Without coolant)」 · 「내부 급유형」) — 그 아래 품번에 붙인다
            subt = [(t, ' '.join(w[0] for w in r)) for t, r in rows if ht + 15 < t < ybot and left <= r[0][1] < right
                    and re.search(r'급유|oolant|타입|Type', ' '.join(w[0] for w in r)) and not any(CODE.match(w[0]) for w in r) and len(r) <= 8]
            for a in sorted(anchors, key=lambda w: w[3]):
              st = [x for x in subt if x[0] < a[3]]
              line = sorted([w for w in region if w[1] < order_r and abs(cy(w) - cy(a)) <= 3 and w[1] >= a[1]], key=lambda w: w[1])
              parts, cur = [], []
              for w in line:
                  if cur and re.match(r'^\d[A-Z]{2,}[A-Z0-9]*$', w[0]):
                      parts.append(cur); cur = []
                  cur.append(w)
              if cur: parts.append(cur)
              for part in parts:
                code = ' '.join(w[0] for w in part)
                variant = ''
                if len(parts) > 1 and sub:
                    variant = min(sub, key=lambda w: abs(w[1] - part[0][1]))[0]
                vals = collections.defaultdict(list)
                if variant: vals['구분'].append((0, variant))
                if st: vals['소구분'].append((0, st[-1][1]))
                if any(abs(cy(n) - cy(a)) <= 4 and 0 < part[0][1] - n[2] < 40 for n in NEW): vals['신제품'].append((0, 'New'))
                for w in region:
                    if w[1] >= order_r and abs(cy(w) - cy(a)) <= 6 and w[3] >= a[3] - 3.2 and not (w[0] in SYM and w[3] < a[3] - 1) and not (len(w[0]) == 1 and KO.match(w[0])):
                        name = min(g, key=lambda c: abs(c[1] - cx(w)))[0]
                        vals[name].append((w[1], w[0]))
                rec = {k: ' '.join(t for _, t in sorted(v)) for k, v in vals.items()}
                if not any(k not in ('구분', '소구분', '신제품') for k in rec):
                    continue   # 값 없는 줄(로고 · 표 밖 글자) 제외
                out.append(dict(page=idx + 1, pp=pp, icon=' '.join(icon), series=state.get('series', ''), title=state.get('title', ''), en=state.get('en', ''),
                                hrc=state.get('hrc', ''), bullets=state.get('bullets', ''), code=code, **{'c_' + k: v for k, v in rec.items()}))
    return out

if __name__ == '__main__':
    d, cache, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    only = set(int(x) for x in sys.argv[4].split(',')) if len(sys.argv) > 4 else None
    ct = json.load(open(cache, encoding='utf-8'))['pages']
    # 시리즈 = 페이지 오른쪽 세로 띠 글자(펼침면 한쪽에만 있음 → 앞뒤 1쪽에 같이 적용)
    KNOWN = ('JJseries','HARDseries','Gseries','FORALUMINUM','FORGRAPHITE','CBNseries','Eseries','FORSUS','Vseries','R-TAC','FORCOPPER','FORCOMPOSITE')
    raw = {}
    for fp in sorted(glob.glob(d + '/*.json')):
        i = int(os.path.basename(fp)[:4])
        W = json.load(open(fp, encoding='utf-8'))['w']
        side = lambda ws: [w for w in ws if re.match(r'^[A-Za-z.&\-]+$', w[0])]
        lab = ''.join(w[0] for w in sorted(side([w for w in W if w[1] >= 560]), key=lambda w: w[3]))
        labl = ' '.join(w[0] for w in sorted(side([w for w in W if w[2] <= 40]), key=lambda w: w[3]))
        if not labl and lab and not any(lab.startswith(k) for k in KNOWN) and len(lab) <= 20:
            labl = lab   # 오른쪽 띠의 일반 라벨(DRILL 등)
        for k in KNOWN:
            if lab.startswith(k) or labl.replace(' ', '').startswith(k):
                raw[i] = k.replace('series', ' series').replace('FOR', 'FOR ').strip(); break
        else:
            if labl and len(labl) <= 30 and re.match(r'^[A-Z][A-Za-z.&\- ]+$', labl):
                raw[i] = labl.strip()
    if MODE == 'COGO':   # COGO: 페이지 왼쪽 위 시리즈 글자(HARD · SPEED · DRILL …) — 없으면 앞 쪽 것을 이어 쓴다
        raw = {}
        for fp in sorted(glob.glob(d + '/*.json')):
            i = int(os.path.basename(fp)[:4])
            W = json.load(open(fp, encoding='utf-8'))['w']
            top = [w for w in W if w[3] < 52 and re.match(r'^[A-Z][A-Za-z&.\-]*$', w[0])]
            lab = ' '.join(w[0] for w in sorted(top, key=lambda w: w[1]))
            if lab and len(lab) <= 25: raw[i] = lab
        labels, last = {}, ''
        for i in range(0, 2000):
            if i in raw: last = raw[i]
            labels[i] = last
        raw = {}
    else:
        labels = {}
    for i, v in raw.items():
        for j in (i - 1, i, i + 1):
            if j == i or j not in raw:
                labels.setdefault(j, v)
    state, allr = {'labels': labels}, []
    for fp in sorted(glob.glob(d + '/*.json')):
        idx = int(os.path.basename(fp)[:4])
        W = json.load(open(fp, encoding='utf-8'))['w']
        r = parse_page(idx, W, ct.get(str(idx), ''), state)
        if only is None or idx in only:
            allr += r
    json.dump(allr, open(outp, 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(allr))
