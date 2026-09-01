@echo off
chcp 65001 > nul
echo ============================================
echo  Trico ERP 뷰어 v2.0 빌드
echo ============================================
echo.

pip install pyinstaller -q
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client -q

pyinstaller ^
  --onefile --windowed ^
  --name "TricoERP" ^
  --add-data "trico_client.py;." ^
  --add-data "daily_dlv_alert.py;." ^
  erp_gui.py

echo.
echo Done: dist\TricoERP.exe
pause
