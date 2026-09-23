<template>
  <div>
    <h2>首页 Banner</h2>
    <el-button type="primary" @click="open()" style="margin-bottom:12px">新增</el-button>
    <el-table :data="items" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="image_url" label="图片URL" />
      <el-table-column prop="sort" label="排序" width="80" />
      <el-table-column prop="status" label="状态" width="80" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="open(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="form.id ? '编辑' : '新增'">
      <el-form label-width="90px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="图片URL"><el-input v-model="form.image_url" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort" /></el-form-item>
        <el-form-item label="状态"><el-input-number v-model="form.status" :min="0" :max="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import http from "../api/http";

const items = ref<any[]>([]);
const visible = ref(false);
const form = reactive<any>({ id: null, title: "", image_url: "", sort: 0, status: 1, link_type: "", link_value: "" });

async function load() {
  items.value = (await http.get("/admin/banners")) as any;
}
function open(row?: any) {
  Object.assign(form, row || { id: null, title: "", image_url: "", sort: 0, status: 1, link_type: "", link_value: "" });
  visible.value = true;
}
async function save() {
  const payload = { ...form };
  delete payload.id;
  if (form.id) await http.put(`/admin/banners/${form.id}`, payload);
  else await http.post("/admin/banners", payload);
  visible.value = false;
  ElMessage.success("已保存");
  load();
}
async function remove(row: any) {
  await http.delete(`/admin/banners/${row.id}`);
  ElMessage.success("已删除");
  load();
}
onMounted(load);
</script>
