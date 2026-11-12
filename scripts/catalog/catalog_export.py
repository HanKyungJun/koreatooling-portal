#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""카탈로그 추출 결과(JSON) → Claude 프로젝트용 제품군 요약 · 품번 치수 CSV    2026-10-28 Cowork 신설
사용: python scripts\catalog\export.py <추출.json> <메이커> <출력폴더>
"""
import json, re, sys, os, csv, collections

SERIES_FIX = {'THREADMILL': 'THREAD MILL', 'FORA.B.S': 'FOR A.B.S', 'GENERALPURPOSE': 'GENERAL PURPOSE', 'PCDseries': 'PCD series'}
SHAPES = [('쓰레드밀', '쓰레드밀'), ('드릴', '드릴'), ('인서트', '인서트'), ('면취|챔퍼', '면취'), ('T.?\\s*커터|T- ', 'T커터'), ('센터링', '센터링'),
          ('테이퍼.*볼|볼.*테이퍼', '테이퍼 볼'), ('테이퍼', '테이퍼'), ('라핑', '라핑'), ('구형', '구형(볼)'), ('볼', '볼'),
          ('코너\\s*R|코너 레디우스|레디우스', '코너R'), ('코너\\s*C|C 엔드밀', '코너C'), ('엔드밀|커터', '평(스퀘어)')]


def shape_of(t):
    for pat, name in SHAPES:
        if re.search(pat, t):
            return name
    return ''


def flutes_of(t, code):
    m = re.match(r'^\s*(?:초경\s*)?([\d&~]+)\s*날', t)
    if m:
        return m.group(1)
    m = re.match(r'^(\d)[A-Z]', code)
    return m.group(1) if m else ''


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def dr(raw):
    """날경 원문 → (D, R). 예: '0.4 X R0.02' · '0.5R X 1' · '10'"""
    s = (raw or '').replace('×', 'X').replace(' ', '')
    m = re.match(r'^([\d.]+)XR([\d.]+)', s)
    if m: return num(m.group(1)), num(m.group(2))
    m = re.match(r'^([\d.]+)RX([\d.]+)', s)
    if m: return num(m.group(2)), num(m.group(1))
    m = re.match(r'^R([\d.]+)X([\d.]+)', s)          # COGO 「R2.0 X 4」
    if m: return num(m.group(2)), num(m.group(1))
    m = re.match(r'^([\d.]+)$', s)
    if m: return num(m.group(1)), None
    m = re.match(r'^([\d.]+)', s)
    return (num(m.group(1)), None) if m else (None, None)


def coat_of(b):
    hits = []
    for pat, name in [('다이아몬드|Diamond', '다이아몬드 코팅'), ('DLC', 'DLC'), ('R-?TAC', 'R-TAC 코팅'), ('실리콘계|Si계|\\(Si\\)|TiSiN|TISIN', '실리콘계(Si · TiSiN) 코팅'),
                      ('AlCrN', 'AlCrN'), ('TiAlN', 'TiAlN'), ('AlTiN', 'AlTiN'), ('HR 코팅|HR코팅', 'HR 코팅'), ('비코팅|무코팅', '비코팅')]:
        if re.search(pat, b) and name not in hits:
            hits.append(name)
    return ' · '.join(hits)


def main():
    src, maker, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    r = json.load(open(src, encoding='utf-8'))
    # 제품 = (제품명, 영문명) 이 같은 연속 블록
    prods, pid_of = collections.OrderedDict(), []
    for x in r:
        sr = SERIES_FIX.get(x['series'].replace(' ', ''), x['series']) if x['series'] else ''
        for pat, rep_ in ((r'^COMPOSITE.*', 'COMPOSITE'), (r'^THREAD ?MILL.*', 'THREAD MILL'), (r'^DOF.*', 'DOF'), (r'^TAPER.*', 'TAPER'), (r'^GSERIES$', 'G SERIES')):
            sr = re.sub(pat, rep_, sr)
        x['series'] = sr
        key = (x['title'], x['en'])
        if key not in prods:
            prods[key] = dict(id=f'{maker}-{len(prods) + 1:03d}', rows=[], x=x)
        prods[key]['rows'].append(x)
    detail_h = ['품번', '제품ID', '쪽', '날수', '형상', 'D_mm', 'R_mm', '날경_원문', '날장', '유효장', '전장', '생크_d', '기타', '신제품']
    summ_h = ['제품ID', '메이커', '시리즈', '제품명', '영문명', '날수', '형상', '쪽', '품번_접두어', 'D_범위_mm', '생크_d_범위', '품번_수', '적용_경도', '코팅', '특징(카탈로그 문구)']
    det, summ = [], []
    std = {'날경', '날장', '유효장', '전장', '생크', '신제품'}
    for (title, en), p in prods.items():
        rows, x = p['rows'], p['x']
        shp = shape_of(title)
        ds, sh, pages, pref = [], [], sorted(set(z.get('pp', z['page']) for z in rows)), collections.Counter()
        for z in rows:
            m = re.match(r'^(S\d{2})\s+(.*)$', z.get('c_날경', ''))
            if m and not re.search(r'\sS\d{2}$', z['code']):   # 품번 끝 「S06」 이 날경 칸으로 밀린 줄(COGO 2DPH 등) → 품번으로 되돌림
                z['code'] += ' ' + m.group(1); z['c_날경'] = m.group(2)
            D, R = dr(z.get('c_날경'))
            fl = flutes_of(title, z['code'])
            other = '; '.join(f'{k[2:]}={v}' for k, v in z.items() if k.startswith('c_') and k[2:] not in std)
            other = re.sub(r'(외부|내부)\s*급유형\s*\(?\s*With(?:out)? coolant\s*\)?', r'\1 급유형', other)
            det.append([z['code'], p['id'], z.get('pp', z['page']), fl, shp, '' if D is None else f'{D:g}', '' if R is None else f'{R:g}', z.get('c_날경', ''),
                        z.get('c_날장', ''), z.get('c_유효장', ''), z.get('c_전장', ''), z.get('c_생크', ''), other, 'Y' if z.get('c_신제품') else ''])
            if D is not None: ds.append(D)
            if num(z.get('c_생크')) is not None: sh.append(num(z.get('c_생크')))
            pref[z['code'].split(' ')[0]] += 1
        pg = f'{pages[0]}' if len(pages) == 1 else f'{pages[0]}-{pages[-1]}'
        summ.append([p['id'], maker, x['series'], title, en, flutes_of(title, rows[0]['code']), shp, pg, ' '.join(k for k, _ in pref.most_common(6)),
                     f'{min(ds):g}~{max(ds):g}' if ds else '', f'{min(sh):g}~{max(sh):g}' if sh else '', len(rows), x.get('hrc', ''),
                     coat_of(x.get('bullets', '') + ' ' + en + ' ' + ' '.join(sorted(set(z.get('icon', '') for z in rows)))), re.sub(r'\s+', ' ', re.split(r' D Size| Condition| 단위 ?:', x.get('bullets', ''))[0])[:240]])
    for name, h, rows in ((f'{maker}_1_제품군_요약.csv', summ_h, summ), (f'{maker}_2_품번_치수.csv', detail_h, det)):
        with open(os.path.join(out, name), 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f); w.writerow(h); w.writerows(rows)
    print(f'{maker}: 제품군 {len(summ)} · 품번 {len(det)}')


if __name__ == '__main__':
    main()
