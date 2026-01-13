"""
Discord User App - 入口文件
使用 discord.py 创建的用户应用
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取 Token
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("请在 .env 文件中设置 DISCORD_TOKEN")

# 导入客户端和命令
from src.client import client
from src.commands import setup_all_commands

# 注册所有命令
setup_all_commands(client)


if __name__ == "__main__":
    client.run(TOKEN)
