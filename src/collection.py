"""
表情和贴纸收藏管理模块
"""

import json
from pathlib import Path

# 收藏文件夹路径
COLLECTIONS_DIR = Path(__file__).parent.parent / "collections"


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


def add_emoji_to_collection(user_id: int, emoji_id: str, name: str, url: str, animated: bool) -> bool:
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


def add_sticker_to_collection(user_id: int, sticker_id: str, name: str, url: str) -> bool:
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
