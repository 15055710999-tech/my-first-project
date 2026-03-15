<template>
  <div class="community-container">
    <section class="hero">
      <div class="hero-text">
        <h1>球迷社区</h1>
        <p>分享你的篮球见解，与球迷一起交流讨论。</p>
      </div>
    </section>

    <!-- 发帖区域 - 可收缩 -->
    <div class="post-create-wrapper">
      <!-- 圆形展开按钮 -->
      <button 
        v-if="!isPostFormExpanded" 
        class="expand-post-btn"
        @click="togglePostForm"
        title="发布新帖"
      >
        <span class="plus-icon">+</span>
      </button>
      
      <!-- 发帖表单 -->
      <div v-show="isPostFormExpanded" class="post-create-card">
        <div class="post-form-header">
          <span class="form-title">发布新帖</span>
          <button class="collapse-btn" @click="togglePostForm" title="收起">
            <span>−</span>
          </button>
        </div>
        <div class="user-info">
          <div class="avatar">
            <img :src="`https://ui-avatars.com/api/?name=${userStore.userInfo?.username || 'User'}&background=667eea&color=fff`" alt="头像">
          </div>
          <div class="user-details">
            <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
          </div>
        </div>
        
        <form class="post-form" @submit.prevent="handleCreatePost" enctype="multipart/form-data">
          <div class="input-group">
            <input
              v-model="newPost.title"
              class="post-title-input"
              type="text"
              placeholder="分享一个与篮球有关的话题标题..."
              maxlength="50"
            />
            <span class="char-count" :class="{ 'over-limit': newPost.title.length > 50 }">
              {{ newPost.title.length }}/50
            </span>
          </div>
          <div class="input-group">
            <textarea
              ref="contentTextarea"
              v-model="newPost.content"
              class="post-content-input"
              rows="4"
              placeholder="写下你的看法或比赛心得，分享给大家..."
              maxlength="2000"
            />
            <span class="char-count" :class="{ 'over-limit': actualContentLength > 2000 }">
              {{ actualContentLength }}/2000
            </span>
          </div>
          <!-- 图片预览区域 -->
          <div v-if="extractedImages.length > 0" class="image-preview-area">
            <div v-for="(img, index) in extractedImages" :key="index" class="preview-item">
              <img :src="img" alt="预览图片">
              <button type="button" @click="removeImage(index)" class="remove-preview-btn">✕</button>
            </div>
          </div>
          <div class="post-actions">
            <div class="post-tools">
              <label class="upload-btn">
                <input type="file" @change="handleImageUpload" accept="image/*" style="display: none;">
                <span>📷 插入图片</span>
              </label>
              <button type="button" class="tool-btn" @click="openTagInput">
                # 添加话题
              </button>
              <div v-if="showTagInput" class="tag-input-container">
                <input 
                  v-model="newTag" 
                  @keyup.enter="addTag"
                  type="text" 
                  placeholder="输入话题后按回车添加"
                  class="tag-input"
                />
                <button type="button" @click="showTagInput = false" class="close-tag-btn">✕</button>
              </div>
              <div v-if="newPost.tags && newPost.tags.length > 0" class="tags-display">
                <span v-for="(tag, index) in newPost.tags" :key="index" class="tag-item">
                  #{{ tag }}
                  <button type="button" @click="removeTag(index)" class="remove-tag-btn">✕</button>
                </span>
              </div>
            </div>
            <button class="post-btn" type="submit" :disabled="posting || !canPost">
              {{ posting ? '发布中...' : '发布' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 帖子列表 -->
    <div class="posts-container">
      <div class="posts-header">
        <div class="tabs">
          <button 
            class="tab-btn" 
            :class="{ active: currentTab === 'all' }"
            @click="currentTab = 'all'"
          >
            最新动态
          </button>
          <button 
            v-if="userStore.userInfo"
            class="tab-btn" 
            :class="{ active: currentTab === 'my' }"
            @click="currentTab = 'my'"
          >
            我的帖子
          </button>
        </div>
        <button class="refresh-btn" @click="refreshPosts" :disabled="loading">
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
      </div>

      <div v-if="posts.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>{{ currentTab === 'my' ? '你还没有发布过帖子' : '还没有帖子，来当第一个发帖的球迷吧！' }}</p>
      </div>
      <ul v-else class="posts-list-simple">
        <li v-for="post in posts" :key="post.id" class="post-item-simple" @click="viewPostDetail(post)">
          <div class="post-title-simple">{{ post.title }}</div>
          <div class="post-stats-simple">
            <span class="stat-item">👁️ {{ post.view_count }}</span>
            <span class="stat-item">💬 {{ post.comment_count }}回复</span>
            <span v-if="currentTab === 'my'" class="status-tag-simple" :class="post.moderation_status">
              {{ getStatusText(post.moderation_status) }}
            </span>
          </div>
        </li>
      </ul>
    </div>
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
            <img :src="`https://ui-avatars.com/api/?name=${currentPost.author}&background=667eea&color=fff`" alt="头像">
          </div>
          <div class="user-info">
            <span class="username">{{ currentPost.author }}</span>
            <span class="time">{{ formatTime(currentPost.created_at) }}</span>
            <span v-if="currentPost.is_essence" class="essence-tag">精华</span>
          </div>
          <!-- 删除按钮 - 只有作者可以删除 -->
          <button 
            v-if="canDeletePost(currentPost)" 
            class="delete-btn"
            @click="handleDeletePost(currentPost.id)"
            title="删除帖子"
          >
            🗑️
          </button>
        </div>
        <h2 class="detail-post-title">{{ currentPost.title }}</h2>
        <div class="detail-post-body" v-html="renderContent(currentPost.content)"></div>
        <div class="detail-post-actions">
          <span class="action-stat">👁️ {{ currentPost.view_count }} 浏览</span>
          <span class="action-stat">💬 {{ currentPost.comment_count }} 回复</span>
        </div>
        
        <!-- 评论区域 -->
        <div class="comments-section">
          <h3 class="comments-title">评论 ({{ currentPost.comments?.length || 0 }})</h3>
          
          <!-- 发表评论或回复评论 -->
          <div v-if="userStore.userInfo" class="comment-input-area">
            <div v-if="replyingTo" class="reply-tip">
              回复 <span class="reply-author">{{ replyingTo.author }}</span>:
              <button class="cancel-reply-btn" @click="cancelReply">取消</button>
            </div>
            <textarea
              v-model="newComment"
              class="comment-input"
              rows="3"
              :placeholder="replyingTo ? '回复评论...' : '发表你的评论...'"
              maxlength="500"
            />
            <div class="comment-actions">
              <span class="char-count">{{ newComment.length }}/500</span>
              <button 
                class="comment-submit-btn" 
                @click="submitComment"
                :disabled="!newComment.trim() || commenting"
              >
                {{ commenting ? '发送中...' : (replyingTo ? '回复' : '发表评论') }}
              </button>
            </div>
          </div>
          <div v-else class="login-tip">
            请<a @click="goToLogin">登录</a>后发表评论
          </div>
          
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
                <div class="comment-actions-right">
                  <button 
                    v-if="userStore.userInfo" 
                    class="reply-btn" 
                    @click="startReply(comment)"
                  >
                    回复
                  </button>
                  <button 
                    v-if="canDeleteComment(comment)" 
                    class="delete-comment-btn" 
                    @click="deleteComment(comment)"
                    :disabled="deletingComment === comment.id"
                  >
                    {{ deletingComment === comment.id ? '删除中...' : '删除' }}
                  </button>
                </div>
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
  
  <!-- 图片查看器 -->
  <div 
    v-if="imageViewer.show" 
    class="image-viewer-overlay"
    @click="imageViewer.show = false"
  >
    <img :src="imageViewer.src" alt="查看原图">
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getPostsApi, createPostApi, deletePostApi, getMyPostsApi, getPostDetailApi, createCommentApi, deleteCommentApi } from '../api/basketball'
import { userStore } from '../stores/user'

const router = useRouter()

interface CommentItem {
  id: number
  content: string
  author: string
  author_id?: number
  parent_comment_id?: number | null
  parent_comment_author?: string | null
  created_at?: string
}

interface PostItem {
  id: number
  title: string
  content: string
  author: string
  author_id?: number
  view_count: number
  comment_count: number
  is_essence: boolean
  is_published?: boolean
  moderation_status?: string
  cover_image?: string
  images?: string[]
  tags?: string[]
  created_at?: string
  comments?: CommentItem[]
}

const loading = ref(false)
const posting = ref(false)
const showTagInput = ref(false)
const newTag = ref('')
const expandedPosts = ref<Set<number>>(new Set())
const currentTab = ref<'all' | 'my'>('all')
const contentTextarea = ref<HTMLTextAreaElement | null>(null)

// 评论相关
const newComment = ref('')
const commenting = ref(false)
const replyingTo = ref<CommentItem | null>(null)
const deletingComment = ref<number | null>(null)

const posts = ref<PostItem[]>([])

// 存储图片数据，使用短标记 [img:0], [img:1] 等
const imageStore = ref<string[]>([])

// 图片查看器状态
const imageViewer = ref({
  show: false,
  src: ''
})

// 帖子详情查看状态
const currentPost = ref<PostItem | null>(null)

const newPost = reactive({
  title: '',
  content: '',
  tags: [] as string[]
})

// 发帖框展开状态
const isPostFormExpanded = ref(false)

// 切换发帖框展开/收起
const togglePostForm = () => {
  isPostFormExpanded.value = !isPostFormExpanded.value
}

// 实际内容长度（排除图片标记）
const actualContentLength = computed(() => {
  return newPost.content.replace(/\[img:\d+\]/g, '').length
})

// 从内容中提取所有图片
const extractedImages = computed(() => {
  const images: string[] = []
  const regex = /\[img:(\d+)\]/g
  let match: RegExpExecArray | null
  while ((match = regex.exec(newPost.content)) !== null) {
    if (match[1]) {
      const index = parseInt(match[1])
      if (imageStore.value[index]) {
        images.push(imageStore.value[index])
      }
    }
  }
  return images
})

const canPost = computed(() => {
  return newPost.title.trim() && newPost.content.trim()
})

// 打开图片查看器
const openImageViewer = (src: string) => {
  imageViewer.value.src = src
  imageViewer.value.show = true
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
  escaped = escaped.replace(/\[img:(data:image\/[^\]]+)\]/g, '<img src="$1" data-src="$1" class="inline-image" alt="帖子图片" onclick="window.openImageViewer && window.openImageViewer(this.dataset.src)">')

  return escaped
}

// 将 openImageViewer 挂载到 window 对象，以便在 v-html 中调用
if (typeof window !== 'undefined') {
  (window as any).openImageViewer = openImageViewer
}

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

const fetchMyPosts = async () => {
  loading.value = true
  try {
    const res: any = await getMyPostsApi()
    posts.value = res.data || []
  } catch (e) {
    console.error('获取我的帖子失败', e)
  } finally {
    loading.value = false
  }
}

const refreshPosts = () => {
  if (currentTab.value === 'all') {
    fetchPosts()
  } else {
    fetchMyPosts()
  }
}

// 监听标签切换
watch(currentTab, (newTab) => {
  expandedPosts.value.clear() // 清空展开状态
  if (newTab === 'all') {
    fetchPosts()
  } else {
    fetchMyPosts()
  }
})

// 获取审核状态文本
const getStatusText = (status?: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待审核',
    'approved': '已通过',
    'rejected': '已拒绝'
  }
  return statusMap[status || ''] || status || '未知'
}

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      const result = e.target?.result as string
      if (result) {
        // 查找可用的最小索引（复用已删除的位置）
        let imageIndex = 0
        const usedIndices = new Set<number>()
        const regex = /\[img:(\d+)\]/g
        let match: RegExpExecArray | null
        while ((match = regex.exec(newPost.content)) !== null) {
          if (match[1]) {
            usedIndices.add(parseInt(match[1]))
          }
        }
        // 找到第一个未使用的索引
        while (usedIndices.has(imageIndex)) {
          imageIndex++
        }
        
        // 存储图片
        imageStore.value[imageIndex] = result
        
        // 在光标位置插入短图片标记
        const imgTag = `[img:${imageIndex}]\n`
        const textarea = contentTextarea.value
        if (textarea) {
          const start = textarea.selectionStart
          const end = textarea.selectionEnd
          const text = newPost.content
          newPost.content = text.substring(0, start) + imgTag + text.substring(end)
          // 设置光标位置到插入的图片后面
          setTimeout(() => {
            textarea.focus()
            const newPos = start + imgTag.length
            textarea.setSelectionRange(newPos, newPos)
          }, 0)
        } else {
          // 如果无法获取光标位置，追加到末尾
          newPost.content += imgTag
        }
      }
    }
    reader.readAsDataURL(file)
  }
  // 清空 input，允许重复选择同一文件
  target.value = ''
}

// 删除图片
const removeImage = (previewIndex: number) => {
  // 找到对应的图片索引
  const regex = /\[img:(\d+)\]/g
  let match: RegExpExecArray | null
  let currentIndex = 0
  let foundIndex = -1
  
  while ((match = regex.exec(newPost.content)) !== null) {
    if (match[1] && currentIndex === previewIndex) {
      foundIndex = parseInt(match[1])
      // 从内容中移除对应的图片标记
      const imgTag = `[img:${foundIndex}]`
      newPost.content = newPost.content.replace(imgTag + '\n', '').replace(imgTag, '')
      // 清理 imageStore 中该位置的图片
      imageStore.value[foundIndex] = ''
      break
    }
    currentIndex++
  }
}

const openTagInput = () => {
  showTagInput.value = true
}

const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !newPost.tags.includes(tag)) {
    newPost.tags.push(tag)
    newTag.value = ''
  }
}

const removeTag = (index: number) => {
  newPost.tags.splice(index, 1)
}

// 查看帖子详情
const viewPostDetail = async (post: PostItem) => {
  try {
    const res: any = await getPostDetailApi(post.id)
    if (res.code === 200) {
      currentPost.value = res.data
      // 更新列表中的浏览量
      const index = posts.value.findIndex(p => p.id === post.id)
      if (index !== -1 && res.data.view_count !== undefined) {
        const targetPost = posts.value[index]
        if (targetPost) {
          targetPost.view_count = res.data.view_count
        }
      }
    }
  } catch (e) {
    console.error('获取帖子详情失败', e)
    currentPost.value = post
  }
}

// 关闭帖子详情
const closePostDetail = () => {
  currentPost.value = null
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// 发表评论
const submitComment = async () => {
  if (!newComment.value.trim() || !currentPost.value) return
  
  commenting.value = true
  try {
    const res: any = await createCommentApi(currentPost.value.id, {
      content: newComment.value.trim(),
      parent_comment_id: replyingTo.value ? replyingTo.value.id : null
    })
    if (res.code === 200) {
      // 添加新评论到列表
      if (!currentPost.value.comments) {
        currentPost.value.comments = []
      }
      currentPost.value.comments.unshift(res.data)
      currentPost.value.comment_count += 1
      newComment.value = ''
      replyingTo.value = null
      
      // 更新列表中的评论数
      const postId = currentPost.value.id
      const index = posts.value.findIndex(p => p.id === postId)
      if (index !== -1) {
        const targetPost = posts.value[index]
        if (targetPost) {
          targetPost.comment_count = currentPost.value.comment_count
        }
      }
    }
  } catch (e) {
    console.error('发表评论失败', e)
    alert('发表评论失败，请重试')
  } finally {
    commenting.value = false
  }
}

// 开始回复评论
const startReply = (comment: CommentItem) => {
  replyingTo.value = comment
  newComment.value = ''
}

// 取消回复
const cancelReply = () => {
  replyingTo.value = null
  newComment.value = ''
}

// 判断是否可以删除评论
const canDeleteComment = (comment: CommentItem) => {
  const currentUser = userStore.userInfo
  if (!currentUser) return false
  
  // 检查是否是评论作者
  const isCommentAuthor = comment.author_id === currentUser.id || comment.author === currentUser.username
  
  // 检查是否是帖子作者
  const isPostAuthor = currentPost.value && 
    (currentPost.value.author_id === currentUser.id || currentPost.value.author === currentUser.username)
  
  return isCommentAuthor || isPostAuthor
}

// 删除评论
const deleteComment = async (comment: CommentItem) => {
  if (!confirm('确定要删除这条评论吗？此操作不可恢复。')) {
    return
  }
  
  deletingComment.value = comment.id
  try {
    const res: any = await deleteCommentApi(comment.id)
    if (res.code === 200) {
      // 从列表中删除评论
      if (currentPost.value && currentPost.value.comments) {
        const index = currentPost.value.comments.findIndex(c => c.id === comment.id)
        if (index !== -1) {
          currentPost.value.comments.splice(index, 1)
          currentPost.value.comment_count -= 1
          
          // 更新列表中的评论数
          const postIndex = posts.value.findIndex(p => p.id === currentPost.value?.id)
          if (postIndex !== -1) {
            const targetPost = posts.value[postIndex]
            if (targetPost) {
              targetPost.comment_count = currentPost.value.comment_count
            }
          }
        }
      }
    }
  } catch (e) {
    console.error('删除评论失败', e)
    alert('删除评论失败，请重试')
  } finally {
    deletingComment.value = null
  }
}

// 判断是否可以删除帖子（只有作者本人可以删除）
const canDeletePost = (post: PostItem) => {
  const currentUser = userStore.userInfo
  if (!currentUser) return false
  
  // 只有作者本人可以删除自己的帖子
  const isAuthor = post.author_id === currentUser.id || post.author === currentUser.username
  
  return isAuthor
}

// 删除帖子
const handleDeletePost = async (postId: number) => {
  if (!confirm('确定要删除这条帖子吗？此操作不可恢复。')) {
    return
  }
  
  try {
    await deletePostApi(postId)
    alert('帖子删除成功')
    // 从列表中移除已删除的帖子
    posts.value = posts.value.filter(post => post.id !== postId)
  } catch (e: any) {
    console.error('删除帖子失败', e)
    alert(e.response?.data?.message || '删除失败，请重试')
  }
}

const formatTime = (time: string | undefined) => {
  if (!time) return '刚刚'
  
  // 将服务器时间（UTC）转换为本地时间
  const now = new Date()
  // 后端返回的时间字符串是UTC时间，需要加上8小时转换为北京时间
  const utcTime = new Date(time)
  const postTime = new Date(utcTime.getTime() + 8 * 60 * 60 * 1000)
  
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

const handleCreatePost = async () => {
  // 字数限制检查
  if (newPost.title.length > 50) {
    alert('标题不能超过50字')
    return
  }
  if (actualContentLength.value > 2000) {
    alert('内容不能超过2000字')
    return
  }
  
  if (!canPost.value) {
    alert('请填写帖子标题和内容')
    return
  }
  posting.value = true
  try {
    // 构建完整内容：将短标记替换为完整图片数据
    let fullContent = newPost.content
    // 替换 [img:index] 为 [img:base64data]
    fullContent = fullContent.replace(/\[img:(\d+)\]/g, (_match, index) => {
      const imgData = imageStore.value[parseInt(index)]
      return imgData ? `[img:${imgData}]` : ''
    })
    
    await createPostApi({
      title: newPost.title.trim(),
      content: fullContent.trim(),
      images: [],
      tags: newPost.tags
    })
    alert('发帖成功，已进入待审核队列，等待管理员审核')
    newPost.title = ''
    newPost.content = ''
    newPost.tags = []
    imageStore.value = [] // 清空图片存储
    showTagInput.value = false
    // 发帖后重新获取最新帖子列表
    await fetchPosts()
  } catch (e) {
    console.error('发帖失败', e)
  } finally {
    posting.value = false
  }
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

/* 发帖区域包装器 */
.post-create-wrapper {
  position: relative;
  margin-bottom: 24px;
}

/* 圆形展开按钮 */
.expand-post-btn {
  position: fixed;
  right: 24px;
  top: 100px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #fff;
  font-size: 28px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
}

.expand-post-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.plus-icon {
  font-weight: 300;
  line-height: 1;
}

/* 发帖卡片 */
.post-create-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 发帖表单头部 */
.post-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.form-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.collapse-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  background-color: #f5f5f5;
  color: #667eea;
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

.input-group {
  position: relative;
}

.char-count {
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 12px;
  color: #999;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 4px;
}

.char-count.over-limit {
  color: #f56c6c;
  font-weight: 600;
}

.post-title-input {
  width: 100%;
  padding: 12px 16px;
  padding-right: 60px;
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
  padding-right: 70px;
  padding-bottom: 30px;
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
  flex-wrap: wrap;
}

.upload-btn {
  background: none;
  border: 1px solid #e0e0e0;
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

.upload-btn:hover {
  background-color: #f0f0f0;
  color: #667eea;
  border-color: #667eea;
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

/* 图片预览区域 */
.image-preview-area {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.preview-item {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-preview-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  border: none;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.remove-preview-btn:hover {
  background: rgba(244, 67, 54, 0.8);
}

.tag-input-container {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-input {
  width: 200px;
  padding: 8px 12px;
  border-radius: 20px;
  border: 1px solid #e0e0e0;
  font-size: 14px;
  outline: none;
}

.tag-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.close-tag-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #999;
  padding: 4px;
  transition: all 0.2s ease;
}

.close-tag-btn:hover {
  color: #f56c6c;
}

.tags-display {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.tag-item {
  background-color: #e8f4fd;
  color: #667eea;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.tag-item:hover {
  background-color: #667eea;
  color: #fff;
}

.remove-tag-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  color: #fff;
  padding: 2px;
  transition: all 0.2s ease;
}

.remove-tag-btn:hover {
  color: #f56c6c;
}

.uploaded-images {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.image-preview {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #f56c6c;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.remove-image-btn:hover {
  background: rgba(255, 255, 255, 1);
  color: #fff;
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

/* 标签切换 */
.tabs {
  display: flex;
  gap: 16px;
}

.tab-btn {
  padding: 8px 16px;
  border: none;
  background: none;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: #667eea;
}

.tab-btn.active {
  color: #667eea;
  font-weight: 600;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 0;
  right: 0;
  height: 2px;
  background: #667eea;
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
}

.stat-item {
  font-size: 12px;
  color: #999;
}

.status-tag-simple {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.status-tag-simple.pending {
  background-color: #fff3e0;
  color: #ff9800;
}

.status-tag-simple.approved {
  background-color: #e8f5e9;
  color: #4caf50;
}

.status-tag-simple.rejected {
  background-color: #ffebee;
  color: #f44336;
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
  gap: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.action-stat {
  font-size: 14px;
  color: #666;
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

.comment-input-area {
  background: #f9f9f9;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.comment-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
  margin-bottom: 12px;
}

.comment-input:focus {
  outline: none;
  border-color: #667eea;
}

.comment-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  padding: 10px 24px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.comment-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.comment-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-tip {
  text-align: center;
  padding: 20px;
  color: #999;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 20px;
}

.login-tip a {
  color: #667eea;
  cursor: pointer;
  text-decoration: underline;
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

.reply-tip {
  font-size: 13px;
  color: #667eea;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reply-author {
  font-weight: 600;
}

.cancel-reply-btn {
  background: none;
  border: 1px solid #ddd;
  color: #666;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-reply-btn:hover {
  border-color: #999;
  color: #333;
}

.comment-actions-right {
  display: flex;
  gap: 8px;
}

.reply-btn {
  background: none;
  border: none;
  color: #667eea;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reply-btn:hover {
  background: rgba(102, 126, 234, 0.1);
}

.delete-comment-btn {
  background: none;
  border: none;
  color: #e74c3c;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-comment-btn:hover:not(:disabled) {
  background: rgba(231, 76, 60, 0.1);
}

.delete-comment-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

/* 删除按钮 */
.delete-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  opacity: 0.5;
  transition: all 0.2s ease;
}

.delete-btn:hover {
  opacity: 1;
  background-color: #ffebee;
  transform: scale(1.1);
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

.essence-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background-color: #ff9800;
  color: #fff;
}

/* 审核状态标签 */
.status-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.status-tag.pending {
  background-color: #fff3e0;
  color: #ff9800;
}

.status-tag.approved {
  background-color: #e8f5e9;
  color: #4caf50;
}

.status-tag.rejected {
  background-color: #ffebee;
  color: #f44336;
  color: #fff;
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

.post-text-wrapper {
  position: relative;
}

.post-text {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
  white-space: pre-wrap;
  margin: 0;
  transition: all 0.3s ease;
}

/* 内联图片样式 - 使用 :deep() 确保应用到 v-html 内容 */
:deep(.inline-image) {
  max-width: 750px;
  max-height: 600px;
  width: auto;
  height: auto;
  border-radius: 8px;
  margin: 12px auto;
  display: block;
  cursor: zoom-in;
  transition: opacity 0.2s ease;
  object-fit: contain;
}

:deep(.inline-image:hover) {
  opacity: 0.85;
}

/* 图片查看器遮罩层 */
.image-viewer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: zoom-out;
}

.image-viewer-overlay img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

/* 折叠状态下的样式 */
.post-text.collapsed {
  max-height: 200px;
  overflow: hidden;
  position: relative;
}

.post-text.collapsed::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: linear-gradient(transparent, rgba(255, 255, 255, 0.9));
  pointer-events: none;
}

.expand-btn {
  background: none;
  border: none;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 0;
  margin-top: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.expand-btn:hover {
  color: #764ba2;
  text-decoration: underline;
}

.post-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.post-tag {
  background-color: #e8f4fd;
  color: #667eea;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  transition: all 0.2s ease;
}

.post-tag:hover {
  background-color: #667eea;
  color: #fff;
}

.post-images {
  margin-top: 12px;
}

/* 图片预览容器（折叠状态） */
.images-preview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  position: relative;
}

/* 更多图片遮罩 */
.more-images-overlay {
  position: absolute;
  right: 0;
  bottom: 0;
  width: calc(33.333% - 5.333px);
  aspect-ratio: 1;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.more-images-overlay:hover {
  background: rgba(0, 0, 0, 0.7);
}

.more-count {
  color: #fff;
  font-size: 20px;
  font-weight: 600;
}

/* 展开状态的图片网格 */
.post-images > template:first-child + * {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

/* 单张图片样式 */
.post-image {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* 预览模式下的图片 */
.images-preview .post-image {
  aspect-ratio: 1;
}

.post-image:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 单张图片时显示更大 */
.post-images:has(> template:first-child + * > img:only-child),
.post-images:has(> .images-preview > img:only-child) {
  max-width: 400px;
}

.post-images:has(> template:first-child + * > img:only-child) .post-image,
.post-images:has(> .images-preview > img:only-child) .post-image {
  aspect-ratio: 16/9;
}

.post-actions-bar {
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