const { request, formatPrice, ensureLogin } = require("../../utils/api");

Page({
  data: { items: [] },
  onShow() {
    this.load();
  },
  async load() {
    await ensureLogin();
    const items = await request({ url: "/favorites", auth: true });
    this.setData({ items: items || [] });
  },
  go(e) {
    const item = e.currentTarget.dataset.item;
    if (item.target_type === "PRODUCT" && item.product) {
      wx.navigateTo({ url: `/pages/product/detail?id=${item.product.id}` });
    } else if (item.merchant) {
      wx.navigateTo({ url: `/pages/merchant/detail?id=${item.merchant.id}` });
    }
  },
  formatPrice,
});
