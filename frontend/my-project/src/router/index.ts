import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import Community from '../views/Community.vue'
import Coach from '../views/Coach.vue'
import Players from '../views/Players.vue'
import Shop from '../views/Shop.vue'
import Profile from '../views/Profile.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true } // 篮球资讯首页
  },
  {
    path: '/community',
    name: 'Community',
    component: Community,
    meta: { requiresAuth: true } // 球迷社区
  },
  {
    path: '/coach',
    name: 'Coach',
    component: Coach,
    meta: { requiresAuth: true } // AI 篮球教练
  },
  {
    path: '/players',
    name: 'Players',
    component: Players,
    meta: { requiresAuth: true } // 球员评分
  },
  {
    path: '/shop',
    name: 'Shop',
    component: Shop,
    meta: { requiresAuth: true } // 篮球商城
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true } // 个人中心
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true } // 游客才能访问
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true } // 游客才能访问
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')

  // 需要登录的页面
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 游客页面（已登录不能访问）
  if (to.meta.requiresGuest && token) {
    next('/')
    return
  }

  next()
})

export default router