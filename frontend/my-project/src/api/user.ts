import request from '../utils/request'

// 获取当前用户信息
export const getUserInfoApi = () => {
  return request.get('/users/info/')
}

// 登录
export const loginApi = (data: {
  username: string
  password: string
}) => {
  return request.post('/users/login/', data)
}

// 注册
export const registerApi = (data: {
  username: string
  password: string
  confirm_password: string
  email?: string
}) => {
  return request.post('/users/register/', data)
}

// 更新个人信息
export const updateProfileApi = (data: {
  username: string
  email: string
  phone?: string
  gender?: string
  birth_date?: string
  bio?: string
}) => {
  return request.put('/users/profile/update/', data)
}

// 修改密码
export const changePasswordApi = (data: {
  old_password: string
  new_password: string
  confirm_password: string
}) => {
  return request.post('/users/change-password/', data)
}

// 上传头像
export const uploadAvatarApi = (formData: FormData) => {
  return request.post('/users/avatar/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取我的帖子
export const getMyPostsApi = () => {
  return request.get('/basketball/posts/my/')
}