<template>
  <div class="players-container">
    <h1>职业 / 网红球员评分</h1>
    <p class="desc">
      一部分评分来自系统根据数据的评估，一部分来自用户打分。
      你可以选中球员并给出你的评分与简短评价。
    </p>

    <div class="players-grid">
      <div
        v-for="(player, index) in players"
        :key="index"
        class="player-card"
        @click="selectPlayer(player)"
      >
        <div class="avatar">
          <span>{{ player.name.charAt(0) }}</span>
        </div>
        <div class="info">
          <h2>{{ player.name }} <small v-if="player.nickname">（{{ player.nickname }}）</small></h2>
          <p class="meta">
            <span v-if="player.team">球队：{{ player.team }}</span>
            <span v-if="player.position"> 位置：{{ player.position }}</span>
          </p>
          <p class="score">
            系统评分：<strong>{{ player.system_score.toFixed(1) }}</strong>
            <span class="user-score">
              用户均分：{{ (player.average_user_score || 0).toFixed(1) }}
            </span>
          </p>
          <p class="tags">
            <span v-if="player.is_professional" class="tag pro">职业球员</span>
            <span v-if="player.is_influencer" class="tag hot">篮球网红</span>
          </p>
          <p class="desc-text" v-if="player.description">{{ player.description }}</p>
        </div>
      </div>
    </div>

    <div v-if="currentPlayer" class="rating-panel">
      <h2>给 {{ currentPlayer.name }} 打分</h2>
      <div class="rating-row">
        <label>评分（1~10 分）：</label>
        <input
          v-model.number="ratingForm.score"
          type="number"
          min="1"
          max="10"
        />
      </div>
      <div class="rating-row">
        <label>简短评价：</label>
        <textarea
          v-model="ratingForm.comment"
          rows="2"
          placeholder="可以简单写下你对他最近状态的评价"
        />
      </div>
      <button class="submit-btn" @click="handleRate" :disabled="ratingLoading">
        {{ ratingLoading ? '提交中...' : '提交评分' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { getPlayersApi, ratePlayerApi } from '../api/basketball'

interface Player {
  id?: number
  name: string
  nickname?: string
  team?: string
  position?: string
  is_professional: boolean
  is_influencer: boolean
  system_score: number
  average_user_score?: number
  description?: string
}

const players = ref<Player[]>([])
const currentPlayer = ref<Player | null>(null)
const ratingLoading = ref(false)

const ratingForm = reactive({
  score: 8,
  comment: ''
})

const fetchPlayers = async () => {
  try {
    const res: any = await getPlayersApi()
    players.value = res.data || []
  } catch (e) {
    console.error('获取球员列表失败', e)
  }
}

const selectPlayer = (player: Player) => {
  currentPlayer.value = player
}

const handleRate = async () => {
  if (!currentPlayer.value?.id) {
    alert('当前示例球员只是演示数据，创建实际球员后即可打分。')
    return
  }
  if (ratingForm.score < 1 || ratingForm.score > 10) {
    alert('评分必须在 1~10 分之间')
    return
  }
  ratingLoading.value = true
  try {
    await ratePlayerApi(currentPlayer.value.id, {
      score: ratingForm.score,
      comment: ratingForm.comment || undefined
    })
    alert('评分提交成功')
    ratingForm.comment = ''
    await fetchPlayers()
  } catch (e) {
    console.error('评分失败', e)
  } finally {
    ratingLoading.value = false
  }
}

onMounted(() => {
  fetchPlayers()
})
</script>

<style scoped>
.players-container {
  padding: 24px;
  max-width: 1100px;
  margin: 0 auto;
}

h1 {
  font-size: 26px;
  color: #333;
  margin-bottom: 8px;
}

.desc {
  color: #666;
  margin-bottom: 18px;
}

.players-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.player-card {
  display: flex;
  gap: 10px;
  background: #fff;
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.1s ease;
}

.player-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #667eea;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
}

.info h2 {
  font-size: 16px;
  margin-bottom: 4px;
}

.info small {
  font-weight: normal;
  color: #666;
}

.meta {
  font-size: 12px;
  color: #777;
  margin-bottom: 4px;
}

.score {
  font-size: 13px;
  margin-bottom: 4px;
}

.user-score {
  margin-left: 10px;
  color: #ff9800;
}

.tags {
  margin-bottom: 4px;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  margin-right: 6px;
}

.tag.pro {
  background: #e3f2fd;
  color: #2196f3;
}

.tag.hot {
  background: #fff3e0;
  color: #ff9800;
}

.desc-text {
  font-size: 12px;
  color: #666;
}

.rating-panel {
  margin-top: 20px;
  padding: 16px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.rating-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.rating-row label {
  width: 120px;
  font-size: 14px;
  color: #333;
}

.rating-row input[type='number'],
.rating-row textarea {
  flex: 1;
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #ddd;
  font-size: 14px;
  box-sizing: border-box;
}

.rating-row textarea {
  resize: vertical;
}

.submit-btn {
  padding: 8px 20px;
  border-radius: 18px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

