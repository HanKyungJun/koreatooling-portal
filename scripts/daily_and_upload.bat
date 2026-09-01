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
python generate.py >> wiki\reports\daily\generate.log 2>&1
