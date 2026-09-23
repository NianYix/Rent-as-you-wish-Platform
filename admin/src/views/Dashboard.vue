<template>
  <div>
    <h2>数据概览</h2>
    <el-row :gutter="16" v-if="stats">
      <el-col :span="6" v-for="item in cards" :key="item.label">
        <el-card><div class="n">{{ item.value }}</div><div>{{ item.label }}</div></el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import http from "../api/http";

const stats = ref<any>(null);
const cards = computed(() => [
  { label: "用户数", value: stats.value?.user_count },
  { label: "商家数", value: stats.value?.merchant_count },
  { label: "商品数", value: stats.value?.product_count },
  { label: "待审商家", value: stats.value?.pending_merchants },
  { label: "待审商品", value: stats.value?.pending_products },
  { label: "浏览量", value: stats.value?.view_count },
  { label: "收藏数", value: stats.value?.favorite_count },
  { label: "联系次数", value: stats.value?.inquiry_count },
]);

onMounted(async () => {
  stats.value = await http.get("/admin/dashboard/stats");
});
</script>

<style scoped>
.n { font-size: 28px; font-weight: 700; color: #1b5e3b; margin-bottom: 8px; }
.el-col { margin-bottom: 16px; }
</style>
