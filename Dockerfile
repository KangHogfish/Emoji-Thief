# 使用 Python 3.11 slim 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 创建非 root 用户
RUN addgroup --system --gid 1001 botgroup && \
    adduser --system --uid 1001 --gid 1001 botuser

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY bot.py .

# 切换到非 root 用户
USER botuser

# 启动 Bot
CMD ["python", "bot.py"]
