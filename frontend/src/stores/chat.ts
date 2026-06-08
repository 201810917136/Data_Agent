import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendMessage, apiSendPreview, apiSendExecute } from '../api'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sql?: string
  data?: any[]
  chartType?: string
  error?: string
  loading?: boolean
  isPreview?: boolean
  questionUnderstanding?: string
  tablesInvolved?: string
  queryLogic?: string
  sqlValid?: boolean
  editing?: boolean
  tempSql?: string
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const sessionId = ref(crypto.randomUUID())

  async function sendPreview(question: string) {
    const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: question }
    messages.value.push(userMsg)

    const assistantMsg: Message = {
      id: crypto.randomUUID(), role: 'assistant',
      content: '', loading: true, isPreview: true
    }
    messages.value.push(assistantMsg)

    try {
      const result = await apiSendPreview(question, sessionId.value)
      assistantMsg.loading = false
      assistantMsg.questionUnderstanding = result.question_understanding
      assistantMsg.tablesInvolved = result.tables_involved
      assistantMsg.queryLogic = result.query_logic
      assistantMsg.sql = result.sql
      assistantMsg.sqlValid = result.sql_valid
      assistantMsg.error = result.error
      assistantMsg.isPreview = true
      if (result.error) {
        assistantMsg.content = 'SQL 校验未通过'
      } else {
        assistantMsg.content = '已生成 SQL，请确认'
      }
    } catch (e: any) {
      assistantMsg.loading = false
      assistantMsg.content = '请求异常'
      assistantMsg.error = e.message
    }
  }

  async function sendExecute(question: string, sql: string) {
    const lastMsg = messages.value[messages.value.length - 1]
    lastMsg.loading = false
    lastMsg.isPreview = false
    lastMsg.tempSql = undefined
    lastMsg.editing = false
    try {
      const result = await apiSendExecute(question, sql, sessionId.value)
      if (result.success) {
        lastMsg.content = '查询成功'
        lastMsg.sql = result.sql
        lastMsg.data = result.data
        lastMsg.chartType = result.chart_type
      } else {
        lastMsg.content = '查询失败'
        lastMsg.error = result.error
        lastMsg.sql = result.sql
      }
    } catch (e: any) {
      lastMsg.content = '请求异常'
      lastMsg.error = e.message
    }
  }

  async function sendQuestion(question: string) {
    await apiSendPreview(question)
  }

  return { messages, sendQuestion, sendPreview, sendExecute, sessionId }
})