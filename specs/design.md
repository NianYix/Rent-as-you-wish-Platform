# README 项目说明文档 — 设计说明

> 依据：`specs/requirements.md`（README 文档任务，已确认）  
> 目标产物：仓库根目录 `README.md`  
> 原则：README 可独立扫读；细节步骤外链 `docs/`，避免与专项文档重复维护

---

## 1. 文档架构

```text
README.md（入口总览）
├── 产品简介
├── 功能说明 ──────────────→ 来源：miniprogram/pages、admin/src/views、backend API
├── 技术栈 ────────────────→ 来源：requirements.txt、admin/package.json、docker-compose
├── 目录结构 ──────────────→ 来源：仓库实际顶层与关键子目录
├── 如何使用（快速启动）────→ 摘要；细节 → docs/local-dev.md
│   ├── start.bat 一键启动
│   ├── 手动分步启动
│   └── 默认账号 / 验证入口
└── 更多文档链接
    ├── docs/local-dev.md
    ├── docs/deploy.md
    ├── docs/wechat-publish.md
    └── docs/cloudflare-tunnel.md
```

**职责边界**

| 文档 | 职责 |
|---|---|
| `README.md` | 是什么、有什么功能、用什么技术、目录在哪、怎么最快跑起来 |
| `docs/local-dev.md` | 数据库二选一、环境变量细项、真机 lan、联调路径、FAQ |
| `docs/deploy.md` | 上云架构与步骤提纲 |
| `docs/wechat-publish.md` | 注册、类目、合法域名、提审清单 |
| `docs/cloudflare-tunnel.md` | 公网临时 HTTPS 隧道 |

---

## 2. README 章节设计

### 2.1 标题与简介

- 标题：乡镇物品租赁微信小程序（Rent As You Wish）
- 一句话定位：面向乡镇的本地物品租赁信息平台 MVP
- 核心闭环：商家发布 → 用户浏览/搜索 → 联系商家

### 2.2 功能说明

按角色/端分小节，条目化（不写实现细节）：

**用户端（小程序）**

- 登录（微信登录 / 本地开发登录）
- 首页：地区、搜索入口、Banner、分类入口、热门商品
- 分类浏览、关键词搜索
- 商品详情（价格/押金/图文、收藏、浏览计数）
- 商家详情与电话/微信联系
- 收藏、浏览记录
- 用户协议、隐私政策

**商家端（小程序内）**

- 商家入驻申请
- 商家中心、资料维护
- 商品发布 / 编辑 / 上下架

**管理后台（Web）**

- 管理员登录
- 数据概览
- 用户管理、商家审核、商品审核
- 分类管理、地区管理、Banner 管理

**后端能力**

- REST API（`/api/v1`）、OpenAPI（`/docs`）、健康检查（`/health`）
- JWT 鉴权、种子数据、本地文件上传

**范围边界**

- 已实现：信息撮合闭环（上表）
- 未做：支付、订单、IM、会员、AI

### 2.3 技术栈

表格或列表，与仓库一致：

| 层 | 技术 |
|---|---|
| 小程序 | 微信原生小程序 |
| 后端 | Python 3.12+、FastAPI、SQLAlchemy 2、Pydantic、Uvicorn、JWT |
| 数据 | 默认 SQLite；可选 MySQL 8 + Redis 7（Docker Compose） |
| 存储 | 本地磁盘 `uploads/`（可扩展对象存储） |
| 管理后台 | Vue 3、TypeScript、Vite、Element Plus、Pinia、Axios |
| 辅助 | Docker Compose、`start.bat`、可选 Cloudflare Tunnel |

### 2.4 目录结构

展示与当前仓库对齐的树（含关键子目录）：

```text
Rent_As_You_Wish_Platform/
├── miniprogram/           # 微信小程序
│   ├── pages/             # 页面（首页/分类/商品/商家/用户等）
│   ├── components/        # 组件
│   └── utils/             # API、配置、媒体工具
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── api/           # 路由与依赖
│   │   ├── core/          # 配置、数据库、安全
│   │   ├── models/        # ORM 模型
│   │   ├── schemas/       # 请求/响应模型
│   │   └── services/      # 业务与存储
│   └── scripts/           # seed 等脚本
├── admin/                 # 管理后台
│   └── src/views/         # 各业务页面
├── docs/                  # 专项文档
├── specs/                 # 需求/设计/任务
├── scripts/               # 隧道等辅助脚本
├── docker-compose.yml     # MySQL + Redis
├── start.bat              # Windows 本地一键启动
├── .env.example           # 环境变量模板
└── README.md
```

### 2.5 如何使用

采用「快速路径 + 链接」：

1. **前置**：Python 3.12+、Node.js 18+、微信开发者工具；可选 Docker Desktop  
2. **配置**：复制 `.env.example` → `.env`  
3. **推荐 Windows**：根目录运行 `start.bat`（自动 venv、依赖、seed、启动后端 :8000 与后台 :5173）  
4. **手动步骤**：摘要后端 / 管理后台 / 小程序三步（与现 README 一致，可略加清晰）  
5. **可选**：`docker compose up -d` 切换 MySQL/Redis  
6. **默认账号**：`admin` / `Admin@123456`  
7. **验证**：`http://127.0.0.1:8000/docs`、`http://127.0.0.1:5173`、小程序勾选不校验合法域名  
8. **更多**：链接四份 `docs/*`

真机 / 公网：一句话提示改 `miniprogram/utils/config.js` 的 `MODE`，细节见 local-dev / cloudflare-tunnel。

---

## 3. 信息来源与依赖

| README 内容 | 权威来源 |
|---|---|
| 功能列表 | `miniprogram/app.json` pages、`admin/src/router`、`backend/app/api/v1/router.py` |
| 技术版本感 | `backend/requirements.txt`、`admin/package.json`、`docker-compose.yml` |
| 启动命令 | `start.bat`、`docs/local-dev.md`、`.env.example` |
| 默认管理员 | `.env.example` 中 `ADMIN_SEED_*` |
| 未做范围 | 既有 MVP 决策与当前代码事实 |

**依赖关系**：README 依赖 `docs/` 存在且路径正确；不反向要求改业务代码。

**冲突处理**：若旧 README 与代码/docs 不一致，以代码与 docs 为准覆盖。

---

## 4. 文风与格式

- 简体中文，Markdown  
- 标题层级：`##` 主块、`###` 子块  
- 命令用 fenced code block；目录用 `text` 树  
- 加粗仅用于少量关键提示（如默认密码、必勾选项）  
- 不嵌入大段隐私政策正文、不贴生产密钥或易变隧道域名作为唯一配置

---

## 5. 变更范围

| 文件 | 动作 |
|---|---|
| `README.md` | 全文重写/大幅充实（执行阶段） |
| `specs/design.md` | 本文件（设计） |
| `specs/tasks.md` | 随后分解执行任务 |
| 业务代码 / `docs/*` | **不修改**（除非执行中发现链接路径错误需极小修正） |

---

## 6. 风险与注意

- `miniprogram/utils/config.js` 当前可能为 `public` 模式与临时隧道域名：README 示例应写本地默认 `local` / `127.0.0.1`，并说明按环境切换，避免把临时隧道写成正式配置。  
- 种子密码写在文档中仅作本地开发默认值，并提示生产必须修改。

---

## 7. 下一步

1. ~~需求确认~~  
2. ~~生成本设计~~  
3. 生成 `specs/tasks.md`  
4. 你回复「开始执行」后，按 tasks 更新 `README.md`
