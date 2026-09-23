const { baseURL } = require("./config");

function getToken() {
  return wx.getStorageSync("token") || "";
}

function request({ url, method = "GET", data = {}, auth = false }) {
  return new Promise((resolve, reject) => {
    const header = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) header.Authorization = `Bearer ${token}`;
    if (auth && !token) {
      reject(new Error("请先登录"));
      return;
    }
    wx.request({
      url: `${baseURL}${url}`,
      method,
      data,
      header,
      success(res) {
        const body = res.data || {};
        if (res.statusCode === 401 || body.code === 401) {
          wx.removeStorageSync("token");
          reject(new Error(body.message || "请先登录"));
          return;
        }
        if (res.statusCode >= 400 || body.code !== 0) {
          reject(new Error(body.message || "请求失败"));
          return;
        }
        resolve(body.data);
      },
      fail(err) {
        reject(new Error(err.errMsg || "网络错误"));
      },
    });
  });
}

function formatPrice(item) {
  if (!item) return "";
  if (item.price_unit === "NEGOTIABLE") return "面议";
  const unitMap = {
    HOUR: "小时",
    DAY: "天",
    TIME: "次",
    MONTH: "月",
    CUSTOM: item.price_unit_custom || "",
  };
  const unit = unitMap[item.price_unit] || "";
  if (item.price == null) return unit || "面议";
  return `¥${item.price}${unit ? " / " + unit : ""}`;
}

async function ensureLogin() {
  let token = getToken();
  if (token) return token;
  // 本地开发：无 AppID 时走开发登录
  try {
    const data = await request({
      url: "/auth/dev/login",
      method: "POST",
      data: { openid: "mp_dev_user", nickname: "小程序用户" },
    });
    wx.setStorageSync("token", data.access_token);
    wx.setStorageSync("role", data.role);
    wx.setStorageSync("user_id", data.user_id);
    return data.access_token;
  } catch (e) {
    // 若已配置微信，可改为 wx.login + /auth/wechat/login
    throw e;
  }
}

module.exports = {
  request,
  formatPrice,
  ensureLogin,
  getToken,
};
