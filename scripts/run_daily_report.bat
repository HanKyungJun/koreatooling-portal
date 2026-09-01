@echo off
chcp 65001 >nul
cd /d "C:\Users\TOOLKOREA\Desktop\cnc-wiki"

echo ===================================
echo  재연마 일일보고 생성 시작
echo  %date% %time%
echo ===================================

echo.
echo [1단계] Excel 보고서 생성 중...
python scripts\daily_report.py
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Excel 보고서 생성 실패
    goto :end
)
echo  -> wiki\reports\daily\ 저장 완료

echo.
echo [2단계] Google Sheets 업로드 중...
python scripts\upload_to_sheets.py 2>> wiki\reports\daily\upload_err.log
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Google Sheets 업로드 실패 (Excel 보고서는 정상 생성됨)
    echo        오류 내용: wiki\reports\daily\upload_err.log 확인
) else (
    echo  -> Google Sheets 업로드 완료
)

:end
echo.
echo ===================================
echo  완료: %date% %time%
echo ===================================
echo.
echo 창을 닫으려면 아무 키나 누르세요...
pause >nul
