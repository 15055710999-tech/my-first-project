import request from '../utils/request'

// 首页资讯流：比赛 + 官方新闻 + 用户帖子摘要
export const getFeedApi = () => {
  return request.get('/basketball/feed/')
}

// 比赛列表（比分）
export const getGamesApi = () => {
  return request.get('/basketball/games/')
}

// 帖子列表 & 发帖
export const getPostsApi = () => {
  return request.get('/basketball/posts/')
}

export const createPostApi = (data: { title: string; content: string }) => {
  return request.post('/basketball/posts/', data)
}

// 帖子详情
export const getPostDetailApi = (id: number) => {
  return request.get(`/basketball/posts/${id}/`)
}

// 球员评分相关
export const getPlayersApi = () => {
  return request.get('/basketball/players/')
}

export const ratePlayerApi = (playerId: number, data: { score: number; comment?: string }) => {
  return request.post(`/basketball/players/${playerId}/rate/`, data)
}

// 商城
export const getProductsApi = () => {
  return request.get('/basketball/shop/products/')
}

export const createOrderApi = (data: { items: { product_id: number; quantity: number }[] }) => {
  return request.post('/basketball/shop/orders/', data)
}

// AI 篮球教练
export const askCoachApi = (data: { question: string }) => {
  return request.post('/basketball/coach/ask/', data)
}

