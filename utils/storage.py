"""存储抽象层，提供统一的数据访问接口"""
import json
import os
import threading
from typing import List, Dict, Any, Optional, Union
import logging
from config.config import PATH_CONFIG, validate_required_configs

logger = logging.getLogger('discord')

class StorageManager:
    """存储管理器，提供对服务器特定数据的访问抽象"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or PATH_CONFIG['SERVER_DATA_DIR']
        self._ensure_base_directory()
        self._file_locks = {}  # 为每个文件路径创建锁
        self._lock_dict_lock = threading.Lock()  # 保护_file_locks字典的锁
    
    def _ensure_base_directory(self):
        """确保基础目录存在"""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path, exist_ok=True)
    
    def _get_file_lock(self, file_path: str) -> threading.Lock:
        """获取特定文件的锁"""
        with self._lock_dict_lock:
            if file_path not in self._file_locks:
                self._file_locks[file_path] = threading.Lock()
            return self._file_locks[file_path]
    
    def get_server_data_path(self, guild_id: str, filename: str) -> str:
        """获取服务器特定数据文件的路径"""
        server_path = os.path.join(self.base_path, guild_id)
        if not os.path.exists(server_path):
            os.makedirs(server_path, exist_ok=True)
        return os.path.join(server_path, filename)
    
    def save_json(self, file_path: str, data: Any) -> bool:
        """保存JSON数据到文件"""
        file_lock = self._get_file_lock(file_path)
        with file_lock:
            try:
                # 确保目录存在
                directory = os.path.dirname(file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                logger.error(f"Error saving JSON to {file_path}: {e}")
                return False
    
    def load_json(self, file_path: str, default: Any = None) -> Any:
        """从文件加载JSON数据"""
        file_lock = self._get_file_lock(file_path)
        with file_lock:
            try:
                if not os.path.exists(file_path):
                    # 如果文件不存在，创建并返回默认值
                    if default is not None:
                        self.save_json(file_path, default)
                    return default or {}
                
                # 检查文件大小以防止加载过大的文件
                file_size = os.path.getsize(file_path)
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    logger.warning(f"File too large to load: {file_path} ({file_size} bytes)")
                    return default or {}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning(f"Invalid or missing JSON file: {file_path}")
                return default or {}
            except OSError as e:
                logger.error(f"OS error loading JSON from {file_path}: {e}")
                return default or {}
            except Exception as e:
                logger.error(f"Error loading JSON from {file_path}: {e}")
                return default or {}

class GlobalDataManager:
    """全局数据管理器"""
    
    def __init__(self):
        self.storage = StorageManager()
        self.global_data_path = 'global_data.json'  # 全局数据文件
    
    def save_global_data(self, data: Dict[str, Any]) -> bool:
        """保存全局数据"""
        try:
            with open(self.global_data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving global data: {e}")
            return False
    
    def load_global_data(self, default: Dict[str, Any] = None) -> Dict[str, Any]:
        """加载全局数据"""
        try:
            if not os.path.exists(self.global_data_path):
                if default is not None:
                    self.save_global_data(default)
                return default or {}
            
            with open(self.global_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning(f"Invalid or missing global data file: {self.global_data_path}")
            return default or {}
        except Exception as e:
            logger.error(f"Error loading global data: {e}")
            return default or {}

class TrustedUsersManager:
    """受信任用户管理器"""
    
    def __init__(self):
        self.storage = StorageManager()
        self.trusted_users_file = 'trusted_users.json'
    
    def load_trusted_users(self) -> List[int]:
        """加载受信任用户列表"""
        data = self.storage.load_json(self.trusted_users_file, default=[])
        # 确保所有项目都是整数
        return [int(user_id) for user_id in data if isinstance(user_id, (int, str))]
    
    def save_trusted_users(self, trusted_users: List[int]) -> bool:
        """保存受信任用户列表"""
        return self.storage.save_json(self.trusted_users_file, trusted_users)
    
    def add_trusted_user(self, user_id: int) -> bool:
        """添加受信任用户"""
        trusted_users = self.load_trusted_users()
        if user_id not in trusted_users:
            trusted_users.append(user_id)
            return self.save_trusted_users(trusted_users)
        return True  # 用户已存在，视为成功
    
    def remove_trusted_user(self, user_id: int) -> bool:
        """移除受信任用户"""
        trusted_users = self.load_trusted_users()
        if user_id in trusted_users:
            trusted_users.remove(user_id)
            return self.save_trusted_users(trusted_users)
        return True  # 用户不存在，视为成功
    
    def is_trusted_user(self, user_id: int) -> bool:
        """检查用户是否受信任"""
        return user_id in self.load_trusted_users()

class TicketDataManager:
    """票证数据管理器"""
    
    def __init__(self):
        self.storage = StorageManager()
    
    def load_ticket_configs(self, guild_id: str) -> List[Dict[str, Any]]:
        """加载票证配置"""
        return self.storage.load_json(
            self.storage.get_server_data_path(guild_id, "ticket_configs.json"), 
            default=[]
        )
    
    def save_ticket_configs(self, guild_id: str, configs: List[Dict[str, Any]]) -> bool:
        """保存票证配置"""
        return self.storage.save_json(
            self.storage.get_server_data_path(guild_id, "ticket_configs.json"), 
            configs
        )
    
    def get_ticket_setup_by_id(self, guild_id: str, setup_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取票证设置"""
        configs = self.load_ticket_configs(guild_id)
        for config in configs:
            if config.get('id') == setup_id:
                return config
        return None
    
    def load_multi_ticket_configs(self, guild_id: str) -> List[Dict[str, Any]]:
        """加载多票证配置"""
        return self.storage.load_json(
            self.storage.get_server_data_path(guild_id, "multi_ticket_configs.json"), 
            default=[]
        )
    
    def save_multi_ticket_configs(self, guild_id: str, configs: List[Dict[str, Any]]) -> bool:
        """保存多票证配置"""
        return self.storage.save_json(
            self.storage.get_server_data_path(guild_id, "multi_ticket_configs.json"), 
            configs
        )
    
    def get_multi_ticket_setup_by_id(self, guild_id: str, setup_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取多票证设置"""
        configs = self.load_multi_ticket_configs(guild_id)
        for config in configs:
            if config.get('id') == setup_id:
                return config
        return None
    
    def load_active_tickets(self, guild_id: str) -> Dict[str, Any]:
        """加载活跃票证"""
        return self.storage.load_json(
            self.storage.get_server_data_path(guild_id, "active_tickets.json"), 
            default={}
        )
    
    def save_active_ticket(self, guild_id: str, user_id: int, thread_id: str, 
                          handle_msg_id: str, setup_id: str, ticket_data: Optional[Dict[str, Any]] = None) -> bool:
        """保存活跃票证"""
        try:
            tickets = self.load_active_tickets(guild_id)
            user_id_str = str(user_id)
            
            if ticket_data is None:
                from datetime import datetime, timezone
                ticket_data = {
                    "thread_id": thread_id,
                    "handle_msg_id": handle_msg_id,
                    "setup_id": setup_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "user_id": user_id_str
                }
            else:
                # 确保必要的字段存在
                ticket_data.update({
                    "thread_id": thread_id,
                    "handle_msg_id": handle_msg_id,
                    "setup_id": setup_id,
                    "user_id": user_id_str
                })
            
            tickets[user_id_str] = ticket_data
            return self.storage.save_json(
                self.storage.get_server_data_path(guild_id, "active_tickets.json"), 
                tickets
            )
        except Exception as e:
            logger.error(f"Failed to save active ticket: {str(e)}")
            return False
    
    def get_ticket_data(self, guild_id: str, identifier: str) -> Optional[Dict[str, Any]]:
        """根据用户ID或线程ID获取票证数据"""
        try:
            tickets = self.load_active_tickets(guild_id)
            
            # 检查identifier是否为用户ID
            if identifier in tickets:
                return tickets[identifier]
            
            # 按线程ID搜索
            for user_id, data in tickets.items():
                if data.get('thread_id') == identifier:
                    return data
            
            return None
        except Exception as e:
            logger.error(f"Error getting ticket data: {str(e)}")
            return None
    
    def update_ticket_data(self, guild_id: str, thread_id: str, ticket_data: Dict[str, Any]) -> bool:
        """更新特定票证的数据"""
        try:
            # 加载所有活跃票证
            tickets = self.load_active_tickets(guild_id)
            
            # 根据线程ID查找票证
            for user_id, data in tickets.items():
                if data.get('thread_id') == thread_id:
                    # 更新票证数据
                    tickets[user_id] = ticket_data
                    
                    # 保存更新后的票证
                    return self.storage.save_json(
                        self.storage.get_server_data_path(guild_id, "active_tickets.json"), 
                        tickets
                    )
            
            logger.warning(f"Ticket not found for update - Server: {guild_id}, Thread: {thread_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error updating ticket data: {str(e)}")
            return False
    
    def remove_active_ticket(self, guild_id: str, identifier: str) -> bool:
        """根据用户ID或线程ID移除活跃票证"""
        try:
            tickets = self.load_active_tickets(guild_id)
            
            # 检查identifier是否为用户ID
            if identifier in tickets:
                setup_id = tickets[identifier].get("setup_id", "unknown")
                del tickets[identifier]
                self.storage.save_json(
                    self.storage.get_server_data_path(guild_id, "active_tickets.json"), 
                    tickets
                )
                logger.info(f"✅ Removed ticket - Server: {guild_id}, User: {identifier}, Setup: {setup_id}")
                return True
            
            # 按线程ID搜索
            for user_id, data in tickets.items():
                if data.get('thread_id') == identifier:
                    setup_id = data.get("setup_id", "unknown")
                    del tickets[user_id]
                    self.storage.save_json(
                        self.storage.get_server_data_path(guild_id, "active_tickets.json"), 
                        tickets
                    )
                    logger.info(f"✅ Removed ticket - Server: {guild_id}, Thread: {identifier}, Setup: {setup_id}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error removing active ticket: {str(e)}")
            return False

class UserDataManager:
    """用户数据管理器"""
    
    def __init__(self):
        self.storage = StorageManager()
    
    def load_user_ticket_counts(self, guild_id: str) -> Dict[str, int]:
        """加载用户票证计数"""
        return self.storage.load_json(
            self.storage.get_server_data_path(guild_id, "user_ticket_counts.json"), 
            default={}
        )
    
    def save_user_ticket_count(self, guild_id: str, user_id: int, count: int) -> None:
        """保存用户票证计数"""
        counts = self.load_user_ticket_counts(guild_id)
        counts[str(user_id)] = count
        self.storage.save_json(
            self.storage.get_server_data_path(guild_id, "user_ticket_counts.json"), 
            counts
        )
    
    def increment_user_ticket_count(self, guild_id: str, user_id: int) -> int:
        """增加用户票证计数"""
        counts = self.load_user_ticket_counts(guild_id)
        current = counts.get(str(user_id), 0)
        new_count = current + 1
        self.save_user_ticket_count(guild_id, user_id, new_count)
        return new_count
    
    def reset_user_ticket_count(self, guild_id: str, user_id: int) -> None:
        """重置用户票证计数"""
        self.save_user_ticket_count(guild_id, user_id, 0)
    
    def load_user_timezones(self, guild_id: str) -> Dict[str, str]:
        """加载用户时区"""
        return self.storage.load_json(
            self.storage.get_server_data_path(guild_id, "user_timezones.json"), 
            default={}
        )
    
    def save_user_timezone(self, guild_id: str, user_id: int, timezone: str) -> None:
        """保存用户时区"""
        timezones = self.load_user_timezones(guild_id)
        timezones[str(user_id)] = timezone
        self.storage.save_json(
            self.storage.get_server_data_path(guild_id, "user_timezones.json"), 
            timezones
        )

class StaffRoleManager:
    """员工角色管理器"""
    
    def __init__(self):
        self.storage = StorageManager()
    
    def load_staff_roles(self, guild_id: str) -> List[str]:
        """加载员工角色"""
        return self.storage.load_json(
            self.storage.get_server_data_path(guild_id, "staff_roles.json"), 
            default=[]
        )
    
    def save_staff_roles(self, guild_id: str, staff_roles: List[str]) -> None:
        """保存员工角色"""
        self.storage.save_json(
            self.storage.get_server_data_path(guild_id, "staff_roles.json"), 
            staff_roles
        )

class DataManager:
    """数据管理器 - 集成所有数据管理功能"""
    
    def __init__(self):
        self.storage = StorageManager()
        self.global_data = GlobalDataManager()
        self.trusted_users = TrustedUsersManager()
        self.tickets = TicketDataManager()
        self.users = UserDataManager()
        self.staff_roles = StaffRoleManager()
    
    def get_all_servers_data(self) -> List[str]:
        """获取所有服务器数据目录"""
        if not os.path.exists(self.storage.base_path):
            return []
        return [d for d in os.listdir(self.storage.base_path) 
                if os.path.isdir(os.path.join(self.storage.base_path, d))]
    
    def export_all_server_data(self) -> Dict[str, Any]:
        """导出所有服务器数据"""
        from datetime import datetime, timezone
        return {
            "ticket_configs": self.load_all_ticket_configs(),
            "multi_ticket_configs": self.load_all_multi_ticket_configs(),
            "active_tickets": self.load_all_active_tickets(),
            "user_ticket_counts": self.load_all_user_ticket_counts(),
            "staff_roles": self.load_all_staff_roles(),
            "user_timezones": self.load_all_user_timezones(),
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_servers": len(self.get_all_servers_data())
        }
    
    def load_all_ticket_configs(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载所有服务器的票证配置"""
        all_data = {}
        for server_id in self.get_all_servers_data():
            all_data[server_id] = self.tickets.load_ticket_configs(server_id)
        return all_data
    
    def load_all_multi_ticket_configs(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载所有服务器的多票证配置"""
        all_data = {}
        for server_id in self.get_all_servers_data():
            all_data[server_id] = self.tickets.load_multi_ticket_configs(server_id)
        return all_data
    
    def load_all_active_tickets(self) -> Dict[str, Dict[str, Any]]:
        """加载所有服务器的活跃票证"""
        all_data = {}
        for server_id in self.get_all_servers_data():
            all_data[server_id] = self.tickets.load_active_tickets(server_id)
        return all_data
    
    def load_all_user_ticket_counts(self) -> Dict[str, Dict[str, int]]:
        """加载所有服务器的用户票证计数"""
        all_data = {}
        for server_id in self.get_all_servers_data():
            all_data[server_id] = self.users.load_user_ticket_counts(server_id)
        return all_data
    
    def load_all_staff_roles(self) -> Dict[str, List[str]]:
        """加载所有服务器的员工角色"""
        all_data = {}
        for server_id in self.get_all_servers_data():
            all_data[server_id] = self.staff_roles.load_staff_roles(server_id)
        return all_data
    
    def load_all_user_timezones(self) -> Dict[str, Dict[str, str]]:
        """加载所有服务器的用户时区"""
        all_data = {}
        for server_id in self.get_all_servers_data():
            all_data[server_id] = self.users.load_user_timezones(server_id)
        return all_data
    
    def import_all_server_data(self, data: Dict[str, Any]) -> bool:
        """导入所有服务器数据"""
        try:
            success = True
            
            # 导入票证配置
            if 'ticket_configs' in data:
                for server_id, configs in data['ticket_configs'].items():
                    if not self.tickets.save_ticket_configs(server_id, configs):
                        success = False
                        logger.error(f"Failed to import ticket configs for server {server_id}")
            
            # 导入多票证配置
            if 'multi_ticket_configs' in data:
                for server_id, configs in data['multi_ticket_configs'].items():
                    if not self.tickets.save_multi_ticket_configs(server_id, configs):
                        success = False
                        logger.error(f"Failed to import multi-ticket configs for server {server_id}")
            
            # 导入活跃票证
            if 'active_tickets' in data:
                for server_id, tickets in data['active_tickets'].items():
                    file_path = self.storage.get_server_data_path(server_id, "active_tickets.json")
                    if not self.storage.save_json(file_path, tickets):
                        success = False
                        logger.error(f"Failed to import active tickets for server {server_id}")
            
            # 导入用户票证计数
            if 'user_ticket_counts' in data:
                for server_id, counts in data['user_ticket_counts'].items():
                    file_path = self.storage.get_server_data_path(server_id, "user_ticket_counts.json")
                    if not self.storage.save_json(file_path, counts):
                        success = False
                        logger.error(f"Failed to import user ticket counts for server {server_id}")
            
            # 导入员工角色
            if 'staff_roles' in data:
                for server_id, roles in data['staff_roles'].items():
                    file_path = self.storage.get_server_data_path(server_id, "staff_roles.json")
                    if not self.storage.save_json(file_path, roles):
                        success = False
                        logger.error(f"Failed to import staff roles for server {server_id}")
            
            # 导入用户时区
            if 'user_timezones' in data:
                for server_id, timezones in data['user_timezones'].items():
                    file_path = self.storage.get_server_data_path(server_id, "user_timezones.json")
                    if not self.storage.save_json(file_path, timezones):
                        success = False
                        logger.error(f"Failed to import user timezones for server {server_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error importing all server data: {str(e)}")
            return False

# 创建全局数据管理器实例
data_manager = DataManager()

# 便捷函数，保持向后兼容
def load_trusted_users() -> List[int]:
    """加载受信任用户 - 向后兼容函数"""
    return data_manager.trusted_users.load_trusted_users()

def save_trusted_users(trusted_users: List[int]) -> bool:
    """保存受信任用户 - 向后兼容函数"""
    return data_manager.trusted_users.save_trusted_users(trusted_users)

def is_bot_owner(user_id: int) -> bool:
    """检查是否为机器人所有者"""
    from config.config import DISCORD_CONFIG
    try:
        return user_id == int(DISCORD_CONFIG['OWNER_USER_ID'])
    except ValueError:
        logger.error(f"Invalid OWNER_USER_ID format: {DISCORD_CONFIG['OWNER_USER_ID']}")
        return False

def is_trusted_user(user_id: int) -> bool:
    """检查用户是否受信任 - 向后兼容函数"""
    return data_manager.trusted_users.is_trusted_user(user_id)

def load_staff_roles(guild_id: str) -> List[str]:
    """加载员工角色 - 向后兼容函数"""
    return data_manager.staff_roles.load_staff_roles(guild_id)

def save_staff_roles(guild_id: str, staff_roles: List[str]) -> None:
    """保存员工角色 - 向后兼容函数"""
    return data_manager.staff_roles.save_staff_roles(guild_id, staff_roles)

def load_ticket_configs(guild_id: str) -> List[Dict[str, Any]]:
    """加载票证配置 - 向后兼容函数"""
    return data_manager.tickets.load_ticket_configs(guild_id)

def save_ticket_configs(guild_id: str, configs: List[Dict[str, Any]]) -> bool:
    """保存票证配置 - 向后兼容函数"""
    return data_manager.tickets.save_ticket_configs(guild_id, configs)

def get_ticket_setup_by_id(guild_id: str, setup_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取票证设置 - 向后兼容函数"""
    return data_manager.tickets.get_ticket_setup_by_id(guild_id, setup_id)

def load_multi_ticket_configs(guild_id: str) -> List[Dict[str, Any]]:
    """加载多票证配置 - 向后兼容函数"""
    return data_manager.tickets.load_multi_ticket_configs(guild_id)

def save_multi_ticket_configs(guild_id: str, configs: List[Dict[str, Any]]) -> bool:
    """保存多票证配置 - 向后兼容函数"""
    return data_manager.tickets.save_multi_ticket_configs(guild_id, configs)

def get_multi_ticket_setup_by_id(guild_id: str, setup_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取多票证设置 - 向后兼容函数"""
    return data_manager.tickets.get_multi_ticket_setup_by_id(guild_id, setup_id)

def load_active_tickets(guild_id: str) -> Dict[str, Any]:
    """加载活跃票证 - 向后兼容函数"""
    return data_manager.tickets.load_active_tickets(guild_id)

def save_active_ticket(guild_id: str, user_id: int, thread_id: str, 
                      handle_msg_id: str, setup_id: str, ticket_data: Optional[Dict[str, Any]] = None) -> bool:
    """保存活跃票证 - 向后兼容函数"""
    return data_manager.tickets.save_active_ticket(
        guild_id, user_id, thread_id, handle_msg_id, setup_id, ticket_data
    )

def get_ticket_data(guild_id: str, identifier: str) -> Optional[Dict[str, Any]]:
    """根据用户ID或线程ID获取票证数据 - 向后兼容函数"""
    return data_manager.tickets.get_ticket_data(guild_id, identifier)

def update_ticket_data(guild_id: str, thread_id: str, ticket_data: Dict[str, Any]) -> bool:
    """更新特定票证的数据 - 向后兼容函数"""
    return data_manager.tickets.update_ticket_data(guild_id, thread_id, ticket_data)

def remove_active_ticket(guild_id: str, identifier: str) -> bool:
    """根据用户ID或线程ID移除活跃票证 - 向后兼容函数"""
    return data_manager.tickets.remove_active_ticket(guild_id, identifier)

def load_user_ticket_counts(guild_id: str) -> Dict[str, int]:
    """加载用户票证计数 - 向后兼容函数"""
    return data_manager.users.load_user_ticket_counts(guild_id)

def save_user_ticket_count(guild_id: str, user_id: int, count: int) -> None:
    """保存用户票证计数 - 向后兼容函数"""
    return data_manager.users.save_user_ticket_count(guild_id, user_id, count)

def increment_user_ticket_count(guild_id: str, user_id: int) -> int:
    """增加用户票证计数 - 向后兼容函数"""
    return data_manager.users.increment_user_ticket_count(guild_id, user_id)

def reset_user_ticket_count(guild_id: str, user_id: int) -> None:
    """重置用户票证计数 - 向后兼容函数"""
    return data_manager.users.reset_user_ticket_count(guild_id, user_id)

def load_user_timezones(guild_id: str) -> Dict[str, str]:
    """加载用户时区 - 向后兼容函数"""
    return data_manager.users.load_user_timezones(guild_id)

def save_user_timezone(guild_id: str, user_id: int, timezone: str) -> None:
    """保存用户时区 - 向后兼容函数"""
    return data_manager.users.save_user_timezone(guild_id, user_id, timezone)

def save_json_data(guild_id: str, filename: str, data: Any) -> None:
    """保存JSON数据 - 向后兼容函数"""
    return data_manager.storage.save_json(data_manager.storage.get_server_data_path(guild_id, filename), data)

def get_server_data_path(guild_id: str, filename: str) -> str:
    """获取服务器数据路径 - 向后兼容函数"""
    return data_manager.storage.get_server_data_path(guild_id, filename)

def export_all_server_data() -> Dict[str, Any]:
    """导出所有服务器数据 - 向后兼容函数"""
    return data_manager.export_all_server_data()

def import_all_server_data(data: Dict[str, Any]) -> bool:
    """导入所有服务器数据 - 向后兼容函数"""
    return data_manager.import_all_server_data(data)

def load_all_ticket_configs() -> Dict[str, List[Dict[str, Any]]]:
    """加载所有服务器的票证配置 - 向后兼容函数"""
    return data_manager.load_all_ticket_configs()

def load_all_multi_ticket_configs() -> Dict[str, List[Dict[str, Any]]]:
    """加载所有服务器的多票证配置 - 向后兼容函数"""
    return data_manager.load_all_multi_ticket_configs()

def load_all_active_tickets() -> Dict[str, Dict[str, Any]]:
    """加载所有服务器的活跃票证 - 向后兼容函数"""
    return data_manager.load_all_active_tickets()

def load_all_user_ticket_counts() -> Dict[str, Dict[str, int]]:
    """加载所有服务器的用户票证计数 - 向后兼容函数"""
    return data_manager.load_all_user_ticket_counts()

def load_all_staff_roles() -> Dict[str, List[str]]:
    """加载所有服务器的员工角色 - 向后兼容函数"""
    return data_manager.load_all_staff_roles()

def load_all_user_timezones() -> Dict[str, Dict[str, str]]:
    """加载所有服务器的用户时区 - 向后兼容函数"""
    return data_manager.load_all_user_timezones()

def get_all_servers_data() -> List[str]:
    """获取所有服务器数据目录 - 向后兼容函数"""
    return data_manager.get_all_servers_data()

def backup_server_data(guild_id: str) -> bool:
    """备份指定服务器的数据"""
    try:
        import shutil
        from datetime import datetime, timezone
        import os
        
        server_path = os.path.join(data_manager.storage.base_path, guild_id)
        backup_dir = f"backup_{guild_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        if not os.path.exists(server_path):
            logger.info(f"No data directory to backup for server {guild_id}")
            return True  # Consider success if no data to backup
        
        # 使用shutil复制整个服务器数据目录到备份目录
        if os.path.exists(server_path):
            shutil.copytree(server_path, backup_dir)
            logger.info(f"✅ Successfully backed up server {guild_id} to {backup_dir}")
            return True
        else:
            logger.info(f"Server data directory does not exist: {server_path}")
            return True  # Consider success if directory doesn't exist
            
    except Exception as e:
        logger.error(f"❌ Error backing up server {guild_id}: {str(e)}")
        return False