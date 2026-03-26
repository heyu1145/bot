import json
from typing import List, Union, Dict, Any
from config.config import PATH_CONFIG
from utils.storage import get_server_data_path, data_manager


def save_item(guild_id: str, item: Union[str, int, Dict, List]) -> None:
    """
    为指定服务器保存一个数据项
    
    Args:
        guild_id: 服务器ID
        item: 要保存的数据项（支持字符串、数字、字典、列表）
    """
    path = get_server_data_path(guild_id, 'data_items.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    data.append(item)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def remove_item(guild_id: str, item: Union[str, int, Dict, List]) -> bool:
    """
    从指定服务器的数据列表中移除一个数据项
    
    Args:
        guild_id: 服务器ID
        item: 要移除的数据项
    
    Returns:
        bool: 是否成功移除
    """
    path = get_server_data_path(guild_id, 'data_items.json')
    try: 
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    
    if item in data:
        data.remove(item)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    return False


def load_items(guild_id: str) -> List[Union[str, int, Dict, List]]:
    """
    加载指定服务器的所有数据项
    
    Args:
        guild_id: 服务器ID
    
    Returns:
        List[Union[str, int, Dict, List]]: 数据项列表
    """
    path = get_server_data_path(guild_id, 'data_items.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_dynamic_message(guild_id: str, channel_id: int, msg_id: int) -> None:
    """
    保存动态消息的引用，用于自动刷新
    
    Args:
        guild_id: 服务器ID
        channel_id: 频道ID
        msg_id: 消息ID
    """
    path = 'dynamic_messages.json'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data.setdefault(guild_id, {}).setdefault(str(channel_id), []).append(str(msg_id))
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_dynamic_messages() -> Dict[str, Dict[str, List[str]]]:
    """
    加载所有动态消息的引用
    
    Returns:
        Dict[str, Dict[str, List[str]]]: 包含所有动态消息引用的字典
    """
    path = 'dynamic_messages.json'

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def clear_items(guild_id: str) -> bool:
    """
    清空指定服务器的所有数据项
    
    Args:
        guild_id: 服务器ID
    
    Returns:
        bool: 是否成功清空
    """
    path = get_server_data_path(guild_id, 'data_items.json')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def update_item(guild_id: str, old_item: Union[str, int, Dict, List], new_item: Union[str, int, Dict, List]) -> bool:
    """
    更新指定服务器中的数据项
    
    Args:
        guild_id: 服务器ID
        old_item: 旧数据项
        new_item: 新数据项
    
    Returns:
        bool: 是否成功更新
    """
    path = get_server_data_path(guild_id, 'data_items.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    
    if old_item in data:
        index = data.index(old_item)
        data[index] = new_item
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    return False


def get_item_count(guild_id: str) -> int:
    """
    获取指定服务器的数据项数量
    
    Args:
        guild_id: 服务器ID
    
    Returns:
        int: 数据项数量
    """
    return len(load_items(guild_id))