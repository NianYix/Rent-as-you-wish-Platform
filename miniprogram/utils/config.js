// 本地开发请勾选「不校验合法域名」
// 上线前改成 https://api.your-domain.com
const config = {
  baseURL: "http://127.0.0.1:8000/api/v1",
  uploadURL: "http://127.0.0.1:8000/api/v1/uploads",
};

module.exports = config;
