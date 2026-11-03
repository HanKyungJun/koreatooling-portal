@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
set "d="
set "opt="
:loop
cls
python scripts\today_output.py %d% %opt%
echo.
set "in="
set /p "in=Enter = refresh / YYYY-MM-DD = other day / s = short <-> detail / t = today / q = quit : "
if /i "%in%"=="q" exit /b
if /i "%in%"=="t" set "d=" & goto loop
if /i "%in%"=="s" (
  if defined opt (set "opt=") else (set "opt=--short")
  goto loop
)
if not "%in%"=="" set "d=%in%"
goto loop
