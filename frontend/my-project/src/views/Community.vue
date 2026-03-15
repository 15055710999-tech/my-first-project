<template>
  <div class="community-container">
    <section class="hero">
      <div class="hero-text">
        <h1>球迷社区</h1>
        <p>分享你的篮球见解，与球迷一起交流讨论。</p>
      </div>
    </section>

    <!-- 发帖区域 -->
    <div class="post-create-card">
      <div class="user-info">
        <div class="avatar">
          <img src="https://ui-avatars.com/api/?name={{ userStore.userInfo?.username || 'User' }}&background=667eea&color=fff" alt="头像">
        </div>
        <div class="user-details">
          <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
          <span class="points">积分: {{ userStore.userInfo?.points_balance || 0 }}</span>
        </div>
      </div>
      
      <form class="post-form" @submit.prevent="handleCreatePost">
        <input
          v-model="newPost.title"
          class="post-title-input"
          type="text"
          placeholder="分享一个与篮球有关的话题标题..."
        />
        <textarea
          v-model="newPost.content"
          class="post-content-input"
          rows="4"
          placeholder="写下你的看法或比赛心得，分享给大家..."
        />
        <div class="post-actions">
          <div class="post-tools">
            <button type="button" class="tool-btn">
              😊 表情
            </button>
            <button type="button" class="tool-btn">
              📷 图片
            </button>
            <button type="button" class="tool-btn">
              # 话题
            </button>
          </div>
          <button class="post-btn" type="submit" :disabled="posting || !canPost">
            {{ posting ? '发布中...' : '发布' }}
          </button>
        </div>
      </form>
    </div>

    <!-- 帖子列表 -->
    <div class="posts-container">
      <div class="posts-header">
        <h2>最新动态</h2>
        <button class="refresh-btn" @click="fetchPosts" :disabled="loading">
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
      </div>

      <div v-if="posts.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>还没有帖子，来当第一个发帖的球迷吧！</p>
      </div>
      <ul v-else class="posts-list">
        <li v-for="post in posts" :key="post.id" class="post-card">
          <div class="post-header">
            <div class="post-user">
              <div class="avatar">
                <img src="https://ui-avatars.com/api/?name={{ post.author }}&background=667eea&color=fff" alt="头像">
              </div>
              <div class="user-info">
                <span class="username">{{ post.author }}</span>
                <div class="post-meta">
                  <span class="time">{{ formatTime(post.created_at) }}</span>
                  <span class="status-tag" :class="{ 'approved': post.is_published }">
                    {{ post.is_published ? '已发布' : '待审核' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="post-content">
            <h3 class="post-title">{{ post.title }}</h3>
            <p class="post-text">{{ post.content }}</p>
          </div>
          
          <div class="post-actions">
            <button class="action-btn">
              <span class="action-icon">👍</span>
              <span class="action-text">点赞</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">💬</span>
              <span class="action-text">评论 {{ post.comment_count }}</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">🔄</span>
              <span class="action-text">转发</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">👁️</span>
              <span class="action-text">浏览 {{ post.view_count }}</span>
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from 'vue'
import { getPostsApi, createPostApi } from '../api/basketball'
import { userStore } from '../stores/user'

interface PostItem {
  id: number
  title: string
  content: string
  author: string
  view_count: number
  comment_count: number
  is_published: boolean
  created_at?: string
}

const loading = ref(false)
const posting = ref(false)

const posts = ref<PostItem[]>([])

const newPost = reactive({
  title: '',
  content: ''
})

const canPost = computed(() => {
  return newPost.title.trim() && newPost.content.trim()
})

const fetchPosts = async () => {
  loading.value = true
  try {
    const res: any = await getPostsApi()
    posts.value = res.data || []
  } catch (e) {
    console.error('获取帖子失败', e)
  } finally {
    loading.value = false
  }
}

const handleCreatePost = async () => {
  if (!canPost.value) {
    alert('请填写帖子标题和内容')
    return
  }
  posting.value = true
  try {
    await createPostApi({
      title: newPost.title.trim(),
      content: newPost.content.trim()
    })
    alert('发帖成功，已进入待审核队列')
    newPost.title = ''
    newPost.content = ''
    // 发帖后重新获取最新帖子列表
    await fetchPosts()
  } catch (e) {
    console.error('发帖失败', e)
  } finally {
    posting.value = false
  }
}

const formatTime = (time: string | undefined) => {
  if (!time) return '刚刚'
  const now = new Date()
  const postTime = new Date(time)
  const diff = now.getTime() - postTime.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return postTime.toLocaleDateString()
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.community-container {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.hero {
  margin-bottom: 24px;
  text-align: center;
}

.hero-text h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 600;
}

.hero-text p {
  color: #666;
  font-size: 16px;
}

/* 发帖卡片 */
.post-create-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  flex: 1;
}

.username {
  font-weight: 600;
  color: #333;
  font-size: 16px;
  display: block;
  margin-bottom: 4px;
}

.points {
  font-size: 12px;
  color: #667eea;
}

.post-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-title-input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 24px;
  border: 1px solid #e0e0e0;
  font-size: 14px;
  box-sizing: border-box;
  background-color: #f9f9f9;
  transition: all 0.3s ease;
}

.post-title-input:focus {
  outline: none;
  border-color: #667eea;
  background-color: #fff;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.post-content-input {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  font-size: 14px;
  line-height: 1.6;
  box-sizing: border-box;
  resize: vertical;
  min-height: 120px;
  transition: all 0.3s ease;
}

.post-content-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.post-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.post-tools {
  display: flex;
  gap: 16px;
}

.tool-btn {
  background: none;
  border: none;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.tool-btn:hover {
  background-color: #f0f0f0;
  color: #667eea;
}

.post-btn {
  padding: 10px 24px;
  border-radius: 24px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.post-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.post-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 帖子列表 */
.posts-container {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.posts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.posts-header h2 {
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.refresh-btn {
  padding: 6px 16px;
  border-radius: 16px;
  border: 1px solid #667eea;
  background: #fff;
  color: #667eea;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #667eea;
  color: #fff;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 16px;
}

.posts-list {
  list-style: none;
}

.post-card {
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.post-card:last-child {
  border-bottom: none;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.post-user {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.post-user .user-info {
  margin-bottom: 0;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.time {
  font-size: 12px;
  color: #999;
}

.status-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background-color: #fff3cd;
  color: #ff9800;
}

.status-tag.approved {
  background-color: #d4edda;
  color: #4caf50;
}

.post-content {
  margin-bottom: 16px;
}

.post-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.post-text {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
  white-space: pre-wrap;
}

.post-actions {
  display: flex;
  gap: 24px;
  padding-top: 12px;
  border-top: 1px solid #f9f9f9;
}

.action-btn {
  background: none;
  border: none;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  padding: 8px 0;
  transition: all 0.2s ease;
}

.action-btn:hover {
  color: #667eea;
  transform: translateY(-1px);
}

.action-icon {
  font-size: 16px;
}

.action-text {
  font-size: 13px;
}

@media (max-width: 768px) {
  .community-container {
    padding: 16px;
    max-width: 100%;
  }
  
  .post-create-card,
  .posts-container {
    padding: 16px;
  }
  
  .post-actions {
    gap: 16px;
  }
  
  .action-btn {
    font-size: 12px;
  }
}
</style>