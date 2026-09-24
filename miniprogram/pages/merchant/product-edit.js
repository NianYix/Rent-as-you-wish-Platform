const { request, ensureLogin, uploadImage } = require("../../utils/api");
const { pickImages, ensurePrivacyAuthorized } = require("../../utils/media");

const UNIT_OPTIONS = [
  { value: "HOUR", label: "小时" },
  { value: "DAY", label: "天" },
  { value: "TIME", label: "次" },
  { value: "MONTH", label: "月" },
  { value: "NEGOTIABLE", label: "面议" },
];
const MAX_IMAGES = 9;

Page({
  data: {
    id: null,
    isEdit: false,
    uploading: false,
    categories: [],
    categoryIndex: 0,
    unitIndex: 1,
    unitLabels: UNIT_OPTIONS.map((u) => u.label),
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
      cover_image: "",
      images: [],
      submit: true,
    },
  },

  async onLoad(q) {
    this._query = q || {};
    try {
      await ensureLogin();
      const tree = await request({ url: "/categories" });
      const categories = [];
      (tree || []).forEach((p) => (p.children || []).forEach((c) => categories.push(c)));

      const id = this._query.id ? Number(this._query.id) : null;
      this.setData({
        categories,
        id,
        isEdit: !!id,
      });
      wx.setNavigationBarTitle({ title: id ? "编辑商品" : "发布商品" });

      if (id) {
        await this.loadProduct(id, categories);
      } else if (categories.length) {
        this.setData({
          "form.category_id": categories[0].id,
          categoryIndex: 0,
        });
      }
    } catch (e) {
      wx.showToast({ title: e.message || "加载失败", icon: "none" });
    }
  },

  async onReady() {
    // 组件已挂载，主动弹出隐私授权（未同意过才弹）
    try {
      await ensurePrivacyAuthorized(this);
    } catch (e) {
      // ignore
    }
  },

  async loadProduct(id, categories) {
    const detail = await request({
      url: `/merchants/me/products/${id}`,
      auth: true,
    });
    const catIdx = Math.max(
      0,
      categories.findIndex((c) => c.id === detail.category_id)
    );
    const unitIdx = Math.max(
      0,
      UNIT_OPTIONS.findIndex((u) => u.value === detail.price_unit)
    );
    const images = (detail.images || []).map((img, i) => ({
      image_url: img.image_url,
      sort: img.sort != null ? img.sort : i,
    }));
    // 若只有封面没有多图，也展示封面
    if (!images.length && detail.cover_image) {
      images.push({ image_url: detail.cover_image, sort: 0 });
    }
    this.setData({
      categoryIndex: catIdx,
      unitIndex: unitIdx,
      form: {
        category_id: detail.category_id,
        name: detail.name || "",
        description: detail.description || "",
        specs: detail.specs || "",
        price: detail.price == null ? "" : String(detail.price),
        price_unit: detail.price_unit || "DAY",
        deposit: detail.deposit == null ? "" : String(detail.deposit),
        stock: detail.stock == null ? 1 : detail.stock,
        address: detail.address || "",
        cover_image: detail.cover_image || (images[0] && images[0].image_url) || "",
        images,
        submit: true,
      },
    });
  },

  onInput(e) {
    this.setData({ [`form.${e.currentTarget.dataset.key}`]: e.detail.value });
  },

  onUnit(e) {
    const idx = Number(e.detail.value);
    this.setData({
      unitIndex: idx,
      "form.price_unit": UNIT_OPTIONS[idx].value,
    });
  },

  onCat(e) {
    const idx = Number(e.detail.value);
    const c = this.data.categories[idx];
    this.setData({
      categoryIndex: idx,
      "form.category_id": c.id,
    });
  },

  async chooseImages() {
    const now = Date.now();
    if (this._pickLock && now - this._pickLock < 1200) return;
    this._pickLock = now;

    const remain = MAX_IMAGES - (this.data.form.images || []).length;
    if (remain <= 0) {
      wx.showToast({ title: `最多上传${MAX_IMAGES}张`, icon: "none" });
      return;
    }
    if (this.data.uploading) return;

    try {
      const paths = await pickImages(remain, this);
      if (!paths.length) return;

      this.setData({ uploading: true });
      wx.showLoading({ title: "上传中", mask: true });
      await ensureLogin();
      const images = [...(this.data.form.images || [])];
      for (const filePath of paths) {
        const url = await uploadImage(filePath);
        images.push({ image_url: url, sort: images.length });
      }
      const cover = this.data.form.cover_image || (images[0] && images[0].image_url) || "";
      this.setData({
        "form.images": images,
        "form.cover_image": cover,
      });
    } catch (e) {
      const msg = (e && e.message) || "无法打开相册/相机";
      if (e && e.code === "PRIVACY_DENY") {
        wx.showModal({
          title: "需要授权",
          content: "请先同意隐私保护指引，再上传商品图片。可在「我的-隐私政策」查看说明。",
          showCancel: false,
        });
      } else {
        wx.showModal({
          title: "选图失败",
          content: msg + "\n请确认已允许微信使用相册/相机权限。",
          showCancel: false,
        });
      }
    } finally {
      this.setData({ uploading: false });
      wx.hideLoading();
    }
  },

  /** 主动申请隐私权限 */
  async requestPrivacy() {
    const ok = await ensurePrivacyAuthorized(this);
    wx.showToast({
      title: ok ? "已授权，可上传图片" : "未同意隐私授权",
      icon: "none",
    });
  },

  removeImage(e) {
    const idx = Number(e.currentTarget.dataset.index);
    const images = [...(this.data.form.images || [])];
    images.splice(idx, 1);
    images.forEach((img, i) => {
      img.sort = i;
    });
    const cover = images[0] ? images[0].image_url : "";
    this.setData({
      "form.images": images,
      "form.cover_image": cover,
    });
  },

  setCover(e) {
    const idx = Number(e.currentTarget.dataset.index);
    const images = [...(this.data.form.images || [])];
    if (!images[idx]) return;
    const [picked] = images.splice(idx, 1);
    images.unshift(picked);
    images.forEach((img, i) => {
      img.sort = i;
    });
    this.setData({
      "form.images": images,
      "form.cover_image": images[0].image_url,
    });
    wx.showToast({ title: "已设为封面", icon: "none" });
  },

  previewImage(e) {
    const idx = Number(e.currentTarget.dataset.index);
    const urls = (this.data.form.images || []).map((i) => i.image_url);
    wx.previewImage({ current: urls[idx], urls });
  },

  async submit() {
    if (this.data.uploading) {
      wx.showToast({ title: "图片上传中，请稍候", icon: "none" });
      return;
    }
    try {
      const f = { ...this.data.form };
      f.price = f.price === "" ? null : Number(f.price);
      f.deposit = f.deposit === "" ? null : Number(f.deposit);
      f.stock = Number(f.stock || 1);
      if (!f.name || !f.category_id) {
        wx.showToast({ title: "请填写名称和分类", icon: "none" });
        return;
      }
      if (!f.images || !f.images.length) {
        wx.showToast({ title: "请至少上传1张商品图片", icon: "none" });
        return;
      }
      f.cover_image = f.cover_image || f.images[0].image_url;
      f.images = f.images.map((img, i) => ({
        image_url: img.image_url,
        sort: i,
      }));

      if (this.data.isEdit) {
        await request({
          url: `/merchants/me/products/${this.data.id}`,
          method: "PUT",
          data: {
            category_id: f.category_id,
            name: f.name,
            description: f.description,
            specs: f.specs,
            price: f.price,
            price_unit: f.price_unit,
            deposit: f.deposit,
            stock: f.stock,
            address: f.address,
            cover_image: f.cover_image,
            images: f.images,
            submit: true,
          },
          auth: true,
        });
        wx.showToast({ title: "已保存并提交审核" });
      } else {
        await request({
          url: "/merchants/me/products",
          method: "POST",
          data: f,
          auth: true,
        });
        wx.showToast({ title: "已提交审核" });
      }
      setTimeout(() => wx.navigateBack(), 500);
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
    }
  },
});
