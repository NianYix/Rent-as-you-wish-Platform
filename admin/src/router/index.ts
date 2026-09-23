import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import Layout from "../views/Layout.vue";
import Dashboard from "../views/Dashboard.vue";
import Users from "../views/Users.vue";
import Merchants from "../views/Merchants.vue";
import Products from "../views/Products.vue";
import Categories from "../views/Categories.vue";
import Regions from "../views/Regions.vue";
import Banners from "../views/Banners.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", component: Login },
    {
      path: "/",
      component: Layout,
      children: [
        { path: "", component: Dashboard },
        { path: "users", component: Users },
        { path: "merchants", component: Merchants },
        { path: "products", component: Products },
        { path: "categories", component: Categories },
        { path: "regions", component: Regions },
        { path: "banners", component: Banners },
      ],
    },
  ],
});

router.beforeEach((to, _from, next) => {
  if (to.path !== "/login" && !localStorage.getItem("admin_token")) {
    next("/login");
  } else {
    next();
  }
});

export default router;
