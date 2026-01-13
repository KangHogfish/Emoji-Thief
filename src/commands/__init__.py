"""
命令模块包
"""

from .basic import setup_basic_commands
from .channel import setup_channel_commands
from .media import setup_media_commands


def setup_all_commands(client):
    """注册所有命令到客户端"""
    setup_basic_commands(client)
    setup_channel_commands(client)
    setup_media_commands(client)
