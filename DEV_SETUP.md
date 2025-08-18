# 開發環境設置指南

## 環境要求
- Python 3.11+
- Windows 系統

## 快速開始

### 1. 啟動 Web 介面
```bash
# 雙擊執行
start_dev.bat

# 或手動執行
venv\Scripts\activate
python main.py
```
Web 介面將在 http://127.0.0.1:8000 啟動

### 2. 啟動 CLI 模式
```bash
# 雙擊執行
start_cli.bat

# 或手動執行
venv\Scripts\activate
python main.py cli
```

### 3. 執行測試
```bash
# 雙擊執行
run_tests.bat

# 或手動執行
venv\Scripts\activate
python -m pytest tests/ -v
```

## 目錄結構
```
├── src/                 # 源代碼
├── config/             # 配置文件
├── data/               # 數據庫文件
├── logs/               # 日誌文件
├── tests/              # 測試文件
├── venv/               # 虛擬環境
├── start_dev.bat       # Web 介面啟動腳本
├── start_cli.bat       # CLI 模式啟動腳本
└── run_tests.bat       # 測試執行腳本
```

## 開發流程
1. 修改代碼後重啟應用程式
2. 使用 `run_tests.bat` 執行測試
3. 查看 `logs/` 目錄中的日誌文件進行調試

## 常用指令
- 添加機器: 在 CLI 模式下使用自然語言或 Web 介面
- 查看機器列表: 輸入 "machines"
- 選擇機器: 輸入 "select <machine_id>"