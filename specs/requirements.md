# README 同步后续更新 — 需求规格说明

> 任务：将「更新版本功能」及之后的改动同步写入根目录 `README.md`  
> 依据：当前代码、`docs/`、未提交变更与既有 README  
> 语法：EARS（WHEN / IF / WHERE / THE SYSTEM SHALL）  
> 范围：仅文档更新，不改业务代码

---

## 1. 文档信息

| 项 | 内容 |
|---|---|
| 目标产物 | 仓库根目录 `README.md`（在现有四块基础上增补） |
| 读者 | 本地联调、真机预览、体验版/公网调试人员 |
| 原则 | 准确反映后续已落地能力；细节外链 `docs/`；不把易变临时隧道 URL 写成唯一正式配置 |
| 明确不做 | 改业务代码；删除既有功能/技术/目录/使用四大块骨架 |

---

## 2. 需同步进 README 的后续能力

### REQ-UPD-FEAT-001
THE SYSTEM SHALL 在功能说明中补充商家发品相关后续能力：选图（拍照/相册）、上传前隐私同意弹窗（`privacy-popup`）、以及开发阶段 `__usePrivacyCheck__` 说明（调试可关，提审前需开并配置隐私指引）。

### REQ-UPD-FEAT-002
THE SYSTEM SHALL 在功能或使用说明中补充：小程序端会将历史入库的图片地址按当前 `config.origin` 改写，避免真机（尤其 4G）因旧局域网/旧隧道域名加载失败。

### REQ-UPD-FEAT-003
THE SYSTEM SHALL 在使用说明中补充公网联调能力：

- 临时隧道：`scripts/start-cloudflare-tunnel.bat`（自动写 `config.js` / `PUBLIC_BASE_URL`）
- 命名隧道 / 体验版固定域名：`api.kinih.xyz`（见 `docs/kinih-cloudflare.md`）
- `start.bat` 在已配置 `cloudflared` 与命名隧道时会一并拉起隧道

### REQ-UPD-FEAT-004
THE SYSTEM SHALL 在「更多文档」中增加 `docs/kinih-cloudflare.md` 链接，并保留 `docs/cloudflare-tunnel.md`。

### REQ-UPD-DIR-001
THE SYSTEM SHALL 在目录结构中体现后续脚本：`scripts/setup-kinih-tunnel.bat`、`start-named-tunnel.bat`、`start-cloudflare-tunnel.*` 等（可概括说明，不必逐文件堆砌）。

### REQ-UPD-USE-001
THE SYSTEM SHALL 更新「如何使用」：说明 `config.js` 的 `MODE`（`local` / `lan` / `public`）；体验版需 HTTPS + 微信后台合法域名；临时隧道仅适合调试、体验版应用固定域名。

### REQ-UPD-USE-002
THE SYSTEM SHALL 提示生产/体验前：域名 ICP 备案要求（摘要 + 外链），以及将协议文案替换为法务版本后再提审（摘要 + 外链 wechat-publish）。

### REQ-UPD-QLT-001
IF 示例需写公网地址 THEN THE SYSTEM SHALL 使用文档化的固定域名示例（如 `https://api.kinih.xyz`），并注明需按实际域名修改；不得把 `*.trycloudflare.com` 临时地址写成唯一正式配置。

### REQ-UPD-QLT-002
THE SYSTEM SHALL 仅修改 `README.md`（及必要时更新本任务相关 specs）；不借机改业务代码。

---

## 3. 验收标准

1. README 仍含功能、技术、目录、使用四块，并覆盖上述后续更新要点。  
2. 读者能从 README 知道：隐私选图、媒体 URL 改写、临时隧道 vs 命名隧道/`kinih`、体验版域名注意。  
3. 「更多文档」含 kinih 与 cloudflare 两份专项文档链接。  
4. 无业务代码变更。

---

## 4. 下一步

1. **请确认本需求**（回复「确认」或提出修改）  
2. 确认后生成 `specs/design.md`、`specs/tasks.md`  
3. **你明确回复「开始执行」后**，才更新 `README.md`
