# 后续服务器部署提纲

本地验证通过后，可按以下步骤上云。

## 推荐最小架构

```text
用户小程序 → HTTPS → Nginx → FastAPI
                              ├─ MySQL
                              ├─ Redis
                              └─ 本地磁盘或 COS/OSS
管理后台 → Nginx 静态托管（admin dist）
```

## 步骤摘要

1. 购买云服务器、域名，完成备案  
2. 安装 Nginx、申请 SSL 证书（Let’s Encrypt 等）  
3. 部署 MySQL / Redis（可用云数据库）  
4. 配置生产 `.env`：`APP_ENV=prod`、强 `SECRET_KEY`、真实微信凭证、`PUBLIC_BASE_URL=https://api.xxx.com`  
5. `uvicorn` 或 `gunicorn`+`uvicorn workers` 常驻（systemd / supervisor）  
6. Nginx 反代 `/api`、`/uploads`，托管 `admin/dist`  
7. 对象存储：将 `STORAGE_BACKEND` 切换为 COS/OSS（代码预留 Local，上线前可扩展）  
8. 配置微信合法域名并提审  

## 安全

- 关闭开发登录  
- 数据库不暴露公网  
- 定期备份 MySQL  
- 限制上传类型与大小（已做基础限制）
