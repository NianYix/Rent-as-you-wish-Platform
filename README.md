# 乡镇物品租赁微信小程序（Rent As You Wish）

面向乡镇的本地物品租赁信息平台 MVP：**商家发布 → 用户浏览/搜索 → 联系商家**。

不含在线支付与订单履约，定位为本地生活信息撮合。

---

## 功能说明

### 用户端（微信小程序）

- 登录：微信登录；本地可用开发登录
- 首页：地区选择、搜索入口、Banner、分类入口、热门商品
- 分类浏览（一级 / 二级）
- 关键词搜索与筛选
- 商品详情：图文、价格与单位、押金、收藏、浏览计数
- 商家详情：认证状态、简介、主营商品
- 联系商家：电话拨打、微信联系（登录后主动触发）
- 我的收藏、浏览记录
- 《用户协议》《隐私政策》入口
- 图片地址按当前 API 域名自动改写（避免旧局域网/旧隧道地址在真机失效）

### 商家端（小程序内）

- 商家入驻申请（待后台审核）
- 商家中心与资料维护
- 商品发布 / 编辑 / 上下架（商品需审核通过后对用户展示）
- 发品选图：拍照或从相册选择（`utils/media.js`）
- 上传前隐私同意弹窗（`components/privacy-popup`）
- 调试阶段 `app.json` 中 `__usePrivacyCheck__` 可为 `false`；**正式提审前**需在公众平台配置隐私指引并改回 `true`（见 [docs/wechat-publish.md](docs/wechat-publish.md)）

### 管理后台（Web）

- 管理员账号密码登录
- 数据概览（用户 / 商家 / 商品等基础指标）
- 用户管理
- 商家审核与管理
- 商品审核、上下架干预
- 分类管理、地区（省/市/区县/乡镇/村）维护、Banner 管理

### 后端能力

- REST API（`/api/v1`）、OpenAPI 文档（`/docs`）、健康检查（`/health`）
- JWT 鉴权、角色权限（用户 / 商家 / 管理员）
- 种子数据（地区、分类、演示商家与商品、超级管理员）
- 本地文件上传（可扩展对象存储）；`PUBLIC_BASE_URL` 决定对外图片域名

### 范围边界

| 已实现 | 未做（非本 MVP） |
|---|---|
| 信息撮合闭环（发布 / 浏览 / 搜索 / 联系 / 审核） | 支付、订单履约、即时通讯、会员/广告、复杂 AI 推荐 |

---

## 技术栈

| 层 | 技术 |
|---|---|
| 小程序 | 微信原生小程序 |
| 后端 | Python 3.12+、FastAPI、SQLAlchemy 2、Pydantic、Uvicorn、JWT |
| 数据 | 默认 SQLite；可选 MySQL 8 + Redis 7（Docker Compose） |
| 存储 | 本地磁盘 `uploads/`（上线前可切换 COS/OSS） |
| 管理后台 | Vue 3、TypeScript、Vite、Element Plus、Pinia、Axios |
| 辅助 | Docker Compose、`start.bat`、Cloudflare Tunnel（临时隧道 / 命名隧道） |

---

## 目录结构

```text
Rent_As_You_Wish_Platform/
├── miniprogram/              # 微信小程序
│   ├── pages/                # 页面（首页/分类/商品/商家/用户/协议等）
│   ├── components/           # 组件（隐私弹窗 privacy-popup 等）
│   ├── utils/                # API、环境配置（config）、媒体选图（media）
│   └── assets/               # Tab 图标等静态资源
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/              # 路由与依赖注入
│   │   ├── core/             # 配置、数据库、安全、响应封装
│   │   ├── models/           # ORM 模型
│   │   ├── schemas/          # 请求/响应 Schema
│   │   └── services/         # 业务逻辑与存储抽象
│   └── scripts/              # seed 等脚本
├── admin/                    # 管理后台
│   └── src/
│       ├── views/            # 业务页面
│       ├── api/              # HTTP 客户端
│       └── router/           # 路由
├── docs/                     # 专项文档
│   ├── local-dev.md          # 本地开发详解
│   ├── deploy.md             # 服务器部署提纲
│   ├── wechat-publish.md     # 微信注册与提审
│   ├── cloudflare-tunnel.md  # 临时 / 通用命名隧道
│   └── kinih-cloudflare.md   # api.kinih.xyz 命名隧道（体验版）
├── specs/                    # 需求 / 设计 / 任务规格
├── scripts/
│   ├── start-cloudflare-tunnel.bat / .ps1   # 临时公网隧道（URL 易变，自动写配置）
│   ├── setup-kinih-tunnel.bat               # 一次性配置命名隧道 → api.kinih.xyz
│   ├── start-named-tunnel.bat               # 日常启动命名隧道
│   └── write-cloudflare-config.ps1          # 写入 cloudflared 配置辅助
├── docker-compose.yml        # MySQL + Redis
├── start.bat                 # Windows 一键启动（后端 + 管理后台 + 可选命名隧道）
├── .env.example              # 环境变量模板
└── README.md
```

---

## 如何使用

### 前置条件

- Python 3.12+
- Node.js 18+
- 微信开发者工具
- （可选）Docker Desktop：使用 MySQL / Redis 时需要
- （可选）`cloudflared`：公网隧道 / 体验版域名时需要

### 1. 配置环境变量

```bash
copy .env.example .env
```

本地默认使用 SQLite，无需 Docker。关键项见 `.env.example`（管理员种子账号、微信凭证、`PUBLIC_BASE_URL` 等）。

公网或体验版时，将 `PUBLIC_BASE_URL` 设为与小程序 API 一致的 HTTPS 地址（例如 `https://api.kinih.xyz`），**修改后需重启后端**，否则图片外链可能仍指向旧域名。

### 2. 推荐：Windows 一键启动

在仓库根目录双击或执行：

```bash
start.bat
```

脚本会创建虚拟环境、安装依赖、写入种子数据，并启动：

- 后端：http://127.0.0.1:8000 （文档：http://127.0.0.1:8000/docs）
- 管理后台：http://127.0.0.1:5173
- 若本机已安装 `cloudflared` 且已完成命名隧道配置：一并拉起隧道（示例公网：https://api.kinih.xyz ）

首次使用命名隧道前，请先运行一次 `scripts\setup-kinih-tunnel.bat`（见 [docs/kinih-cloudflare.md](docs/kinih-cloudflare.md)）。

然后用微信开发者工具打开 `miniprogram/` 目录即可。

### 3. 手动分步启动

```bash
# 后端
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example ..\.env
python scripts\seed.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 管理后台（新开终端）
cd admin
npm install
npm run dev
```

小程序：

1. 微信开发者工具 → 导入项目 → 选择 `miniprogram/`
2. AppID 可用测试号 / 游客模式（体验版需正式 AppID）
3. 详情 → 本地设置 → 勾选「不校验合法域名…」（仅开发预览；体验版/正式版会强制校验）
4. 按场景设置 `miniprogram/utils/config.js` 的 `MODE`（见下表）

### 4. 可选：MySQL + Redis

```bash
docker compose up -d
```

再将 `.env` 中 `DATABASE_URL` / `REDIS_URL` 改为 MySQL / Redis 连接串（示例见 `docs/local-dev.md`）。

### 默认管理员

- 账号：`admin`
- 密码：`Admin@123456`（可通过环境变量 `ADMIN_SEED_USERNAME` / `ADMIN_SEED_PASSWORD` 修改）

### 真机预览 / 公网联调 / 体验版

`miniprogram/utils/config.js` 通过 `MODE` 切换 API 地址：

| 场景 | `MODE` | 说明 |
|---|---|---|
| 电脑模拟器 | `local` | `http://127.0.0.1:8000` |
| 同一 WiFi 真机 | `lan` | 填写电脑局域网 IP；防火墙放行 8000 |
| 4G / 公网调试 | `public` | 临时隧道或命名隧道 HTTPS |
| 体验版 / 正式版 | `public` | **固定备案域名**（示例 `https://api.kinih.xyz`）；勿用 `*.trycloudflare.com` |

**临时隧道（调试，URL 每次可能变化）：**

```bat
scripts\start-cloudflare-tunnel.bat
```

会自动写入 `config.js` 的 `HOSTS.public`、`MODE=public`，并同步 `.env` 的 `PUBLIC_BASE_URL`。详见 [docs/cloudflare-tunnel.md](docs/cloudflare-tunnel.md)。

**命名隧道（固定域名，适合体验版）：**

1. 一次性：`scripts\setup-kinih-tunnel.bat`
2. 日常：`start.bat` 或 `scripts\start-named-tunnel.bat`
3. 微信公众平台配置 request / uploadFile / downloadFile 合法域名为 `api.kinih.xyz`（不要加 `https://`）
4. 国内体验版通常要求域名已 **ICP 备案**

详见 [docs/kinih-cloudflare.md](docs/kinih-cloudflare.md)。

更多本地步骤与 FAQ 见 [docs/local-dev.md](docs/local-dev.md)。

### 建议联调路径

1. 管理后台登录，确认演示商品存在  
2. 小程序首页看到热门商品  
3. 详情页 → 收藏 / 电话 / 微信联系  
4. 新用户「商家入驻」→ 后台审核 → 发品（选图需同意隐私）→ 后台审核上架  

---

## 更多文档

| 文档 | 说明 |
|---|---|
| [docs/local-dev.md](docs/local-dev.md) | 本地开发、环境变量、真机联调、FAQ |
| [docs/deploy.md](docs/deploy.md) | 服务器部署提纲 |
| [docs/wechat-publish.md](docs/wechat-publish.md) | 小程序注册、合法域名、隐私指引、提审清单 |
| [docs/cloudflare-tunnel.md](docs/cloudflare-tunnel.md) | Cloudflare 临时 / 通用命名隧道 |
| [docs/kinih-cloudflare.md](docs/kinih-cloudflare.md) | `api.kinih.xyz` 命名隧道与体验版配置 |
| [specs/](specs/) | 需求 / 设计 / 任务规格 |
