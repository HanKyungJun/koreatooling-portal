@echo off
chcp 65001 > nul
echo ============================================
echo  Trico ERP 뷰어 v2.1 빌드
echo ============================================
echo.

python -m pip install pyinstaller pandas openpyxl requests -q
python -m pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client -q

rem 2026-11-19: pyinstaller.exe is not on PATH on the new PC -> run as module
python -m PyInstaller --noconfirm ^
  --onefile --windowed ^
  --name "TricoERP" ^
  --add-data "trico_client.py;." ^
  --add-data "daily_dlv_alert.py;." ^
  --add-data "zero_price_alert.py;." ^
  --hidden-import googleapiclient.discovery ^
  --hidden-import google.auth.transport.requests ^
  --hidden-import email.mime.multipart ^
  --hidden-import email.mime.base ^
  --hidden-import email.mime.text ^
  --hidden-import email.encoders ^
  --collect-data googleapiclient ^
  erp_gui.py

if errorlevel 1 (
  echo.
  echo [FAILED] build error - see messages above
  pause
  exit /b 1
)

echo.
echo Done: dist\TricoERP.exe
pause
