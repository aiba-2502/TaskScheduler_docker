# Pythonスクリプト定期実行システム

指定したディレクトリ内のPythonスクリプトを定期的に実行するDockerアプリケーションです。

## 機能

- **柔軟なスケジューリング**
  - Cron形式での時間指定
  - インターバル実行（秒/分/時間/日単位）
  - 特定日時での単発実行
  
- **実行制御**
  - 最大実行回数の指定
  - ジョブの有効/無効化
  - 実行ログの記録

- **Docker対応**
  - コンテナ化された環境での安定動作
  - ボリュームマウントによる柔軟な設定

## ディレクトリ構成

```
.
├── scheduler.py        # メインアプリケーション
├── Dockerfile         # Dockerイメージ定義
├── docker-compose.yml # Docker Compose設定
├── requirements.txt   # Python依存パッケージ
├── config/           # 設定ファイルディレクトリ
│   └── scheduler.json # スケジュール設定
├── scripts/          # 実行するPythonスクリプト
│   ├── daily_report.py
│   ├── health_check.py
│   └── ...
└── logs/            # ログファイル出力先
    └── scheduler.log
```

## セットアップ

1. **プロジェクトディレクトリの作成**
```bash
mkdir python-scheduler
cd python-scheduler
```

2. **必要なファイルの配置**
- 上記のファイルをすべて配置
- `scripts/`ディレクトリに実行したいPythonスクリプトを配置
- `config/scheduler.json`でスケジュールを設定

3. **Dockerイメージのビルドと起動**
```bash
# イメージのビルドと起動
docker-compose up -d

# ログの確認
docker-compose logs -f

# 停止
docker-compose down
```

## 設定ファイル（scheduler.json）の書き方

### 基本構造
```json
{
  "jobs": {
    "ジョブ名": {
      "script_path": "スクリプトファイル名",
      "schedule_type": "スケジュールタイプ",
      "schedule_config": { スケジュール設定 },
      "max_runs": 最大実行回数（オプション）,
      "enabled": true/false
    }
  }
}
```

### スケジュールタイプ

#### 1. cron - Cron形式での指定
```json
{
  "schedule_type": "cron",
  "schedule_config": {
    "year": 2024,
    "month": 12,
    "day": 25,
    "hour": 15,
    "minute": 30,
    "second": 0,
    "day_of_week": "mon"  // mon, tue, wed, thu, fri, sat, sun
  }
}
```

#### 2. interval - 一定間隔での実行
```json
{
  "schedule_type": "interval",
  "schedule_config": {
    "weeks": 1,
    "days": 1,
    "hours": 1,
    "minutes": 30,
    "seconds": 0
  }
}
```

#### 3. date - 特定日時での単発実行
```json
{
  "schedule_type": "date",
  "schedule_config": {
    "run_date": "2024-12-25 15:30:00"
  }
}
```

## 使用例

### 例1: 毎日朝9時にレポート生成
```json
{
  "daily_report": {
    "script_path": "generate_report.py",
    "schedule_type": "cron",
    "schedule_config": {
      "hour": 9,
      "minute": 0
    },
    "enabled": true
  }
}
```

### 例2: 30分ごとにヘルスチェック（最大48回）
```json
{
  "health_check": {
    "script_path": "health_check.py",
    "schedule_type": "interval",
    "schedule_config": {
      "minutes": 30
    },
    "max_runs": 48,
    "enabled": true
  }
}
```

### 例3: 特定日時に1回だけ実行
```json
{
  "migration": {
    "script_path": "db_migration.py",
    "schedule_type": "date",
    "schedule_config": {
      "run_date": "2024-12-31 23:59:00"
    },
    "max_runs": 1,
    "enabled": true
  }
}
```

## 注意事項

1. **タイムゾーン**: docker-compose.ymlで`TZ=Asia/Tokyo`を設定しています
2. **ログ**: `/app/logs/scheduler.log`に出力されます
3. **スクリプトの実行環境**: scriptsディレクトリがカレントディレクトリとして実行されます
4. **エラーハンドリング**: スクリプトがエラーで終了してもスケジューラーは継続動作します

## トラブルシューティング

### ログの確認
```bash
# リアルタイムログ表示
docker-compose logs -f

# ログファイルの確認
tail -f logs/scheduler.log
```

### コンテナ内での確認
```bash
# コンテナに入る
docker-compose exec scheduler bash

# Pythonスクリプトの手動実行テスト
cd /app/scripts
python your_script.py
```

### 設定の再読み込み
設定ファイルを変更した場合は、コンテナを再起動してください：
```bash
docker-compose restart
```