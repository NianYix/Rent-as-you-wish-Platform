const { request, formatPrice, ensureLogin } = require("../../utils/api");

Page({
  data: { profile: null },
  onShow() {
    this.load();
  },
  async load() {
    try {
      await ensureLogin();
      const profile = await request({ url: "/users/me", auth: true });
      this.setData({ profile });
    } catch (e) {
      this.setData({ profile: null });
    }
  },
  async login() {
    try {
      await ensureLogin();
      this.load();
      wx.showToast({ title: "登录成功" });
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
    }
  },
  go(e) {
    wx.navigateTo({ url: e.currentTarget.dataset.url });
  },
});
