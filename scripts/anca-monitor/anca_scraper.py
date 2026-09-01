"""
anca_scraper.py — ANCA 중고 장비 모니터링
==========================================
SurplusRecord / MachineSales / Machineseeker 3곳을 스크랩하여
새 매물 발견 시 이메일 알림 발송.

실행:
  python anca_scraper.py              # 1회 즉시 실행
  python anca_scraper.py --schedule   # 스케줄 모드 (config.yaml 시간)
  python anca_scraper.py --debug      # HTML 저장 후 종료 (셀렉터 튜닝용)

환경변수 (.env 또는 시스템):
  ALERT_EMAIL_FROM   발신 Gmail 주소
  ALERT_EMAIL_PASS   Gmail 앱 비밀번호 (16자리)
  ALERT_EMAIL_TO     수신 주소 (쉼표 구분 복수 가능)
"""

import os
import sys
import csv
import json
import hashlib
import smtplib
import ssl
import time
import argparse
import traceback
from datetime import datetime
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup
import yaml

# .env 로드 (없어도 동작)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / '.env')   # cnc-wiki/.env
    load_dotenv(Path(__file__).parent / '.env')                 # 로컬 .env 우선
except ImportError:
    pass

# ── 경로 ─────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR / 'data'
CONFIG_FILE = BASE_DIR / 'config.yaml'
CSV_FILE    = DATA_DIR / 'listings.csv'
HASH_FILE   = DATA_DIR / 'hashes.json'
LOG_FILE    = DATA_DIR / 'run_log.txt'

DATA_DIR.mkdir(exist_ok=True)

# ── 설정 로드 ─────────────────────────────────────────────
with open(CONFIG_FILE, encoding='utf-8') as f:
    CFG = yaml.safe_load(f)

EMAIL_FROM   = os.getenv('ALERT_EMAIL_FROM', CFG.get('email', {}).get('from', ''))
EMAIL_PASS   = os.getenv('ALERT_EMAIL_PASS', CFG.get('email', {}).get('password', ''))
EMAIL_TO_RAW = os.getenv('ALERT_EMAIL_TO',   CFG.get('email', {}).get('to', EMAIL_FROM))
EMAIL_TO     = [e.strip() for e in EMAIL_TO_RAW.split(',') if e.strip()]

SITES        = CFG.get('sites', [])
KEYWORDS     = CFG.get('keywords', ['ANCA'])
SCHEDULE_TIME = CFG.get('schedule_time', '08:00')


# ── 헤더 (봇 차단 우회) ────────────────────────────────────
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/125.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}


# ─────────────────────────────────────────────────────────
#  로깅
# ─────────────────────────────────────────────────────────
def log(msg: str):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'))
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


# ─────────────────────────────────────────────────────────
#  해시 관리
# ─────────────────────────────────────────────────────────
def load_hashes() -> dict:
    if HASH_FILE.exists():
        return json.loads(HASH_FILE.read_text(encoding='utf-8'))
    return {}


def save_hashes(hashes: dict):
    HASH_FILE.write_text(json.dumps(hashes, ensure_ascii=False, indent=2), encoding='utf-8')


def listing_hash(title: str, url: str) -> str:
    return hashlib.md5(f"{title}|{url}".encode()).hexdigest()


# ─────────────────────────────────────────────────────────
#  CSV 저장
# ─────────────────────────────────────────────────────────
CSV_FIELDS = ['date', 'site', 'title', 'price', 'location', 'url', 'hash']

def append_csv(rows: list[dict]):
    write_header = not CSV_FILE.exists()
    with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if write_header:
            w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, '') for k in CSV_FIELDS})


# ─────────────────────────────────────────────────────────
#  HTTP 요청
# ─────────────────────────────────────────────────────────
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def fetch(url: str, timeout: int = 15) -> BeautifulSoup | None:
    try:
        resp = SESSION.get(url, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')
    except requests.HTTPError as e:
        log(f"  HTTP 오류 {e.response.status_code}: {url}")
        if e.response.status_code in (403, 429):
            log("  ⚠️  봇 차단 감지 — 로컬 PC에서 실행하거나 --debug 로 HTML 확인 필요")
        return None
    except Exception as e:
        log(f"  요청 실패: {e}")
        return None


# ─────────────────────────────────────────────────────────
#  사이트별 스크래퍼
# ─────────────────────────────────────────────────────────
def scrape_site(site_cfg: dict) -> list[dict]:
    """
    config.yaml 의 sites[] 항목 하나를 받아 매물 목록 반환.
    각 매물: {title, price, location, url, site}
    """
    name     = site_cfg['name']
    url      = site_cfg['url']
    sel      = site_cfg.get('selectors', {})

    log(f"  [{name}] 요청: {url}")
    soup = fetch(url)
    if soup is None:
        return []

    # 매물 컨테이너 목록
    container_sel = sel.get('container')
    if not container_sel:
        log(f"  [{name}] selectors.container 미설정 — config.yaml 확인 필요")
        return []

    items = soup.select(container_sel)
    if not items:
        log(f"  [{name}] 매물 요소 0건 — 셀렉터 확인 필요: {container_sel}")
        return []

    results = []
    base_url = site_cfg.get('base_url', '')

    for item in items[:CFG.get('max_per_site', 50)]:
        # 제목
        title = ''
        if sel.get('title'):
            el = item.select_one(sel['title'])
            title = el.get_text(strip=True) if el else ''
        if not title:
            title = item.get_text(separator=' ', strip=True)[:100]

        # 키워드 필터 (하나라도 포함 시 통과)
        if KEYWORDS and not any(kw.lower() in title.lower() for kw in KEYWORDS):
            continue

        # 가격
        price = ''
        if sel.get('price'):
            el = item.select_one(sel['price'])
            price = el.get_text(strip=True) if el else ''

        # 위치
        location = ''
        if sel.get('location'):
            el = item.select_one(sel['location'])
            location = el.get_text(strip=True) if el else ''

        # URL
        link = ''
        if sel.get('link'):
            el = item.select_one(sel['link'])
            link = el.get('href', '') if el else ''
        elif item.name == 'a':
            link = item.get('href', '')
        else:
            el = item.find('a')
            link = el.get('href', '') if el else ''

        if link and not link.startswith('http'):
            link = base_url.rstrip('/') + '/' + link.lstrip('/')

        results.append({
            'site':     name,
            'title':    title,
            'price':    price,
            'location': location,
            'url':      link,
        })

    log(f"  [{name}] 키워드 매칭 {len(results)}건")
    return results


# ─────────────────────────────────────────────────────────
#  디버그 모드 — HTML 저장
# ─────────────────────────────────────────────────────────
def debug_mode():
    log("=== DEBUG 모드: HTML 저장 ===")
    for site_cfg in SITES:
        name = site_cfg['name']
        url  = site_cfg['url']
        log(f"  [{name}] {url}")
        soup = fetch(url)
        if soup is None:
            continue
        out = DATA_DIR / f"debug_{name.lower().replace(' ','_')}.html"
        out.write_text(str(soup), encoding='utf-8')
        log(f"  → 저장: {out}")
    log("브라우저로 data/debug_*.html 을 열어 CSS 셀렉터를 확인하세요.")


# ─────────────────────────────────────────────────────────
#  이메일 발송
# ─────────────────────────────────────────────────────────
def send_email(new_listings: list[dict]):
    if not EMAIL_FROM or not EMAIL_PASS:
        log("⚠️  이메일 설정 없음 — .env 에 ALERT_EMAIL_FROM / ALERT_EMAIL_PASS 입력 필요")
        return
    if not EMAIL_TO:
        log("⚠️  수신 주소 없음 — ALERT_EMAIL_TO 입력 필요")
        return

    count = len(new_listings)
    subject = f"[ANCA 중고] 신규 매물 {count}건 발견"

    # HTML 본문 생성
    rows_html = ''
    for item in new_listings:
        link_html = f'<a href="{item["url"]}">{item["url"][:60]}…</a>' if item.get('url') else '-'
        rows_html += f"""
        <tr>
          <td style="padding:6px 10px;border-bottom:1px solid #eee">{item['site']}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee"><b>{item['title']}</b></td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;color:#0070c0">{item.get('price','')}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;color:#666">{item.get('location','')}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;font-size:12px">{link_html}</td>
        </tr>"""

    html = f"""<html><body style="font-family:sans-serif;color:#222">
<h2 style="color:#c00">🔔 ANCA 중고 장비 신규 매물 {count}건</h2>
<p>수집 시각: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<table style="border-collapse:collapse;width:100%;font-size:13px">
  <thead>
    <tr style="background:#f0f0f0">
      <th style="padding:6px 10px;text-align:left">사이트</th>
      <th style="padding:6px 10px;text-align:left">제목</th>
      <th style="padding:6px 10px;text-align:left">가격</th>
      <th style="padding:6px 10px;text-align:left">위치</th>
      <th style="padding:6px 10px;text-align:left">링크</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
<hr style="margin-top:24px">
<p style="font-size:11px;color:#999">ANCA 중고 장비 모니터 · cnc-wiki</p>
</body></html>"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = EMAIL_FROM
    msg['To']      = ', '.join(EMAIL_TO)
    msg.attach(MIMEText(html, 'html', 'utf-8'))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ctx) as smtp:
            smtp.login(EMAIL_FROM, EMAIL_PASS)
            smtp.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_bytes())
        log(f"✅ 이메일 발송 완료 → {', '.join(EMAIL_TO)}")
    except Exception as e:
        log(f"❌ 이메일 발송 실패: {e}")


# ─────────────────────────────────────────────────────────
#  메인 실행
# ─────────────────────────────────────────────────────────
def run_once():
    log("=" * 50)
    log("ANCA 중고 장비 스크래퍼 시작")

    hashes = load_hashes()
    new_listings = []
    today = datetime.now().strftime('%Y-%m-%d')

    for site_cfg in SITES:
        try:
            listings = scrape_site(site_cfg)
            time.sleep(CFG.get('delay_between_sites', 3))
        except Exception:
            log(f"  [{site_cfg['name']}] 오류:\n{traceback.format_exc()}")
            continue

        for item in listings:
            h = listing_hash(item['title'], item['url'])
            if h not in hashes:
                item['hash'] = h
                item['date'] = today
                hashes[h] = today
                new_listings.append(item)

    if new_listings:
        log(f"✨ 신규 매물 {len(new_listings)}건 발견")
        append_csv(new_listings)
        save_hashes(hashes)
        send_email(new_listings)
    else:
        log("신규 매물 없음")
        save_hashes(hashes)  # 마지막 실행 시각 갱신

    log("완료")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--schedule',   action='store_true', help='스케줄 모드')
    parser.add_argument('--debug',      action='store_true', help='HTML 저장 후 종료')
    parser.add_argument('--test-email', action='store_true', help='테스트 메일 발송 후 종료')
    args = parser.parse_args()

    if args.debug:
        debug_mode()
        return

    if args.test_email:
        dummy = [{
            'site': '테스트', 'title': 'ANCA MX7 (테스트 메일)', 'price': '문의',
            'location': '서울', 'url': 'https://example.com',
        }]
        send_email(dummy)
        return

    if args.schedule:
        try:
            import schedule
        except ImportError:
            print("schedule 패키지 필요: pip install schedule")
            sys.exit(1)

        log(f"스케줄 모드: 매일 {SCHEDULE_TIME} 실행")
        schedule.every().day.at(SCHEDULE_TIME).do(run_once)
        run_once()   # 시작 즉시 1회 실행
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_once()


if __name__ == '__main__':
    main()
