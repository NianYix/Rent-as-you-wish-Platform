# kinih.xyz + Cloudflare 命名隧道（体验版可用）

域名：`kinih.xyz`  
API：`https://api.kinih.xyz` → 本机 `http://127.0.0.1:8000`

## 前置条件

1. 域名 `kinih.xyz` 的 **DNS 已接入 Cloudflare**（Nameserver 已改成 Cloudflare 的）  
2. 本机已装 `cloudflared`  
3. 后端可用：`http://127.0.0.1:8000/health`

## 一次性配置

双击：

```bat
scripts\setup-kinih-tunnel.bat
```

会依次：

1. `cloudflared tunnel login`（浏览器授权你的 Cloudflare 账号）  
2. `tunnel create rent-api`  
3. `tunnel route dns rent-api api.kinih.xyz`（自动加 CNAME）  
4. 生成 `%USERPROFILE%\.cloudflared\config.yml`

## 日常启动

1. `start.bat`（后端）  
2. `scripts\start-named-tunnel.bat`（隧道，不要关）  
3. 浏览器打开：https://api.kinih.xyz/health 应返回 ok  

小程序 `config.js` 已指向：

```text
https://api.kinih.xyz
```

请同步把 `backend/.env` 的 `PUBLIC_BASE_URL` 设为同一地址，并**重启后端**。

## 微信公众平台（体验版必做）

开发管理 → 开发设置 → 服务器域名（不要加 `https://`）：

- request 合法域名：`api.kinih.xyz`  
- uploadFile 合法域名：`api.kinih.xyz`  
- downloadFile 合法域名：`api.kinih.xyz`  

然后重新上传小程序 → 设为体验版。

### 关于备案

国内微信小程序配置服务器域名，通常要求域名已 **ICP 备案**。  
若后台提示域名未备案/校验失败，需要先给 `kinih.xyz` 备案（或换已备案域名），否则体验版仍可能拦截。

## 不要用临时隧道做体验版

`*.trycloudflare.com` 只适合真机调试；体验版请固定用 `api.kinih.xyz`。
