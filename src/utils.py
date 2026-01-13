"""
工具函数模块
"""

import re
import discord


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
