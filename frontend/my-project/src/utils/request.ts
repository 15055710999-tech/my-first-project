import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://localhost:8000/api',  // 后端 API 地址
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})
// 添加用户信息到请求头
const user = localStorage.getItem('user')
if (user) {
  try {
    const userInfo = JSON.parse(user)
    if (userInfo && userInfo.username) {
      request.defaults.headers.common['X-USER'] = userInfo.username
    }
  } catch (error) {
    console.error('解析用户信息失败:', error)
  }
}
// 请求拦截器
request.interceptors.request.use(
  config => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加用户信息到请求头
    const user = localStorage.getItem('user')
    if (user) {
      try {
        const userInfo = JSON.parse(user)
        if (userInfo && userInfo.username) {
          config.headers['X-USER'] = userInfo.username
        }
      } catch (error) {
        console.error('解析用户信息失败:', error)
      }
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          alert(data.message || '请求参数错误')
          break
        case 401:
          alert('登录已过期，请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          break
        case 403:
          alert('没有权限')
          break
        case 404:
          alert('请求的资源不存在')
          break
        case 500:
          alert('服务器错误')
          break
        default:
          alert(data.message || '请求失败')
      }
    } else {
      alert('网络错误，请检查后端服务是否启动')
    }
    return Promise.reject(error)
  }
)



export default request