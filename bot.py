"""
Discord User App - 最小实现
使用 discord.py 创建的用户应用示例
"""

import os
import json
import re
from pathlib import Path
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

# 用户配置文件路径
CONFIG_FILE = Path(__file__).parent / "user_config.json"
# 表情和贴纸收藏文件夹
COLLECTIONS_DIR = Path(__file__).parent / "collections"


def load_config() -> dict:
    """加载用户配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    """保存用户配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_user_channel(user_id: int) -> int | None:
    """获取用户配置的频道 ID"""
    config = load_config()
    return config.get(str(user_id), {}).get("channel_id")


def set_user_channel(user_id: int, channel_id: int):
    """设置用户的目标频道"""
    config = load_config()
    config[str(user_id)] = {"channel_id": channel_id}
    save_config(config)


def get_user_collection_file(user_id: int) -> Path:
    """获取用户的收藏文件路径"""
    COLLECTIONS_DIR.mkdir(exist_ok=True)
    return COLLECTIONS_DIR / f"{user_id}.json"


def load_collection(user_id: int) -> dict:
    """加载用户的表情和贴纸收藏"""
    collection_file = get_user_collection_file(user_id)
    if collection_file.exists():
        with open(collection_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"emojis": {}, "stickers": {}}


def save_collection(user_id: int, collection: dict):
    """保存用户的表情和贴纸收藏"""
    collection_file = get_user_collection_file(user_id)
    with open(collection_file, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)


def add_emoji_to_collection(user_id: int, emoji_id: str, name: str, url: str, animated: bool):
    """添加表情到用户收藏"""
    collection = load_collection(user_id)
    if emoji_id not in collection["emojis"]:
        collection["emojis"][emoji_id] = {
            "name": name,
            "url": url,
            "animated": animated
        }
        save_collection(user_id, collection)
        return True
    return False


def add_sticker_to_collection(user_id: int, sticker_id: str, name: str, url: str):
    """添加贴纸到用户收藏"""
    collection = load_collection(user_id)
    if sticker_id not in collection["stickers"]:
        collection["stickers"][sticker_id] = {
            "name": name,
            "url": url
        }
        save_collection(user_id, collection)
        return True
    return False


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


@client.tree.command(name="set_channel", description="设置媒体链接发送的目标频道")
@app_commands.describe(channel="选择要发送链接的目标频道")
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    """设置用户的目标频道"""
    set_user_channel(interaction.user.id, channel.id)
    await interaction.response.send_message(
        f"✅ 已设置目标频道为: **#{channel.name}** (ID: {channel.id})\n"
        f"现在可以使用右键菜单「发送到我的频道」了！",
        ephemeral=True
    )


@client.tree.command(name="my_channel", description="查看当前设置的目标频道")
async def my_channel(interaction: discord.Interaction):
    """查看用户当前设置的频道"""
    channel_id = get_user_channel(interaction.user.id)
    if channel_id:
        channel = client.get_channel(channel_id)
        if channel:
            await interaction.response.send_message(
                f"📌 当前目标频道: **#{channel.name}** (ID: {channel_id})",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ 已配置频道 ID: {channel_id}，但无法访问该频道。",
                ephemeral=True
            )
    else:
        await interaction.response.send_message(
            "❌ 尚未设置目标频道。请使用 `/set_channel` 命令设置。",
            ephemeral=True
        )


def extract_media_links(message: discord.Message) -> list[str]:
    """从消息中提取媒体链接"""
    links = []
    
    # 提取附件
    for attachment in message.attachments:
        links.append(attachment.url)
    
    # 提取嵌入图片
    for embed in message.embeds:
        if embed.image:
            links.append(embed.image.url)
        if embed.thumbnail:
            links.append(embed.thumbnail.url)
    
    # 提取自定义表情
    emoji_pattern = r'<(a?):(\w+):(\d+)>'
    for match in re.finditer(emoji_pattern, message.content):
        animated = match.group(1) == 'a'
        emoji_id = match.group(3)
        ext = 'gif' if animated else 'png'
        links.append(f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}")
    
    # 提取贴纸
    for sticker in message.stickers:
        links.append(sticker.url)
    
    return links


@client.tree.context_menu(name="发送到我的频道")
async def send_to_channel(interaction: discord.Interaction, message: discord.Message):
    """将提取的媒体链接发送到用户配置的频道"""
    # 检查用户是否已配置频道
    channel_id = get_user_channel(interaction.user.id)
    if not channel_id:
        await interaction.response.send_message(
            "❌ 请先使用 `/set_channel` 命令设置目标频道！",
            ephemeral=True
        )
        return
    
    # 获取目标频道
    channel = client.get_channel(channel_id)
    if not channel:
        await interaction.response.send_message(
            f"❌ 无法访问频道 (ID: {channel_id})，请检查 Bot 权限或重新设置频道。",
            ephemeral=True
        )
        return
    
    # 提取链接
    links = extract_media_links(message)
    
    if not links:
        await interaction.response.send_message(
            "❌ 这条消息中没有找到图片、表情或贴纸。",
            ephemeral=True
        )
        return
    
    # 自动保存表情和贴纸到收藏
    saved_emojis = 0
    saved_stickers = 0
    
    # 保存自定义表情
    emoji_pattern = r'<(a?):(\w+):(\d+)>'
    for match in re.finditer(emoji_pattern, message.content):
        animated = match.group(1) == 'a'
        name = match.group(2)
        emoji_id = match.group(3)
        ext = 'gif' if animated else 'png'
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
        if add_emoji_to_collection(interaction.user.id, emoji_id, name, url, animated):
            saved_emojis += 1
    
    # 保存贴纸
    for sticker in message.stickers:
        if add_sticker_to_collection(interaction.user.id, str(sticker.id), sticker.name, sticker.url):
            saved_stickers += 1
    
    # 构建保存信息
    save_info = ""
    if saved_emojis > 0 or saved_stickers > 0:
        save_info = f"\n📥 新保存: {saved_emojis} 个表情, {saved_stickers} 个贴纸"
    
    # 构建并发送消息到目标频道
    embed = discord.Embed(
        title="📎 提取的媒体链接",
        description=f"来自 {message.author.mention} 的消息",
        color=discord.Color.green(),
        url=message.jump_url
    )
    embed.add_field(name="原消息链接", value=f"[点击跳转]({message.jump_url})", inline=False)
    embed.add_field(name="媒体链接", value="\n".join(links[:10]), inline=False)  # 限制10个
    if len(links) > 10:
        embed.set_footer(text=f"共 {len(links)} 个链接，仅显示前 10 个")
    
    try:
        await channel.send(embed=embed)
        # 发送纯链接消息
        await channel.send("\n".join(links))
        await interaction.response.send_message(
            f"✅ 已将 {len(links)} 个链接发送到 **#{channel.name}**{save_info}",
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            f"❌ 没有在 **#{channel.name}** 发送消息的权限！",
            ephemeral=True
        )


@client.tree.command(name="my_collection", description="查看收藏的表情和贴纸")
async def my_collection(interaction: discord.Interaction):
    """查看已收藏的表情和贴纸数量及链接"""
    collection = load_collection(interaction.user.id)
    emoji_count = len(collection.get("emojis", {}))
    sticker_count = len(collection.get("stickers", {}))
    
    embed = discord.Embed(
        title="📦 我的收藏",
        color=discord.Color.purple()
    )
    embed.add_field(name="😀 表情", value=f"{emoji_count} 个", inline=True)
    embed.add_field(name="🏷️ 贴纸", value=f"{sticker_count} 个", inline=True)
    
    # 显示最近几个表情
    if emoji_count > 0:
        recent_emojis = list(collection["emojis"].values())[-5:]
        emoji_list = "\n".join([f":{e['name']}: - {e['url']}" for e in recent_emojis])
        embed.add_field(name="最近表情", value=emoji_list, inline=False)
    
    # 显示最近几个贴纸
    if sticker_count > 0:
        recent_stickers = list(collection["stickers"].values())[-5:]
        sticker_list = "\n".join([f"{s['name']} - {s['url']}" for s in recent_stickers])
        embed.add_field(name="最近贴纸", value=sticker_list, inline=False)
    
    embed.set_footer(text=f"数据保存在 collections/{interaction.user.id}.json")
    await interaction.response.send_message(embed=embed, ephemeral=True)


if __name__ == "__main__":
    client.run(TOKEN)
