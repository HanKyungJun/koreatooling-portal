@echo off
:: ============================================================
:: ANCA 중고 장비 모니터 — 1회 실행 배치
:: Windows 작업 스케줄러에 이 파일을 등록하세요.
:: ============================================================

:: Python 경로 (기본: PATH에서 자동 탐색)
set PYTHON=python

:: 스크립트 위치로 이동
cd /d "%~dp0"

:: 실행
%PYTHON% anca_scraper.py >> data\run_log.txt 2>&1

:: 종료 코드 출력 (스케줄러 확인용)
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 종료 코드: %ERRORLEVEL% >> data\run_log.txt
)
