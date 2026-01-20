# 先看看 walk_commands 到底接受什么
import inspect
import discord
from discord.ext import commands

# 创建一个简单的测试
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

# 查看源码或文档
print("检查 walk_commands 的类型注解...")

# 方法1：用 help() 查看
help(bot.walk_commands)

# 方法2：用 inspect 查看
sig = inspect.signature(bot.walk_commands)
print(f"签名: {sig}")

# 方法3：查看 __annotations__
print(f"注解: {bot.walk_commands.__annotations__}")
