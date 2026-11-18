@echo off
chcp 65001 >nul
REM Sales board (regrind) - ERP shipment amount/qty + input sheet -> HTML. 2026-11-18, Cowork.
REM Output and input stay in wiki\_private\sales_board (not in git). ASCII only - no Korean text in this file.
title Sales board
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
python erp\sales_board.py --open
echo.
pause
