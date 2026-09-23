App({
  globalData: {
    region: null,
  },
  onLaunch() {
    const region = wx.getStorageSync("selectedRegion");
    if (region) this.globalData.region = region;
  },
});
