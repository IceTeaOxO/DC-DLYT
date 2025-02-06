# 使用 Python 3.10 作為基礎映像
FROM python:3.10-slim

# 安裝 ffmpeg (用於音訊處理)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製需要的檔案
COPY requirements.txt .
COPY config/ ./config/
COPY src/ ./src/
COPY run.py .

# 建立下載目錄
RUN mkdir -p downloads

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 運行 bot
CMD ["python", "run.py"]