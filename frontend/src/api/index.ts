import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export async function sendMessage(message: string, sessionId: string = '') {
  const response = await api.post('/chat', { message, session_id: sessionId })
  return response.data
}

export async function apiSendPreview(message: string, sessionId: string = '') {
  const response = await api.post('/chat/preview', { message, session_id: sessionId })
  return response.data
}

export async function apiSendExecute(message: string, sql: string, sessionId: string = '') {
  const response = await api.post('/chat/execute', { message, sql, session_id: sessionId })
  return response.data
}