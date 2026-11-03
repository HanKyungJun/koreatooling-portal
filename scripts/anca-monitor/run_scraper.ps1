# ANCA 중고장비 스크래퍼 실행 래퍼
# 이메일 자격증명은 cnc-wiki\.env 에 둡니다 (ALERT_EMAIL_FROM / ALERT_EMAIL_PASS / ALERT_EMAIL_TO).
# anca_scraper.py 가 python-dotenv 로 cnc-wiki/.env 를 자동 로드합니다.
# 2026-09-02: 평문 앱 비밀번호 제거 (공개 저장소 추적 파일이었음)
Set-Location "C:\Users\TOOLKOREA\Desktop\cnc-wiki\scripts\anca-monitor"
& "C:\Users\TOOLKOREA\AppData\Local\Python\pythoncore-3.14-64\python.exe" anca_scraper.py
