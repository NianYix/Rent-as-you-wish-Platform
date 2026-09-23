<template>
  <div>
    <h2>分类管理</h2>
    <el-button type="primary" @click="openCreate(null)" style="margin-bottom:12px">新增一级分类</el-button>
    <el-table :data="flat" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="label" label="名称" />
      <el-table-column prop="sort" label="排序" width="100" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button size="small" v-if="!row.parent_id" @click="openCreate(row.id)">加子类</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" title="新增分类">
      <el-input v-model="name" placeholder="分类名称" />
      <template #footer>
        <el-button type="primary" @click="create">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import http from "../api/http";

const tree = ref<any[]>([]);
const visible = ref(false);
const name = ref("");
const parentId = ref<number | null>(null);

const flat = computed(() => {
  const rows: any[] = [];
  for (const p of tree.value) {
    rows.push({ ...p, label: p.name, parent_id: null });
    for (const c of p.children || []) {
      rows.push({ ...c, label: `└ ${c.name}`, parent_id: p.id });
    }
  }
  return rows;
});

async function load() {
  tree.value = (await http.get("/admin/categories")) as any;
}
function openCreate(pid: number | null) {
  parentId.value = pid;
  name.value = "";
  visible.value = true;
}
async function create() {
  await http.post("/admin/categories", {
    name: name.value,
    parent_id: parentId.value,
    sort: 0,
    status: 1,
  });
  visible.value = false;
  ElMessage.success("已创建");
  load();
}
async function remove(row: any) {
  await http.delete(`/admin/categories/${row.id}`);
  ElMessage.success("已删除");
  load();
}
onMounted(load);
</script>
