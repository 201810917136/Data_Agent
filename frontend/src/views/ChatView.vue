<template>
  <div class="chat-container">
    <div class="chat-header">
      <h2>AI 问数 - 二手车拍卖数据分析</h2>
    </div>
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="msg in chatStore.messages" :key="msg.id" class="message" :class="msg.role">
        <div class="message-bubble">
          <div class="message-content">{{ msg.content }}</div>
          <div v-if="msg.loading" class="loading">思考中...</div>
          <div v-if="msg.error" class="error">{{ msg.error }}</div>
          <div v-if="msg.sql" class="sql-block">
            <details>
              <summary>查看 SQL</summary>
              <pre><code>{{ msg.sql }}</code></pre>
            </details>
          </div>
          <div v-if="msg.data && msg.data.length > 0" class="result-table">
            <el-table :data="msg.data" stripe border size="small" max-height="400">
              <el-table-column v-for="(val, key) in msg.data[0]" :key="key" :prop="key" :label="key" />
            </el-table>
          </div>
        </div>
      </div>
    </div>
    <div class="chat-input">
      <el-input
        v-model="inputText"
        placeholder="输入你的问题，例如：昨日各门店销售额"
        @keyup.enter="handleSend"
        :disabled="isSending"
      >
        <template #append>
          <el-button type="primary" @click="handleSend" :loading="isSending">发送</el-button>
        </template>
      </el-input>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'

const chatStore = useChatStore()
const inputText = ref('')
const isSending = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

async function handleSend() {
  if (!inputText.value.trim()) return
  const question = inputText.value.trim()
  inputText.value = ''
  isSending.value = true
  await chatStore.sendQuestion(question)
  isSending.value = false
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(() => chatStore.messages.length, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
})
</script>

<style scoped>
.chat-container { display: flex; flex-direction: column; height: 100vh; }
.chat-header { padding: 16px 24px; border-bottom: 1px solid #e4e7ed; background: #fff; }
.chat-header h2 { margin: 0; font-size: 18px; color: #303133; }
.chat-messages { flex: 1; overflow-y: auto; padding: 24px; background: #f5f7fa; }
.message { margin-bottom: 16px; display: flex; }
.message.user { justify-content: flex-end; }
.message-bubble { max-width: 70%; padding: 12px 16px; border-radius: 12px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.message.user .message-bubble { background: #409eff; color: #fff; }
.sql-block { margin-top: 8px; }
.sql-block pre { background: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 12px; }
.error { color: #f56c6c; margin-top: 8px; }
.result-table { margin-top: 12px; }
.chat-input { padding: 16px 24px; border-top: 1px solid #e4e7ed; background: #fff; }
</style>