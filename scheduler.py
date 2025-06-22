#!/usr/bin/env python3
"""
Pythonスクリプト定期実行アプリケーション
指定したディレクトリ内のPythonスクリプトを定期的に実行します
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
import signal
import time

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JobConfig:
    """ジョブの設定"""
    script_path: str
    schedule_type: str  # 'cron', 'interval', 'date'
    schedule_config: Dict
    max_runs: Optional[int] = None  # 実行回数制限（Noneは無制限）
    enabled: bool = True
    run_count: int = field(default=0, init=False)  # 実行回数カウンター

class ScriptScheduler:
    """Pythonスクリプトのスケジューラー"""
    
    def __init__(self, scripts_dir: str, config_file: str):
        self.scripts_dir = Path(scripts_dir)
        self.config_file = config_file
        self.scheduler = BackgroundScheduler()
        self.jobs: Dict[str, JobConfig] = {}
        self.job_ids: Dict[str, str] = {}  # JobConfig.script_path -> APScheduler job_id
        
    def load_config(self):
        """設定ファイルの読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            for job_name, job_data in config_data.get('jobs', {}).items():
                job_config = JobConfig(
                    script_path=job_data['script_path'],
                    schedule_type=job_data['schedule_type'],
                    schedule_config=job_data['schedule_config'],
                    max_runs=job_data.get('max_runs'),
                    enabled=job_data.get('enabled', True)
                )
                self.jobs[job_name] = job_config
                
            logger.info(f"設定ファイルを読み込みました: {len(self.jobs)}個のジョブ")
            
        except Exception as e:
            logger.error(f"設定ファイルの読み込みエラー: {e}")
            raise
    
    def execute_script(self, job_name: str):
        """スクリプトの実行"""
        job_config = self.jobs[job_name]
        script_full_path = self.scripts_dir / job_config.script_path
        
        # 実行回数チェック
        if job_config.max_runs is not None:
            if job_config.run_count >= job_config.max_runs:
                logger.info(f"ジョブ '{job_name}' は最大実行回数に達しました")
                # ジョブを削除
                if job_name in self.job_ids:
                    self.scheduler.remove_job(self.job_ids[job_name])
                    del self.job_ids[job_name]
                return
        
        logger.info(f"スクリプト実行開始: {script_full_path}")
        
        try:
            # スクリプトを実行
            result = subprocess.run(
                [sys.executable, str(script_full_path)],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.scripts_dir
            )
            
            # 実行回数をインクリメント
            job_config.run_count += 1
            
            logger.info(f"スクリプト実行成功: {script_full_path}")
            logger.debug(f"標準出力: {result.stdout}")
            
            if result.stderr:
                logger.warning(f"標準エラー出力: {result.stderr}")
                
            # 実行回数が上限に達した場合の処理
            if job_config.max_runs is not None and job_config.run_count >= job_config.max_runs:
                logger.info(f"ジョブ '{job_name}' は最大実行回数 ({job_config.max_runs}) に達しました")
                if job_name in self.job_ids:
                    self.scheduler.remove_job(self.job_ids[job_name])
                    del self.job_ids[job_name]
                    
        except subprocess.CalledProcessError as e:
            logger.error(f"スクリプト実行エラー: {script_full_path}")
            logger.error(f"終了コード: {e.returncode}")
            logger.error(f"標準出力: {e.stdout}")
            logger.error(f"標準エラー出力: {e.stderr}")
            
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
    
    def create_trigger(self, job_config: JobConfig):
        """トリガーの作成"""
        schedule_type = job_config.schedule_type
        config = job_config.schedule_config
        
        if schedule_type == 'cron':
            return CronTrigger(**config)
        elif schedule_type == 'interval':
            return IntervalTrigger(**config)
        elif schedule_type == 'date':
            return DateTrigger(**config)
        else:
            raise ValueError(f"不明なスケジュールタイプ: {schedule_type}")
    
    def start(self):
        """スケジューラーの開始"""
        self.load_config()
        
        # ジョブの登録
        for job_name, job_config in self.jobs.items():
            if not job_config.enabled:
                logger.info(f"ジョブ '{job_name}' は無効化されています")
                continue
                
            try:
                trigger = self.create_trigger(job_config)
                job = self.scheduler.add_job(
                    func=self.execute_script,
                    trigger=trigger,
                    args=[job_name],
                    id=f"job_{job_name}",
                    name=job_name,
                    replace_existing=True
                )
                self.job_ids[job_name] = job.id
                logger.info(f"ジョブ '{job_name}' を登録しました")
                
            except Exception as e:
                logger.error(f"ジョブ '{job_name}' の登録エラー: {e}")
        
        # スケジューラー開始
        self.scheduler.start()
        logger.info("スケジューラーを開始しました")
        
    def stop(self):
        """スケジューラーの停止"""
        self.scheduler.shutdown()
        logger.info("スケジューラーを停止しました")
    
    def list_jobs(self):
        """登録されているジョブの一覧"""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            job_name = job.name
            job_config = self.jobs.get(job_name)
            if job_config:
                jobs_info.append({
                    'name': job_name,
                    'script_path': job_config.script_path,
                    'next_run': str(job.next_run_time),
                    'run_count': job_config.run_count,
                    'max_runs': job_config.max_runs
                })
        return jobs_info

def signal_handler(signum, frame):
    """シグナルハンドラー"""
    logger.info(f"シグナル {signum} を受信しました。終了します...")
    sys.exit(0)

def main():
    """メイン関数"""
    # 環境変数から設定を読み込み
    scripts_dir = os.environ.get('SCRIPTS_DIR', '/app/scripts')
    config_file = os.environ.get('CONFIG_FILE', '/app/config/scheduler.json')
    
    # スケジューラーの作成と開始
    scheduler = ScriptScheduler(scripts_dir, config_file)
    
    # シグナルハンドラーの設定
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        scheduler.start()
        
        # メインループ
        while True:
            # 定期的にジョブ状態をログ出力
            jobs_info = scheduler.list_jobs()
            logger.info(f"アクティブなジョブ数: {len(jobs_info)}")
            for job_info in jobs_info:
                logger.info(f"ジョブ: {job_info['name']}, 次回実行: {job_info['next_run']}, "
                          f"実行回数: {job_info['run_count']}/{job_info['max_runs'] or '無制限'}")
            
            # 60秒待機
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("キーボード割り込みを検出しました")
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
    finally:
        scheduler.stop()

if __name__ == '__main__':
    main()