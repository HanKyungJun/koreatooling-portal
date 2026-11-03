@echo off
chcp 65001 >nul
REM 2026-08-28: redirected stdout defaults to cp949 on this box, which killed
REM update_overview.py with UnicodeEncodeError on a checkmark character.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d C:\Users\TOOLKOREA\Desktop\cnc-wiki

REM ============================================================
REM  cnc-wiki daily automation  (rev 2026-08-28)
REM  Registered as Windows task: CNC_Daily_Report  @ 16:00 weekdays
REM  Also used by CNC_Daily_Report_OnBoot as catch-up run.
REM
REM  Merged from the old 17:00 "cnc-wiki Netlify upload" task,
REM  which was missed ~62%% of the time when the PC was powered off
REM  before 17:00 (25 of last 40 runs fired next morning instead).
REM
REM  ASCII only - do not add Korean text to this file.
REM ============================================================

REM 1) daily report xlsx
python scripts\daily_report.py >> wiki\reports\daily\run.log 2>&1

REM 2) calendar artifacts
python scripts\update_calendar_artifact.py >> wiki\reports\daily\run.log 2>&1
python scripts\update_calendar_claude_work.py >> wiki\reports\daily\run.log 2>&1

REM 3) wiki overview stats
python scripts\update_overview.py >> wiki\reports\daily\run.log 2>&1

REM 4) portal build + GitHub Pages push  (must run last)
REM 2026-10-13 diagnostic: morning OnBoot runs exit 1 at this step instantly
REM with nothing in generate.log (09-10, 10-12, 10-13). The outer 2>> keeps
REM cmd own error text (e.g. redirect target in use) in step5_err.log.
REM 2026-10-14 fix: 10-14 morning step5_err.log said "being used by another
REM process" but run.log said rc=0. A failed redirect does NOT set ERRORLEVEL,
REM only the || branch fires. So RC5 is marked FAIL there and forced non-zero.
REM On failure, python/cmd processes are dumped to step5_err.log to find who
REM holds generate.log. Backup: daily_and_upload.bat.bak_20261014
echo [step5-start] %DATE% %TIME% >> wiki\reports\daily\run.log
set "RC5=OK"
(python generate.py >> wiki\reports\daily\generate.log 2>&1) 2>> wiki\reports\daily\step5_err.log || set "RC5=FAIL"
set "EL5=%ERRORLEVEL%"
if "%RC5%"=="FAIL" if "%EL5%"=="0" set "EL5=1"
set "RC5=%EL5%"
if not "%RC5%"=="0" echo [step5-fail] %DATE% %TIME% rc=%RC5% process dump: >> wiki\reports\daily\step5_err.log
if not "%RC5%"=="0" powershell -NoProfile -NonInteractive -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|cmd|wscript|powershell' } | Select-Object ProcessId,ParentProcessId,CreationDate,Name,CommandLine | Format-List | Out-String -Width 400" >> wiki\reports\daily\step5_err.log 2>&1
echo [step5-end] %DATE% %TIME% rc=%RC5% >> wiki\reports\daily\run.log
exit /b %RC5%
