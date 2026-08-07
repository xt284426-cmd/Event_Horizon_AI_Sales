import axios from 'axios'
import { ElMessage } from 'element-plus'

const productionApi = 'https://event-horizon-ai-sales-api.onrender.com/api'
const defaultApi = window.location.hostname.endsWith('chatgpt.site') ? productionApi : '/api'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || defaultApi,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败，请稍后重试'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export default request
