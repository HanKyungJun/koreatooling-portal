# -*- coding: utf-8 -*-
"""거래처 발주·재고 조회(워크숍 범위 ③) — 거래처별 데이터 내보내기 (2026-10-08 신설)

흐름 (decisions.md 2026-10-08 (2)·(3))
  ① 경준님 PC 정규 실행이 ERP 수주를 받아 둔 스냅샷 erp/snapshot/jae_detail_latest.csv 를 읽는다
  ② 허용 열만 남기고(화이트리스트) 거래처별로 묶는다
  ③ --upload 이면 거래처 조회용 Apps Script(scripts/customer_portal_gas.gs)에 POST → 비공개 구글 시트

🔴 원칙
  - 허용 열(ALLOWED)만 내보낸다. 직원명(cnm·mnm·so_nm)·사내 메모(rmks)·배송지·단가는 절대 나가지 않는다.
    스냅샷에 새 열이 생겨도 여기 목록에 없으면 나가지 않는다.
  - 올리는 거래처는 .env 의 CUSTOMER_PORTAL_CUSTS(거래처 코드, 쉼표 구분)에 적힌 곳뿐이다.
    비어 있으면 아무것도 올리지 않는다(닫힌 기본값).
  - URL·토큰은 .env 에만 둔다 (이 저장소는 Public).

사용법 (cnc-wiki 폴더에서)
  python erp/customer_portal_export.py                 # 드라이런: 거래처별 건수 + outputs/customer_portal/ 미리보기
  python erp/customer_portal_export.py --upload        # 허용 거래처만 업로드
  python erp/customer_portal_export.py --new-code      # 거래처 접속 코드 1개 생성(시트 「codes」 탭에 붙여넣기)
  python erp/customer_portal_export.py --codes-tsv     # 허용 거래처 전부의 codes 탭 행(탭 구분) 출력 → 시트 A2 에 붙여넣기
  python erp/customer_portal_export.py --ping          # 웹 앱 연결 확인(틀린 코드로 조회 → denied 가 정상)
"""
import os, sys, csv, json, secrets, argparse
from datetime import date, datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.path.join(BASE_DIR, 'erp', 'snapshot')
OUT_DIR  = os.path.join(BASE_DIR, 'outputs', 'customer_portal')

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'))
except ImportError:
    pass

# 고객 화면으로 나가는 열 — 이 목록 밖의 열은 절대 내보내지 않는다
ALLOWED = ('so_no', 'so_dt', 'dlv_dt', 'itm_nm', 'jae_coating', 'jae_angle', 'so_qty', 'out_dt', 'out_qty')
SHIPPED_KEEP_DAYS = 60          # 출하 완료 건은 최근 60일만 보여 준다
CODE_ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'   # 0/O·1/I/L 처럼 헷갈리는 글자 제외


def _d(v):
    """'2026-09-28T00:00:00+09:00' → '2026-09-28' (빈 값은 '')."""
    v = (v or '').strip()
    return v[:10] if len(v) >= 10 else ''


def _n(v):
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return 0


def load_rows(snap_dir=SNAP_DIR, today=None):
    """스냅샷 → 고객용 행 목록. 반환: (rows, cust_names, saved_kst)"""
    today = today or date.today()
    meta = {}
    try:
        with open(os.path.join(snap_dir, 'snapshot_meta.json'), encoding='utf-8') as f:
            meta = json.load(f)
    except Exception:
        pass
    saved_kst = (meta.get('jae_detail') or {}).get('saved_kst', '')

    rows, names = [], {}
    cutoff = (today - timedelta(days=SHIPPED_KEEP_DAYS)).isoformat()
    with open(os.path.join(snap_dir, 'jae_detail_latest.csv'), encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            cust = (r.get('cust_cd') or '').strip()
            if not cust:
                continue
            names.setdefault(cust, (r.get('cust_nm') or '').strip())
            so_qty, out_qty = _n(r.get('so_qty')), _n(r.get('out_qty'))
            rest = max(so_qty - out_qty, 0)
            out_dt = _d(r.get('out_dt'))
            if rest == 0 and out_dt and out_dt < cutoff:
                continue
            status = '진행중' if out_qty == 0 else ('일부출하' if rest > 0 else '출하완료')
            row = {k: (r.get(k) or '').strip() for k in ALLOWED}
            row.update({'so_dt': _d(row['so_dt']), 'dlv_dt': _d(row['dlv_dt']), 'out_dt': out_dt,
                        'so_qty': so_qty, 'out_qty': out_qty, 'rest': rest, 'status': status,
                        'cust_cd': cust})
            rows.append(row)
    rows.sort(key=lambda x: (x['cust_cd'], x['status'] == '출하완료', x['dlv_dt'], x['so_no']))
    return rows, names, saved_kst


def allowed_custs():
    return [c.strip() for c in os.getenv('CUSTOMER_PORTAL_CUSTS', '').split(',') if c.strip()]


def build_payload(rows, names, saved_kst, custs):
    sel = [r for r in rows if r['cust_cd'] in custs]
    return {
        'token': os.getenv('CUSTOMER_PORTAL_UPLOAD_TOKEN', ''),
        'snapshot_kst': saved_kst,
        'uploaded_kst': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'customers': {c: names.get(c, '') for c in custs},
        'columns': list(ALLOWED) + ['rest', 'status', 'cust_cd'],
        'rows': sel,
    }


def _post(obj, timeout=60):
    """웹 앱에 JSON 본문 POST. Apps Script 는 302 로 결과 주소를 돌려주고 requests 가 GET 으로 따라간다.
    반환: (dict 또는 None, 오류 문자열)"""
    import requests
    url = os.getenv('CUSTOMER_PORTAL_GAS_URL', '')
    if not url:
        return None, 'CUSTOMER_PORTAL_GAS_URL 미설정'
    # 2026-10-08: 리다이렉트를 requests 에 맡기지 않고 직접 따라간다.
    #   업로드(큰 본문)가 doGet 응답을 받아 「성공」으로 찍힌 사례가 있어, 경로를 눈에 보이게 한다.
    #   Apps Script 정상 경로 = POST /exec → 302 → GET script.googleusercontent.com/macros/echo…
    from urllib.parse import urlparse
    first = requests.post(url, data=json.dumps(obj, ensure_ascii=False).encode('utf-8'),
                          headers={'Content-Type': 'text/plain; charset=utf-8'},
                          timeout=timeout, allow_redirects=False)
    diag = f'POST {first.status_code}'
    resp = first
    if first.status_code in (301, 302, 303, 307, 308):
        loc = first.headers.get('Location', '')
        diag += f' → GET {urlparse(loc).netloc}{urlparse(loc).path[:30]}'
        resp = requests.get(loc, timeout=timeout)
        diag += f' {resp.status_code}'
    _post.last_diag = diag
    try:
        return resp.json(), ''
    except ValueError:
        return None, f'응답이 JSON 이 아님 ({diag}): {resp.text[:200]}'


def ping():
    res, err = _post({'action': 'view', 'code': 'PINGTEST0000'}, timeout=30)
    st = (res or {}).get('status')
    print(f'  경로: {getattr(_post, "last_diag", "-")}')
    if st == 'denied':
        print('✅ 웹 앱 정상 — POST 경로 동작 · 스크립트 속성 설정됨 (틀린 코드 → denied)')
        return True
    if st == 'not_configured':
        print('❌ 스크립트 속성(SHEET_ID · UPLOAD_TOKEN) 미설정 또는 미저장')
    elif res and res.get('note') == 'POST only':
        print('❌ POST 가 doGet 으로 처리됨 — 리다이렉트 처리 문제(가이드 §3)')
    else:
        print(f'❌ 예상 밖 응답: {res or err}')
    return False


def probe():
    """본문 크기별로 POST 가 doPost 에 닿는지 확인한다 (2026-10-08 진단용). 토큰을 보내지 않으므로 시트에 쓰지 않는다.
    doPost 에 닿으면 forbidden, doGet 으로 빠지면 note=POST only."""
    import time
    for kb in (1, 10, 30, 60, 100, 200):
        obj = {'token': 'probe-no-write', 'columns': ['x'], 'rows': [], 'pad': ('가나다abc' * 60000)[: kb * 1024 * 6 // 11]}
        size = len(json.dumps(obj, ensure_ascii=False).encode('utf-8'))
        t0 = time.time()
        try:
            res, err = _post(obj, timeout=60)
        except Exception as e:
            res, err = None, f'{type(e).__name__}: {e}'
        st = (res or {}).get('status')
        where = 'doPost ✅' if st == 'forbidden' else ('doGet ❌' if (res or {}).get('note') == 'POST only' else f'? {res or err}')
        print(f'  {size/1024:6.1f} KB → {where}  ({getattr(_post, "last_diag", "-")}, {time.time()-t0:.1f}s)')


def codes_tsv(names, custs):
    """codes 탭에 붙여넣을 행 — 거래처코드 · 거래처명 · 접속코드 · 사용 · 메모 (탭 구분)."""
    today = date.today().isoformat()
    lines = []
    for c in custs:
        code = ''.join(secrets.choice(CODE_ALPHABET) for _ in range(12))
        lines.append('\t'.join([c, names.get(c, ''), code, 'Y', f'{today} 발급']))
    print('\n'.join(lines))
    # PowerShell 창에서 복사하면 탭이 공백으로 바뀌어 시트에서 한 칸에 몰린다 → 탭이 살아 있는 파일로도 남긴다
    #   (outputs/ 는 .gitignore 대상. 시트에 붙인 뒤에는 지워도 된다)
    os.makedirs(OUT_DIR, exist_ok=True)
    fp = os.path.join(OUT_DIR, f'codes_{today.replace("-", "")}_{datetime.now():%H%M%S}.tsv')
    with open(fp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'\n→ 붙여넣기용 파일: {os.path.relpath(fp, BASE_DIR)} (메모장으로 열어 Ctrl+A → Ctrl+C → 시트 codes 탭 A2)')


def upload(payload):
    if not payload['token']:
        print('⚠️ CUSTOMER_PORTAL_UPLOAD_TOKEN 미설정 — 업로드하지 않습니다')
        return False
    res, err = _post(payload)
    if res and res.get('note') == 'POST only':
        # 2026-10-08: 스크립트 속성 저장 직후 첫 업로드가 doGet 응답을 받고, 같은 명령 재실행은 성공했다(원인 미확정).
        #   한 번만 다시 시도한다.
        import time
        time.sleep(5)
        res, err = _post(payload)
    if res is None:
        print(f'❌ 업로드 실패: {err}')
        return False
    if res.get('status') != 'ok' or res.get('rows') is None:
        # rows 가 없는 ok = doGet 응답(「POST only」) — 업로드가 doPost 에 닿지 않았다. 성공으로 치지 않는다
        print(f'❌ 업로드 실패: {res} (경로: {getattr(_post, "last_diag", "-")})')
        return False
    print(f"✅ 업로드 완료: 거래처 {len(payload['customers'])}곳 · {res.get('rows')}행 (스냅샷 {payload['snapshot_kst']})")
    return True


def upload_from_env(log=print):
    """generate.py 정규 실행용 — 허용 거래처가 있으면 업로드. 예외를 밖으로 던지지 않는다.
    반환: True(성공) / False(실패) / None(대상 없음 — 건너뜀)"""
    try:
        custs = allowed_custs()
        if not custs or not os.getenv('CUSTOMER_PORTAL_GAS_URL'):
            return None
        rows, names, saved = load_rows()
        payload = build_payload(rows, names, saved, custs)
        if not payload['token']:
            log('  ⚠️ 거래처 조회 업로드: 토큰 미설정 — 건너뜀')
            return False
        res, err = _post(payload)
        if res and res.get('note') == 'POST only':      # 원인 미확정 1회성 — 한 번만 재시도 (2026-10-08)
            import time
            time.sleep(5)
            res, err = _post(payload)
        if res and res.get('status') == 'ok' and res.get('rows') is not None:
            log(f"  → 거래처 조회 업로드: {len(custs)}곳 · {res.get('rows')}행 (스냅샷 {saved})")
            return True
        log(f"  ⚠️ 거래처 조회 업로드 실패: {(res or {}).get('status') or err} (경로: {getattr(_post, 'last_diag', '-')})")
        return False
    except Exception as e:
        log(f'  ⚠️ 거래처 조회 업로드 예외(무시): {type(e).__name__}: {str(e)[:120]}')
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--upload', action='store_true', help='허용 거래처만 Apps Script 로 업로드')
    ap.add_argument('--new-code', action='store_true', help='거래처 접속 코드 1개 생성')
    ap.add_argument('--codes-tsv', action='store_true', help='허용 거래처 전부의 codes 탭 행 출력')
    ap.add_argument('--ping', action='store_true', help='웹 앱 연결 확인')
    ap.add_argument('--probe', action='store_true', help='본문 크기별 POST 도달 진단(시트에 쓰지 않음)')
    ap.add_argument('--view', metavar='CODE', help='접속 코드로 조회 시험(브라우저 없이 — 화면과 같은 요청)')
    a = ap.parse_args()

    if a.view:
        res, err = _post({'action': 'view', 'code': a.view}, timeout=30)
        print(f'  경로: {getattr(_post, "last_diag", "-")}')
        if res and res.get('status') == 'ok':
            rows = res.get('rows') or []
            print(f"✅ 조회 성공: {res.get('customer')} · {len(rows)}행 · 기준 {res.get('snapshot_kst')}")
            return 0
        print(f'❌ 조회 실패: {res or err}')
        return 1

    if a.probe:
        probe()
        return 0

    if a.ping:
        return 0 if ping() else 1

    if a.new_code:
        print(''.join(secrets.choice(CODE_ALPHABET) for _ in range(12)))
        return 0

    rows, names, saved = load_rows()
    custs = allowed_custs()
    if a.codes_tsv:
        if not custs:
            print('⚠️ CUSTOMER_PORTAL_CUSTS 가 비어 있습니다')
            return 1
        codes_tsv(names, custs)
        return 0
    by = {}
    for r in rows:
        by.setdefault(r['cust_cd'], []).append(r)
    print(f'스냅샷 {saved} · 고객용 행 {len(rows)} · 거래처 {len(by)}곳 · 업로드 허용 {len(custs)}곳 {custs}')
    for c in custs:
        if c not in by:
            print(f'  ⚠️ 허용 거래처 {c} 의 행이 스냅샷에 없습니다')

    os.makedirs(OUT_DIR, exist_ok=True)
    preview = build_payload(rows, names, saved, custs or sorted(by, key=lambda c: -len(by[c]))[:1])
    preview['token'] = '(미리보기에는 넣지 않음)'
    with open(os.path.join(OUT_DIR, 'preview.json'), 'w', encoding='utf-8') as f:
        json.dump(preview, f, ensure_ascii=False, indent=1)
    print(f'  미리보기: outputs/customer_portal/preview.json ({len(preview["rows"])}행)')

    if a.upload:
        if not custs:
            print('⚠️ CUSTOMER_PORTAL_CUSTS 가 비어 있어 업로드하지 않습니다(닫힌 기본값)')
            return 1
        return 0 if upload(build_payload(rows, names, saved, custs)) else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
