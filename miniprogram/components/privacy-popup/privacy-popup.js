Component({
  data: {
    show: false,
  },
  lifetimes: {
    attached() {
      const app = getApp();
      app.globalData.openPrivacyPopup = (resolve) => {
        this._resolve = resolve;
        this.setData({ show: true });
      };
    },
  },
  methods: {
    /** 页面主动弹出，返回 Promise<boolean> */
    open() {
      return new Promise((resolve) => {
        this._pageResolve = resolve;
        this.setData({ show: true });
      });
    },
    onAgree() {
      wx.setStorageSync("privacy_image_agreed", 1);
      if (typeof this._resolve === "function") {
        try {
          this._resolve({ event: "agree", buttonId: "privacy-agree-btn" });
        } catch (e) {}
        this._resolve = null;
      }
      if (typeof this._pageResolve === "function") {
        this._pageResolve(true);
        this._pageResolve = null;
      }
      this.setData({ show: false });
      this.triggerEvent("agree");
    },
    onDisagree() {
      if (typeof this._resolve === "function") {
        try {
          this._resolve({ event: "disagree" });
        } catch (e) {}
        this._resolve = null;
      }
      if (typeof this._pageResolve === "function") {
        this._pageResolve(false);
        this._pageResolve = null;
      }
      this.setData({ show: false });
      this.triggerEvent("disagree");
      wx.showToast({ title: "需同意后才能上传图片", icon: "none" });
    },
    noop() {},
  },
});
