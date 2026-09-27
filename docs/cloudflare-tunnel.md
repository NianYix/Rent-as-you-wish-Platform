# Cloudflare Tunnel 公网调试

本机已安装 `cloudflared`（`E:\JerrySoftware\cloudflared\cloudflared.exe`）。

## 方式 A：临时隧道（最快，URL 每次会变，自动写配置）

1. 先启动后端（`start.bat` 或保证 `http://127.0.0.1:8000/health` 正常）
2. 双击或运行：

```bat
scripts\start-cloudflare-tunnel.bat
```

脚本会：

- 启动 `cloudflared tunnel --url http://127.0.0.1:8000`
- **自动**把公网地址写入 `miniprogram/utils/config.js` 的 `HOSTS.public`
- **自动**设置 `MODE = "public"`
- **自动**同步 `backend/.env` 与根目录 `.env` 的 `PUBLIC_BASE_URL`

3. 微信开发者工具 **重新编译**；建议重启后端使图片域名生效  
4. 预览真机（可用 4G）；**隧道窗口不要关**

> 若出现 `api.trycloudflare.com ... timeout`，说明访问 Cloudflare 临时隧道 API 被网络限制，请改用方式 B。

## 方式 B：命名隧道（推荐，固定域名）

适合你已有 Cloudflare 账号 / 域名。

```bat
cloudflared tunnel login
cloudflared tunnel create rent-api
cloudflared tunnel route dns rent-api api.你的域名.com
```

创建配置文件 `%USERPROFILE%\.cloudflared\config.yml`：

```yaml
tunnel: <TUNNEL_ID>
credentials-file: C:\Users\Jerry\.cloudflared\<TUNNEL_ID>.json

ingress:
  - hostname: api.你的域名.com
    service: http://127.0.0.1:8000
  - service: http_status:404
```

启动：

```bat
cloudflared tunnel run rent-api
```

然后：

```js
// miniprogram/utils/config.js
const MODE = "public";
HOSTS.public = "https://api.你的域名.com";
```

```env
PUBLIC_BASE_URL=https://api.你的域名.com
```

## 小程序注意

- 开发预览：详情 → 本地设置 → **不校验合法域名**
- 正式版：必须把该 HTTPS 域名配进微信公众平台 request / uploadFile 合法域名
- 隧道窗口不能关，关了公网就断

## 切换回局域网

```js
const MODE = "lan";
```
