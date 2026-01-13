"""
频道配置命令模块 - set_channel, my_channel
"""

import discord
from discord import app_commands
from ..config import get_user_channel, set_user_channel


def setup_channel_commands(client):
    """注册频道配置命令"""
    
    @client.tree.command(name="set_channel", description="设置媒体链接发送的目标频道")
    @app_commands.describe(channel="选择要发送链接的目标频道")
    async def set_channel_cmd(interaction: discord.Interaction, channel: discord.TextChannel):
        """设置用户的目标频道"""
        set_user_channel(interaction.user.id, channel.id)
        await interaction.response.send_message(
            f"✅ 已设置目标频道为: **#{channel.name}** (ID: {channel.id})\n"
            f"现在可以使用右键菜单「发送到我的频道」了！",
            ephemeral=True
        )

    @client.tree.command(name="my_channel", description="查看当前设置的目标频道")
    async def my_channel_cmd(interaction: discord.Interaction):
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
