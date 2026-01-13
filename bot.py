"""
Discord User App - 最小实现
使用 discord.py 创建的用户应用示例
"""

import os
import discord
from discord import app_commands
from dotenv import load_dotenv
import aiohttp

# 加载环境变量
load_dotenv()

# 获取 Token 和代理配置
TOKEN = os.getenv("DISCORD_TOKEN")
PROXY = os.getenv("PROXY_URL", "http://127.0.0.1:7897")

if not TOKEN:
    raise ValueError("请在 .env 文件中设置 DISCORD_TOKEN")


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


@client.tree.context_menu(name="提取媒体链接")
async def extract_media(interaction: discord.Interaction, message: discord.Message):
    """从消息中提取图片、表情和贴纸链接"""
    links = []
    
    # 提取附件（图片、视频等）
    for attachment in message.attachments:
        links.append(f"📎 附件: {attachment.url}")
    
    # 提取嵌入图片
    for embed in message.embeds:
        if embed.image:
            links.append(f"🖼️ 嵌入图片: {embed.image.url}")
        if embed.thumbnail:
            links.append(f"🖼️ 缩略图: {embed.thumbnail.url}")
    
    # 提取自定义表情（使用正则匹配消息内容）
    import re
    # 匹配 <:name:id> 或 <a:name:id>（动态表情）
    emoji_pattern = r'<(a?):(\w+):(\d+)>'
    for match in re.finditer(emoji_pattern, message.content):
        animated = match.group(1) == 'a'
        name = match.group(2)
        emoji_id = match.group(3)
        ext = 'gif' if animated else 'png'
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
        links.append(f"😀 表情 :{name}:: {url}")
    
    # 提取贴纸
    for sticker in message.stickers:
        links.append(f"🏷️ 贴纸 {sticker.name}: {sticker.url}")
    
    # 构建响应
    if links:
        content = "**找到以下媒体链接：**\n" + "\n".join(links)
    else:
        content = "❌ 这条消息中没有找到图片、表情或贴纸。"
    
    # 仅自己可见
    await interaction.response.send_message(content, ephemeral=True)


if __name__ == "__main__":
    client.run(TOKEN)
