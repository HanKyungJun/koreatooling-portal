#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""견적문의 접수 → 규격 줄별 예상 정가 · 소계 · 합계    2026-10-28 Cowork 신설

사내 접수현황(현황판) 전용. generate.py 가 접수현황 스냅샷을 만들 때 「견적문의」 탭에 붙인다.
정가는 scripts/price_lookup.py 의 Lookup 그대로(정가표 계산 + ERP 등록 정가, 둘이 다르면 「확인 필요」).
**정가만** 쓴다 — 할인율 · 거래처 단가는 읽지 않는다(그건 대외비, CLAUDE.md §4).

한 줄의 판정
  OK          값이 하나로 정해짐 → 정가 × 수량 = 소계
  코팅 확인    코팅(또는 날수)을 안 적어 후보가 여러 개 → 후보만 보여 주고 소계는 비움
  확인 필요    정가표 계산값 ≠ 등록 정가, 사업장끼리 다름 → 참고값만
  정보 부족    형상(평/볼/코너…)이나 직경을 못 읽음
  대상 아님    구분이 재연마가 아님 · 재질 SKD/기타 (정가표 없음)
합계는 OK 줄만 더하고, OK 가 아닌 줄이 하나라도 있으면 「일부 합계」로 표시한다.

시험:
  python scripts\quote_price.py "Ø10 2날 평 / 6 4날 볼 일반코팅" "5 / 10"
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

TAB = '견적문의'
_LK = None


def get_lookup():
    global _LK
    if _LK is None:
        import price_lookup as pl
        _LK = pl.Lookup()
    return _LK


def _split(s):
    return [x.strip() for x in str(s or '').split(' / ')]


def _qty(s):
    try:
        q = float(str(s).replace(',', '').strip())
        return int(q) if q == int(q) else q
    except (TypeError, ValueError):
        return None


def price_line(lk, spec, qty, material=''):
    """규격 한 줄 → dict(spec, qty, status, name, price, subtotal, options, note)."""
    mat = material if material in ('초경', 'HSS') else ''
    out = dict(spec=spec, qty=qty, status='', name='', price=None, subtotal=None, options=[], note='')
    if material in ('SKD', '기타'):
        out.update(status='대상 아님', note=f'재질 {material} — 정가표 없음, 담당자 확인')
        return out
    res = lk.answer(f'{mat} {spec}'.strip())
    if res['missing']:
        miss = ' · '.join({'shape': '형상(평/볼/코너…)', 'dia': '직경'}[m] for m in res['missing'])
        out.update(status='정보 부족', note=f'{miss} 미기재 — 담당자 확인')
        return out
    rows = res['rows']
    assumed = [a for a in res['assumed'] if '모두 표시' not in a]
    if assumed:
        out['note'] = ' · '.join(assumed)
    if len(rows) == 1:
        r = rows[0]
        out.update(name=r['name'], price=r['price'])
        if r['status'] == 'OK':
            out['status'] = 'OK'
            if qty is not None and r['price'] is not None:
                out['subtotal'] = r['price'] * qty
        else:
            out['status'] = '확인 필요' if r['status'] == '확인 필요' else '정보 부족'
            out['note'] = ' · '.join(x for x in (out['note'], r['note']) if x)
        return out
    out['status'] = '코팅 확인'
    out['options'] = [dict(name=r['name'], price=r['price'], status=r['status']) for r in rows]
    why = [a for a in res['assumed'] if '모두 표시' in a]
    out['note'] = ' · '.join(x for x in (out['note'], *[w.split('→')[0].strip() for w in why]) if x)
    return out


def quote_row(lk, headers, row):
    """견적문의 한 행 → dict(lines, total, complete, applicable)."""
    def col(name):
        try:
            i = headers.index(name)
        except ValueError:
            return ''
        return row[i] if i < len(row) else ''
    cat, mat = col('구분').strip(), col('재질').strip()
    specs, qtys = _split(col('규격')), _split(col('수량'))
    if cat and cat != '재연마':
        return dict(applicable=False, reason=f'구분 「{cat}」 — 재연마만 자동 계산', lines=[], total=None, complete=False)
    lines = []
    for i, sp in enumerate(specs):
        if not sp:
            continue
        q = _qty(qtys[i]) if i < len(qtys) else None
        lines.append(price_line(lk, sp, q, mat))
    if len(qtys) != len(specs):
        for ln in lines:
            ln['note'] = ' · '.join(x for x in (ln['note'], '규격 · 수량 줄 수가 다름 — 짝 확인') if x)
    ok = [ln for ln in lines if ln['status'] == 'OK' and ln['subtotal'] is not None]
    total = sum(ln['subtotal'] for ln in ok) if ok else None
    return dict(applicable=True, reason='', lines=lines, total=total,
                complete=bool(lines) and len(ok) == len(lines))


def annotate(data, log=print):
    """접수현황 data(dict 탭명 → {headers, rows}) 의 견적문의 탭에 quotes · price_meta 를 붙인다.
    실패해도 예외를 밖으로 던지지 않는다 — 정가가 빠질 뿐 접수현황은 그대로 나간다."""
    tab = (data or {}).get(TAB)
    if not tab or not tab.get('rows'):
        return False
    try:
        lk = get_lookup()
        tab['quotes'] = [quote_row(lk, tab['headers'], r) for r in tab['rows']]
        tab['price_meta'] = dict(price_list=os.path.basename(lk.pl_path), sheet=lk.pl.name,
                                 master=lk.master_src, missing_blocks=list(lk.blocks.missing))
        n = sum(len(q['lines']) for q in tab['quotes'])
        log(f'  → 견적문의 예상 정가: {len(tab["rows"])}건 · {n}줄 (정가표 {tab["price_meta"]["price_list"]})')
        return True
    except Exception as e:
        log(f'  ⚠️ 견적문의 예상 정가 생략: {type(e).__name__}: {str(e)[:120]}')
        return False


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    import json
    spec = sys.argv[1] if len(sys.argv) > 1 else 'Ø10 2날 평'
    qty = sys.argv[2] if len(sys.argv) > 2 else '1'
    mat = sys.argv[3] if len(sys.argv) > 3 else '초경'
    hd = ['접수일시', '회사명', '담당자', '연락처', '이메일', '구분', '재질', '규격', '수량']
    print(json.dumps(quote_row(get_lookup(), hd, ['', '', '', '', '', '재연마', mat, spec, qty]),
                     ensure_ascii=False, indent=1, default=str))
