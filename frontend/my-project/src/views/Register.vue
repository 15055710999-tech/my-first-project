<template>
  <div class="register-container">
    <div class="form-wrapper">
      <h2>注册篮球社区</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>用户名：</label>
          <input 
            type="text" 
            v-model="form.username" 
            placeholder="请输入用户名"
            required
          >
        </div>
        <div class="form-group">
          <label>密码：</label>
          <input 
            type="password" 
            v-model="form.password" 
            placeholder="请输入密码"
            required
          >
        </div>
        <div class="form-group">
          <label>确认密码：</label>
          <input 
            type="password" 
            v-model="form.confirmPassword" 
            placeholder="请再次输入密码"
            required
          >
        </div>
        <div class="form-group">
          <label>邮箱：</label>
          <input 
            type="email" 
            v-model="form.email" 
            placeholder="请输入邮箱（选填）"
          >
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="switch-link">
        已有账号？
        <a href="#" @click.prevent="goToLogin">立即登录</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'  // 导入 useRouter
import { registerApi } from '../api/user'

const router = useRouter()  // 使用 useRouter 钩子
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

const handleRegister = async () => {
  // 前端验证
  if (!form.username || !form.password || !form.confirmPassword) {
    alert('请填写必填项')
    return
  }
  
  if (form.password !== form.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  
  if (form.password.length < 6) {
    alert('密码长度不能小于6位')
    return
  }

  loading.value = true
  try {
    const res: any = await registerApi({
      username: form.username,
      password: form.password,
      confirm_password: form.confirmPassword,
      email: form.email || undefined
    })
    
    console.log('注册成功:', res)
    alert('注册成功！请登录')
    router.push('/login')
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.form-wrapper {
  background: white;
  padding: 40px;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-size: 14px;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.switch-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

.switch-link a {
  color: #667eea;
  text-decoration: none;
  cursor: pointer;
}

.switch-link a:hover {
  text-decoration: underline;
}
</style>