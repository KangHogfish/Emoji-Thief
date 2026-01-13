"""
用户配置管理模块
"""

import json
from pathlib import Path

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "user_config.json"


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
