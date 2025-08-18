# Docker 部署指南

本文件提供 SSH AI Assistant 的 Docker 部署詳細說明。

## 檔案結構

Docker 相關檔案：
```
├── Dockerfile                    # Docker 映像定義
├── docker-compose.yml           # Docker Compose 配置
├── docker-compose.override.yml  # 開發環境覆蓋配置
├── .dockerignore               # Docker 建置忽略檔案
├── healthcheck.py              # 容器健康檢查腳本
├── test_docker_integration.py  # Docker 整合測試
└── tests/test_docker.py        # Docker 單元測試
```

## 快速開始

### 1. 使用 Docker Compose（推薦）

```bash
# 建置並啟動服務
docker-compose up -d

# 進入互動模式
docker-compose exec ssh-ai-assistant python main.py interactive

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

### 2. 使用 Docker 指令

```bash
# 建置映像
docker build -t ssh-ai-assistant .

# 執行容器
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  -v ~/.ssh:/home/appuser/.ssh:ro \
  ssh-ai-assistant
```

## 配置說明

### Dockerfile 特色

- **基礎映像**: Python 3.11 slim（輕量化）
- **安全性**: 使用非 root 用戶 `appuser`
- **依賴管理**: 分層建置，優化快取
- **健康檢查**: 內建容器健康監控
- **SSH 支援**: 預裝 openssh-client

### Docker Compose 配置

- **持久化存儲**: 
  - `./config` → `/app/config` (機器配置)
  - `./logs` → `/app/logs` (應用日誌)
  - `~/.ssh` → `/home/appuser/.ssh` (SSH 金鑰，只讀)

- **網路**: 獨立的 bridge 網路 `ssh-ai-network`
- **重啟策略**: `unless-stopped`

### 開發環境配置

`docker-compose.override.yml` 提供開發專用配置：
- 即時代碼掛載（`./src` → `/app/src`）
- 測試目錄掛載（`./tests` → `/app/tests`）
- 開發環境變數

## 使用方式

### 基本操作

```bash
# 列出機器
docker-compose exec ssh-ai-assistant python main.py machines

# 添加機器
docker-compose exec ssh-ai-assistant python main.py add-machine \
  --name "測試伺服器" --host "192.168.1.100" --username "admin"

# 互動模式
docker-compose exec ssh-ai-assistant python main.py interactive
```

### 開發操作

```bash
# 重新建置並啟動
docker-compose up --build -d

# 執行測試
docker-compose exec ssh-ai-assistant python -m pytest tests/ -v

# 進入容器調試
docker-compose exec ssh-ai-assistant bash

# 查看容器狀態
docker-compose ps
```

## 測試

### 單元測試

```bash
# 執行 Docker 相關測試
python -m pytest tests/test_docker.py -v

# 執行所有測試
python -m pytest tests/ -v
```

### 整合測試

```bash
# 執行 Docker 整合測試
python test_docker_integration.py
```

測試項目包括：
- Dockerfile 語法驗證
- Docker Compose 配置驗證
- 容器建置測試
- 健康檢查測試
- 基本功能測試

## 故障排除

### 常見問題

#### 1. 權限問題
```bash
# 確保目錄權限正確
chmod 755 config logs
chown -R $USER:$USER config logs
```

#### 2. SSH 金鑰問題
```bash
# 確保 SSH 金鑰權限正確
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

#### 3. 容器無法啟動
```bash
# 查看詳細日誌
docker-compose logs ssh-ai-assistant

# 檢查容器狀態
docker-compose ps

# 重新建置
docker-compose up --build --force-recreate
```

#### 4. 網路連線問題
```bash
# 檢查網路配置
docker network ls
docker network inspect ssh-ai-network

# 測試容器網路
docker-compose exec ssh-ai-assistant ping google.com
```

### 健康檢查

容器包含自動健康檢查：
```bash
# 查看健康狀態
docker-compose ps

# 手動執行健康檢查
docker-compose exec ssh-ai-assistant python healthcheck.py
```

### 日誌調試

```bash
# 查看應用日誌
docker-compose logs -f ssh-ai-assistant

# 查看容器內日誌檔案
docker-compose exec ssh-ai-assistant tail -f /app/logs/ssh_ai.log
```

## 生產部署建議

### 安全性

1. **使用具體版本標籤**：
   ```dockerfile
   FROM python:3.11.6-slim
   ```

2. **掃描安全漏洞**：
   ```bash
   docker scan ssh-ai-assistant
   ```

3. **限制資源使用**：
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

### 監控

1. **健康檢查監控**
2. **日誌聚合**（如 ELK Stack）
3. **效能監控**（如 Prometheus）

### 備份

```bash
# 備份配置
docker run --rm -v ssh-ai-assistant_config:/data -v $(pwd):/backup \
  alpine tar czf /backup/config-backup.tar.gz -C /data .

# 恢復配置
docker run --rm -v ssh-ai-assistant_config:/data -v $(pwd):/backup \
  alpine tar xzf /backup/config-backup.tar.gz -C /data
```

## 進階配置

### 自定義環境變數

在 `docker-compose.yml` 中添加：
```yaml
environment:
  - SSH_AI_LOG_LEVEL=DEBUG
  - SSH_AI_CONFIG_PATH=/app/config
```

### 多環境部署

```bash
# 開發環境
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# 生產環境
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### 擴展服務

```yaml
# 添加資料庫服務
services:
  database:
    image: postgres:15
    environment:
      POSTGRES_DB: ssh_ai
      POSTGRES_USER: ssh_ai
      POSTGRES_PASSWORD: password
```

## 支援

如遇到問題，請：
1. 查看本文件的故障排除章節
2. 執行整合測試診斷問題
3. 查看 GitHub Issues
4. 提交新的 Issue 並附上日誌