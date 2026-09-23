const { request, formatPrice, ensureLogin } = require("../../utils/api");

Page({
  data: { items: [] },
  onShow() {
    this.load();
  },
  async load() {
    await ensureLogin();
    const data = await request({ url: "/merchants/me/products", auth: true });
    this.setData({ items: data.items || [] });
  },
  async offline(e) {
    const id = e.currentTarget.dataset.id;
    await request({ url: `/merchants/me/products/${id}/offline`, method: "POST", auth: true });
    this.load();
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
