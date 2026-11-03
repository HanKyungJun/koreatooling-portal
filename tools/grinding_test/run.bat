@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo [연삭 테스트 Excel → Wiki 변환기]
echo.
echo 1. grinding_test_input.xlsx 의 C열에 데이터를 입력하고 저장하세요.
echo 2. 이 창에서 아무 키나 누르면 변환을 시작합니다.
echo.
pause

python excel_to_wiki.py
if errorlevel 1 (
    echo.
    echo 오류가 발생했습니다. 위 메시지를 확인하세요.
    pause
) else (
    echo.
    echo wiki\measurements\ 폴더에 .md 파일이 생성되었습니다.
    pause
)
