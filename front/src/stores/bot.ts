import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

interface BotStatus {
  bot_status: string
  disk_usage: {
    total: number
    used: number
    free: number
    percent: number
  }
  memory_usage: {
    total: number
    available: number
    percent: number
    used: number
    free: number
  }
  cpu_usage: number
  thread_count: number
  bot_latency_ms: number
}

export const useBotStore = defineStore('bot', () => {
  const status = ref<BotStatus | null>(null)
  const loading = ref(false)
  const refreshing = ref(false)
  const error = ref<string | null>(null)
  const autoUpdate = ref(true)
  const updateInterval = ref<number | null>(null)
  const pingResult = ref<{reply: string, timestamp: number, responseTime?: number} | null>(null)
  const pinging = ref(false)

  const isBotRunning = computed(() => status.value?.bot_status === 'running')
  const formattedUptime = computed(() => {
    if (!status.value) return 'N/A'
    // 这里可以根据需要添加运行时间计算逻辑
    return 'Calculating...'
  })

  async function fetchStatus(isAutoRefresh = false) {
    if (!isAutoRefresh) {
      loading.value = true
    } else {
      refreshing.value = true
    }
    error.value = null
    try {
      const response = await fetch('/api/status')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      status.value = await response.json()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch bot status'
      console.error('Error fetching bot status:', err)
    } finally {
      if (!isAutoRefresh) {
        loading.value = false
      } else {
        refreshing.value = false
      }
    }
  }

  async function sendBotCommand(command: string) {
    try {
      const response = await fetch('/api/bot-control', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: command })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      return { success: true, data: result }
    } catch (err) {
      return { 
        success: false, 
        error: err instanceof Error ? err.message : 'Failed to send command' 
      }
    }
  }

  async function ping() {
    pinging.value = true
    error.value = null
    const startTime = Date.now() // 记录请求开始时间
    
    try {
      const response = await fetch('/api/ping')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      
      // 计算response time：当前时间 - 后端timestamp（转换为毫秒）
      const backendTime = data.timestamp * 1000 // 后端返回的是秒，转换为毫秒
      const responseTime = Date.now() - backendTime
      
      pingResult.value = {
        ...data,
        responseTime: Math.max(0, responseTime) // 确保非负数
      }
      
      return { success: true, data: pingResult.value }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to ping backend'
      console.error('Error pinging backend:', err)
      return { success: false, error: error.value }
    } finally {
      pinging.value = false
    }
  }

  function startAutoUpdate(intervalMs = 1000) {
    if (updateInterval.value) {
      clearInterval(updateInterval.value)
    }
    autoUpdate.value = true
    updateInterval.value = setInterval(() => fetchStatus(true), intervalMs) as unknown as number
  }

  function stopAutoUpdate() {
    if (updateInterval.value) {
      clearInterval(updateInterval.value)
      updateInterval.value = null
    }
    autoUpdate.value = false
  }

  function toggleAutoUpdate() {
    if (autoUpdate.value) {
      stopAutoUpdate()
    } else {
      startAutoUpdate()
    }
  }

  // 初始化时获取一次状态
  fetchStatus()

  return {
    status,
    loading,
    refreshing,
    error,
    autoUpdate,
    pingResult,
    pinging,
    isBotRunning,
    formattedUptime,
    fetchStatus,
    sendBotCommand,
    ping,
    startAutoUpdate,
    stopAutoUpdate,
    toggleAutoUpdate
  }
})