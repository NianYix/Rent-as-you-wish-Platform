# 乡镇物品租赁微信小程序 — 架构设计（MVP）

> 依据：`specs/requirements.md`（已确认决策 2026-09-23）  
> 目标：本地可完整跑通；结构可迁移至云服务器并满足微信小程序提审

---

## 1. 系统上下文

```text
┌─────────────────┐   HTTPS/HTTP(本地)   ┌──────────────────────────────┐
│ 微信小程序       │ ──────────────────→ │  Backend (FastAPI)            │
│ miniprogram/    │ ← JSON + JWT         │  /api/*                       │
└─────────────────┘                      │                               │
                                         │  Auth / User / Merchant /     │
┌─────────────────┐   HTTP               │  Product / Category / Region  │
│ 管理后台 Vue3    │ ──────────────────→ │  Favorite / Inquiry / Admin   │
│ admin/          │                      └───────────┬──────────────────┘
└─────────────────┘                                  │
                                    ┌────────────────┼────────────────┐
                                    ▼                ▼                ▼
                               MySQL 8.x         Redis           本地存储/MinIO
                               (业务数据)      (缓存/限流)      (图片 URL)
```

本地开发不依赖公网域名；上线时 Nginx 终结 TLS，小程序合法域名指向公网 API。

---

## 2. 仓库目录结构

```text
Rent_As_You_Wish_Platform/
├── specs/                    # 需求/设计/任务
├── miniprogram/              # 微信原生小程序 (TypeScript)
├── backend/                  # FastAPI
├── admin/                    # Vue3 + Vite + Element Plus
├── docker-compose.yml        # MySQL + Redis (+ 可选 MinIO)
├── docs/
│   ├── local-dev.md          # 本地启动
│   └── wechat-publish.md     # 注册/配置/提审清单
└── README.md
```

---

## 3. 技术选型与依赖

| 层 | 选型 | 说明 |
|---|---|---|
| 小程序 | 原生 + TypeScript + 微信开发者工具 | 减少跨端框架成本 |
| 后端 | Python 3.12 + FastAPI + SQLAlchemy 2.x + Alembic + Pydantic v2 | REST JSON |
| 鉴权 | JWT（python-jose / PyJWT）+ passlib（管理员密码） | 小程序与后台共用签发体系，claim 区分端 |
| DB | MySQL 8.x | 主存储 |
| 缓存 | Redis | 分类缓存、热门、限流计数、可选 session |
| 文件 | `StorageBackend` 抽象：`LocalStorage`（默认）/ `MinIO` / 预留 `COS` | 库表只存 URL |
| 后台 | Vue 3 + TypeScript + Vite + Element Plus + Pinia + Vue Router | SPA |
| 编排 | docker-compose：mysql、redis | 后端/管理端本地进程或一并容器化 |

### 3.1 关键环境变量（后端）

```text
APP_ENV=local|prod
SECRET_KEY=
DATABASE_URL=mysql+pymysql://...
REDIS_URL=redis://...
WECHAT_APPID=               # 未申请时可空；本地走 mock 登录
WECHAT_SECRET=
JWT_EXPIRE_MINUTES=10080
ADMIN_SEED_USERNAME=admin
ADMIN_SEED_PASSWORD=        # 首次启动种子
STORAGE_BACKEND=local|minio
STORAGE_LOCAL_DIR=./uploads
PUBLIC_BASE_URL=http://127.0.0.1:8000
```

未配置微信凭证时：提供 `POST /api/auth/dev/login`（仅 `APP_ENV=local`）便于开发者工具联调。

---

## 4. 后端分层

```text
backend/
├── app/
│   ├── main.py                 # FastAPI 入口、CORS、路由挂载
│   ├── core/                   # config, security, deps, exceptions, redis
│   ├── models/                 # SQLAlchemy ORM
│   ├── schemas/                # Pydantic 入参/出参
│   ├── api/
│   │   ├── deps.py             # get_current_user / require_roles
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── products.py
│   │   │   ├── categories.py
│   │   │   ├── merchants.py
│   │   │   ├── search.py
│   │   │   ├── favorites.py
│   │   │   ├── history.py
│   │   │   ├── regions.py
│   │   │   ├── uploads.py
│   │   │   └── admin/          # 管理端专用路由前缀 /api/admin/*
│   ├── services/               # 业务编排
│   ├── repositories/           # 可选：数据访问封装
│   └── utils/
├── alembic/
├── scripts/seed.py             # 管理员 + 分类 + 地区乡镇种子
├── requirements.txt
└── Dockerfile
```

原则：路由薄、service 承载业务规则（审核状态流转、联系方式脱敏、角色校验）。

---

## 5. 数据模型（核心）

### 5.1 枚举

| 枚举 | 值 |
|---|---|
| UserRole | USER, MERCHANT, ADMIN |
| MerchantVerifyStatus | NONE, PENDING, APPROVED, REJECTED |
| ProductAuditStatus | DRAFT, PENDING_REVIEW, APPROVED, REJECTED |
| ProductShelfStatus | ONLINE, OFFLINE |
| PriceUnit | HOUR, DAY, TIME, MONTH, NEGOTIABLE, CUSTOM |
| FavoriteTargetType | PRODUCT, MERCHANT |
| InquiryType | PHONE, WECHAT, NAV |

### 5.2 表一览

| 表 | 用途 |
|---|---|
| user | openid、昵称头像、手机、role、status |
| admin_account | 后台登录（可与 user 分离；MVP 用独立表绑定 role=ADMIN 的 user 或纯 admin 表） |
| merchant | 商家资料、五级地区、认证状态 |
| merchant_material | 入驻材料 URL |
| category | parent_id 树形分类 |
| region | 五级行政区：level=1..5，parent_id |
| product | 商品核心字段 + 审核/上下架 + 统计 |
| product_image | 多图 sort |
| favorite | user + target_type + target_id 唯一 |
| browse_history | user + product，按最近时间 upsert |
| inquiry | 联系行为埋点 |
| banner / home_recommend | 首页运营位 |
| system_config | 可选 |

### 5.3 地区 `region`

```text
id, parent_id, name, level(1省2市3区县4乡镇5村), code, sort, status
```

- Seed：预置示例省/市/区县/若干乡镇（可虚构或选真实公开区划片段）。  
- 村：表结构与级联 API 就绪；后台可增删村；MVP 可不批量灌村数据。

### 5.4 商品公开展示条件

```text
audit_status == APPROVED
AND shelf_status == ONLINE
AND merchant.verify_status == APPROVED
AND merchant/user 未被禁用
```

### 5.5 微信号脱敏

- 商家详情/商品详情公开字段 **不含** `wechat`。  
- `POST /api/merchants/{id}/contact/wechat`（需登录）返回微信号并写 `inquiry(type=WECHAT)`。  
- 电话：`wx.makePhoneCall` 前可调 `.../contact/phone` 记 inquiry（或客户端拨打后回调记录）。

---

## 6. API 设计（摘要）

前缀：`/api/v1`

### 公开 / 用户

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /auth/wechat/login | code → token |
| POST | /auth/dev/login | 仅本地 mock |
| GET/PUT | /users/me | 资料 |
| GET | /categories | 树 |
| GET | /regions | 级联 ?parent_id= |
| GET | /products | 列表筛选 |
| GET | /products/{id} | 详情（脱敏） |
| GET | /search/products | 关键词+筛选 |
| GET | /merchants/{id} | 商家详情（脱敏） |
| GET | /merchants/{id}/products | 商家商品 |
| POST | /merchants/{id}/contact/phone | 记询盘 |
| POST | /merchants/{id}/contact/wechat | 登录后取微信号 |
| POST/DELETE | /favorites | 收藏 |
| GET | /favorites | 我的收藏 |
| GET | /browse-history | 浏览记录 |
| POST | /uploads | 上传图片（登录） |
| GET | /home | Banner + 热门 + 推荐商家 |

### 商家

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /merchants/apply | 入驻 |
| GET/PUT | /merchants/me | 资料 |
| POST/PUT | /merchants/me/products | 发布/编辑 |
| POST | /merchants/me/products/{id}/submit | 提交审核 |
| POST | /merchants/me/products/{id}/offline\|online | 上下架 |

### 管理 `/api/v1/admin`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /auth/login | 管理员登录 |
| GET | /dashboard/stats | 概览 |
| CRUD | /users, /merchants, /products, /categories, /regions, /banners | 审核与运营 |

统一响应：

```json
{ "code": 0, "message": "ok", "data": {} }
```

错误：`code != 0` + HTTP 4xx/5xx。

---

## 7. 小程序信息架构

### TabBar

1. 首页 `pages/index/index`  
2. 分类 `pages/category/category`  
3. 我的 `pages/user/user`

### 主要页面

| 页面 | 职责 |
|---|---|
| index | 地区、搜索入口、Banner、分类宫格、热门商品、推荐商家 |
| search | 关键词 + 分类/地区/价格筛选 |
| category | 一二级分类 + 商品列表 |
| product/detail | 详情、收藏、联系 |
| merchant/detail | 商家与商品列表 |
| favorite | 收藏 |
| history | 浏览记录 |
| merchant/apply | 入驻 |
| merchant/center | 商家中心 |
| merchant/product-edit | 发布/编辑 |
| merchant/products | 我的商品 |
| legal/privacy、legal/agreement | 隐私政策/用户协议 |
| region/select | 五级地区选择器 |

### 组件

`ProductCard`、`MerchantCard`、`CategoryGrid`、`SearchBar`、`Empty`、`PriceTag`

### 配置

- `project.config.json`：`appid` 占位，文档说明如何替换。  
- `app.ts`：`baseURL` 读本地配置（开发：`http://127.0.0.1:8000`；注意开发者工具勾选「不校验合法域名」）。

---

## 8. 管理后台信息架构

| 模块 | 功能 |
|---|---|
| 登录 | 种子管理员 |
| Dashboard | 基础统计 |
| 用户管理 | 列表、禁用 |
| 商家管理 | 列表、审核通过/拒绝（填原因） |
| 商品管理 | 列表、审核、强制下架 |
| 分类管理 | 树形 CRUD |
| 地区管理 | 五级维护（重点补村） |
| 首页运营 | Banner、推荐商品/商家 |

路由守卫：无 token 跳转登录。

---

## 9. 关键业务流程

### 9.1 微信登录（生产）

```text
wx.login → code → POST /auth/wechat/login
→ code2session → openid → upsert user → JWT
```

### 9.2 商家入驻 → 发品 → 上架

```text
申请(PENDING) → 后台审核 APPROVED
→ 发布商品(PENDING_REVIEW) → 后台审核 APPROVED + ONLINE
→ C 端可见
```

### 9.3 联系商家

```text
电话：记录 inquiry → makePhoneCall
微信：登录校验 → 返回 wechat → 用户复制 → 记录 inquiry
```

---

## 10. 安全设计

- JWT Bearer；角色装饰器。  
- 密码 bcrypt；种子密码仅首次写入。  
- Pydantic 校验；上传 MIME/大小限制（如 ≤5MB）。  
- Redis 滑动窗口限流：登录、搜索、上传。  
- CORS：本地放行 admin 与开发者工具来源。  
- 生产关闭 `/auth/dev/login`。

---

## 11. 本地运行架构

```text
docker compose up -d mysql redis
uvicorn backend → :8000
npm run dev admin → :5173
微信开发者工具打开 miniprogram/（不校验域名）
seed 脚本：管理员 + 分类 + 地区乡镇
```

静态上传文件由 FastAPI `/uploads/...` 挂载；小程序 download/展示走同一 host。

---

## 12. 微信注册与上架准备（非代码但交付）

`docs/wechat-publish.md` 覆盖：

1. 注册小程序（个人/企业主体差异、类目建议：生活服务/信息查询等以平台最新类目为准）  
2. 获取 AppID，填入 `project.config.json` 与后端 `WECHAT_APPID/SECRET`  
3. 服务器域名、HTTPS、备案  
4. 隐私指引、用户协议页路径  
5. 提审材料与类目一致性自检  
6. 从本地切生产：域名、关闭 mock 登录、切换 COS/OSS

---

## 13. 明确不做（防范围蔓延）

支付、订单、IM、评价、会员、广告、AI、复杂距离排序/地图选点（MVP 仅地址文本 + 可选打开地图 App）、分布式拆分。

---

## 14. 风险与缓解

| 风险 | 缓解 |
|---|---|
| 尚无 AppID | 本地 mock 登录 + 文档化注册步骤 |
| 微信审核对「信息中介」要求 | 强制商家/商品人工审核；协议与隐私齐全 |
| 地区村数据量大 | 结构预留 + 后台维护；seed 只到乡镇 |
| 本地 HTTP 与真机调试 | 文档说明局域网 IP / 内网穿透可选方案 |

---

## 15. 设计确认点

若无异议，执行阶段将严格按本设计落地。若需调整技术细节（如后台与用户共用一张 `user` 表），可在回复「开始执行」前指出。
