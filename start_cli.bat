@echo off
echo 啟動 SSH AI Assistant CLI 模式...

REM 啟動虛擬環境
call venv\Scripts\activate

REM 啟動 CLI 介面
python main.py cli

pause