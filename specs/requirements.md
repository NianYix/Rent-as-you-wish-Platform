# README 项目说明文档 — 需求规格说明

> 任务：完善仓库根目录 `README.md`，使其完整说明产品功能、技术栈、目录结构与使用方法  
> 依据：当前已实现代码、既有 `docs/` 文档与 MVP 设计结论  
> 语法：EARS（WHEN / IF / WHERE / THE SYSTEM SHALL）  
> 范围：仅文档更新，不改业务代码

---

## 1. 文档信息

| 项 | 内容 |
|---|---|
| 目标产物 | 仓库根目录 `README.md` |
| 读者 | 新加入的开发者、本地联调人员、后续部署/提审人员 |
| 原则 | 准确反映当前仓库已实现能力；细节步骤可链接到 `docs/`，README 本身须可独立读懂「是什么 / 用什么 / 怎么跑」 |
| 明确不做 | 重写业务代码；删除或覆盖 `docs/` 中的专项文档；编造未实现功能 |

---

## 2. 功能说明

### REQ-README-FEAT-001
THE SYSTEM SHALL 在 `README.md` 中概述产品定位：面向乡镇的本地物品租赁信息平台（商家发布 → 用户浏览/搜索 → 联系商家）。

### REQ-README-FEAT-002
THE SYSTEM SHALL 按端（微信小程序用户侧、商家侧、Web 管理后台、后端能力）分条列出已实现功能，至少覆盖：

- 用户：微信/开发登录、首页（地区/Banner/分类/热门）、分类浏览、搜索、商品详情、商家详情、电话/微信联系、收藏、浏览记录、用户协议与隐私政策
- 商家：入驻申请、商家中心、商品发布/编辑/上下架
- 管理后台：登录、数据概览、用户/商家/商品审核与管理、分类、地区、Banner
- 后端：JWT 鉴权、REST API、本地/可扩展对象存储、种子数据、健康检查与 OpenAPI 文档

### REQ-README-FEAT-003
THE SYSTEM SHALL 明确写出 MVP 范围边界：已实现上述信息撮合闭环；**未做**支付、订单履约、即时通讯、会员/广告、复杂 AI 推荐。

---

## 3. 技术栈说明

### REQ-README-TECH-001
THE SYSTEM SHALL 在 `README.md` 中列出各端技术栈，并与仓库实际依赖一致，至少包含：

| 端 | 技术 |
|---|---|
| 小程序 | 微信原生小程序 |
| 后端 | Python 3.12+、FastAPI、SQLAlchemy、Pydantic、JWT（python-jose）、Passlib |
| 数据 | 本地默认 SQLite；可选 MySQL 8 + Redis 7（Docker Compose） |
| 存储 | 本地磁盘上传（可扩展 COS/OSS） |
| 管理后台 | Vue 3、TypeScript、Vite、Element Plus、Pinia、Vue Router、Axios |
| 编排/辅助 | Docker Compose、`start.bat`、Cloudflare Tunnel 脚本（可选） |

### REQ-README-TECH-002
IF 技术栈条目无法从仓库依赖或配置直接确认 THEN THE SYSTEM SHALL 不写入该条目，或标注为「规划/可选」而非已使用。

---

## 4. 目录结构说明

### REQ-README-DIR-001
THE SYSTEM SHALL 在 `README.md` 中提供顶层目录树（或等价列表），至少说明：

```text
miniprogram/   微信小程序
backend/       FastAPI 后端
admin/         Vue 管理后台
docs/          开发/部署/上架专项文档
specs/         需求/设计/任务规格
scripts/       辅助脚本（如 Cloudflare Tunnel）
docker-compose.yml
start.bat
.env.example
```

### REQ-README-DIR-002
THE SYSTEM SHALL 对各主要目录补充 1～2 级关键子目录说明（如 `backend/app/{api,core,models,schemas,services}`、`miniprogram/pages/`、`admin/src/views/`），帮助读者快速定位代码，但不要求罗列每一个文件。

---

## 5. 使用方法说明

### REQ-README-USE-001
THE SYSTEM SHALL 在 `README.md` 中给出本地快速启动步骤，覆盖：环境前置条件、配置 `.env`、启动后端、启动管理后台、导入小程序、可选 Docker（MySQL/Redis）。

### REQ-README-USE-002
THE SYSTEM SHALL 说明可使用仓库根目录 `start.bat`（Windows）一键拉起后端与管理后台，并指引用微信开发者工具打开 `miniprogram/`。

### REQ-README-USE-003
THE SYSTEM SHALL 给出默认管理员账号说明（与种子数据一致：`admin` / `Admin@123456`，并提示可通过环境变量覆盖），以及验证入口（API Docs、Admin 地址、Health）。

### REQ-README-USE-004
THE SYSTEM SHALL 链接到专项文档，避免 README 过长重复：

- 本地开发细节 → `docs/local-dev.md`
- 服务器部署提纲 → `docs/deploy.md`
- 微信注册与提审 → `docs/wechat-publish.md`
- 公网隧道（可选）→ `docs/cloudflare-tunnel.md`

### REQ-README-USE-005
WHEN 描述真机预览或公网联调 THE SYSTEM SHALL 仅作摘要说明，并指向 `docs/local-dev.md` / `docs/cloudflare-tunnel.md` 的完整步骤。

---

## 6. 文档质量与约束

### REQ-README-QLT-001
THE SYSTEM SHALL 使用简体中文撰写 `README.md`，结构清晰，含标题层级，便于扫读。

### REQ-README-QLT-002
THE SYSTEM SHALL 以当前仓库实际实现为准更新内容；若与旧 README 冲突，以代码与 `docs/` 为准覆盖更新。

### REQ-README-QLT-003
THE SYSTEM SHALL 不在 README 中提交真实密钥、生产密码或私有 IP 作为唯一示例；示例可使用 `.env.example` 中的占位/默认值，并提示修改。

### REQ-README-QLT-004
WHERE 已有 `specs/design.md`、`specs/tasks.md` 等 MVP 实现规格 THE SYSTEM SHALL 保留其历史价值；本次任务仅新增/改写面向「README 文档」的 specs，执行阶段只修改 `README.md`（及必要时微调 specs 文件本身），不借机改业务代码。

---

## 7. 验收标准

1. `README.md` 至少包含四块：**功能**、**技术栈**、**目录结构**、**如何使用**。  
2. 功能列表与当前小程序页面、管理后台路由、后端能力大致一致，且标明未做范围。  
3. 按 README 步骤可在本机完成：后端可访问 `/docs`、管理后台可登录、小程序可指向本地 API（细节可再读 `docs/local-dev.md`）。  
4. 未引入无关业务代码变更。

---

## 8. 下一步

1. **请确认本需求**（可直接回复「确认」或提出修改意见）  
2. 确认后生成 `specs/design.md`（README 内容结构与信息来源）  
3. 再生成 `specs/tasks.md`  
4. **你明确回复「开始执行」后**，才更新根目录 `README.md`
