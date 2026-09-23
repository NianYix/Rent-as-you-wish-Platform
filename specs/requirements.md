# 乡镇物品租赁微信小程序 — 需求规格说明（MVP）

> 依据：《乡镇物品租赁微信小程序项目设计文档.md》  
> 范围：第一阶段 MVP（信息撮合闭环，不含支付/订单/IM/AI）  
> 目标：功能可落地，并满足微信小程序上架审核与合规要求  
> 语法：EARS（WHEN / IF / WHERE / THE SYSTEM SHALL）

---

## 1. 文档信息

| 项 | 内容 |
|---|---|
| 产品名称 | 乡镇本地物品租赁信息平台（暂定：Rent As You Wish） |
| 产品形态 | 微信小程序（用户/商家）+ Web 管理后台（管理员）+ 后端 API |
| MVP 核心闭环 | 商家发布商品 → 用户发现商品 → 查看价格 → 联系商家 |
| 明确不做（V1） | 在线支付、订单履约、即时通讯、会员/广告、复杂推荐、分布式架构 |

---

## 2. 角色与权限

### 2.1 角色定义

| 角色 | 说明 |
|---|---|
| 普通用户（USER） | 浏览、搜索、收藏、查看商家联系方式 |
| 商家（MERCHANT） | 入驻认证后发布与管理商品 |
| 平台管理员（ADMIN） | 审核商家/商品，维护分类与推荐，管理用户 |

### REQ-ROLE-001
THE SYSTEM SHALL 支持三种业务角色：`USER`、`MERCHANT`、`ADMIN`。

### REQ-ROLE-002
WHEN 用户完成微信登录但未入驻商家 THE SYSTEM SHALL 默认赋予 `USER` 角色。

### REQ-ROLE-003
WHEN 用户不具备对应角色权限时 THE SYSTEM SHALL 拒绝执行受保护操作并返回明确错误信息。

---

## 3. 用户端（微信小程序）

### 3.1 登录与账号

### REQ-AUTH-001
WHEN 用户首次进入需要登录的页面或主动触发登录 THE SYSTEM SHALL 通过 `wx.login` 获取 `code` 并由后端换取 `openid` 创建或查询用户。

### REQ-AUTH-002
WHEN 微信登录成功 THE SYSTEM SHALL 向客户端返回业务 Token（JWT 或等价会话凭证），且不得将微信 AppSecret 等敏感凭证下发到客户端。

### REQ-AUTH-003
WHEN 用户授权手机号（若业务需要） THE SYSTEM SHALL 安全解密并绑定到用户资料。

### REQ-AUTH-004
IF 用户未登录 THEN THE SYSTEM SHALL 允许匿名浏览首页、分类、商品列表与商品详情的公开信息；WHEN 用户执行收藏、联系商家、商家入驻等操作 THE SYSTEM SHALL 引导登录。

### 3.2 首页

### REQ-HOME-001
THE SYSTEM SHALL 提供首页，至少包含：地区选择入口、搜索入口、Banner 区域、常用分类入口、附近/热门商品列表、推荐商家区域。

### REQ-HOME-002
WHEN 用户选择或切换地区 THE SYSTEM SHALL 按所选地区刷新首页商品与商家推荐数据。

### REQ-HOME-003
IF 用户未授权定位 THEN THE SYSTEM SHALL 允许手动选择省/市/区县/乡镇/村，不得强制阻断浏览。

### REQ-HOME-004
WHEN 管理员配置了首页推荐商品或 Banner THE SYSTEM SHALL 在首页按配置展示。

### 3.3 分类与商品列表

### REQ-CAT-001
THE SYSTEM SHALL 支持一级分类 + 二级分类的浏览结构，分类数据由后台动态维护。

### REQ-CAT-002
WHEN 用户选择某一分类 THE SYSTEM SHALL 展示该分类下已审核通过且已上架的商品列表。

### REQ-CAT-003
THE SYSTEM SHALL 在商品卡片上展示：封面图、名称、价格与价格单位、商家名称、所在地区（支持展示至村级）、联系入口。

### 3.4 搜索与筛选

### REQ-SEARCH-001
WHEN 用户输入关键词搜索 THE SYSTEM SHALL 返回匹配商品名称/描述的已上架已审核商品。

### REQ-SEARCH-002
THE SYSTEM SHALL 支持按分类、地区、价格区间筛选搜索结果。

### REQ-SEARCH-003
WHEN 无匹配结果 THE SYSTEM SHALL 展示空状态提示，不得报错中断。

### 3.5 商品详情

### REQ-PROD-001
WHEN 用户打开商品详情 THE SYSTEM SHALL 展示：图片轮播、名称、租赁价格与单位、押金、描述、关键参数（若有）、商家信息摘要、收藏按钮、联系商家入口。

### REQ-PROD-002
WHEN 用户查看商品详情 THE SYSTEM SHALL 累加该商品浏览次数，并为已登录用户写入浏览记录。

### REQ-PROD-003
IF 商品未通过审核或已下架 THEN THE SYSTEM SHALL 不对普通用户展示该商品详情（管理员/所属商家除外）。

### 3.6 商家详情与联系

### REQ-MER-001
WHEN 用户打开商家详情 THE SYSTEM SHALL 展示：头像、名称、认证状态、营业时间、所在地区、商家介绍、主营商品列表。

### REQ-MER-002
WHEN 用户点击联系商家 THE SYSTEM SHALL 提供电话拨打能力；并按策略提供微信联系/地址查看/地图导航中的一种或多种。

### REQ-MER-003
WHEN 用户触发联系行为（电话/微信等） THE SYSTEM SHALL 记录咨询行为（inquiry），用于统计，不得在客户端默认明文暴露不应公开的敏感字段策略冲突项。

### REQ-MER-004
WHERE 微信号展示策略为「非默认暴露」 THE SYSTEM SHALL 仅在登录用户主动请求联系时按业务规则展示或复制微信号。

### 3.7 收藏与浏览记录

### REQ-FAV-001
WHEN 已登录用户收藏或取消收藏商品/商家 THE SYSTEM SHALL 持久化 `target_type` + `target_id` 收藏关系。

### REQ-FAV-002
THE SYSTEM SHALL 提供「我的收藏」列表，支持取消收藏。

### REQ-HIST-001
THE SYSTEM SHALL 为已登录用户保存商品浏览记录，并在「浏览记录」页展示。

### REQ-HIST-002
WHEN 同一用户重复浏览同一商品 THE SYSTEM SHALL 更新最近浏览时间而非无限堆积无效重复记录（实现上可采用去重或覆盖策略）。

### 3.8 我的

### REQ-ME-001
THE SYSTEM SHALL 提供「我的」页面，展示用户头像昵称、收藏入口、浏览记录入口、商家入驻/商家中心入口（按角色）、联系客服/关于/隐私政策入口。

### REQ-ME-002
WHEN 用户更新个人资料（昵称、头像等） THE SYSTEM SHALL 保存并在相关页面同步展示。

---

## 4. 商家端（微信小程序内）

### 4.1 入驻与认证

### REQ-APPLY-001
WHEN 用户提交商家入驻申请 THE SYSTEM SHALL 收集商家名称、联系电话、地区、地址、简介，以及按合规要求的营业/身份相关材料，并将审核状态置为待审核。

### REQ-APPLY-002
THE SYSTEM SHALL 支持个人商家与企业商家两种入驻类型。

### REQ-APPLY-003
IF 商家审核未通过 THEN THE SYSTEM SHALL 禁止该账号发布商品，并展示拒绝原因（若管理员填写）。

### REQ-APPLY-004
WHEN 管理员审核通过商家入驻 THE SYSTEM SHALL 将用户角色升级/关联为 `MERCHANT`，并允许发布商品。

### REQ-APPLY-005
THE SYSTEM SHALL 展示商家认证状态（未认证/待审核/已认证/已拒绝）。

### 4.2 商家资料

### REQ-MPROF-001
WHEN 已认证商家编辑资料（头像、简介、营业时间、电话、微信、地址等） THE SYSTEM SHALL 保存变更；关键联系方式变更可按策略要求复审（MVP 默认保存即生效，除非合规强制复审）。

### 4.3 商品发布与管理

### REQ-MPROD-001
WHEN 商家发布商品 THE SYSTEM SHALL 要求填写：名称、分类、封面与图片、描述、价格、价格单位、押金（可选）、库存、地区与地址，并进入待审核状态。

### REQ-MPROD-002
THE SYSTEM SHALL 支持价格单位至少包含：按小时、按天、按次、按月、面议（及可扩展自定义）。

### REQ-MPROD-003
WHEN 商家提交商品审核 THE SYSTEM SHALL 将商品状态设为 `PENDING_REVIEW`，审核通过后方可对用户侧上架展示。

### REQ-MPROD-004
THE SYSTEM SHALL 支持商家编辑商品、上下架商品、查看自有商品列表。

### REQ-MPROD-005
WHEN 商家下架商品 THE SYSTEM SHALL 立即对普通用户隐藏该商品。

### REQ-MPROD-006
THE SYSTEM SHALL 支持商品审核状态：`DRAFT`、`PENDING_REVIEW`、`APPROVED`、`REJECTED`、`OFFLINE`（或等价字段组合表达上下架与审核）。

### REQ-MPROD-007
WHEN 商品被审核拒绝 THE SYSTEM SHALL 通知商家（站内提示即可）并展示拒绝原因，允许修改后再次提交。

---

## 5. 管理后台（Web）

### REQ-ADMIN-001
WHEN 管理员使用账号密码（或等价安全方式）登录后台 THE SYSTEM SHALL 校验身份并建立管理员会话。

### REQ-ADMIN-002
THE SYSTEM SHALL 提供用户管理：查看用户列表、状态启用/禁用。

### REQ-ADMIN-003
THE SYSTEM SHALL 提供商家管理：商家列表、商家详情、商家审核（通过/拒绝）。

### REQ-ADMIN-004
THE SYSTEM SHALL 提供商品管理：商品列表、商品审核（通过/拒绝）、商品上下架干预。

### REQ-ADMIN-005
THE SYSTEM SHALL 提供分类管理：增删改一级/二级分类、图标、排序、启用/停用。

### REQ-ADMIN-006
THE SYSTEM SHALL 提供首页推荐管理：配置 Banner 与/或推荐商品、推荐商家。

### REQ-ADMIN-007
THE SYSTEM SHALL 提供基础数据概览：用户数、商家数、商品数、浏览量、收藏量、联系点击量等（MVP 可先做当日/累计基础指标）。

### REQ-ADMIN-008
THE SYSTEM SHALL 提供地区数据维护能力（省/市/区县/乡镇/村五级），供商品与商家绑定；MVP 须预置乡镇级种子数据，村级数据结构与后台维护能力就绪，村级明细可后续补录。

---

## 6. 数据与领域规则

### REQ-DATA-001
THE SYSTEM SHALL 使用关系型数据库持久化用户、商家、商品、分类、收藏、浏览记录、咨询记录等核心实体。

### REQ-DATA-002
THE SYSTEM SHALL 将商品图片/视频存储于对象存储，数据库仅保存 URL 与排序元数据。

### REQ-DATA-003
THE SYSTEM SHALL 为商品与商家绑定省/市/区县/乡镇/村地区字段（`village_id` 可为空，但模型与 API 必须支持）。

### REQ-DATA-004
WHEN 写入用户、商家、商品等数据 THE SYSTEM SHALL 记录创建时间与更新时间。

---

## 7. API 与安全

### REQ-API-001
THE SYSTEM SHALL 对外提供 HTTPS RESTful JSON API，供小程序与管理后台调用。

### REQ-API-002
WHEN 客户端携带有效业务 Token THE SYSTEM SHALL 识别当前用户身份；IF Token 无效或过期 THEN THE SYSTEM SHALL 返回未授权错误。

### REQ-API-003
THE SYSTEM SHALL 对写操作与敏感读操作进行参数校验与权限校验。

### REQ-API-004
THE SYSTEM SHALL 对登录、搜索、发布等关键接口实施基础频率限制，降低刷接口与滥用风险。

### REQ-API-005
THE SYSTEM SHALL 避免在日志与接口响应中泄露微信密钥、对象存储密钥等敏感配置。

### REQ-API-006
WHERE 内容审核策略生效 THE SYSTEM SHALL 阻止明显违规商品/商家资料进入公开展示（至少依赖人工审核；自动化审核为后续增强）。

---

## 8. 微信小程序上架与合规（必须）

### REQ-WX-001
THE SYSTEM SHALL 使用已备案且可公网访问的 HTTPS API 域名，不得在正式提审包中依赖 `localhost`、内网 IP 或明文 HTTP。

### REQ-WX-002
THE SYSTEM SHALL 在微信公众平台配置 request 合法域名、uploadFile 合法域名、downloadFile 合法域名（及所需业务域名）。

### REQ-WX-003
THE SYSTEM SHALL 提供符合微信要求的用户隐私保护指引：明确收集的信息类型（如头像昵称、手机号、位置、设备信息等）及用途。

### REQ-WX-004
WHEN 小程序需要定位能力 THE SYSTEM SHALL 在调用前说明用途，并在未授权时提供手动选地区的降级路径。

### REQ-WX-005
THE SYSTEM SHALL 提供《用户协议》与《隐私政策》页面入口，供审核与用户查阅。

### REQ-WX-006
THE SYSTEM SHALL 避免诱导分享、虚假营销、未审内容公开传播等违反微信小程序运营规范的行为路径。

### REQ-WX-007
THE SYSTEM SHALL 支持类目与功能声明与实际能力一致（本地生活/信息中介类定位），商家发布内容经审核后展示。

### REQ-WX-008
THE SYSTEM SHALL 提供可提审的小程序代码包结构（原生或等价编译产物），包含完整页面路径、TabBar（若使用）、错误处理与加载态。

### REQ-WX-009
IF 使用手机号、位置等受控接口 THEN THE SYSTEM SHALL 按微信最新接口规范申请权限并正确声明隐私接口。

### REQ-WX-010
THE SYSTEM SHALL 在提交审核前具备：基础冒烟可用（登录、浏览、详情、联系、商家发布、后台审核）的生产或预发环境。

---

## 9. 非功能需求

### REQ-NFR-001
THE SYSTEM SHALL 在常规 4G 网络下，首屏关键接口目标响应时间控制在可接受范围（建议 P95 < 2s，MVP 以可用性优先）。

### REQ-NFR-002
THE SYSTEM SHALL 适配主流 iOS/Android 微信客户端最近两个大版本。

### REQ-NFR-003
THE SYSTEM SHALL 对图片上传限制大小与格式（如 jpg/png/webp），防止过大文件拖垮上传链路。

### REQ-NFR-004
THE SYSTEM SHALL 支持基础日志与错误追踪，便于上线后排查故障。

### REQ-NFR-005
THE SYSTEM SHALL 提供数据库备份策略说明或脚本（至少日备可恢复）。

---

## 10. 推荐技术约束（来自设计文档，可在 design 阶段微调）

### REQ-TECH-001
WHERE 无充分理由替换 THE SYSTEM SHALL 采用：微信小程序原生 + TypeScript、后端 FastAPI（Python 3.12+）、MySQL 8.x、Redis、对象存储抽象（本地开发用本地磁盘/MinIO，上线前切换 COS/OSS）、管理后台 Vue3 + Element Plus。

### REQ-TECH-002
THE SYSTEM SHALL 采用前后端分离架构，小程序与管理后台均通过 API 访问业务能力。

---

## 11. 验收标准（MVP Done）

以下全部满足即视为 MVP 可进入提审准备：

1. 用户可微信登录、按地区/分类浏览、搜索、查看商品与商家详情、收藏、查看浏览记录、电话联系商家。  
2. 商家可入驻申请、审核通过后发布/编辑/下架商品。  
3. 管理员可登录后台审核商家与商品、管理分类与首页推荐、查看基础数据。  
4. 生产 API 使用 HTTPS 合法域名，小程序可配置合法域名并提交审核。  
5. 具备隐私政策、用户协议及隐私指引配置。  
6. 明确不包含支付、订单、IM 等二期能力，且产品文案不承诺未实现能力。

---

## 12. 已确认决策（2026-09-23）

| # | 议题 | 决策 |
|---|---|---|
| 1 | 小程序主体 | 当前尚未注册；需另行申请微信小程序账号后再配置 AppID/域名/提审 |
| 2 | 技术栈 | 原生小程序 + FastAPI + MySQL + Redis + Vue3 管理后台；对象存储本地先用本地/MinIO，上线前切 COS/OSS |
| 3 | 微信号策略 | 默认不暴露；用户登录后主动点击「微信联系」再展示/复制 |
| 4 | 地区层级 | 做到村级（五级：省/市/区县/乡镇/村）；MVP 先预置乡镇种子数据，村级字段与维护能力预留 |
| 5 | 管理员 | 需要超级管理员种子账号（用户名/密码，可由环境变量配置） |
| 6 | 部署节奏 | 先本地 Docker/本机可完整跑通；上服务器与正式域名作为后续上线阶段 |

### REQ-SEED-001
WHEN 系统首次初始化 THE SYSTEM SHALL 创建可配置的超级管理员账号（默认可通过环境变量覆盖用户名与密码）。

### REQ-SEED-002
WHEN 系统首次初始化 THE SYSTEM SHALL 导入预置乡镇级地区种子数据，并保证村级表结构可用。

### REQ-WX-REG-001
THE SYSTEM SHALL 在文档中提供微信小程序注册、类目选择、开发者工具配置、合法域名与提审检查清单；代码侧使用可配置 `AppID`，本地可用测试号/开发者模式联调。

### REQ-LOCAL-001
THE SYSTEM SHALL 提供本地一键/文档化启动方式（后端、MySQL、Redis、管理后台、小程序开发者工具指向本地 API），无需公网域名即可完成功能验收。

---

## 13. 下一步

1. ~~需求确认~~（已完成）  
2. 已同步生成 `specs/design.md`、`specs/tasks.md`  
3. **你明确回复「开始执行」后**，才开始改代码实现  

当前仓库几乎为空（仅有设计文档与 specs），实现阶段将从零搭建 `miniprogram/`、`backend/`、`admin/` 工程。
