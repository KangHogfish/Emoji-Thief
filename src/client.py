"""
Discord 客户端模块
"""

import os
import discord
from discord import app_commands
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取代理配置
PROXY = os.getenv("PROXY_URL", "http://127.0.0.1:7897")


class MyClient(discord.Client):
    """自定义 Discord 客户端"""

    def __init__(self):
        # 设置 intents（用户应用通常不需要特权 intents）
        intents = discord.Intents.default()
        
        # 配置代理
        super().__init__(
            intents=intents,
            proxy=PROXY,
        )

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
