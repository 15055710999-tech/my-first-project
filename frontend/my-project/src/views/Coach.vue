<template>
  <div class="coach-container">
    <section class="intro">
      <h1>AI 智能篮球教练（Demo）</h1>
      <p>
        现在是占位版本，会根据你的提问给出通用训练建议。
        后续可以接入大模型 / Agent 和知识库，生成更个性化的训练计划。
      </p>
    </section>

    <section class="chat-card">
      <form class="question-form" @submit.prevent="handleAsk">
        <textarea
          v-model="question"
          class="textarea"
          rows="4"
          placeholder="例如：我想提高三分命中率，该怎么练？"
        />
        <button class="submit-btn" type="submit" :disabled="loading || !question.trim()">
          {{ loading ? '思考中...' : '向教练提问' }}
        </button>
      </form>

      <div v-if="answer" class="answer-card">
        <h2>教练建议</h2>
        <p class="answer-text">{{ answer }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { askCoachApi } from '../api/basketball'

const question = ref('')
const answer = ref('')
const loading = ref(false)

const handleAsk = async () => {
  if (!question.value.trim()) return
  loading.value = true
  answer.value = ''
  try {
    const res: any = await askCoachApi({ question: question.value.trim() })
    answer.value = res.data.answer
  } catch (e) {
    console.error('提问失败', e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.coach-container {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.intro h1 {
  font-size: 26px;
  color: #333;
  margin-bottom: 8px;
}

.intro p {
  color: #666;
  margin-bottom: 20px;
}

.chat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.question-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.textarea {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  resize: vertical;
  font-size: 14px;
  box-sizing: border-box;
}

.textarea:focus {
  outline: none;
  border-color: #667eea;
}

.submit-btn {
  align-self: flex-end;
  padding: 8px 20px;
  border-radius: 18px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.answer-card {
  margin-top: 16px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.answer-card h2 {
  font-size: 18px;
  margin-bottom: 8px;
}

.answer-text {
  color: #444;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>

