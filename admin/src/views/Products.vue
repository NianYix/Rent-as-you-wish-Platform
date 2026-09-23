<template>
  <div>
    <h2>商品审核</h2>
    <el-radio-group v-model="status" @change="load" style="margin-bottom:12px">
      <el-radio-button label="">全部</el-radio-button>
      <el-radio-button label="PENDING_REVIEW">待审</el-radio-button>
      <el-radio-button label="APPROVED">已通过</el-radio-button>
      <el-radio-button label="REJECTED">已拒绝</el-radio-button>
    </el-radio-group>
    <el-table :data="items" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="商品" />
      <el-table-column prop="merchant_name" label="商家" />
      <el-table-column prop="price" label="价格" width="100" />
      <el-table-column prop="audit_status" label="审核" width="140" />
      <el-table-column prop="shelf_status" label="上下架" width="100" />
      <el-table-column label="操作" width="280">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="audit(row, 'approve')">通过</el-button>
          <el-button size="small" type="danger" @click="audit(row, 'reject')">拒绝</el-button>
          <el-button size="small" @click="offline(row)">下架</el-button>
          <el-button size="small" type="primary" @click="recommend(row)">推荐</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import http from "../api/http";

const items = ref<any[]>([]);
const status = ref("PENDING_REVIEW");
async function load() {
  const data: any = await http.get("/admin/products", {
    params: { page_size: 100, audit_status: status.value || undefined },
  });
  items.value = data.items || [];
}
async function audit(row: any, action: string) {
  let reason = "";
  if (action === "reject") {
    const { value } = await ElMessageBox.prompt("拒绝原因", "审核拒绝");
    reason = value;
  }
  await http.post(`/admin/products/${row.id}/audit`, { action, reason });
  ElMessage.success("已处理");
  load();
}
async function offline(row: any) {
  await http.post(`/admin/products/${row.id}/offline`);
  ElMessage.success("已下架");
  load();
}
async function recommend(row: any) {
  await http.post(`/admin/products/${row.id}/recommend`, null, { params: { recommended: true } });
  ElMessage.success("已设为推荐");
}
onMounted(load);
</script>
