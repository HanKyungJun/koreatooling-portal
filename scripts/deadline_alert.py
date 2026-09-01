"""
deadline_alert.py — 납기 현황 이메일 알림
===========================================
매일 아침 raw/수주현황/ 최신 xlsx를 읽어
납기 현황을 HTML 이메일로 발송합니다.

실행: python scripts/deadline_alert.py
스케줄: Windows 작업 스케줄러 (매일 08:30 권장)

환경변수 (.env):
  ALERT_EMAIL_FROM   발신 Gmail 주소
  ALERT_EMAIL_PASS   Gmail 앱 비밀번호 (16자리)
  ALERT_EMAIL_TO     수신 이메일 주소 (쉼표 구분 복수 가능)
"""

import os
import sys
import glob
import smtplib
import pandas as pd
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# .env 로드
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')
except ImportError:
    pass

# ── 설정 ────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent.parent
DATA_DIR     = BASE_DIR / 'raw' / '수주현황'
SHEET_NAME   = '재연마 수주현황'
STATUS_DONE  = {'완결'}          # 납품 완료 상태 (알림 제외)
STATUS_SKIP  = {None, float('nan')}

EMAIL_FROM   = os.getenv('ALERT_EMAIL_FROM', '')
EMAIL_PASS   = os.getenv('ALERT_EMAIL_PASS', '')
EMAIL_TO_RAW = os.getenv('ALERT_EMAIL_TO', EMAIL_FROM)
EMAIL_TO     = [e.strip() for e in EMAIL_TO_RAW.split(',') if e.strip()]
# ────────────────────────────────────────────────────────


def load_latest_excel() -> pd.DataFrame:
    """수주현황 폴더에서 가장 최근 수정된 xlsx 로드"""
    files = glob.glob(str(DATA_DIR / '*.xlsx'))
    if not files:
        raise FileNotFoundError(f"수주현황 파일 없음: {DATA_DIR}")
    latest = max(files, key=os.path.getmtime)  # 수정 시간 기준 최신
    print(f"[로드] {latest}")
    df = pd.read_excel(latest, sheet_name=SHEET_NAME)
    return df, Path(latest).name


def classify(df: pd.DataFrame, today: date) -> dict:
    """납기일자 기준으로 항목 분류"""
    result = {
        'overdue':  [],   # 납기 초과
        'today':    [],   # 오늘
        'd3':       [],   # D-1 ~ D-3
        'd7':       [],   # D-4 ~ D-7
        'future':   [],   # D-8 이상
    }

    for _, row in df.iterrows():
        status = str(row.get('진행상태', '')).strip()
        if status in STATUS_DONE or status == 'nan':
            continue

        due = row.get('납기일자')
        if pd.isna(due):
            continue

        due_date = pd.Timestamp(due).date()
        delta = (due_date - today).days

        item = {
            'due':      due_date.strftime('%m/%d'),
            'customer': str(row.get('납품처명', '-')),
            'item':     str(row.get('품목명', '-')),
            'qty':      row.get('수주량', '-'),
            'status':   status,
            'delta':    delta,
        }

        if delta < 0:
            result['overdue'].append(item)
        elif delta == 0:
            result['today'].append(item)
        elif delta <= 3:
            result['d3'].append(item)
        elif delta <= 7:
            result['d7'].append(item)
        else:
            result['future'].append(item)

    return result


def build_table(items: list, color: str) -> str:
    if not items:
        return '<p style="color:#888;font-size:13px;">해당 없음</p>'
    rows = ''
    for it in sorted(items, key=lambda x: x['delta']):
        d_label = f"D+{abs(it['delta'])}" if it['delta'] < 0 else (
                  '오늘' if it['delta'] == 0 else f"D-{it['delta']}")
        rows += f"""
        <tr>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;font-weight:700;color:{color}">{d_label}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee">{it['due']}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee">{it['customer']}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;font-size:12px">{it['item']}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right">{it['qty']}개</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;color:#888">{it['status']}</td>
        </tr>"""
    return f"""
    <table style="width:100%;border-collapse:collapse;font-size:13px;">
      <tr style="background:#f5f5f5;font-size:12px;color:#555">
        <th style="padding:6px 10px;text-align:left">D-Day</th>
        <th style="padding:6px 10px;text-align:left">납기</th>
        <th style="padding:6px 10px;text-align:left">납품처</th>
        <th style="padding:6px 10px;text-align:left">품목</th>
        <th style="padding:6px 10px;text-align:right">수량</th>
        <th style="padding:6px 10px;text-align:left">상태</th>
      </tr>
      {rows}
    </table>"""


def build_html(groups: dict, today: date, filename: str) -> str:
    total = sum(len(v) for v in groups.values())
    overdue_cnt = len(groups['overdue'])
    urgent_cnt  = len(groups['today']) + len(groups['d3'])

    badge_overdue = f'<span style="background:#d32f2f;color:#fff;border-radius:12px;padding:2px 10px;font-size:12px">{overdue_cnt}건 초과</span>' if overdue_cnt else ''
    badge_urgent  = f'<span style="background:#f57c00;color:#fff;border-radius:12px;padding:2px 10px;font-size:12px">{urgent_cnt}건 긴급</span>' if urgent_cnt else ''

    def section(title, color, icon, items):
        cnt = len(items)
        if cnt == 0:
            return ''
        return f"""
        <div style="margin-bottom:20px">
          <h3 style="color:{color};font-size:14px;margin:0 0 8px;border-left:4px solid {color};padding-left:8px">
            {icon} {title} ({cnt}건)
          </h3>
          {build_table(items, color)}
        </div>"""

    return f"""
<!DOCTYPE html><html lang="ko"><body style="margin:0;padding:0;background:#f0f2f5;font-family:'Malgun Gothic',sans-serif">
<div style="max-width:680px;margin:20px auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08)">

  <div style="background:#1A3A6B;padding:20px 24px">
    <h2 style="color:#fff;margin:0;font-size:17px">📦 납기 현황 알림</h2>
    <p style="color:rgba(255,255,255,0.7);margin:4px 0 0;font-size:13px">
      {today.strftime('%Y년 %m월 %d일 (%a)')} 기준 · 진행 중 {total}건
      &nbsp; {badge_overdue} {badge_urgent}
    </p>
  </div>

  <div style="padding:20px 24px">
    {section('⛔ 납기 초과', '#d32f2f', '⛔', groups['overdue'])}
    {section('🔴 오늘 납기', '#c62828', '🔴', groups['today'])}
    {section('🟠 D-3 이내', '#f57c00', '🟠', groups['d3'])}
    {section('🟡 D-4 ~ D-7', '#f9a825', '🟡', groups['d7'])}
    {section('🟢 D-8 이상', '#388e3c', '🟢', groups['future'])}
  </div>

  <div style="background:#f5f5f5;padding:12px 24px;font-size:11px;color:#999">
    데이터: {filename} · 자동발송 (코리아툴링 생산팀)
  </div>
</div>
</body></html>"""


def send_email(subject: str, html: str):
    if not EMAIL_FROM or not EMAIL_PASS:
        print("[경고] 이메일 설정 없음 — .env에 ALERT_EMAIL_FROM / ALERT_EMAIL_PASS 입력 필요")
        print("[미리보기] 이메일 발송 건너뜀")
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = EMAIL_FROM
    msg['To']      = ', '.join(EMAIL_TO)
    msg.attach(MIMEText(html, 'html', 'utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    print(f"[완료] 이메일 발송 → {EMAIL_TO}")


def main():
    today = date.today()
    df, filename = load_latest_excel()
    groups = classify(df, today)

    total   = sum(len(v) for v in groups.values())
    overdue = len(groups['overdue'])
    urgent  = len(groups['today']) + len(groups['d3'])

    subject_flag = '⛔ 납기초과 있음' if overdue else ('⚠️ 긴급 있음' if urgent else '✅ 정상')
    subject = f"[납기알림] {today.strftime('%m/%d')} {subject_flag} — 진행중 {total}건"

    html = build_html(groups, today, filename)
    send_email(subject, html)

    # 콘솔 요약
    print(f"\n{'─'*40}")
    print(f"기준일: {today}  /  진행 중: {total}건")
    print(f"  초과: {overdue}건  |  오늘: {len(groups['today'])}건  |  D-3: {len(groups['d3'])}건")
    print(f"  D-7: {len(groups['d7'])}건  |  D-8+: {len(groups['future'])}건")
    print(f"{'─'*40}")


if __name__ == '__main__':
    main()(f"{'─'*40}")


if __name__ == '__main__':
    main()
