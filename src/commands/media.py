"""
媒体提取命令模块 - 提取媒体链接、发送到频道、收藏管理
"""

import re
import discord
from ..config import get_user_channel
from ..collection import load_collection, add_emoji_to_collection, add_sticker_to_collection
from ..utils import extract_media_links


def setup_media_commands(client):
    """注册媒体相关命令"""
    
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
        embed.add_field(name="媒体链接", value="\n".join(links[:10]), inline=False)
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
    async def my_collection_cmd(interaction: discord.Interaction):
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

    # 表情搜索自动补全
    async def emoji_autocomplete(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
        """自动补全表情名称"""
        collection = load_collection(interaction.user.id)
        emojis = collection.get("emojis", {})
        
        # 过滤匹配的表情
        choices = []
        for emoji_id, data in emojis.items():
            name = data.get("name", "")
            if current.lower() in name.lower():
                choices.append(discord.app_commands.Choice(
                    name=f":{name}:",
                    value=emoji_id
                ))
                if len(choices) >= 25:  # Discord 限制最多 25 个选项
                    break
        return choices

    @client.tree.command(name="search_emoji", description="搜索已收藏的表情")
    @discord.app_commands.describe(name="输入表情名称进行搜索")
    @discord.app_commands.autocomplete(name=emoji_autocomplete)
    async def search_emoji_cmd(interaction: discord.Interaction, name: str):
        """搜索表情并返回链接"""
        collection = load_collection(interaction.user.id)
        emojis = collection.get("emojis", {})
        
        # 通过 ID 查找
        if name in emojis:
            emoji = emojis[name]
            await interaction.response.send_message(
                f"**:{emoji['name']}:**\n```\n{emoji['url']}\n```",
                ephemeral=True
            )
        else:
            # 尝试通过名称模糊匹配
            for emoji_id, data in emojis.items():
                if data.get("name", "").lower() == name.lower().strip(":"):
                    await interaction.response.send_message(
                        f"**:{data['name']}:**\n```\n{data['url']}\n```",
                        ephemeral=True
                    )
                    return
            await interaction.response.send_message(
                "❌ 未找到该表情，请检查名称或先收藏。",
                ephemeral=True
            )

    # 贴纸搜索自动补全
    async def sticker_autocomplete(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
        """自动补全贴纸名称"""
        collection = load_collection(interaction.user.id)
        stickers = collection.get("stickers", {})
        
        # 过滤匹配的贴纸
        choices = []
        for sticker_id, data in stickers.items():
            name = data.get("name", "")
            if current.lower() in name.lower():
                choices.append(discord.app_commands.Choice(
                    name=name,
                    value=sticker_id
                ))
                if len(choices) >= 25:
                    break
        return choices

    @client.tree.command(name="search_sticker", description="搜索已收藏的贴纸")
    @discord.app_commands.describe(name="输入贴纸名称进行搜索")
    @discord.app_commands.autocomplete(name=sticker_autocomplete)
    async def search_sticker_cmd(interaction: discord.Interaction, name: str):
        """搜索贴纸并返回链接"""
        collection = load_collection(interaction.user.id)
        stickers = collection.get("stickers", {})
        
        # 通过 ID 查找
        if name in stickers:
            sticker = stickers[name]
            await interaction.response.send_message(
                f"**{sticker['name']}**\n```\n{sticker['url']}\n```",
                ephemeral=True
            )
        else:
            # 尝试通过名称模糊匹配
            for sticker_id, data in stickers.items():
                if data.get("name", "").lower() == name.lower():
                    await interaction.response.send_message(
                        f"**{data['name']}**\n```\n{data['url']}\n```",
                        ephemeral=True
                    )
                    return
            await interaction.response.send_message(
                "❌ 未找到该贴纸，请检查名称或先收藏。",
                ephemeral=True
            )
