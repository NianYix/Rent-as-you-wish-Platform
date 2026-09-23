# 本地开发指南

## 前置条件

- Docker Desktop（MySQL + Redis）
- Python 3.12+
- Node.js 18+
- 微信开发者工具

## 1. 数据库（二选一）

### 方式 A：SQLite（默认，推荐先用）

无需 Docker。`.env` 中保持：

```text
DATABASE_URL=sqlite:///./rent_as_you_wish.db
```

### 方式 B：MySQL + Redis（接近生产）

需先启动 Docker Desktop，然后：

```bash
docker compose up -d
```

并将 `.env` 改为：

```text
DATABASE_URL=mysql+pymysql://rent:rent123@127.0.0.1:3306/rent_as_you_wish?charset=utf8mb4
REDIS_URL=redis://127.0.0.1:6379/0
```

确认端口：`3306`（MySQL）、`6379`（Redis）。

## 2. 配置环境变量

```bash
copy .env.example .env
```

关键项：

- `ADMIN_SEED_USERNAME` / `ADMIN_SEED_PASSWORD`
- `WECHAT_APPID` / `WECHAT_SECRET`（未申请可留空，使用开发登录）
- `PUBLIC_BASE_URL=http://127.0.0.1:8000`

后端启动时会从仓库根目录或当前工作目录查找 `.env`。建议把 `.env` 放在仓库根目录，并在 `backend` 目录启动时通过环境变量加载；也可复制一份到 `backend/.env`。

## 3. 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env .env
python scripts\seed.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

验证：

- Health：http://127.0.0.1:8000/health
- Docs：http://127.0.0.1:8000/docs

开发登录：

```http
POST /api/v1/auth/dev/login
{ "openid": "mp_dev_user", "nickname": "小程序用户" }
```

## 4. 管理后台

```bash
cd admin
npm install
npm run dev
```

打开 http://127.0.0.1:5173 ，使用种子管理员登录。

## 5. 微信小程序

1. 打开微信开发者工具 → 导入项目 → 选择 `miniprogram/`
2. AppID：可先用测试号 / 游客模式（`touristappid`）
3. 详情 → 本地设置 → **不校验合法域名、web-view、TLS 版本以及 HTTPS 证书**
4. 编译运行

`miniprogram/utils/config.js` 中 `baseURL` 默认指向 `http://127.0.0.1:8000/api/v1`。

真机预览时，请把 `baseURL` 改成电脑局域网 IP（如 `http://192.168.x.x:8000/api/v1`），并保证手机与电脑同一网络。

## 6. 建议联调路径

1. 管理后台查看演示商品是否存在  
2. 小程序首页看到热门商品  
3. 进入详情 → 收藏 / 电话 / 微信联系  
4. 新用户「商家入驻」→ 后台审核 → 发布商品 → 后台审核上架  

## 常见问题

- **连接 MySQL 失败**：等待容器 healthy 后再 seed  
- **CORS**：本地已放开；管理端走 Vite 代理 `/api`  
- **小程序 request 失败**：检查是否勾选不校验域名，以及后端是否在 8000 端口  
- **商家发品 403**：需后台先审核通过入驻申请（角色变为 MERCHANT）
