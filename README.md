# Discord Emoji Thief

一个 Discord User App，用于提取和收藏消息中的表情、贴纸和图片链接。

## 功能

### 右键菜单
- **提取媒体链接** - 提取消息中的图片、表情、贴纸链接（仅自己可见）
- **发送到我的频道** - 提取链接并发送到指定频道，同时自动收藏表情/贴纸

### 斜杠命令
| 命令 | 说明 |
|------|------|
| `/ping` | 测试 Bot 响应 |
| `/info` | 查看 Bot 信息 |
| `/set_channel` | 设置媒体发送的目标频道 |
| `/my_channel` | 查看当前设置的频道 |
| `/my_collection` | 查看已收藏的表情和贴纸 |
| `/search_emoji` | 搜索收藏（支持自动补全） |

## 快速开始

### 1. 创建 Discord 应用

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 创建应用，在 **Installation** 配置 User Install
3. 在 **Bot** 页面获取 Token

### 2. 配置

```bash
# 复制配置文件
cp .env.example .env
# 编辑 .env，填入 Token 和代理地址（如需）

# 编辑 config.ini 配置是否使用代理
```

### 3. 本地运行

```bash
pip install -r requirements.txt
python bot.py
```

### 4. Docker 部署

```bash
docker-compose up -d --build
```

## 项目结构

```
dcbot/
├── bot.py              # 入口文件
├── config.ini          # 应用配置
├── requirements.txt    # 依赖
├── Dockerfile
├── docker-compose.yml
└── src/
    ├── client.py       # Discord 客户端
    ├── config.py       # 用户配置管理
    ├── collection.py   # 表情/贴纸收藏
    ├── utils.py        # 工具函数
    └── commands/       # 命令模块
        ├── basic.py
        ├── channel.py
        └── media.py
```

## 数据存储

- `user_config.json` - 用户频道配置
- `collections/{用户ID}.json` - 用户收藏（按用户分文件）

## License

MIT
