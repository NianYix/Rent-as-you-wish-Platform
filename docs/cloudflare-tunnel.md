# Cloudflare Tunnel 公网调试

本机已安装 `cloudflared`（`E:\JerrySoftware\cloudflared\cloudflared.exe`）。

## 方式 A：临时隧道（最快，URL 每次会变）

1. 先启动后端（`start.bat` 或保证 `http://127.0.0.1:8000/health` 正常）
2. 运行：

```bat
scripts\start-cloudflare-tunnel.bat
```

或自动改配置：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start-cloudflare-tunnel.ps1
```

成功后日志里会出现：

```text
https://xxxx.trycloudflare.com
```

3. 把该地址写入：

- `miniprogram/utils/config.js` → `MODE: "public"`，`HOSTS.public`
- `backend/.env` → `PUBLIC_BASE_URL`（图片 URL 用）

4. **重启后端**（让 `PUBLIC_BASE_URL` 生效）
5. 微信开发者工具 **编译**，勾选不校验合法域名，再预览真机（可用 4G）

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
