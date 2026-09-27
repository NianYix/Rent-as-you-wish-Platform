/**
 * API 地址配置
 *
 * MODE:
 * - local  仅电脑模拟器
 * - lan    同一 WiFi 真机
 * - public 固定域名 api.kinih.xyz（Cloudflare 命名隧道）
 */
const MODE = "public"; // lan | local | public

const HOSTS = {
  local: "http://127.0.0.1:8000",
  lan: "http://192.168.2.145:8000",
  // 命名隧道固定域名（需 cloudflared tunnel run + Cloudflare DNS）
  public: "https://api.kinih.xyz",
};

const origin = HOSTS[MODE] || HOSTS.lan;

const config = {
  mode: MODE,
  origin,
  baseURL: `${origin}/api/v1`,
  uploadURL: `${origin}/api/v1/uploads`,
};

module.exports = config;
