"""配置模块，用于管理所有应用配置常量"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Discord Bot 配置
DISCORD_CONFIG = {
    'TOKEN': os.getenv('TOKEN'),
    'OWNER_USER_ID': os.getenv('OWNER_USER_ID'),
    'COMMAND_PREFIX': '!',
    'INTENTS': {
        'message_content': True,
        'guilds': True,
        'guild_scheduled_events': True,
        'members': True,
        'messages': True
    }
}

# 应用配置
APP_CONFIG = {
    'PORT': int(os.getenv('PORT', 10000)),
    'DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
    'HOST': os.getenv('HOST', '0.0.0.0'),
    'THREADS': int(os.getenv('THREADS', 4))
}

# 时间相关配置
TIME_CONFIG = {
    'UPTIME_DIVISORS': {
        'day_seconds': 86400,
        'hour_seconds': 3600,
        'minute_seconds': 60
    },
    'MONITOR_INTERVAL': 30,  # 监控间隔（秒）
    'PING_INTERVAL': 300,    # 自检间隔（秒）
    'AUTO_UPDATE_INTERVAL': 1000  # 自动更新间隔（毫秒）
}

# API 和 HTTP 配置
API_CONFIG = {
    'DEFAULT_TIMEOUT': 10,
    'HEALTH_CHECK_STATUS_CODE': 503,
    'RETRY_ATTEMPTS': 3
}

# 系统资源配置
SYSTEM_CONFIG = {
    'CPU_INTERVAL': 0.5,
    'MEMORY_UNIT': 1024 * 1024  # MB
}

# 消息和 Embed 配置
MESSAGE_CONFIG = {
    'EMBED_FIELD_LIMIT': 25,
    'EMBED_DESCRIPTION_LIMIT': 4096,
    'EMBED_TITLE_LIMIT': 256,
    'EMBED_FOOTER_LIMIT': 2048,
    'MESSAGE_CONTENT_LIMIT': 2000,
    'THREAD_NAME_LIMIT': 100
}

# 错误处理配置
ERROR_CONFIG = {
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# 速率限制配置
RATE_LIMIT_CONFIG = {
    'BATCH_SIZE': 5,  # 批处理大小
    'BATCH_DELAY': 1,  # 批处理间延迟（秒）
    'MAX_RETRIES': 3
}

# 路径配置
PATH_CONFIG = {
    'SERVER_DATA_DIR': 'servers',
    'CONFIG_DIR': 'config',
    'UTILS_DIR': 'utils',
    'COGS_DIR': 'cogs',
    'STATIC_DIR': 'static',
    'TEMPLATES_DIR': 'templates'
}

# 票证系统配置
TICKET_CONFIG = {
    'DEFAULT_TITLE_FORMAT': 'ticket-{username}',
    'DEFAULT_OPEN_MESSAGE': 'Please describe your issue...',
    'MAX_TITLE_LENGTH': 100,
    'MAX_DESCRIPTION_LENGTH': 1000,
    'MAX_EMOJI_LENGTH': 10,
    'DEFAULT_BUTTON_LABEL': 'Ticket',
    'DEFAULT_PANEL_TITLE': 'Support Tickets',
    'DEFAULT_PANEL_DESCRIPTION': 'Click the button below to create a ticket'
}

def validate_required_configs():
    """验证必需的配置是否存在"""
    errors = []
    
    if not DISCORD_CONFIG['TOKEN']:
        errors.append("DISCORD_CONFIG['TOKEN'] is required")
    
    if not DISCORD_CONFIG['OWNER_USER_ID']:
        errors.append("DISCORD_CONFIG['OWNER_USER_ID'] is required")
    
    if errors:
        raise ValueError(f"Missing required configurations: {', '.join(errors)}")

def get_config_value(config_dict, key, default=None):
    """安全获取配置值的辅助函数"""
    return config_dict.get(key, default)

# 初始化时验证配置
validate_required_configs()