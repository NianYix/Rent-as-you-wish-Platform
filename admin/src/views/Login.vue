<template>
  <div class="login">
    <el-card class="box">
      <h2>乡镇租赁管理后台</h2>
      <el-form @submit.prevent>
        <el-form-item label="账号">
          <el-input v-model="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" show-password />
        </el-form-item>
        <el-button type="primary" style="width: 100%" @click="login">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import http from "../api/http";

const router = useRouter();
const username = ref("admin");
const password = ref("Admin@123456");

async function login() {
  try {
    const data: any = await http.post("/admin/auth/login", {
      username: username.value,
      password: password.value,
    });
    localStorage.setItem("admin_token", data.access_token);
    router.push("/");
  } catch (e: any) {
    ElMessage.error(e.message || "登录失败");
  }
}
</script>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, #1b5e3b, #f3f6f2 55%);
}
.box {
  width: 380px;
}
h2 {
  margin: 0 0 20px;
  text-align: center;
  color: #1b5e3b;
}
</style>
