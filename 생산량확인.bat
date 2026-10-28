@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
set "d="
:loop
cls
python scripts\today_output.py %d%
echo.
set "d="
set /p "d=Enter = refresh / YYYY-MM-DD = other day / q = quit : "
if /i "%d%"=="q" exit /b
goto loop
