import { reactive } from 'vue'

export interface User {
  id: number
  username: string
  email?: string
  phone?: string
  avatar?: string
  points_balance: number
  points?: number
  level?: number
  gender?: string
  birth_date?: string
  bio?: string
  last_sign_in?: string
  sign_in_streak: number
  is_staff: boolean
}

export const userStore = reactive({
  token: localStorage.getItem('token') || '',
  userInfo: JSON.parse(localStorage.getItem('user') || 'null') as User | null,

  // 是否已登录
  get isLoggedIn() {
    return !!this.token
  },

  // 设置 token
  setToken(token: string) {
    this.token = token
    localStorage.setItem('token', token)
  },

  // 设置用户信息
  setUserInfo(user: User | null) {
    this.userInfo = user
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
    } else {
      localStorage.removeItem('user')
    }
  },

  // 退出登录
  logout() {
    this.token = ''
    this.userInfo = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
})