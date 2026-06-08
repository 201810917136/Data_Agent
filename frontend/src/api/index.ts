import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export async function sendMessage(message: string, sessionId: string = '') {
  const response = await api.post('/chat', { message, session_id: sessionId })
  return response.data
}