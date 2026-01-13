# Discord User App

基于 discord.py 的 Discord 用户应用最小实现。

## 功能

- `/ping` - 测试 Bot 响应和延迟
- `/info` - 显示 Bot 信息

## 快速开始

### 1. 创建 Discord 应用

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 点击 "New Application" 创建应用
3. 在 "Installation" 页面配置安装设置（选择 User Install）
4. 在 "Bot" 页面获取 Token

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Token
```

### 3. 运行

**本地运行：**

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 Bot
python bot.py
```

**Docker 运行：**

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 项目结构

```
dcbot/
├── bot.py              # 主程序
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量模板
├── Dockerfile          # Docker 镜像
└── docker-compose.yml  # 容器编排
```

## License

MIT
