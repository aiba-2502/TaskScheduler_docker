FROM python:3.13-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY scheduler.py .

# ディレクトリの作成
RUN mkdir -p /app/scripts /app/config /app/logs

# 実行権限の設定
RUN chmod +x scheduler.py

# ログディレクトリの権限設定
RUN chmod 755 /app/logs

# 環境変数の設定
ENV SCRIPTS_DIR=/app/scripts
ENV CONFIG_FILE=/app/config/scheduler.json
ENV PYTHONUNBUFFERED=1

# コンテナ起動時のコマンド
CMD ["python", "-u", "scheduler.py"]