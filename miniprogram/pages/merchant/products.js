const { request, formatPrice, ensureLogin } = require("../../utils/api");

Page({
  data: { items: [], loading: false },
  onShow() {
    this.load();
  },
  async load() {
    this.setData({ loading: true });
    try {
      await ensureLogin();
      const data = await request({ url: "/merchants/me/products", auth: true });
      this.setData({ items: data.items || [] });
    } catch (e) {
      this.setData({ items: [] });
      wx.showToast({ title: e.message || "加载失败", icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  },
  async offline(e) {
    const id = e.currentTarget.dataset.id;
    try {
      await request({ url: `/merchants/me/products/${id}/offline`, method: "POST", auth: true });
      this.load();
    } catch (err) {
      wx.showToast({ title: err.message, icon: "none" });
    }
  },
  async online(e) {
    const id = e.currentTarget.dataset.id;
    try {
      await request({ url: `/merchants/me/products/${id}/online`, method: "POST", auth: true });
      this.load();
    } catch (err) {
      wx.showToast({ title: err.message, icon: "none" });
    }
  },
  edit(e) {
    wx.navigateTo({ url: `/pages/merchant/product-edit?id=${e.currentTarget.dataset.id}` });
  },
  formatPrice,
});
