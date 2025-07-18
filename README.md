# 🐳 Docker Compose デプロイメント仕様書

## 1. 概要
ガーデニング水やりシステムをDocker Composeで簡単にデプロイできるようにする仕様書。家庭内ネットワークでの使用に特化したシンプルな構成。

## 2. コンテナ構成

### 2.1 サービス構成
- **web**: Flaskアプリケーション（水やり制御API + Web UI）のみのシンプル構成

### 2.2 特殊要件
- Raspberry PiのGPIOアクセスのためのデバイスマウント
- 特権モードでの実行（GPIO制御に必要）

## 3. ディレクトリ構造
```
water-supply-system/
├── compose.yml
├── Dockerfile
├── .dockerignore
├── .env.example
├── app/
│   ├── app.py
│   ├── relay_control.py
│   ├── requirements.txt
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── app.js
│   │   └── images/
│   │       ├── tomato.svg
│   │       └── watering-can.svg
│   └── templates/
│       └── index.html
└── logs/
```

## 4. Docker設定

### 4.1 Dockerfile
```dockerfile
# Raspberry Pi対応のPythonイメージ
FROM python:3.9-slim-bullseye

# GPIO制御に必要なパッケージ
RUN apt-get update && apt-get install -y \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存関係のインストール
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY app/ .

# ポート公開
EXPOSE 5000

# Flaskアプリケーションの起動
CMD ["python", "app.py"]
```

### 4.2 compose.yml
```yaml
services:
  web:
    build: .
    container_name: watering-system
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - GPIO_PIN=17
      - WATERING_DURATION=3
    devices:
      # Raspberry PiのGPIOアクセス
      - /dev/gpiomem:/dev/gpiomem
    volumes:
      - ./logs:/app/logs
      - watering-data:/app/data
    # Raspberry PiでGPIO制御するために必要
    privileged: true

volumes:
  watering-data:
```

### 4.3 環境変数設定（.env.example）
```env
# GPIO設定
GPIO_PIN=17
WATERING_DURATION=3

# アプリケーション設定
FLASK_ENV=production
```

### 4.4 requirements.txt
```txt
flask==2.3.2
gpiozero==1.6.2
RPi.GPIO==0.7.1
```

## 5. デプロイ手順

### 5.1 Raspberry Piの準備
```bash
# Dockerのインストール（最新版）
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose V2の確認
docker compose version

# 再ログインまたは
newgrp docker
```

### 5.2 アプリケーションのデプロイ
```bash
# プロジェクトのクローンまたはコピー
git clone [リポジトリURL]
cd water-supply-system

# 環境変数の設定（必要に応じて）
cp .env.example .env

# ビルドと起動
docker compose up -d

# ログの確認
docker compose logs -f
```

### 5.3 動作確認
```bash
# ヘルスチェック
curl http://localhost:5000/health

# ブラウザでアクセス
# http://[Raspberry PiのIPアドレス]:5000
```

## 6. 運用管理

### 6.1 起動・停止
```bash
# 停止
docker compose stop

# 起動
docker compose start

# 再起動
docker compose restart

# 完全停止（コンテナ削除）
docker compose down
```

### 6.2 ログ管理
```bash
# リアルタイムログ確認
docker compose logs -f

# 過去のログ確認
docker compose logs --tail=100

# ログファイルへの出力
docker compose logs > logs/app_$(date +%Y%m%d).log
```

### 6.3 アップデート
```bash
# 最新コードの取得
git pull

# 再ビルド
docker compose build --no-cache

# 再起動
docker compose up -d
```

## 7. 開発環境での使用

### 7.1 GPIO モックモード
開発PCでテストする場合は、環境変数でMOCK_GPIO=trueを設定：

```bash
# 環境変数を設定して起動
MOCK_GPIO=true docker compose up
```

### 7.2 開発時の注意点
- GPIOが無い環境では自動的にモックモードになる
- モックモード時はログに「モックモードで動作中」と表示される

## 8. トラブルシューティング

### 8.1 よくある問題と解決方法

#### GPIO アクセスエラー
```bash
# デバイスの確認
ls -la /dev/gpiomem

# コンテナ内から確認
docker exec watering-system ls -la /dev/gpiomem
```

#### ポート競合
```bash
# 使用中のポート確認
sudo netstat -tlnp | grep 5000

# 別のポートを使う場合
# compose.ymlのportsを変更
ports:
  - "8080:5000"
```

#### 権限エラー
```bash
# Docker権限の確認
groups | grep docker

# 権限追加後は再ログインが必要
```

## 9. バックアップとリストア

### 9.1 設定のバックアップ
```bash
# 設定とログのバックアップ
tar -czf watering-backup-$(date +%Y%m%d).tar.gz \
  compose.yml \
  .env \
  logs/
```

### 9.2 データのバックアップ
```bash
# Dockerボリュームのバックアップ
docker run --rm \
  -v watering-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/data-backup-$(date +%Y%m%d).tar.gz -C /data .
```

## 10. セキュリティ考慮事項

### 10.1 家庭内ネットワーク限定
- ルーターのファイアウォール設定で外部アクセスを遮断
- 必要に応じてRaspberry Pi自体のファイアウォール設定

### 10.2 最小権限の原則
- GPIO制御に必要な権限のみ付与
- 不要なポートは開放しない

## 11. 今後の拡張案
- 複数のリレー制御対応
- スケジュール機能の追加
- 水やり履歴のデータベース保存
- 温度・湿度センサーとの連携