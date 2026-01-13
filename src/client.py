"""
Discord 客户端模块
"""

import os
import configparser
from pathlib import Path
import discord
from discord import app_commands
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 加载配置文件
CONFIG_PATH = Path(__file__).parent.parent / "config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding="utf-8")

# 检查是否使用代理
USE_PROXY = config.getboolean("DEFAULT", "USE_PROXY", fallback=False)

# 获取代理配置
PROXY = None
if USE_PROXY:
    PROXY = os.getenv("PROXY_URL")
    if not PROXY:
        raise ValueError("config.ini 中启用了 USE_PROXY，但未在 .env 中设置 PROXY_URL")


class MyClient(discord.Client):
    """自定义 Discord 客户端"""

    def __init__(self):
        # 设置 intents（用户应用通常不需要特权 intents）
        intents = discord.Intents.default()
        
        # 根据配置决定是否使用代理
        if USE_PROXY:
            super().__init__(
                intents=intents,
                proxy=PROXY,
            )
        else:
            super().__init__(intents=intents)

        # 创建命令树用于斜杠命令
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        """在 Bot 启动时同步命令"""
        # 同步全局命令（用户应用需要全局命令）
        await self.tree.sync()
        print(f"已同步 {len(self.tree.get_commands())} 个命令")

    async def on_ready(self):
        """当 Bot 成功连接时触发"""
        print(f"已登录为 {self.user} (ID: {self.user.id})")
        print("------")
        print("Bot 已准备就绪！")


# 创建客户端实例
client = MyClient()
