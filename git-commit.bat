@echo off
cd /d C:\Users\TOOLKOREA\Desktop\cnc-wiki

git status --short --untracked-files=all
set HASCHG=
for /f "delims=" %%i in ('git status --porcelain --untracked-files^=all') do set HASCHG=1
if not defined HASCHG (
    echo [INFO] 변경사항 없음. 커밋 건너뜀.
    pause
    exit /b 0
)

:: 수동 백업 버튼 - 위 목록 전부가 커밋됨. 세션 끝 커밋은 CLAUDE.md 0-B 명령(바꾼 파일만 add)
echo.
echo 위 파일이 모두 커밋됩니다. 세션에서 바꾼 파일만 올리려면 취소하고 CLAUDE.md 0-B 명령을 쓰세요.
set ANS=
set /p ANS=커밋하려면 Y 입력 후 Enter, 그 외는 취소 : 
if /i not "%ANS%"=="Y" (
    echo [취소] 커밋하지 않았습니다.
    pause
    exit /b 0
)

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
if errorlevel 1 (
    echo.
    echo [실패] 커밋이 안 됐습니다. 위 메시지를 확인하세요.
    pause
    exit /b 1
)

echo.
echo [완료] 커밋: %MSG%
pause
