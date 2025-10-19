import json
from utils.storage import get_server_data_path

def save(guild_id: str,msg: str | int):
  path = get_server_data_path(guild_id, 'test.json')
  try:
    with open(path, 'r') as f:
      data = json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
      data = []
  data.append(msg)
  with open(path, 'w') as f:
    json.dump(data,f)
    
def remove(guild_id:str,msg:str | int) -> bool:
  path = get_server_data_path(guild_id,'test.json')
  try: 
    with open(path,'r') as f:
      data = json.load(f)
  except (FileNotFoundError,json.JSONDecodeError):
    return False
  
  if msg in data:
    data.remove(msg)
    with open(path,'w') as f:
      json.dump(data,f)
    return True
  return False

def load(guild_id:str) -> list[int | str]:
  path = get_server_data_path(guild_id, 'test.json')
  try:
    with open(path,'r') as f:
      data = json.load(f)
  except (FileNotFoundError,json.JSONDecodeError):
    data = []
  return data
  
def save_msg(guild_id: str, channel_id: int, msg_id: int):
  path = 'msg.json'
  try:
    with open(path, 'r') as f:
        data = json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
    data = {}

  data.setdefault(guild_id, {}).setdefault(channel_id, []).append(msg_id)
    
  with open(path, 'w') as f:
    json.dump(data, f)

def load_msg() -> dict[int,dict[int,list[int]]]:
  path = 'msg.json'

  try:
    with open(path, 'r') as f:
      return json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
    return {}
