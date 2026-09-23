<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="brand">Rent Admin</div>
      <el-menu router :default-active="$route.path">
        <el-menu-item index="/">数据概览</el-menu-item>
        <el-menu-item index="/users">用户管理</el-menu-item>
        <el-menu-item index="/merchants">商家审核</el-menu-item>
        <el-menu-item index="/products">商品审核</el-menu-item>
        <el-menu-item index="/categories">分类管理</el-menu-item>
        <el-menu-item index="/regions">地区管理</el-menu-item>
        <el-menu-item index="/banners">首页 Banner</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>乡镇物品租赁平台</span>
        <el-button link type="danger" @click="logout">退出</el-button>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
const router = useRouter();
function logout() {
  localStorage.removeItem("admin_token");
  router.push("/login");
}
</script>

<style scoped>
.layout { min-height: 100vh; }
.aside { background: #123825; color: #fff; }
.brand { padding: 20px; font-weight: 700; color: #fff; }
.aside :deep(.el-menu) { border-right: none; background: transparent; }
.aside :deep(.el-menu-item) { color: #dce8e0; }
.aside :deep(.el-menu-item.is-active) { background: #1b5e3b; color: #fff; }
.header { display: flex; justify-content: space-between; align-items: center; background: #fff; border-bottom: 1px solid #eef2f0; }
</style>
