<template>
  <div>
    <h2>地区管理（五级，可补录村）</h2>
    <el-breadcrumb separator="/" style="margin-bottom:12px">
      <el-breadcrumb-item @click="jump(-1)">根</el-breadcrumb-item>
      <el-breadcrumb-item v-for="(p, idx) in path" :key="p.id" @click="jump(idx)">{{ p.name }}</el-breadcrumb-item>
    </el-breadcrumb>
    <el-button type="primary" @click="visible=true" style="margin-bottom:12px">新增下级地区</el-button>
    <el-table :data="items" border @row-click="enter">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="level" label="级别" width="100" />
      <el-table-column prop="code" label="编码" />
      <el-table-column prop="status" label="状态" width="100" />
    </el-table>

    <el-dialog v-model="visible" title="新增地区">
      <el-form label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="级别"><el-input-number v-model="form.level" :min="1" :max="5" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="form.code" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="create">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import http from "../api/http";

const items = ref<any[]>([]);
const path = ref<any[]>([]);
const visible = ref(false);
const form = reactive({ name: "", level: 1, code: "" });

async function load(parentId: number | null = null) {
  items.value = (await http.get("/admin/regions", {
    params: parentId == null ? {} : { parent_id: parentId },
  })) as any;
}
function enter(row: any) {
  if (row.level >= 5) return;
  path.value.push(row);
  form.level = row.level + 1;
  load(row.id);
}
function jump(idx: number) {
  if (idx < 0) {
    path.value = [];
    form.level = 1;
    load(null);
    return;
  }
  path.value = path.value.slice(0, idx + 1);
  const cur = path.value[idx];
  form.level = cur.level + 1;
  load(cur.id);
}
async function create() {
  const parent = path.value[path.value.length - 1];
  await http.post("/admin/regions", {
    ...form,
    parent_id: parent ? parent.id : null,
    sort: 0,
    status: 1,
  });
  visible.value = false;
  ElMessage.success("已创建");
  load(parent ? parent.id : null);
}
onMounted(() => load(null));
</script>
