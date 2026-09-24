App({
  globalData: {
    region: null,
    openPrivacyPopup: null,
  },
  onLaunch() {
    const region = wx.getStorageSync("selectedRegion");
    if (region) this.globalData.region = region;

    // 仅在微信需要授权时弹出一次；用户点「同意」后由官方记录，不再反复弹
    if (wx.onNeedPrivacyAuthorization) {
      wx.onNeedPrivacyAuthorization((resolve) => {
        if (typeof this.globalData.openPrivacyPopup === "function") {
          this.globalData.openPrivacyPopup(resolve);
        } else {
          // 页面尚未挂载组件时的兜底：等下一帧再试
          setTimeout(() => {
            if (typeof this.globalData.openPrivacyPopup === "function") {
              this.globalData.openPrivacyPopup(resolve);
            } else {
              resolve({ event: "disagree" });
            }
          }, 300);
        }
      });
    }
  },
});
