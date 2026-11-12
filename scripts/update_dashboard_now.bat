@echo off
chcp 65001 >nul
REM Dashboard update button (2026-11-10, Cowork). Runs generate.py once, same as the 16:00 job.
REM Logic and guards are in scripts\update_dashboard_now.py. ASCII only - no Korean text in this file.
title Dashboard update
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d C:\Users\TOOLKOREA\Desktop\cnc-wiki
python scripts\update_dashboard_now.py
echo.
pause
