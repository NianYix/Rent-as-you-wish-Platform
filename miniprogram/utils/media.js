/**
 * 选图工具
 *
 * 说明：开发/真机调试阶段 app.json 中 __usePrivacyCheck__ 为 false，
 * 否则在公众平台未配置「隐私指引」时，相册/相机接口会被微信直接拦截。
 * 上线前请配置隐私指引后改回 true。
 */

function hasLocalAgree() {
  return !!wx.getStorageSync("privacy_image_agreed");
}

function setLocalAgree() {
  wx.setStorageSync("privacy_image_agreed", 1);
}

/**
 * 主动弹出页面隐私框（产品层同意；不等于系统相册权限）
 */
async function ensurePrivacyAuthorized(page) {
  if (hasLocalAgree()) return true;

  if (page && typeof page.selectComponent === "function") {
    const comp = page.selectComponent("#privacyPopup");
    if (comp && typeof comp.open === "function") {
      const ok = await comp.open();
      if (ok) setLocalAgree();
      return !!ok;
    }
  }
  // 无弹窗组件时，不阻断选图（调试兼容）
  setLocalAgree();
  return true;
}

function showSourceSheet() {
  return new Promise((resolve) => {
    wx.showActionSheet({
      itemList: ["拍照", "从相册选择"],
      success: (res) => {
        resolve(res.tapIndex === 0 ? "camera" : "album");
      },
      fail: () => resolve(""),
    });
  });
}

function authorizeCamera() {
  return new Promise((resolve) => {
    wx.getSetting({
      success: (setting) => {
        if (setting.authSetting && setting.authSetting["scope.camera"]) {
          resolve(true);
          return;
        }
        wx.authorize({
          scope: "scope.camera",
          success: () => resolve(true),
          fail: () => {
            wx.showModal({
              title: "需要相机权限",
              content: "请在设置中允许微信使用相机，以便拍摄商品照片",
              confirmText: "去设置",
              success: (r) => {
                if (r.confirm) {
                  wx.openSetting({
                    success: (s) =>
                      resolve(!!(s.authSetting && s.authSetting["scope.camera"])),
                    fail: () => resolve(false),
                  });
                } else {
                  resolve(false);
                }
              },
            });
          },
        });
      },
      fail: () => resolve(true),
    });
  });
}

function chooseBySource(count, source) {
  const sourceType = source === "camera" ? ["camera"] : ["album"];
  return new Promise((resolve, reject) => {
    // 优先 chooseMedia
    if (wx.chooseMedia) {
      wx.chooseMedia({
        count: source === "camera" ? 1 : count,
        mediaType: ["image"],
        sourceType,
        sizeType: ["compressed"],
        success: (res) => {
          const paths = (res.tempFiles || [])
            .map((f) => f.tempFilePath)
            .filter(Boolean);
          resolve(paths);
        },
        fail: (err) => {
          // 回退 chooseImage
          wx.chooseImage({
            count: source === "camera" ? 1 : count,
            sizeType: ["compressed"],
            sourceType,
            success: (res) => resolve(res.tempFilePaths || []),
            fail: (err2) => reject(err2 || err),
          });
        },
      });
      return;
    }
    wx.chooseImage({
      count: source === "camera" ? 1 : count,
      sizeType: ["compressed"],
      sourceType,
      success: (res) => resolve(res.tempFilePaths || []),
      fail: (err) => reject(err),
    });
  });
}

function formatPickError(err) {
  const msg = (err && (err.errMsg || err.message)) || "";
  const errno = err && err.errno;
  if (/auth deny|authorize|permission|隐私|privacy/i.test(msg)) {
    return "没有相册/相机权限。请在手机系统设置 → 微信 → 允许相册和相机。";
  }
  if (/cancel/i.test(msg)) return "";
  return (msg || "调起相册/相机失败") + (errno != null ? ` (${errno})` : "");
}

/**
 * @param {number} count
 * @param {*} page
 * @returns {Promise<string[]>}
 */
async function pickImages(count, page) {
  const ok = await ensurePrivacyAuthorized(page);
  if (!ok) {
    const err = new Error("请先同意后再上传图片");
    err.code = "PRIVACY_DENY";
    throw err;
  }

  const source = await showSourceSheet();
  if (!source) return [];

  if (source === "camera") {
    const camOk = await authorizeCamera();
    if (!camOk) {
      const err = new Error("未获得相机权限");
      err.code = "CAMERA_DENY";
      throw err;
    }
  }

  try {
    return await chooseBySource(count, source);
  } catch (e) {
    const tip = formatPickError(e);
    if (!tip) return [];
    const err = new Error(tip);
    err.raw = e;
    throw err;
  }
}

module.exports = {
  pickImages,
  ensurePrivacyAuthorized,
  hasLocalAgree,
  setLocalAgree,
};
