<template>
  <div class="home-container">
    <section class="hero">
      <div class="hero-text">
        <h1>篮球资讯中心</h1>
        <p>实时比分、权威资讯，一站式篮球资讯平台。</p>
      </div>
    </section>

    <section class="content-grid">
      <div class="card scores-card">
        <div class="card-header">
          <h2>今日焦点比赛</h2>
          <button class="refresh-btn" @click="fetchFeed" :disabled="loading">
            {{ loading ? '刷新中...' : '刷新' }}
          </button>
        </div>
        <div v-if="feed.games.length === 0" class="empty-text">
          暂无比赛数据，试试点击刷新。
        </div>
        <ul v-else class="game-list">
          <li v-for="(game, index) in feed.games" :key="index" class="game-item">
            <div class="teams">
              <span class="league">{{ game.league }}</span>
              <span class="team-name">{{ game.home_team }}</span>
              <span class="score">{{ game.home_score }} : {{ game.away_score }}</span>
              <span class="team-name">{{ game.away_team }}</span>
            </div>
            <div class="meta">
              <span class="status">{{ formatStatus(game.status) }}</span>
              <a
                v-if="game.external_url"
                class="link"
                :href="game.external_url"
                target="_blank"
                rel="noopener noreferrer"
              >
                查看详情（跳转 NBA 官网等）
              </a>
            </div>
          </li>
        </ul>
      </div>

      <div class="card news-card">
        <div class="card-header">
          <h2>最新篮球资讯</h2>
        </div>
        <div v-if="feed.news.length === 0" class="empty-text">
          暂无资讯。
        </div>
        <ul v-else class="news-list">
          <li v-for="(item, index) in feed.news" :key="index" class="news-item">
            <div class="news-main">
              <h3>{{ item.title }}</h3>
              <p class="summary">{{ item.summary }}</p>
            </div>
            <div class="news-meta">
              <span class="source">{{ item.source_name || '篮球资讯' }}</span>
              <a
                v-if="item.external_url"
                class="link"
                :href="item.external_url"
                target="_blank"
                rel="noopener noreferrer"
              >
                查看原文
              </a>
            </div>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { getFeedApi } from '../api/basketball'

interface Game {
  league: string
  home_team: string
  away_team: string
  home_score: number
  away_score: number
  status: string
  external_url?: string
}

interface NewsItem {
  title: string
  summary: string
  source: string
  source_name?: string
  external_url?: string
}

const loading = ref(false)

const feed = reactive<{
  games: Game[]
  news: NewsItem[]
}>({
  games: [],
  news: []
})

const fetchFeed = async () => {
  loading.value = true
  try {
    const res: any = await getFeedApi()
    feed.games = res.data.games || []
    feed.news = res.data.news || []
  } catch (e) {
    console.error('获取资讯失败', e)
  } finally {
    loading.value = false
  }
}

const formatStatus = (status: string) => {
  switch (status) {
    case 'live':
      return '进行中'
    case 'finished':
      return '已结束'
    case 'scheduled':
    default:
      return '未开始'
  }
}

onMounted(() => {
  fetchFeed()
})
</script>

<style scoped>
.home-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  margin-bottom: 24px;
}

.hero-text h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.hero-text p {
  color: #666;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1.5fr;
  gap: 20px;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-header h2 {
  font-size: 18px;
  color: #333;
}

.refresh-btn {
  padding: 6px 12px;
  border-radius: 16px;
  border: none;
  background: #667eea;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-text {
  color: #999;
  font-size: 14px;
}

.game-list {
  list-style: none;
}

.game-item {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.game-item:last-child {
  border-bottom: none;
}

.teams {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.league {
  font-size: 12px;
  color: #667eea;
  padding: 2px 8px;
  border-radius: 10px;
  background: #f0f2ff;
}

.team-name {
  font-weight: 500;
}

.score {
  font-weight: 600;
  color: #333;
}

.meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.status {
  color: #999;
}

.link {
  color: #667eea;
  text-decoration: none;
}

.news-list {
  list-style: none;
}

.news-item {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.news-item:last-child {
  border-bottom: none;
}

.news-main h3 {
  font-size: 15px;
  margin-bottom: 4px;
}

.summary {
  font-size: 13px;
  color: #666;
}

.news-meta {
  margin-top: 4px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.source {
  font-style: italic;
}

@media (max-width: 900px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>