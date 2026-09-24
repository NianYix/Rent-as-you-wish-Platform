# README 项目说明文档 — 任务分解

> 依据：`specs/requirements.md`、`specs/design.md`  
> 执行闸门：仅在用户明确回复「开始执行」后，才修改 `README.md`

---

## 任务列表

### T1 — 起草 README 骨架与简介
- [x] 写入标题、产品定位、MVP 核心闭环一句话说明
- [x] 验收：开篇即可理解「这是什么产品」

### T2 — 编写功能说明
- [x] 按用户端 / 商家端 / 管理后台 / 后端分节列出已实现功能
- [x] 增加「范围边界」：已实现 vs 未做（支付、订单、IM、会员、AI）
- [x] 验收：与 `app.json` pages、admin 路由、后端能力大致一致

### T3 — 编写技术栈说明
- [x] 用表格或列表列出小程序、后端、数据、存储、管理后台、辅助工具
- [x] 验收：与 `requirements.txt`、`package.json`、`docker-compose.yml` 一致

### T4 — 编写目录结构说明
- [x] 按 design 中的目录树写入顶层 + 关键子目录说明
- [x] 验收：路径在仓库中真实存在

### T5 — 编写如何使用
- [x] 前置条件、`.env` 配置、`start.bat` 一键启动、手动分步启动摘要
- [x] 默认管理员、验证入口（docs / admin / health）
- [x] 可选 Docker、真机/公网一句话 + 外链
- [x] 链接：`docs/local-dev.md`、`deploy.md`、`wechat-publish.md`、`cloudflare-tunnel.md`
- [x] 验收：读者可不翻源码完成本地启动路径扫读

### T6 — 通读与收尾
- [x] 对照 requirements 验收标准逐条检查
- [x] 确认无业务代码变更、无真实密钥/临时隧道域名作为唯一正式配置
- [x] 验收：四块齐全（功能、技术、目录、使用），中文清晰

---

## 执行顺序

`T1 → T2 → T3 → T4 → T5 → T6`（可在同一次编辑中合并完成，但验收按上表）

## 变更文件

- 预期修改：`README.md`
- 不修改：业务代码、`docs/*`（除非发现死链需极小修正）

---

## 状态

| 阶段 | 状态 |
|---|---|
| requirements | 已确认 |
| design | 已完成 |
| tasks | 已完成（待执行） |
| 更新 README | **已完成** |
