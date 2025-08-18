# LLTC

初步的 Python 原型，提供：

- 簡易的主機資訊管理 (`Host` 與 `HostManager`)
- 自然語意到命令字串的對應 (`command_parser`) – 目前使用簡單關鍵字比對，未使用固定表格
- 基於 FastAPI 的簡易 Web 介面，可新增主機並解析自然語意為命令

## 執行 Web 介面

```bash
uvicorn lltc.web:app --reload
```

## Docker 部署

```bash
docker build -t lltc .
docker run -p 8000:8000 lltc
```

## 執行測試

```bash
pytest
```
