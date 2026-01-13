"""
Discord User App - 最小实现
使用 discord.py 创建的用户应用示例
"""

import os
import discord
from discord import app_commands
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取 Token
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("请在 .env 文件中设置 DISCORD_TOKEN")


class MyClient(discord.Client):
    """自定义 Discord 客户端"""

    def __init__(self):
        # 设置 intents（用户应用通常不需要特权 intents）
        intents = discord.Intents.default()
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


# 定义斜杠命令
@client.tree.command(name="ping", description="测试 Bot 响应")
async def ping(interaction: discord.Interaction):
    """简单的 ping 命令，返回延迟信息"""
    latency = round(client.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! 延迟: {latency}ms")


@client.tree.command(name="info", description="显示 Bot 信息")
async def info(interaction: discord.Interaction):
    """显示 Bot 的基本信息"""
    embed = discord.Embed(
        title="📌 Bot 信息",
        description="这是一个 Discord User App 示例",
        color=discord.Color.blue(),
    )
    embed.add_field(name="discord.py 版本", value=discord.__version__, inline=True)
    embed.add_field(
        name="延迟", value=f"{round(client.latency * 1000)}ms", inline=True
    )
    await interaction.response.send_message(embed=embed)


if __name__ == "__main__":
    client.run(TOKEN)
