<template>
  <div id="app">
    <nav>
      <div class="logo" @click="goToHome">
        <h2>🏀 篮球社区</h2>
      </div>

      <div class="nav-links" v-if="userStore.isLoggedIn">
        <button
          @click="router.push('/')"
          :class="{ active: route.path === '/' }"
        >
          篮球资讯
        </button>
        <button
          @click="router.push('/community')"
          :class="{ active: route.path === '/community' }"
        >
          球迷社区
        </button>
        <button
          @click="router.push('/coach')"
          :class="{ active: route.path === '/coach' }"
        >
          AI 篮球教练
        </button>
        <button
          @click="router.push('/players')"
          :class="{ active: route.path === '/players' }"
        >
          球员评分
        </button>
        <button
          @click="router.push('/shop')"
          :class="{ active: route.path === '/shop' }"
        >
          篮球商城
        </button>
        <button
          @click="router.push('/profile')"
          :class="{ active: route.path === '/profile' }"
        >
          个人中心
        </button>
      </div>

      <div class="auth-links" v-if="!userStore.isLoggedIn">
        <button @click="router.push('/login')" :class="{ active: route.path === '/login' }">
          登录
        </button>
        <button @click="router.push('/register')" :class="{ active: route.path === '/register' }">
          注册
        </button>
      </div>

      <div class="user-info" v-else>
        <span>欢迎，{{ userStore.userInfo?.username }}</span>
        <span class="points">积分: {{ userStore.userInfo?.points_balance }}</span>
        <button @click="router.push('/profile')" class="profile-btn">
          个人中心
        </button>
        <button @click="handleLogout">退出</button>
      </div>
    </nav>

    <main class="page-wrapper">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { userStore } from './stores/user'

const router = useRouter()
const route = useRoute()

const goToHome = () => {
  if (userStore.isLoggedIn) {
    router.push('/')
  } else {
    router.push('/login')
  }
}

const handleLogout = () => {
  userStore.logout()
  alert('已退出登录')
  router.push('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  min-height: 100vh;
}

nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1000;
}

.logo {
  cursor: pointer;
}

.logo h2 {
  color: #667eea;
  margin: 0;
  font-size: 1.5rem;
}

.nav-links button,
.auth-links button {
  margin-left: 10px;
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.auth-links button:first-child {
  background-color: #667eea;
  color: white;
}

.auth-links button:last-child {
  background-color: #f0f0f0;
  color: #333;
}

.nav-links button.active,
.auth-links button.active {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info span {
  color: #333;
}

.user-info .points {
  color: #667eea;
  font-weight: bold;
}

.user-info button {
  padding: 5px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.user-info .profile-btn {
  background-color: #667eea;
  color: white;
  margin-right: 10px;
}

.user-info .profile-btn:hover {
  background-color: #764ba2;
}

.user-info button:last-child {
  background-color: #f56c6c;
  color: white;
}

.user-info button:last-child:hover {
  background-color: #e64242;
}

.page-wrapper {
  padding-top: 80px;
}
</style>