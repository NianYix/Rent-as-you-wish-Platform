<template>
  <div>
    <h2>商家审核</h2>
    <el-radio-group v-model="status" @change="load" style="margin-bottom:12px">
      <el-radio-button label="">全部</el-radio-button>
      <el-radio-button label="PENDING">待审</el-radio-button>
      <el-radio-button label="APPROVED">已通过</el-radio-button>
      <el-radio-button label="REJECTED">已拒绝</el-radio-button>
    </el-radio-group>
    <el-table :data="items" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="merchant_name" label="名称" />
      <el-table-column prop="phone" label="电话" />
      <el-table-column prop="wechat" label="微信" />
      <el-table-column prop="verify_status" label="状态" width="120" />
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="audit(row, 'approve')">通过</el-button>
          <el-button size="small" type="danger" @click="audit(row, 'reject')">拒绝</el-button>
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
const status = ref("PENDING");
async function load() {
  const data: any = await http.get("/admin/merchants", {
    params: { page_size: 100, verify_status: status.value || undefined },
  });
  items.value = data.items || [];
}
async function audit(row: any, action: string) {
  let reason = "";
  if (action === "reject") {
    const { value } = await ElMessageBox.prompt("拒绝原因", "审核拒绝");
    reason = value;
  }
  await http.post(`/admin/merchants/${row.id}/audit`, { action, reason });
  ElMessage.success("已处理");
  load();
}
onMounted(load);
</script>
