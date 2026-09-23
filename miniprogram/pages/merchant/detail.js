const { request, formatPrice } = require("../../utils/api");

Page({
  data: { merchant: null, products: [] },
  onLoad(q) {
    this.id = Number(q.id);
    this.load();
  },
  async load() {
    const merchant = await request({ url: `/merchants/${this.id}` });
    const products = await request({ url: `/merchants/${this.id}/products` });
    this.setData({ merchant, products: products.items || [] });
  },
  goProduct(e) {
    wx.navigateTo({ url: `/pages/product/detail?id=${e.currentTarget.dataset.id}` });
  },
  formatPrice,
});
