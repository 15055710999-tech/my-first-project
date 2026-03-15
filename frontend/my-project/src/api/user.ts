import request from '../utils/request'

// 登录接口
export const loginApi = (data: { username: string; password: string }) => {
  return request.post('/users/login/', data)
}

// 注册接口
export const registerApi = (data: {
  username: string
  password: string
  confirm_password: string
  email?: string
  phone?: string
}) => {
  return request.post('/users/register/', data)
}

// 获取用户信息
export const getProfileApi = () => {
  return request.get('/users/profile/')
}