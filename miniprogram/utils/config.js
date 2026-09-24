/**
 * API 地址配置
 *
 * MODE:
 * - local  仅电脑模拟器
 * - lan    同一 WiFi 真机
 * - public Cloudflare 隧道 / 云服务器（当前已切公网调试）
 */
const MODE = "public"; // lan | local | public

const HOSTS = {
  local: "http://127.0.0.1:8000",
  lan: "http://192.168.2.145:8000",
  // 临时隧道每次启动会变；关隧道后需重跑 scripts/start-cloudflare-tunnel.bat
  public: "https://stopping-sql-definition-slides.trycloudflare.com",
};

const origin = HOSTS[MODE] || HOSTS.lan;

const config = {
  mode: MODE,
  origin,
  baseURL: `${origin}/api/v1`,
  uploadURL: `${origin}/api/v1/uploads`,
};

module.exports = config;
