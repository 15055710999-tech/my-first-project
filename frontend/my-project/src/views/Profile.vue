<template>
  <div class="profile-container">
    <section class="hero">
      <div class="hero-text">
        <h1>个人中心</h1>
        <p>管理你的个人信息和设置</p>
      </div>
    </section>

    <div class="profile-content">
      <!-- 左侧导航 -->
      <div class="profile-sidebar">
        <div class="user-card">
          <div class="avatar-container">
            <img 
              :src="userInfo.avatar || 'https://neeko-copilot.bytedance.net/api/text2image?prompt=default%20user%20avatar%20placeholder&size=200x200'" 
              :alt="userInfo.username"
              class="avatar"
            />
            <button class="avatar-upload-btn" @click="triggerAvatarUpload">
              更换头像
            </button>
          </div>
          <h3>{{ userInfo.username }}</h3>
          <p class="user-level">Lv.{{ userInfo.level }}</p>
          <p class="user-points">积分: {{ userInfo.points }}</p>
        </div>
        
        <div class="sidebar-menu">
          <button 
            :class="['menu-item', { active: activeTab === 'basic' }]"
            @click="activeTab = 'basic'"
          >
            <span class="menu-icon">👤</span>
            基本信息
          </button>
          <button 
            :class="['menu-item', { active: activeTab === 'password' }]"
            @click="activeTab = 'password'"
          >
            <span class="menu-icon">🔒</span>
            修改密码
          </button>
           <button 
            :class="['menu-item', { active: activeTab === 'liked' }]"
            @click="activeTab = 'liked'"
          >
            <span class="menu-icon">❤️</span>
            我的点赞
          </button>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="profile-main">
        <!-- 基本信息编辑 -->
        <div v-if="activeTab === 'basic'" class="tab-content">
          <h2>基本信息</h2>
          <form @submit.prevent="updateProfile" class="profile-form">
            <div class="form-group">
              <label>用户名</label>
              <input 
                type="text" 
                v-model="form.username" 
                class="form-input"
                :disabled="isUpdating"
              />
              <p v-if="errors.username" class="error-message">{{ errors.username }}</p>
            </div>

            <div class="form-group">
              <label>邮箱</label>
              <input 
                type="email" 
                v-model="form.email" 
                class="form-input"
                :disabled="isUpdating"
              />
              <p v-if="errors.email" class="error-message">{{ errors.email }}</p>
            </div>

            <div class="form-group">
              <label>手机号</label>
              <input 
                type="tel" 
                v-model="form.phone" 
                class="form-input"
                :disabled="isUpdating"
              />
              <p v-if="errors.phone" class="error-message">{{ errors.phone }}</p>
            </div>

            <div class="form-group">
              <label>性别</label>
              <select v-model="form.gender" class="form-select" :disabled="isUpdating">
                <option value="">请选择</option>
                <option value="male">男</option>
                <option value="female">女</option>
                <option value="other">其他</option>
              </select>
            </div>

            <div class="form-group">
              <label>出生年月</label>
              <div class="date-input-container">
                <input 
                  ref="dateInput"
                  type="date" 
                  v-model="form.birth_date" 
                  class="actual-date-input"
                  :disabled="isUpdating"
                  @change="handleNativeDateChange"
                />
                <div 
                  class="custom-date-input"
                  :class="{ 'disabled': isUpdating }"
                  @click="openDatePicker"
                >
                  {{ form.birth_date ? formattedBirthDate : '请选择出生年月' }}
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>个人简介</label>
              <textarea 
                v-model="form.bio" 
                class="form-textarea"
                rows="4"
                :disabled="isUpdating"
              ></textarea>
            </div>

            <div class="form-actions">
              <button 
                type="submit" 
                class="submit-btn"
                :disabled="isUpdating"
              >
                {{ isUpdating ? '保存中...' : '保存更改' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 密码修改 -->
        <div v-if="activeTab === 'password'" class="tab-content">
          <h2>修改密码</h2>
          <form @submit.prevent="changePassword" class="profile-form">
            <div class="form-group">
              <label>旧密码</label>
              <input 
                type="password" 
                v-model="passwordForm.old_password" 
                class="form-input"
                :disabled="isChangingPassword"
              />
              <p v-if="passwordErrors.old_password" class="error-message">{{ passwordErrors.old_password }}</p>
            </div>

            <div class="form-group">
              <label>新密码</label>
              <input 
                type="password" 
                v-model="passwordForm.new_password" 
                class="form-input"
                :disabled="isChangingPassword"
              />
              <p v-if="passwordErrors.new_password" class="error-message">{{ passwordErrors.new_password }}</p>
            </div>

            <div class="form-group">
              <label>确认新密码</label>
              <input 
                type="password" 
                v-model="passwordForm.confirm_password" 
                class="form-input"
                :disabled="isChangingPassword"
              />
              <p v-if="passwordErrors.confirm_password" class="error-message">{{ passwordErrors.confirm_password }}</p>
            </div>

            <div class="form-actions">
              <button 
                type="submit" 
                class="submit-btn"
                :disabled="isChangingPassword"
              >
                {{ isChangingPassword ? '修改中...' : '修改密码' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 我的点赞 -->
        <div v-if="activeTab === 'liked'" class="tab-content">
          <h2>我的点赞</h2>
          <div v-if="loadingLikedPosts" class="loading">
            加载中...
          </div>
          <div v-else-if="likedPosts.length === 0" class="no-posts">
            你还没有点赞过任何帖子
          </div>
          <ul v-else class="posts-list-simple">
            <li v-for="post in likedPosts" :key="post.id" class="post-item-simple">
              <div class="post-title-simple" @click="viewPostDetail(post)">{{ post.title }}</div>
              <div class="post-stats-simple">
                <span class="stat-item">👁️ {{ post.view_count }}</span>
                <span class="stat-item">💬 {{ post.comment_count }}回复</span>
                <button 
                  class="like-btn" 
                  @click.stop="handleLike(post)"
                  :class="{ 'liked': post.is_liked }"
                  title="点赞"
                >
                  <span class="like-icon">{{ post.is_liked ? '❤️' : '🤍' }}</span>
                  <span class="like-count">{{ post.like_count }}</span>
                </button>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 头像上传文件输入 -->
    <input 
      ref="avatarInput" 
      type="file" 
      accept="image/*" 
      style="display: none" 
      @change="handleAvatarUpload"
    />
  </div>

  <!-- 帖子详情页面 -->
  <div v-if="currentPost" class="post-detail-overlay">
    <div class="post-detail-container">
      <div class="post-detail-header">
        <button class="back-btn" @click="closePostDetail">
          ← 返回
        </button>
        <span class="detail-title">帖子详情</span>
      </div>
      <div class="post-detail-content">
        <div class="detail-post-header">
          <div class="avatar">
            <img :src="currentPost.author_avatar ? `http://localhost:8000${currentPost.author_avatar}` : `https://ui-avatars.com/api/?name=${currentPost.author}&background=667eea&color=fff&length=1`" alt="头像">
          </div>
          <div class="user-info">
            <span class="username">{{ currentPost.author }}</span>
            <span class="time">{{ formatTime(currentPost.created_at) }}</span>
            <span v-if="currentPost.is_essence" class="essence-tag">精华</span>
          </div>
        </div>
        <h2 class="detail-post-title">{{ currentPost.title }}</h2>
        <div class="detail-post-body" v-html="renderContent(currentPost.content)"></div>
        <div class="detail-post-actions">
          <div class="detail-actions-left">
            <span class="action-stat">👁️ {{ currentPost.view_count }} 浏览</span>
            <span class="action-stat">💬 {{ currentPost.comment_count }} 回复</span>
          </div>
          <button 
            class="detail-like-btn" 
            @click="handleLike(currentPost)"
            :class="{ 'liked': currentPost.is_liked }"
            title="点赞"
          >
            <span class="like-icon">{{ currentPost.is_liked ? '❤️' : '🤍' }}</span>
            <span class="like-count">{{ currentPost.like_count }}</span>
          </button>
        </div>
        
        <!-- 评论区域 -->
        <div class="comments-section">
          <h3 class="comments-title">评论 ({{ currentPost.comments?.length || 0 }})</h3>
          
          <!-- 评论列表 -->
          <div class="comments-list">
            <div v-if="!currentPost.comments || currentPost.comments.length === 0" class="no-comments">
              暂无评论，来抢沙发吧！
            </div>
            <div 
              v-for="comment in currentPost.comments" 
              :key="comment.id" 
              class="comment-item"
            >
              <div class="comment-header">
                <span class="comment-author">{{ comment.author }}</span>
                <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
              </div>
              <div v-if="comment.parent_comment_id" class="parent-comment">
                回复 <span class="reply-author">@{{ comment.parent_comment_author }}</span>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { userStore } from '../stores/user'
import { updateProfileApi, changePasswordApi, uploadAvatarApi } from '../api/user'
import { getMyLikedPostsApi, likePostApi, getPostDetailWithLikeStatusApi } from '../api/basketball'

const router = useRouter()
const avatarInput = ref<HTMLInputElement | null>(null)
const dateInput = ref<HTMLInputElement | null>(null)

// 状态管理
const activeTab = ref('basic')
const isUpdating = ref(false)
const isChangingPassword = ref(false)
const errors = ref({ username: '', email: '', phone: '' })
const passwordErrors = ref({ old_password: '', new_password: '', confirm_password: '' })

// 我的点赞相关
const likedPosts = ref<any[]>([])
const loadingLikedPosts = ref(false)
const currentPost = ref<any>(null)

// 用户信息
const userInfo = computed(() => userStore.userInfo || {
  id: 0,
  username: '',
  email: '',
  phone: '',
  avatar: '',
  level: 1,
  points: 0,
  points_balance: 0,
  gender: '',
  birth_date: '',
  bio: '',
  sign_in_streak: 0,
  is_staff: false
})

// 表单数据
const form = reactive({
  username: userInfo.value.username,
  email: userInfo.value.email || '',
  phone: userInfo.value.phone || '',
  gender: userInfo.value.gender || '',
  birth_date: userInfo.value.birth_date || '',
  bio: userInfo.value.bio || ''
})

// 格式化出生日期显示
const formattedBirthDate = computed(() => {
  if (!form.birth_date) return ''
  const date = new Date(form.birth_date)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
})

// 打开日期选择器
const openDatePicker = () => {
  if (!isUpdating.value) {
    const input = dateInput.value
    if (!input) return
    // 优先使用原生 showPicker（支持的浏览器体验更好）
    // 不支持时退回到 click()
    // @ts-ignore
    if (typeof input.showPicker === 'function') {
      // @ts-ignore
      input.showPicker()
    } else {
      input.click()
    }
  }
}

// 原生日期选择变化时，确保 v-model 已同步
const handleNativeDateChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target && target.value) {
    form.birth_date = target.value
  }
}

// 密码修改表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 触发头像上传
const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}





// 处理头像上传
const handleAvatarUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const formData = new FormData()
  formData.append('avatar', file)

  try {
    const res: any = await uploadAvatarApi(formData)
    if (res.code === 200) {
      // 更新用户信息
      if (userStore.userInfo) {
        const updatedUserInfo = {
          ...userStore.userInfo,
          avatar: `http://localhost:8000${res.data.avatar}`
        }
        userStore.setUserInfo(updatedUserInfo)
      }
      alert('头像更新成功！')
    }
  } catch (error) {
    console.error('头像上传失败', error)
    alert('头像上传失败，请重试')
  } finally {
    // 清空文件输入
    if (avatarInput.value) {
      avatarInput.value.value = ''
    }
  }
}

// 更新个人信息
const updateProfile = async () => {
  // 重置错误
  errors.value = { username: '', email: '', phone: '' }
  
  // 简单验证
  if (!form.username) {
    errors.value.username = '用户名不能为空'
    return
  }
  
  if (!form.email) {
    errors.value.email = '邮箱不能为空'
    return
  }

  isUpdating.value = true
  try {
    const res: any = await updateProfileApi(form)
    if (res.code === 200) {
      // 更新用户信息
      if (userStore.userInfo) {
        userStore.userInfo = {
          ...userStore.userInfo,
          ...form
        }
      }
      alert('个人信息更新成功！')
    } else {
      // 处理错误
      if (res.data) {
        Object.assign(errors.value, res.data)
      }
    }
  } catch (error) {
    console.error('更新失败', error)
    alert('更新失败，请重试')
  } finally {
    isUpdating.value = false
  }
}

// 修改密码
const changePassword = async () => {
  // 重置错误
  passwordErrors.value = { old_password: '', new_password: '', confirm_password: '' }
  
  // 验证
  if (!passwordForm.old_password) {
    passwordErrors.value.old_password = '旧密码不能为空'
    return
  }
  
  if (!passwordForm.new_password) {
    passwordErrors.value.new_password = '新密码不能为空'
    return
  }
  
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordErrors.value.confirm_password = '两次密码不一致'
    return
  }

  isChangingPassword.value = true
  try {
    const res: any = await changePasswordApi(passwordForm)
    if (res.code === 200) {
      alert('密码修改成功！')
      // 清空表单
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
    } else {
      if (res.data) {
        Object.assign(passwordErrors.value, res.data)
      }
    }
  } catch (error) {
    console.error('密码修改失败', error)
    alert('密码修改失败，请重试')
  } finally {
    isChangingPassword.value = false
  }
}

// 获取用户已点赞的帖子
const fetchLikedPosts = async () => {
  if (!userStore.userInfo) return
  
  loadingLikedPosts.value = true
  try {
    const res: any = await getMyLikedPostsApi()
    if (res.code === 200) {
      likedPosts.value = res.data || []
    }
  } catch (e) {
    console.error('获取已点赞帖子失败', e)
  } finally {
    loadingLikedPosts.value = false
  }
}

// 查看帖子详情
const viewPostDetail = async (post: any) => {
  try {
    const res: any = await getPostDetailWithLikeStatusApi(post.id)
    if (res.code === 200) {
      currentPost.value = res.data
      // 更新列表中的点赞状态
      const index = likedPosts.value.findIndex(p => p.id === post.id)
      if (index !== -1) {
        const targetPost = likedPosts.value[index]
        if (targetPost) {
          targetPost.like_count = res.data.like_count
          targetPost.is_liked = res.data.is_liked
        }
      }
    }
  } catch (e) {
    console.error('获取帖子详情失败', e)
    currentPost.value = post
  }
}

// 处理点赞
const handleLike = async (post: any) => {
  if (!userStore.userInfo) {
    alert('请先登录后再点赞')
    router.push('/login')
    return
  }
  
  try {
    const res: any = await likePostApi(post.id)
    if (res.code === 200) {
      // 更新帖子的点赞数和点赞状态
      post.like_count = res.data.like_count
      post.is_liked = res.data.is_liked
      
      // 如果是当前查看的帖子，也更新currentPost
      if (currentPost.value && currentPost.value.id === post.id) {
        currentPost.value.like_count = res.data.like_count
        currentPost.value.is_liked = res.data.is_liked
      }
    }
  } catch (e) {
    console.error('点赞操作失败', e)
    alert('点赞操作失败，请重试')
  }
}

// 关闭帖子详情
const closePostDetail = () => {
  currentPost.value = null
}

// 监听标签切换
watch(activeTab, (newTab) => {
  if (newTab === 'liked') {
    fetchLikedPosts()
  }
})

// 格式化时间显示
const formatTime = (time: string | undefined) => {
  if (!time) return '未知时间'
  
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

// 渲染内容，将图片标记转换为图片标签
const renderContent = (content: string) => {
  if (!content) return ''
  // 转义HTML特殊字符（防止XSS攻击）
  let escaped = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')

  // 将换行符转换为 <br>
  escaped = escaped.replace(/\n/g, '<br>')

  // 将 [img:base64data] 标记转换为图片标签（处理已发布的帖子）
  // 使用 data-src 存储原图地址，点击时打开查看器
  escaped = escaped.replace(/\[img:(data:image\/[^\]]+)\]/g, '<img src="$1" data-src="$1" class="inline-image" alt="帖子图片" style="max-width: 100%; height: auto;">')

  return escaped
}

// 页面加载时获取用户信息
onMounted(() => {
  // 同步表单数据
  form.username = userInfo.value.username
  form.email = userInfo.value.email || ''
  form.phone = userInfo.value.phone || ''
  form.gender = userInfo.value.gender || ''
  form.birth_date = userInfo.value.birth_date || ''
  form.bio = userInfo.value.bio || ''
})
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.hero {
  text-align: center;
  padding: 60px 20px;
  color: white;
}

.hero h1 {
  font-size: 32px;
  margin-bottom: 10px;
}

.hero p {
  font-size: 18px;
  opacity: 0.9;
}

.profile-content {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  gap: 30px;
}

.profile-sidebar {
  width: 300px;
  flex-shrink: 0;
}

.user-card {
  background: white;
  border-radius: 12px;
  padding: 30px 20px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.avatar-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 20px;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #667eea;
}

.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.avatar-upload-btn:hover {
  background: #764ba2;
  transform: scale(1.1);
}

.user-card h3 {
  font-size: 18px;
  margin-bottom: 10px;
  color: #333;
}

.user-level {
  color: #667eea;
  font-weight: 600;
  margin-bottom: 5px;
}

.user-points {
  color: #666;
  font-size: 14px;
}

.sidebar-menu {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.menu-item {
  width: 100%;
  padding: 15px 20px;
  border: none;
  background: none;
  text-align: left;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 12px;
}

.menu-item:hover {
  background: #f0f0f0;
  color: #667eea;
}

.menu-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.menu-icon {
  font-size: 16px;
}

.profile-main {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.tab-content h2 {
  font-size: 24px;
  margin-bottom: 30px;
  color: #333;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.form-input,
.form-select,
.form-textarea {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.error-message {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 4px;
}

.form-help {
  color: #666;
  font-size: 12px;
  margin-top: 4px;
}

.date-input-wrapper {
  position: relative;
}

.date-display {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  color: #667eea;
  font-weight: 500;
  pointer-events: none;
}

.date-input-container {
  position: relative;
  height: 44px;
}

.actual-date-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
  /* 不拦截鼠标事件，让点击落在自定义容器上触发 openDatePicker */
  pointer-events: none;
  padding: 0;
  margin: 0;
  border: none;
  background: transparent;
  display: block;
}

.custom-date-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
  cursor: pointer;
  background-color: #fff;
  position: relative;
  z-index: 1;
  /* 需要响应点击来打开日期选择器 */
  pointer-events: auto;
}

.custom-date-input:hover:not(.disabled) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.custom-date-input.disabled {
  cursor: not-allowed;
  opacity: 0.6;
  background-color: #f9f9f9;
}

.hidden-date-input {
  display: none;
}

.date-input-container {
  position: relative;
  height: 44px;
}

.actual-date-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
  /* 不拦截鼠标事件，让点击落在自定义容器上触发 openDatePicker */
  pointer-events: none;
  padding: 0;
  margin: 0;
  border: none;
  background: transparent;
  display: block;
}

.custom-date-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
  cursor: pointer;
  background-color: #fff;
  position: relative;
  z-index: 1;
  /* 需要响应点击来打开日期选择器 */
  pointer-events: auto;
}

.custom-date-input:hover:not(.disabled) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.custom-date-input.disabled {
  cursor: not-allowed;
  opacity: 0.6;
  background-color: #f9f9f9;
}

.form-actions {
  margin-top: 20px;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.no-posts {
  text-align: center;
  padding: 60px;
  color: #999;
  font-size: 16px;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-card {
  padding: 20px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.post-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.post-title {
  font-size: 18px;
  margin-bottom: 10px;
  color: #333;
}

.post-meta {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.post-status {
  display: inline-block;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.approved {
  background: #d4edda;
  color: #155724;
}

.status-badge.rejected {
  background: #f8d7da;
  color: #721c24;
}

/* 帖子详情页面 */
.post-detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 100;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 60px;
  overflow-y: auto;
}

.post-detail-container {
  background: #fff;
  width: 100%;
  max-width: 800px;
  max-height: calc(100vh - 80px);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.post-detail-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn {
  background: none;
  border: none;
  font-size: 14px;
  color: #667eea;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background-color: #f0f0f0;
}

.detail-title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-right: 60px;
}

.post-detail-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.detail-post-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-post-header .avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #667eea;
}

.detail-post-header .avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-post-header .user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-post-header .username {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.detail-post-header .time {
  font-size: 12px;
  color: #999;
}

.detail-post-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  line-height: 1.4;
}

.detail-post-body {
  font-size: 15px;
  color: #333;
  line-height: 1.8;
  margin-bottom: 20px;
}

.detail-post-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.detail-actions-left {
  display: flex;
  gap: 24px;
}

.action-stat {
  font-size: 14px;
  color: #666;
}

/* 点赞按钮样式 */
.like-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  font-size: 12px;
  color: #999;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 16px;
  transition: all 0.2s ease;
}

.like-btn:hover {
  background-color: #f0f0f0;
  color: #667eea;
}

.like-btn.liked {
  color: #f56c6c;
}

.like-btn.liked:hover {
  background-color: #ffebee;
}

.like-icon {
  font-size: 14px;
}

.like-count {
  font-size: 12px;
}

/* 详情页点赞按钮 */
.detail-like-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: 1px solid #e0e0e0;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.detail-like-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background-color: rgba(102, 126, 234, 0.05);
}

.detail-like-btn.liked {
  border-color: #f56c6c;
  color: #f56c6c;
  background-color: #ffebee;
}

.detail-like-btn.liked:hover {
  background-color: #fef0f0;
}

/* 评论区域样式 */
.comments-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.comments-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.no-comments {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 14px;
}

.comment-item {
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-author {
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.parent-comment {
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #f0f0f0;
  border-radius: 4px;
}

.parent-comment .reply-author {
  color: #667eea;
}

.essence-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background-color: #ff9800;
  color: #fff;
}

/* 简洁列表样式 */
.posts-list-simple {
  list-style: none;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  background: #fff;
}

.post-item-simple {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.post-item-simple:last-child {
  border-bottom: none;
}

.post-item-simple:hover {
  background-color: #f5f5f5;
}

.post-title-simple {
  flex: 1;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 16px;
}

.post-stats-simple {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  justify-content: flex-end;
  width: 300px;
}

.post-stats-simple .like-btn {
  margin-left: auto;
}

.stat-item {
  font-size: 12px;
  color: #999;
}

@media (max-width: 768px) {
  .profile-content {
    flex-direction: column;
  }
  
  .profile-sidebar {
    width: 100%;
  }
  
  .profile-main {
    padding: 20px;
  }
}
</style>