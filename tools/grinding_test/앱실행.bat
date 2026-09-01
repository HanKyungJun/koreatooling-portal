@echo off
chcp 65001 > nul
cd /d "%~dp0"
start /b pythonw app.py 2>nul
if errorlevel 1 (
    start /b python app.py
)
