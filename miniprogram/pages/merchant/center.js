const { request, ensureLogin } = require("../../utils/api");

Page({
  data: { merchant: null },
  onShow() {
    this.load();
  },
  async load() {
    try {
      await ensureLogin();
      const merchant = await request({ url: "/merchants/me", auth: true });
      this.setData({ merchant });
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
    }
  },
  goApply() {
    wx.navigateTo({ url: "/pages/merchant/apply" });
  },
  goProducts() {
    wx.navigateTo({ url: "/pages/merchant/products" });
  },
  goEdit() {
    wx.navigateTo({ url: "/pages/merchant/product-edit" });
  },
});
