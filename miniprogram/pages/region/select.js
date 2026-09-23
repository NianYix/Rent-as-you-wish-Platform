const { request } = require("../../utils/api");

Page({
  data: {
    level: 1,
    parentId: null,
    list: [],
    path: [],
  },
  onShow() {
    this.load(null, 1);
  },
  async load(parentId, level) {
    const list = await request({
      url: "/regions",
      data: parentId == null ? {} : { parent_id: parentId },
    });
    this.setData({ list, parentId, level });
  },
  async select(e) {
    const item = e.currentTarget.dataset.item;
    const path = this.data.path.concat([item]);
    this.setData({ path });
    if (item.level >= 4) {
      // 选到乡镇即可；村可选继续
      const next = await request({ url: "/regions", data: { parent_id: item.id } });
      if (item.level === 5 || !next.length) {
        const selected = {
          id: item.id,
          name: path.map((p) => p.name).join(" / "),
          townId: item.level >= 4 ? (item.level === 4 ? item.id : path.find((p) => p.level === 4)?.id) : null,
          villageId: item.level === 5 ? item.id : null,
          path,
        };
        wx.setStorageSync("selectedRegion", selected);
        getApp().globalData.region = selected;
        wx.navigateBack();
        return;
      }
      this.setData({ list: next, parentId: item.id, level: item.level + 1 });
      return;
    }
    this.load(item.id, item.level + 1);
  },
  confirmTown() {
    const path = this.data.path;
    if (!path.length) return;
    const item = path[path.length - 1];
    const selected = {
      id: item.id,
      name: path.map((p) => p.name).join(" / "),
      townId: item.level >= 4 ? item.id : null,
      villageId: null,
      path,
    };
    wx.setStorageSync("selectedRegion", selected);
    getApp().globalData.region = selected;
    wx.navigateBack();
  },
});
