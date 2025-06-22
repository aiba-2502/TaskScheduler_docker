#!/usr/bin/env python3
import logging
import os
from datetime import datetime

def setup_logger(log_type):
    """
    共通ログ設定関数
    
    Args:
        log_type (str): ログタイプ（billing, confirm, cancel）
    
    Returns:
        logger: 設定済みのloggerオブジェクト
    """
    # ログディレクトリの作成
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # ログファイル名（タイプとタイムスタンプ付き）
    log_filename = os.path.join(log_dir, f'{log_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # ロガーの作成
    logger = logging.getLogger(f'{log_type}_logger')
    logger.setLevel(logging.INFO)
    
    # 既存のハンドラーをクリア（重複を防ぐ）
    logger.handlers.clear()
    
    # ファイルハンドラーの設定
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # フォーマッターの設定
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # ハンドラーをロガーに追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger