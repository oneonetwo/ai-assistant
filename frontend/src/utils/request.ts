import axios, { AxiosError } from 'axios'
import { showToast, showDialog } from 'vant'

interface RetryConfig {
  retries: number
  retryDelay: number
  retryCondition?: (error: AxiosError) => boolean
}

const defaultRetryConfig: RetryConfig = {
  retries: 3,
  retryDelay: 1000,
  retryCondition: (error: AxiosError) => {
    return error.response?.status === 429 || // Rate limit
           error.response?.status === 503 || // Service unavailable
           error.code === 'ECONNABORTED' // Timeout
  }
}

export const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加认证信息等
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  (response) => response.data,
  async (error: AxiosError) => {
    const config = error.config as any
    
    // 处理重试逻辑
    if (!config.retryConfig) {
      config.retryConfig = { ...defaultRetryConfig }
    }
    
    if (config.retryConfig.retries > 0 && 
        (!config.retryConfig.retryCondition || 
         config.retryConfig.retryCondition(error))) {
      config.retryConfig.retries--
      
      // 延迟重试
      await new Promise(resolve => 
        setTimeout(resolve, config.retryConfig.retryDelay)
      )
      
      return request(config)
    }
    
    // 错误处理
    if (error.response) {
      switch (error.response.status) {
        case 401:
          showDialog({
            title: '登录已过期',
            message: '请重新登录',
            confirmButtonText: '确定'
          })
          break
        case 403:
          showToast('没有权限执行此操作')
          break
        case 429:
          showToast('请求过于频繁，请稍后再试')
          break
        default:
          showToast('请求失败，请重试')
      }
    } else if (error.code === 'ECONNABORTED') {
      showToast('请求超时，请检查网络')
    } else {
      showToast('网络错误，请检查连接')
    }
    
    return Promise.reject(error)
  }
)
