# README 同步后续更新 — 设计说明

> 依据：`specs/requirements.md`（已确认）  
> 目标：在现有 README 四块骨架上增补后续能力，不推倒重写

---

## 1. 变更策略

| 策略 | 说明 |
|---|---|
| 增量更新 | 保留简介、功能、技术、目录、使用、更多文档结构 |
| 功能块 | 用户端/商家端各补 1～2 条；可加「联调与体验」小节或并入使用说明 |
| 使用块 | 扩展真机/公网/体验版路径；`start.bat` 行为与隧道脚本 |
| 目录块 | `scripts/` 说明写清临时隧道 vs 命名隧道/kinih |
| 文档表 | 新增 `docs/kinih-cloudflare.md` |

不修改业务代码与 `docs/` 正文（除非发现死链）。

---

## 2. README 增补点映射

### 2.1 功能说明

**商家端追加：**

- 发品选图：拍照 / 相册（`utils/media.js`）
- 上传前隐私同意弹窗（`components/privacy-popup`）
- 调试期 `app.json` 中 `__usePrivacyCheck__` 可为 `false`；提审前需配置隐私指引并改回 `true`（细节外链 wechat-publish）

**用户端或通用追加：**

- 接口返回的图片地址会按当前 `config.origin` 改写，避免旧局域网/旧隧道域名在真机失效

### 2.2 技术栈 / 辅助

辅助行已含 Cloudflare Tunnel；可注明支持临时隧道与命名隧道（固定域名如 `api.kinih.xyz`）。

### 2.3 目录结构

`scripts/` 注释扩展为：

```text
scripts/
  start-cloudflare-tunnel.*   # 临时公网隧道（URL 易变，自动写配置）
  setup-kinih-tunnel.bat      # 一次性配置命名隧道 → api.kinih.xyz
  start-named-tunnel.bat      # 日常启动命名隧道
```

（若某文件尚未入库，以仓库实际存在文件为准写入。）

### 2.4 如何使用

在「真机预览 / 公网联调」扩展为清晰三档：

| 场景 | 做法 |
|---|---|
| 模拟器 | `MODE=local`，`127.0.0.1` |
| 同 WiFi 真机 | `MODE=lan` + 电脑局域网 IP |
| 4G / 公网调试 | 临时隧道脚本，或命名隧道固定域名 |
| 体验版 | HTTPS 固定域名 + 微信后台合法域名；勿用 `*.trycloudflare.com` |

`start.bat`：启动后端与管理后台；若已安装 `cloudflared` 且存在命名隧道配置，会尝试启动 `api.kinih.xyz` 隧道。

`PUBLIC_BASE_URL` 需与公网 API 一致（图片外链依赖），改后需重启后端。

### 2.5 更多文档

增加一行：`docs/kinih-cloudflare.md` — kinih.xyz 命名隧道与体验版域名。

---

## 3. 信息来源

| 内容 | 来源 |
|---|---|
| 隐私选图 | `media.js`、`privacy-popup`、`wechat-publish.md` §八 |
| 媒体 URL 改写 | `miniprogram/utils/api.js` `fixMediaUrl` |
| 临时隧道 | `docs/cloudflare-tunnel.md`、`scripts/start-cloudflare-tunnel.*` |
| 命名隧道 / kinih | `docs/kinih-cloudflare.md`、`start.bat`、`scripts/setup-kinih-tunnel.bat` |
| MODE | `miniprogram/utils/config.js` |

---

## 4. 文风约束

- 简体中文，增量段落简洁  
- 固定域名示例可用 `https://api.kinih.xyz`，并注明可按实际域名替换  
- 不把临时 `trycloudflare.com` URL 写成正式唯一配置  
- 本机 `cloudflared` 绝对路径不必写入 README（避免环境绑定）

---

## 5. 下一步

生成 `tasks.md` → 用户回复「开始执行」后改 `README.md`
