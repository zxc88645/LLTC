# SSH AI Assistant

一個基於自然語言處理的 SSH 指令執行助手，讓您可以用中文或英文與遠端機器進行互動。

## 功能特色

- 🤖 **自然語言理解**: 支援中文和英文指令解析
- 🔐 **安全連線**: 支援密碼和私鑰認證，密碼加密存儲
- 🖥️ **多機器管理**: 可管理多台遠端機器配置
- 💬 **對話式介面**: 直觀的命令列對話介面
- 📊 **豐富輸出**: 格式化的命令執行結果顯示

## 支援的指令類型

### 系統資訊查詢
- "幫我查看這台作業系統版本"
- "檢查系統狀態"
- "查看網路資訊"

### 軟體安裝
- "幫我安裝CUDA"
- "安裝 Docker"

### 硬體檢查
- "幫我檢查當前裝置有哪些設備"
- "查看 GPU 資訊"

## 安裝

### 方法一：使用 Docker（推薦）

> 📖 詳細的 Docker 部署說明請參考 [DOCKER.md](./DOCKER.md)

1. 確保已安裝 Docker 和 Docker Compose

2. 使用 Docker Compose 啟動：
```bash
docker-compose up -d
```

3. 進入互動模式：
```bash
docker-compose exec ssh-ai-assistant python main.py interactive
```

或者直接運行：
```bash
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  -v ~/.ssh:/home/appuser/.ssh:ro \
  ssh-ai-assistant
```

### 方法二：本地安裝

1. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

2. 執行程式：
```bash
python main.py interactive
```

## 使用方法

### Docker 使用方式

#### 啟動互動模式
```bash
# 使用 Docker Compose
docker-compose exec ssh-ai-assistant python main.py interactive

# 或直接使用 Docker
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  ssh-ai-assistant interactive
```

#### 添加機器
```bash
# 使用 Docker Compose
docker-compose exec ssh-ai-assistant python main.py add-machine --name "我的伺服器" --host "192.168.1.100" --username "admin"

# 或直接使用 Docker
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  ssh-ai-assistant add-machine --name "我的伺服器" --host "192.168.1.100" --username "admin"
```

#### 列出所有機器
```bash
# 使用 Docker Compose
docker-compose exec ssh-ai-assistant python main.py machines

# 或直接使用 Docker
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  ssh-ai-assistant machines
```

### 本地使用方式

#### 啟動互動模式
```bash
python main.py interactive
```

#### 添加機器
```bash
python main.py add-machine --name "我的伺服器" --host "192.168.1.100" --username "admin"
```

#### 列出所有機器
```bash
python main.py machines
```

## 互動模式使用流程

1. **啟動程式**: 執行 `python main.py interactive`
2. **查看機器**: 輸入 `machines` 查看所有可用機器
3. **選擇機器**: 輸入 `select <machine_id>` 選擇要操作的機器
4. **執行指令**: 用自然語言輸入您想執行的操作
5. **查看結果**: 系統會自動執行相應的 SSH 指令並顯示結果

## 範例對話

```
您: machines
[顯示機器列表]

您: select abc123
✓ 已選擇機器: 我的伺服器 (192.168.1.100)

您: 幫我查看這台作業系統版本
✓ 已成功檢查作業系統版本
系統資訊: Linux ubuntu 20.04.3 LTS x86_64

您: 幫我檢查當前裝置有哪些設備
✓ 已檢查系統設備 (7 個檢查項目成功)
[顯示詳細的硬體資訊]
```

## 安全性

- 所有密碼都使用 Fernet 加密存儲
- 配置文件設置為僅擁有者可讀寫 (600 權限)
- 支援 SSH 私鑰認證
- 自動添加主機金鑰 (可根據需要調整安全策略)

## 架構設計

```
src/
├── models.py              # 資料模型定義
├── machine_manager.py     # 機器配置管理
├── ssh_manager.py         # SSH 連線和指令執行
├── command_interpreter.py # 自然語言指令解析
├── ai_agent.py           # AI 代理主控制器
└── cli_interface.py      # 命令列介面

config/                   # 配置文件目錄
tests/                   # 單元測試
```

## 開發

### 本地開發

#### 執行測試
```bash
python -m pytest tests/ -v
```

### Docker 開發

#### 建置 Docker 映像
```bash
docker build -t ssh-ai-assistant .
```

#### 使用 Docker Compose 進行開發
```bash
# 啟動服務
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 進入容器進行調試
docker-compose exec ssh-ai-assistant bash

# 執行測試
docker-compose exec ssh-ai-assistant python -m pytest tests/ -v

# 停止服務
docker-compose down
```

#### 重新建置並啟動
```bash
docker-compose up --build -d
```

### 添加新的指令模式
在 `command_interpreter.py` 中的 `_init_command_patterns` 方法中添加新的模式：

```python
'new_intent': [
    {
        'patterns': [r'新指令模式', r'new command pattern'],
        'commands': ['command1', 'command2'],
        'description': '新功能描述'
    }
]
```

## 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案！

## 授權

MIT License
