@echo off
echo 執行測試...

REM 啟動虛擬環境
call venv\Scripts\activate

REM 執行測試
python -m pytest tests/ -v

pause