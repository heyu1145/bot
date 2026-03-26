let autoUpdate = true;
let updateInterval;

// 通知系统
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// 加载状态
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

// 自动更新控制
function toggleAutoUpdate() {
    autoUpdate = !autoUpdate;
    const toggleBtn = document.getElementById('autoUpdateToggle');

    if (autoUpdate) {
        toggleBtn.textContent = '⏸️ Pause Updates';
        startAutoUpdate();
    } else {
        toggleBtn.textContent = '▶️ Resume Updates';
        clearInterval(updateInterval);
    }
}

// 更新指示器
function showUpdateIndicator() {
    const indicator = document.getElementById('updateIndicator');
    indicator.style.display = 'block';
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 1000);
}

// 更新元素内容
function updateElement(id, value, isUpdating = true) {
    const element = document.getElementById(id);
    if (element) {
        if (isUpdating) {
            element.classList.add('updating');
            setTimeout(() => {
                element.classList.remove('updating');
            }, 500);
        }
        element.textContent = value;
    }
}

// 机器人控制
async function sendBotCommand(command) {
    showLoading(true);
    try {
        const response = await fetch('/api/bot-control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`Bot ${command} command sent successfully!`, 'success');
            // 刷新数据
            setTimeout(fetchData, 1000);
        } else {
            showNotification(`Failed to ${command} bot: ${result.error}`, 'error');
        }
    } catch (error) {
        showNotification('Error sending command: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// 获取数据
function fetchData() {
    showLoading(true);
    fetch('/api/live-data')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateDashboard(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            showNotification('Failed to fetch live data', 'error');
        })
        .finally(() => {
            showLoading(false);
        });
}

// 更新仪表板
function updateDashboard(data) {
    showUpdateIndicator();

    // Update bot status
    updateElement('botStatusValue', data.bot_status.toUpperCase());
    updateElement('botPid', data.bot_pid);
    updateElement('uptimeValue', data.uptime);
    updateElement('cpuUsage', data.cpu_usage + '% CPU');
    updateElement('memoryUsage', data.memory_usage);
    updateElement('responseTime', data.response_time);

    // Update system stats
    updateElement('cpuCores', data.cpu_cores);
    updateElement('memoryMb', data.memory_mb + ' MB');
    updateElement('threadCount', data.thread_count);
    updateElement('diskUsage', data.disk_usage + '%');

    // Update bot status visual
    const botStatus = document.getElementById('botStatus');
    if (data.bot_status === 'running') {
        botStatus.className = 'bot-status online';
        botStatus.textContent = '🤖 Bot is RUNNING';
    } else {
        botStatus.className = 'bot-status offline';
        botStatus.textContent = '🤖 Bot is STOPPED';
    }

    // Update status icon and message
    const statusIcon = document.getElementById('statusIcon');
    const statusMessage = document.getElementById('statusMessage');
    if (data.bot_status === 'running') {
        statusIcon.textContent = '🤖';
        statusMessage.textContent = 'Your Discord bot is running successfully!';
    } else {
        statusIcon.textContent = '⚠️';
        statusMessage.textContent = 'Bot process is currently offline';
    }

    // Update control buttons
    document.getElementById('startBtn').disabled = data.bot_status === 'running';
    document.getElementById('stopBtn').disabled = data.bot_status !== 'running';
}

// 启动自动更新
function startAutoUpdate() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    updateInterval = setInterval(fetchData, 1000);
}

// 页面加载完成
document.addEventListener('DOMContentLoaded', function() {
    startAutoUpdate();
});
