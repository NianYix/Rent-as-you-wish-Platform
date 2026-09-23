const { request, formatPrice, ensureLogin } = require("../../utils/api");

Page({
  data: { items: [] },
  onShow() {
    this.load();
  },
  async load() {
    await ensureLogin();
    const items = await request({ url: "/browse-history", auth: true });
    this.setData({ items: items || [] });
  },
  go(e) {
    wx.navigateTo({ url: `/pages/product/detail?id=${e.currentTarget.dataset.id}` });
  },
  formatPrice,
});
