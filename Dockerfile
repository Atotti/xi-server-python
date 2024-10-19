# ベースイメージ
FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なファイルをコピー
COPY ./requirements.txt /app/requirements.txt

# パッケージのインストール
RUN pip install --no-cache-dir -r /app/requirements.txt

# アプリケーションコードをコピー
COPY . /app

# アプリケーションの起動コマンドを指定
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
