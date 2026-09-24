const { request, formatPrice, ensureLogin } = require("../../utils/api");

Page({
  data: {
    id: 0,
    detail: null,
    priceText: "",
  },
  onLoad(q) {
    this.setData({ id: Number(q.id) });
    this.load();
  },
  async load() {
    try {
      await ensureLogin().catch(() => {});
      const detail = await request({ url: `/products/${this.data.id}` });
      let images = detail.images || [];
      if (!images.length && detail.cover_image) {
        images = [{ id: 0, image_url: detail.cover_image, sort: 0 }];
      }
      detail.images = images;
      this.setData({ detail, priceText: formatPrice(detail) });
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
    }
  },
  async toggleFav() {
    try {
      await ensureLogin();
      const d = this.data.detail;
      if (d.is_favorited) {
        await request({
          url: `/favorites?target_type=PRODUCT&target_id=${d.id}`,
          method: "DELETE",
          auth: true,
        });
      } else {
        await request({
          url: "/favorites",
          method: "POST",
          data: { target_type: "PRODUCT", target_id: d.id },
          auth: true,
        });
      }
      this.load();
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
    }
  },
  async callPhone() {
    try {
      await ensureLogin().catch(() => {});
      const d = this.data.detail;
      const data = await request({
        url: `/merchants/${d.merchant_id}/contact/phone?product_id=${d.id}`,
        method: "POST",
      });
      if (!data.phone) {
        wx.showToast({ title: "商家未留电话", icon: "none" });
        return;
      }
      wx.makePhoneCall({ phoneNumber: data.phone });
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
    }
  },
  async showWechat() {
    try {
      await ensureLogin();
      const d = this.data.detail;
      const data = await request({
        url: `/merchants/${d.merchant_id}/contact/wechat?product_id=${d.id}`,
        method: "POST",
        auth: true,
      });
      wx.setClipboardData({ data: data.wechat });
      wx.showModal({
        title: "商家微信",
        content: data.wechat + "\n（已复制到剪贴板）",
        showCancel: false,
      });
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
    }
  },
  goMerchant() {
    wx.navigateTo({
      url: `/pages/merchant/detail?id=${this.data.detail.merchant_id}`,
    });
  },
});
