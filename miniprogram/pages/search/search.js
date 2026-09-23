const { request, formatPrice } = require("../../utils/api");

Page({
  data: { keyword: "", items: [] },
  onInput(e) {
    this.setData({ keyword: e.detail.value });
  },
  async onSearch() {
    try {
      const data = await request({
        url: "/search/products",
        data: { keyword: this.data.keyword, page_size: 50 },
      });
      this.setData({ items: data.items || [] });
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
    }
  },
  goProduct(e) {
    wx.navigateTo({ url: `/pages/product/detail?id=${e.currentTarget.dataset.id}` });
  },
  formatPrice,
});
