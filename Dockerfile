# 使用官方 Python 精简版基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--no-use-colors"]