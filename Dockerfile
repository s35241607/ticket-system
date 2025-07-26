# 使用官方Python鏡像作為基礎鏡像
FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 複製requirements.txt並安裝Python依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製項目文件
COPY . .

# 暴露端口
EXPOSE 8000 8001

# 啟動命令
CMD ["uvicorn", "src.backend.ticket_api.main:app", "--host", "0.0.0.0", "--port", "8000"]