import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendMessage } from '../api'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sql?: string
  data?: any[]
  chartType?: string
  error?: string
  loading?: boolean
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const sessionId = ref(crypto.randomUUID())

  async function sendQuestion(question: string) {
    const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: question }
    messages.value.push(userMsg)

    const assistantMsg: Message = { id: crypto.randomUUID(), role: 'assistant', content: '', loading: true }
    messages.value.push(assistantMsg)

    try {
      const result = await sendMessage(question, sessionId.value)
      assistantMsg.loading = false
      if (result.success) {
        assistantMsg.content = '查询成功'
        assistantMsg.sql = result.sql
        assistantMsg.data = result.data
        assistantMsg.chartType = result.chart_type
      } else {
        assistantMsg.content = '查询失败'
        assistantMsg.error = result.error
        assistantMsg.sql = result.sql
      }
    } catch (e: any) {
      assistantMsg.loading = false
      assistantMsg.content = '请求异常'
      assistantMsg.error = e.message
    }
  }

  return { messages, sendQuestion }
})