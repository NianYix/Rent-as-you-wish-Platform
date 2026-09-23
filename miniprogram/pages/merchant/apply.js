const { request, ensureLogin } = require("../../utils/api");

Page({
  data: {
    form: {
      merchant_name: "",
      merchant_type: "PERSONAL",
      phone: "",
      wechat: "",
      description: "",
      address: "",
      business_hours: "08:00-20:00",
    },
  },
  onInput(e) {
    const key = e.currentTarget.dataset.key;
    this.setData({ [`form.${key}`]: e.detail.value });
  },
  async submit() {
    try {
      await ensureLogin();
      const f = this.data.form;
      if (!f.merchant_name || !f.phone) {
        wx.showToast({ title: "请填写名称和电话", icon: "none" });
        return;
      }
      await request({ url: "/merchants/apply", method: "POST", data: f, auth: true });
      wx.showToast({ title: "已提交审核" });
      setTimeout(() => wx.navigateTo({ url: "/pages/merchant/center" }), 500);
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
    }
  },
});
