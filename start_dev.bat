@echo off
echo 啟動 SSH AI Assistant 開發環境...

REM 啟動虛擬環境
call venv\Scripts\activate

REM 設置環境變數
set HOST=127.0.0.1
set PORT=8000

REM 啟動 Web 介面
echo 正在啟動 Web 介面於 http://127.0.0.1:8000
python main.py

pause