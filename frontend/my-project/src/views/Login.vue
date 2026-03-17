<template>
  <div class="login-container">
    <div class="form-wrapper">
      <h2>登录篮球社区</h2>
      <form @submit.prevent="handleLogin">
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
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="switch-link">
        还没有账号？
        <a href="#" @click.prevent="goToRegister">立即注册</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'  // 导入 useRouter
import { loginApi } from '../api/user'
import { userStore } from '../stores/user'

const router = useRouter()  // 使用 useRouter 钩子
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

// 跳转到注册页
const goToRegister = () => {
  router.push('/register')
}

const handleLogin = async () => {
  if (!form.username || !form.password) {
    alert('请填写用户名和密码')
    return
  }

  loading.value = true
  try {
    const res: any = await loginApi(form)
    console.log('登录成功:', res)
    
    // 保存 token 和用户信息
    const userInfo = res.data.user
    // 确保头像URL是完整的
    if (userInfo.avatar && !userInfo.avatar.startsWith('http')) {
      userInfo.avatar = `http://localhost:8000${userInfo.avatar}`
    }
    userStore.setToken(res.data.token)
    userStore.setUserInfo(userInfo)
    
    alert('登录成功！')
    router.push('/')  // 跳转到首页
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
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