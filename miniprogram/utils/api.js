const { baseURL, uploadURL, origin } = require("./config");

const MEDIA_KEYS = {
  cover_image: true,
  image_url: true,
  avatar: true,
  url: true,
};

function getToken() {
  return wx.getStorageSync("token") || "";
}

/**
 * 把历史入库的本机/局域网/旧隧道图片地址，改写成当前 config.origin
 * 否则开发者工具能显示，真机（尤其 4G）加载失败
 */
function fixMediaUrl(url) {
  if (!url || typeof url !== "string") return url;
  if (url.startsWith("/uploads/")) {
    return `${origin}${url}`;
  }
  const m = url.match(/^(https?:\/\/[^/]+)(\/uploads\/.+)$/i);
  if (m) {
    return `${origin}${m[2]}`;
  }
  return url;
}

function fixMediaInData(data) {
  if (data == null) return data;
  if (typeof data === "string") return data;
  if (Array.isArray(data)) return data.map(fixMediaInData);
  if (typeof data === "object") {
    const out = {};
    Object.keys(data).forEach((k) => {
      const v = data[k];
      if (MEDIA_KEYS[k] && typeof v === "string") {
        out[k] = fixMediaUrl(v);
      } else {
        out[k] = fixMediaInData(v);
      }
    });
    return out;
  }
  return data;
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
        resolve(fixMediaInData(body.data));
      },
      fail(err) {
        const msg = (err && err.errMsg) || "网络错误";
        // 体验版/正式版常见：未配置 request 合法域名
        if (/url not in domain list|不在.*合法域名|domain list/i.test(msg)) {
          reject(
            new Error(
              "接口域名未配置到微信后台「服务器域名」。体验版会强制校验，真机调试不校验。"
            )
          );
          return;
        }
        reject(new Error(msg));
      },
    });
  });
}

/** 上传本地图片，返回可访问的 url（并改写为当前 origin） */
function uploadImage(filePath) {
  return new Promise((resolve, reject) => {
    const token = getToken();
    if (!token) {
      reject(new Error("请先登录"));
      return;
    }
    wx.uploadFile({
      url: uploadURL,
      filePath,
      name: "file",
      header: { Authorization: `Bearer ${token}` },
      success(res) {
        let body = res.data;
        try {
          body = typeof body === "string" ? JSON.parse(body) : body;
        } catch (e) {
          reject(new Error("上传响应解析失败"));
          return;
        }
        if (res.statusCode >= 400 || !body || body.code !== 0) {
          reject(new Error((body && body.message) || "上传失败"));
          return;
        }
        resolve(fixMediaUrl(body.data.url));
      },
      fail(err) {
        reject(new Error(err.errMsg || "上传失败"));
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
    throw e;
  }
}

module.exports = {
  request,
  uploadImage,
  formatPrice,
  ensureLogin,
  getToken,
  fixMediaUrl,
};
