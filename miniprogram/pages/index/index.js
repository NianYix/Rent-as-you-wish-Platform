const { request, formatPrice } = require("../../utils/api");

Page({
  data: {
    regionName: "选择地区",
    banners: [],
    categories: [],
    hotProducts: [],
    merchants: [],
  },
  onShow() {
    const region = getApp().globalData.region || wx.getStorageSync("selectedRegion");
    if (region) {
      this.setData({ regionName: region.name || region.townName || "已选地区" });
    }
    this.loadHome();
  },
  async loadHome() {
    try {
      const data = await request({ url: "/home" });
      const cats = [];
      (data.categories || []).forEach((c) => {
        cats.push(c);
        (c.children || []).slice(0, 1).forEach(() => {});
      });
      this.setData({
        banners: data.banners || [],
        categories: (data.categories || []).slice(0, 8),
        hotProducts: data.hot_products || data.recommended_products || [],
        merchants: data.recommended_merchants || [],
      });
    } catch (e) {
      wx.showToast({ title: e.message || "加载失败", icon: "none" });
    }
  },
  goRegion() {
    wx.navigateTo({ url: "/pages/region/select" });
  },
  goSearch() {
    wx.navigateTo({ url: "/pages/search/search" });
  },
  goCategory() {
    wx.switchTab({ url: "/pages/category/category" });
  },
  goProduct(e) {
    wx.navigateTo({ url: `/pages/product/detail?id=${e.currentTarget.dataset.id}` });
  },
  goMerchant(e) {
    wx.navigateTo({ url: `/pages/merchant/detail?id=${e.currentTarget.dataset.id}` });
  },
  formatPrice,
});
