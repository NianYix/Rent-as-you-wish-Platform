const { request, ensureLogin } = require("../../utils/api");

Page({
  data: {
    id: null,
    categories: [],
    form: {
      category_id: null,
      name: "",
      description: "",
      specs: "",
      price: "",
      price_unit: "DAY",
      deposit: "",
      stock: 1,
      address: "",
      submit: true,
    },
  },
  async onLoad(q) {
    await ensureLogin();
    const tree = await request({ url: "/categories" });
    const categories = [];
    tree.forEach((p) => (p.children || []).forEach((c) => categories.push(c)));
    this.setData({
      categories,
      "form.category_id": categories[0] && categories[0].id,
      id: q.id ? Number(q.id) : null,
    });
  },
  onInput(e) {
    this.setData({ [`form.${e.currentTarget.dataset.key}`]: e.detail.value });
  },
  onUnit(e) {
    const units = ["HOUR", "DAY", "TIME", "MONTH", "NEGOTIABLE"];
    this.setData({ "form.price_unit": units[e.detail.value] });
  },
  onCat(e) {
    const c = this.data.categories[e.detail.value];
    this.setData({ "form.category_id": c.id });
  },
  async submit() {
    try {
      const f = { ...this.data.form };
      f.price = f.price === "" ? null : Number(f.price);
      f.deposit = f.deposit === "" ? null : Number(f.deposit);
      f.stock = Number(f.stock || 1);
      f.images = [];
      if (!f.name || !f.category_id) {
        wx.showToast({ title: "请填写名称和分类", icon: "none" });
        return;
      }
      if (this.data.id) {
        await request({
          url: `/merchants/me/products/${this.data.id}`,
          method: "PUT",
          data: f,
          auth: true,
        });
      } else {
        await request({ url: "/merchants/me/products", method: "POST", data: f, auth: true });
      }
      wx.showToast({ title: "已提交" });
      setTimeout(() => wx.navigateBack(), 500);
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
    }
  },
});
