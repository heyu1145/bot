<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useBotStore } from '@/stores/bot'

const botStore = useBotStore()

const status = computed(() => botStore.status)
const isBotRunning = computed(() => botStore.isBotRunning)
const loading = computed(() => botStore.loading)
const refreshing = computed(() => botStore.refreshing)
const error = computed(() => botStore.error)
const autoUpdate = computed(() => botStore.autoUpdate)
const pingResult = computed(() => botStore.pingResult)
const pinging = computed(() => botStore.pinging)

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatPercent = (value: number) => {
  return value.toFixed(2) + '%'
}

const handleBotCommand = async (command: string) => {
  const result = await botStore.sendBotCommand(command)
  if (result.success) {
    // 命令发送成功，稍后刷新状态
    setTimeout(() => botStore.fetchStatus(), 1000)
  } else {
    console.error('Command failed:', result.error)
  }
}

const handlePing = async () => {
  const result = await botStore.ping()
  if (result.success) {
    console.log('Ping successful:', result.data)
  } else {
    console.error('Ping failed:', result.error)
  }
}

const toggleAutoUpdate = () => {
  botStore.toggleAutoUpdate()
}

onMounted(() => {
  botStore.startAutoUpdate()
})

onUnmounted(() => {
  botStore.stopAutoUpdate()
})
</script>

<template>
  <div class="dashboard">
    <!-- 通知区域 -->
    <div v-if="error" class="notification error">
      {{ error }}
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
    </div>

    <!-- 更新指示器 -->
    <div class="update-indicator" :style="{ display: refreshing ? 'block' : 'none' }">
      🔄 Updating...
    </div>

    <div class="container">
      <!-- 状态图标 -->
      <div class="status-icon" :class="isBotRunning ? 'status-online' : 'status-offline'">
        {{ isBotRunning ? '🤖' : '⚠️' }}
      </div>

      <h1>Discord Bot Dashboard</h1>

      <div class="status-text">
        {{ isBotRunning ? 'Your Discord bot is running successfully!' : 'Bot process is currently offline' }}
      </div>

      <!-- 统计网格 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Bot Status</div>
          <div class="stat-value" :class="isBotRunning ? 'status-online' : 'status-offline'">
            {{ isBotRunning ? 'RUNNING' : 'STOPPED' }}
          </div>
          <div class="stat-subvalue">Latency: {{ status?.bot_latency_ms || 'N/A' }}ms</div>
        </div>

        <div class="stat-card">
          <div class="stat-label">CPU Usage</div>
          <div class="stat-value">
            {{ status?.cpu_usage ? formatPercent(status.cpu_usage) : 'N/A' }}
          </div>
          <div class="stat-subvalue">Threads: {{ status?.thread_count || 'N/A' }}</div>
        </div>

        <div class="stat-card">
          <div class="stat-label">Memory Usage</div>
          <div class="stat-value">
            {{ status?.memory_usage?.percent ? formatPercent(status.memory_usage.percent) : 'N/A' }}
          </div>
          <div class="stat-subvalue">
            {{ status?.memory_usage?.used ? formatBytes(status.memory_usage.used) : 'N/A' }} / 
            {{ status?.memory_usage?.total ? formatBytes(status.memory_usage.total) : 'N/A' }}
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-label">Disk Usage</div>
          <div class="stat-value">
            {{ status?.disk_usage?.percent ? formatPercent(status.disk_usage.percent) : 'N/A' }}
          </div>
          <div class="stat-subvalue">
            {{ status?.disk_usage?.used ? formatBytes(status.disk_usage.used) : 'N/A' }} / 
            {{ status?.disk_usage?.total ? formatBytes(status.disk_usage.total) : 'N/A' }}
          </div>
        </div>
      </div>

      <!-- 系统信息 -->
      <div class="system-info">
        <div class="stat-label">System Resources</div>
        <div class="system-stats">
          <div class="system-stat">
            <div class="system-label">CPU Usage</div>
            <div class="system-value">
              {{ status?.cpu_usage ? formatPercent(status.cpu_usage) : 'N/A' }}
            </div>
          </div>
          <div class="system-stat">
            <div class="system-label">Memory</div>
            <div class="system-value">
              {{ status?.memory_usage?.percent ? formatPercent(status.memory_usage.percent) : 'N/A' }}
            </div>
          </div>
          <div class="system-stat">
            <div class="system-label">Threads</div>
            <div class="system-value">
              {{ status?.thread_count || 'N/A' }}
            </div>
          </div>
          <div class="system-stat">
            <div class="system-label">Disk</div>
            <div class="system-value">
              {{ status?.disk_usage?.percent ? formatPercent(status.disk_usage.percent) : 'N/A' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Bot 状态指示器 -->
      <div class="bot-status" :class="isBotRunning ? 'online' : 'offline'">
        🤖 Bot is {{ isBotRunning ? 'RUNNING' : 'STOPPED' }}
      </div>

      <!-- 控制面板 -->
      <div class="control-panel">
        <div class="stat-label" style="margin-bottom: 10px;">Bot Controls</div>
        <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
          <button 
            class="control-btn" 
            @click="handleBotCommand('start')" 
            :disabled="isBotRunning"
          >
            ▶️ Start Bot
          </button>
          <button 
            class="control-btn" 
            @click="handleBotCommand('stop')" 
            :disabled="!isBotRunning"
          >
            ⏹️ Stop Bot
          </button>
          <button 
            class="control-btn" 
            @click="handleBotCommand('restart')"
          >
            🔄 Restart
          </button>
          <button 
            class="control-btn" 
            @click="botStore.fetchStatus()"
          >
            📊 Refresh
          </button>
        </div>
      </div>

      <!-- 页脚 -->
      <div class="footer">
        <p>Powered by Vue 3 & FastAPI • Auto-update: {{ autoUpdate ? 'ON' : 'OFF' }}</p>
        <div class="links">
          <button class="link-btn" @click="handlePing" :disabled="pinging">
            {{ pinging ? 'Pinging...' : 'Ping Test' }}
          </button>
          <button class="link-btn" @click="toggleAutoUpdate">
            {{ autoUpdate ? '⏸️ Pause Updates' : '▶️ Resume Updates' }}
          </button>
        </div>
        <!-- Ping结果显示 -->
        <div v-if="pingResult" class="ping-result">
          <div class="ping-success">✅ Ping successful!</div>
          <div class="ping-details">
            Reply: {{ pingResult.reply }} • 
            Response Time: {{ pingResult.responseTime?.toFixed(2) || 'N/A' }}ms • 
            Timestamp: {{ new Date(pingResult.timestamp * 1000).toLocaleTimeString() }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  color: #ffffff;
}

.container {
  background: rgba(18, 18, 30, 0.95);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
  max-width: 600px;
  width: 100%;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  position: relative;
  animation: glow 3s ease-in-out infinite alternate;
}

@keyframes glow {
  from {
    box-shadow: 0 0 20px rgba(79, 195, 247, 0.3);
  }
  to {
    box-shadow: 0 0 30px rgba(79, 195, 247, 0.5),
               0 0 40px rgba(79, 195, 247, 0.2);
  }
}

.status-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  text-shadow: 0 0 20px rgba(79, 195, 247, 0.5);
}

.status-online {
  color: #4fc3f7;
}

.status-offline {
  color: #ff5252;
}

h1 {
  color: #e0f7fa;
  margin-bottom: 10px;
  font-size: 2.2rem;
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.3);
}

.status-text {
  font-size: 1.1rem;
  color: #b3e5fc;
  margin-bottom: 30px;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgba(38, 50, 56, 0.6);
  padding: 15px;
  border-radius: 12px;
  border-left: 4px solid #4fc3f7;
  backdrop-filter: blur(5px);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(79, 195, 247, 0.3);
}

.stat-label {
  font-size: 0.85rem;
  color: #81d4fa;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: bold;
  color: #e0f7fa;
  transition: all 0.3s ease;
}

.stat-subvalue {
  font-size: 0.9rem;
  color: #b3e5fc;
  margin-top: 3px;
}

.bot-status {
  display: inline-block;
  padding: 12px 25px;
  border-radius: 25px;
  font-weight: bold;
  margin-top: 15px;
  font-size: 1.1rem;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.online {
  background: linear-gradient(135deg, #00c853 0%, #64dd17 100%);
  color: #000;
  box-shadow: 0 0 20px rgba(0, 200, 83, 0.4);
}

.offline {
  background: linear-gradient(135deg, #ff5252 0%, #ff1744 100%);
  color: #fff;
  box-shadow: 0 0 20px rgba(255, 82, 82, 0.4);
}

.system-info {
  background: rgba(38, 50, 56, 0.6);
  padding: 15px;
  border-radius: 12px;
  margin-top: 20px;
  border-left: 4px solid #ff9800;
}

.system-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 10px;
}

.system-stat {
  text-align: center;
}

.system-label {
  font-size: 0.8rem;
  color: #ffcc80;
  margin-bottom: 3px;
}

.system-value {
  font-size: 1.1rem;
  font-weight: bold;
  color: #fff;
}

.control-panel {
  margin-top: 25px;
  padding: 15px;
  background: rgba(38, 50, 56, 0.4);
  border-radius: 12px;
}

.control-btn {
  background: rgba(79, 195, 247, 0.3);
  color: #e0f7fa;
  border: 1px solid rgba(79, 195, 247, 0.5);
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.control-btn:hover:not(:disabled) {
  background: rgba(79, 195, 247, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(79, 195, 247, 0.3);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.footer {
  margin-top: 30px;
  color: #81d4fa;
  font-size: 0.9rem;
  opacity: 0.8;
}

.links {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.link-btn {
  color: #4fc3f7;
  text-decoration: none;
  padding: 8px 15px;
  border-radius: 15px;
  background: rgba(38, 50, 56, 0.6);
  transition: all 0.3s ease;
  border: 1px solid rgba(79, 195, 247, 0.3);
  cursor: pointer;
  font-size: 0.9rem;
}

.link-btn:hover {
  background: rgba(79, 195, 247, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(79, 195, 247, 0.3);
}

.update-indicator {
  position: fixed;
  top: 10px;
  right: 10px;
  background: rgba(255, 152, 0, 0.9);
  color: white;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  z-index: 1000;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(18, 18, 30, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 20px;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(79, 195, 247, 0.3);
  border-top: 4px solid #4fc3f7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 152, 0, 0.9);
  color: white;
  padding: 10px 20px;
  border-radius: 25px;
  z-index: 1000;
}

.notification.error {
  background: rgba(255, 82, 82, 0.9);
}

/* Ping结果样式 */
.ping-result {
  margin-top: 15px;
  padding: 10px;
  background: rgba(38, 50, 56, 0.6);
  border-radius: 12px;
  border-left: 4px solid #00c853;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.ping-success {
  color: #00c853;
  font-weight: bold;
  margin-bottom: 5px;
}

.ping-details {
  font-size: 0.85rem;
  color: #b3e5fc;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 20px;
    margin: 10px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .system-stats {
    grid-template-columns: 1fr;
  }
  
  h1 {
    font-size: 1.8rem;
  }
  
  .links {
    flex-direction: column;
    align-items: center;
  }
  
  .link-btn {
    width: 200px;
    text-align: center;
  }
}
</style>