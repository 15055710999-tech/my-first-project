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
export const getPostsApi = (params?: any) => {
  return request.get('/basketball/posts/', { params })
}

export const createPostApi = (data: { title: string; content: string; images?: string[]; tags?: string[] }) => {
  return request.post('/basketball/posts/', data)
}

// 帖子详情
export const getPostDetailApi = (id: number) => {
  return request.get(`/basketball/posts/${id}/`)
}

// 发表评论或回复评论
export const createCommentApi = (postId: number, data: { content: string; parent_comment_id?: number | null }) => {
  return request.post(`/basketball/posts/${postId}/comment/`, data)
}

// 删除帖子
export const deletePostApi = (id: number) => {
  return request.post(`/basketball/posts/${id}/delete/`)
}

// 删除评论
export const deleteCommentApi = (id: number) => {
  return request.post(`/basketball/comments/${id}/delete/`)
}

// 获取我的所有帖子（包括待审核、已拒绝）
export const getMyPostsApi = () => {
  return request.get('/basketball/posts/my/')
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

// 帖子点赞相关
export const likePostApi = (postId: number) => {
  return request.post(`/basketball/posts/${postId}/like/`)
}

// 获取帖子详情（包含点赞状态）
export const getPostDetailWithLikeStatusApi = (postId: number) => {
  return request.get(`/basketball/posts/${postId}/detail/`)
}

// 获取用户已点赞的帖子
export const getMyLikedPostsApi = () => {
  return request.get('/basketball/posts/my/liked/')
}

