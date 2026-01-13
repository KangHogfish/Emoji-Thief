"""
基础命令模块 - ping, info
"""

import discord


def setup_basic_commands(client):
    """注册基础命令"""
    
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
