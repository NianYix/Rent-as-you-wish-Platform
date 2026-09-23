# 乡镇物品租赁微信小程序（Rent As You Wish）

面向乡镇的本地物品租赁信息平台 MVP：商家发布 → 用户浏览/搜索 → 联系商家。

## 技术栈

- 微信小程序（原生）
- 后端：FastAPI + MySQL + Redis
- 管理后台：Vue 3 + Element Plus
- 本地编排：Docker Compose（MySQL / Redis）

## 快速启动（本地）

详见 [docs/local-dev.md](docs/local-dev.md)。

```bash
# 1. 后端（默认 SQLite，无需 Docker）
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example ..\.env
python scripts/seed.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. 管理后台
cd admin
npm install
npm run dev

# 3. 小程序
# 用微信开发者工具打开 miniprogram/ 目录
# 详情 → 本地设置 → 勾选「不校验合法域名」

# （可选）接近生产时再用 Docker 起 MySQL/Redis：
# docker compose up -d
```

### 默认管理员

- 账号：`admin`
- 密码：`Admin@123456`（可用环境变量修改）

### 演示数据

种子脚本会创建示例乡镇地区、分类、1 个演示商家与若干已上架商品。

## 目录

```text
miniprogram/   微信小程序
backend/       FastAPI
admin/         管理后台
specs/         需求/设计/任务
docs/          本地开发与上架说明
```

## 微信小程序注册与上架

当前仓库可先本地跑通。申请小程序账号与提审步骤见 [docs/wechat-publish.md](docs/wechat-publish.md)。

## 范围说明（MVP）

已实现：登录、首页、分类、搜索、详情、收藏、浏览记录、商家入驻、发品、后台审核、地区五级结构。

未做：支付、订单、IM、会员、AI。
