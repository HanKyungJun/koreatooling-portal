@echo off
cd /d C:\Users\TOOLKOREA\Desktop\cnc-wiki

git add .

:: 변경사항 있는지 확인
git diff --cached --quiet
if %errorlevel% == 0 (
    echo [INFO] 변경사항 없음. 커밋 건너뜀.
    pause
    exit /b 0
)

:: 날짜 기반 자동 커밋 메시지
for /f "tokens=1-3 delims=-" %%a in ("%date%") do (
    set YY=%%a
    set MM=%%b
    set DD=%%c
)
set MSG=자동커밋 %YY%-%MM%-%DD%

git commit -m "%MSG%"

echo.
echo [완료] 커밋: %MSG%
pause
