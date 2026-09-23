# 乡镇物品租赁微信小程序 — 任务拆解（MVP）

> 依据：`requirements.md` + `design.md`  
> 规则：**仅当用户回复「开始执行」后**才开始编码  
> 建议顺序：基础设施 → 后端核心 → 小程序 C 端 → 商家端 → 管理后台 → 文档与联调

---

## Phase 0 — 工程脚手架

- [ ] T0.1 创建根 `README.md`、`.gitignore`、`.env.example`
- [ ] T0.2 编写 `docker-compose.yml`（MySQL 8、Redis；可选 MinIO）
- [ ] T0.3 初始化 `backend/`：FastAPI、配置、CORS、统一响应、异常处理
- [ ] T0.4 初始化 `miniprogram/`：app 入口、TabBar、基础样式、请求封装
- [ ] T0.5 初始化 `admin/`：Vite + Vue3 + Element Plus + 路由 + Pinia
- [ ] T0.6 编写 `docs/local-dev.md`（本地启动步骤）

**验收**：三端目录存在；compose 可起 MySQL/Redis；后端 `/health` 可访问。

---

## Phase 1 — 数据层与种子

- [ ] T1.1 SQLAlchemy 模型：user、admin_account、merchant、category、region、product、product_image、favorite、browse_history、inquiry、banner/recommend
- [ ] T1.2 Alembic 初始化与首版迁移
- [ ] T1.3 `StorageBackend` + LocalStorage + `/uploads` 静态挂载
- [ ] T1.4 Seed：超级管理员（环境变量）、一级/二级分类、省/市/区县/乡镇示例数据
- [ ] T1.5 村级 region API 与后台可写（可不灌数据）

**验收**：迁移可重复执行；种子管理员可登录后台；地区级联到乡镇有数据。

---

## Phase 2 — 认证与用户

- [ ] T2.1 JWT 签发/校验、角色依赖注入
- [ ] T2.2 `POST /auth/wechat/login`（有凭证走微信；无凭证文档说明）
- [ ] T2.3 `POST /auth/dev/login`（仅 local）
- [ ] T2.4 `GET/PUT /users/me`
- [ ] T2.5 管理端 `POST /admin/auth/login` + 种子账号校验
- [ ] T2.6 小程序登录态存储与请求拦截器

**验收**：开发登录拿到 token；管理端可登录；无 token 访问受保护接口返回 401。

---

## Phase 3 — 分类 / 地区 / 首页 / 商品只读

- [ ] T3.1 分类树 API
- [ ] T3.2 地区级联 API（五级）
- [ ] T3.3 商品列表/详情（公开规则过滤 + 字段脱敏）
- [ ] T3.4 搜索 API（关键词 + 分类 + 地区 + 价格）
- [ ] T3.5 首页聚合 API（Banner、热门、推荐商家）
- [ ] T3.6 浏览计数 + browse_history upsert
- [ ] T3.7 小程序：首页、分类、搜索、商品详情、地区选择

**验收**：无商家数据时可用 seed 演示商品（可选 T3.8 演示 seed）；C 端可浏览详情。

---

## Phase 4 — 商家入驻与商品管理

- [ ] T4.1 商家申请 API + 材料上传
- [ ] T4.2 商家资料 GET/PUT
- [ ] T4.3 商品发布/编辑/提交审核/上下架
- [ ] T4.4 联系商家：phone / wechat（登录后返回微信号 + inquiry）
- [ ] T4.5 小程序：入驻、商家中心、商品编辑/列表、商家详情、联系流程

**验收**：用户可申请入驻；审核通过后可发品；联系微信需登录后可见。

---

## Phase 5 — 收藏与「我的」

- [ ] T5.1 收藏商品/商家 API
- [ ] T5.2 浏览记录列表 API
- [ ] T5.3 小程序：我的、收藏、浏览记录、协议/隐私页占位内容

**验收**：登录用户可完成收藏与历史查看。

---

## Phase 6 — 管理后台

- [ ] T6.1 布局、鉴权路由、Dashboard 统计
- [ ] T6.2 用户管理（禁用）
- [ ] T6.3 商家审核
- [ ] T6.4 商品审核与强制下架
- [ ] T6.5 分类 CRUD
- [ ] T6.6 地区维护（含村）
- [ ] T6.7 Banner / 首页推荐管理

**验收**：管理员可完成「审商家 → 审商品 → 首页可见」闭环。

---

## Phase 7 — 安全、限流与打磨

- [ ] T7.1 上传校验与限流
- [ ] T7.2 生产关闭 dev login 的开关检查
- [ ] T7.3 基础错误页、空状态、加载态
- [ ] T7.4 演示数据脚本（可选）：1 商家 + 若干商品便于截图

**验收**：本地完整业务闭环可演示。

---

## Phase 8 — 上架文档（无服务器也可先交付）

- [ ] T8.1 `docs/wechat-publish.md`：注册小程序、类目、AppID、隐私指引、合法域名、提审检查清单
- [ ] T8.2 `docs/deploy.md`：后续上云（Nginx、HTTPS、域名、COS、环境变量）提纲
- [ ] T8.3 README 串联本地开发与上架路径

**验收**：无小程序账号时，按文档可独立完成注册与后续配置；代码侧 AppID 可配置。

---

## 依赖关系（简图）

```text
T0 → T1 → T2 → T3 → T4 → T5
                ↘ T6（可与 T4/T5 部分并行）
                     → T7 → T8
```

---

## 执行约定

1. 用户回复 **「开始执行」** 后，按 Phase 0→8 推进。  
2. 每完成一个 Phase，做一次本机冒烟说明（无需你额外确认，除非阻塞选型）。  
3. 不提前引入支付/订单/IM 等二期范围。  
4. 微信小程序账号注册需你在微信公众平台人工完成；代码与文档会预留全部配置位。
