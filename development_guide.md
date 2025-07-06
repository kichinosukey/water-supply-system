# 🌱 ガーデニング水やりシステム 開発手順書

## 1. 開発環境の準備

### 1.1 Raspberry Pi側の準備
```bash
# 必要なパッケージのインストール
sudo apt update
sudo apt install python3-pip python3-venv

# 仮想環境の作成
python3 -m venv watering_env
source watering_env/bin/activate

# 必要なライブラリのインストール
pip install flask gpiozero
```

### 1.2 開発PC側の準備
- テキストエディタ（VS Code推奨）
- SSH接続環境
- ブラウザ（Chrome/Firefox）

## 2. プロジェクト構造
```
water-supply-system/
├── app.py              # Flaskアプリケーション
├── relay_control.py    # GPIO制御モジュール（main.pyを改修）
├── static/
│   ├── css/
│   │   └── style.css   # ガーデニングテーマのスタイル
│   ├── js/
│   │   └── app.js      # フロントエンドのロジック
│   └── images/
│       ├── tomato.svg  # トマトのイラスト
│       └── watering-can.svg # ジョウロのイラスト
├── templates/
│   └── index.html      # メインページ
└── requirements.txt    # 依存関係
```

## 3. 実装手順

### Step 1: GPIO制御モジュールの作成
1. 既存のmain.pyをrelay_control.pyにリファクタリング
2. 関数化して再利用可能にする
3. エラーハンドリングを追加

### Step 2: Flaskバックエンドの実装
1. app.pyの作成
2. ルーティングの設定
   - GET /: メインページ
   - POST /api/water: 水やり実行
   - GET /api/status: 状態確認
3. CORS設定（必要に応じて）

### Step 3: フロントエンドの実装
1. index.htmlの作成（ガーデニングレイアウト）
2. style.cssでかわいいデザインを実装
3. app.jsで水やりボタンの処理を実装

### Step 4: アニメーションの追加
1. CSSアニメーションで水やり演出
2. ボタンの無効化/有効化
3. 完了メッセージの表示

## 4. 詳細実装ガイド

### 4.1 relay_control.py
```python
import gpiozero
from time import sleep
import datetime

class WateringSystem:
    def __init__(self, gpio_pin=17):
        self.relay = gpiozero.LED(gpio_pin)
        self.is_watering = False
        self.last_watered = None
    
    def water_plants(self, duration=3):
        if self.is_watering:
            return False, "すでに水やり中です"
        
        self.is_watering = True
        self.relay.on()
        sleep(duration)
        self.relay.off()
        self.is_watering = False
        self.last_watered = datetime.datetime.now()
        
        return True, "水やり完了！"
```

### 4.2 app.py（基本構造）
```python
from flask import Flask, render_template, jsonify
from relay_control import WateringSystem

app = Flask(__name__)
watering_system = WateringSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/water', methods=['POST'])
def water():
    success, message = watering_system.water_plants()
    return jsonify({
        'success': success,
        'message': message
    })
```

### 4.3 フロントエンドの実装ポイント
- fetchAPIを使用してバックエンドと通信
- ボタンクリック時にローディング状態を表示
- エラーハンドリングを適切に実装
- モバイルファーストでレスポンシブデザイン

## 5. テスト手順

### 5.1 ローカルテスト
1. GPIO制御のモックを作成
2. 開発PCでUIの動作確認

### 5.2 Raspberry Piでのテスト
1. コードをRaspberry Piに転送
2. Flaskアプリを起動
3. 同一ネットワークからアクセス
4. 実際のリレー動作を確認

## 6. デプロイ手順

### 6.1 サービス化
```bash
# systemdサービスファイルの作成
sudo nano /etc/systemd/system/watering.service
```

### 6.2 自動起動設定
```bash
sudo systemctl enable watering.service
sudo systemctl start watering.service
```

### 6.3 セキュリティ設定
- ファイアウォールでポート制限
- ローカルネットワークのみアクセス許可

## 7. トラブルシューティング

### よくある問題
1. **GPIO権限エラー**
   - sudoで実行するか、ユーザーをgpioグループに追加

2. **ポートが使えない**
   - 別のポート番号を使用（5000以外）

3. **リレーが動作しない**
   - GPIO番号の確認
   - 配線の確認

## 8. 今後の改善案
- 定期水やり機能
- 水やり履歴の保存
- 複数植物の管理
- LINE通知機能