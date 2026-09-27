# README 同步后续更新 — 任务分解

> 依据：`specs/requirements.md`、`specs/design.md`  
> 执行闸门：仅在用户明确回复「开始执行」后修改 `README.md`

---

## 任务列表

### T1 — 功能说明增补
- [x] 商家端：选图、隐私弹窗、`__usePrivacyCheck__` 提审注意（外链）
- [x] 通用：媒体 URL 按当前 origin 改写
- [x] 验收：与 media / privacy-popup / api.js 一致

### T2 — 目录与辅助说明
- [x] 更新 `scripts/` 目录说明（临时隧道 / kinih 命名隧道相关脚本）
- [x] 技术栈辅助行可点明临时 + 命名隧道
- [x] 验收：路径与仓库实际文件一致

### T3 — 如何使用增补
- [x] 三档联调：local / lan / public（临时或命名）
- [x] `start.bat` 可拉命名隧道的行为说明
- [x] 体验版：合法域名、备案摘要、勿用临时隧道
- [x] `PUBLIC_BASE_URL` 与重启后端提示
- [x] 验收：读者能区分调试 vs 体验版路径

### T4 — 更多文档
- [x] 增加 `docs/kinih-cloudflare.md` 链接
- [x] 验收：链接可点、表格完整

### T5 — 通读验收
- [x] 对照 requirements 验收标准
- [x] 确认仅改 README（及本任务 specs 状态），无业务代码变更

---

## 执行顺序

`T1 → T2 → T3 → T4 → T5`（可同一次编辑完成）

## 状态

| 阶段 | 状态 |
|---|---|
| requirements | 已确认 |
| design | 已完成 |
| tasks | 已完成（待执行） |
| 更新 README | **已完成** |
