const { request, formatPrice } = require("../../utils/api");

Page({
  data: { tree: [], current: null, products: [], categoryId: null },
  onLoad(q) {
    if (q.categoryId) this.setData({ categoryId: Number(q.categoryId) });
    this.load();
  },
  onShow() {
    if (typeof this.getTabBar === "function" && this.getTabBar()) {
      // noop
    }
  },
  async load() {
    const tree = await request({ url: "/categories" });
    let current = tree[0];
    if (this.data.categoryId) {
      current = tree.find((c) => c.id === this.data.categoryId) || current;
    }
    this.setData({ tree, current });
    if (current) this.loadProducts(current.id);
  },
  selectCat(e) {
    const id = e.currentTarget.dataset.id;
    const current = this.data.tree.find((c) => c.id === id);
    this.setData({ current });
    this.loadProducts(id);
  },
  async loadProducts(categoryId) {
    const data = await request({ url: "/products", data: { category_id: categoryId, page_size: 50 } });
    this.setData({ products: data.items || [] });
  },
  goProduct(e) {
    wx.navigateTo({ url: `/pages/product/detail?id=${e.currentTarget.dataset.id}` });
  },
  formatPrice,
});
