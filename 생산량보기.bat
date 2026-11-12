@echo off
rem Regrind NC output viewer (ERP read-only, manual refresh F5). 2026-11-02
cd /d "%~dp0"
where pythonw >nul 2>&1
if errorlevel 1 (
  python scripts\today_output_gui.py
  if errorlevel 1 pause
  exit /b
)
start "" pythonw scripts\today_output_gui.py
