<template>
  <div>
    <h2>用户管理</h2>
    <el-table :data="items" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="nickname" label="昵称" />
      <el-table-column prop="role" label="角色" width="120" />
      <el-table-column prop="phone" label="手机" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="setStatus(row, 'DISABLED')" v-if="row.status==='ACTIVE'">禁用</el-button>
          <el-button size="small" type="primary" @click="setStatus(row, 'ACTIVE')" v-else>启用</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import http from "../api/http";

const items = ref<any[]>([]);
async function load() {
  const data: any = await http.get("/admin/users", { params: { page_size: 100 } });
  items.value = data.items || [];
}
async function setStatus(row: any, status: string) {
  await http.post(`/admin/users/${row.id}/status`, null, { params: { status } });
  ElMessage.success("已更新");
  load();
}
onMounted(load);
</script>
