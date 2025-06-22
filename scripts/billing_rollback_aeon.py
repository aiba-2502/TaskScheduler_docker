import requests
import json
from datetime import datetime
from logger import setup_logger


logger = setup_logger('billing_rollback')

def generate_request_at():
    """YYYYMMDDHHMMSSmmm形式の17桁タイムスタンプ"""
    now = datetime.now()
    return now.strftime("%Y%m%d%H%M%S") + now.strftime("%f")[:3]

def test_billing_rollback_aeon():
    url = "http://localhost:8000/api/aeonpay/cancel"  # AEONの決済APIエンドポイント
    
    logger.info("=== AEON決済処理開始 ===")

    # ヘッダー
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
 
    # リクエストボディ（AEON形式）
    request_body = {
        "header_div": {
            "store_code": "2014",
            "block_type": "99",
            "shop_type": "22",
            "data_type": "153000",
            "transaction_send_div": "7",
            "terminal_no": "string",
            "store_transaction_id": "00001",
            "request_at": generate_request_at(),
            "register_no": "0000"
        },
        "data_div": {
            "business_div": "4",
            "card_div": "3",
            "code_payment_div_req": "10",
            "product_code": "0000990",
            "pay_amount": "00000010",
            "company_code": "9944 769999"
        }
    }

    print("\n=== 決済リクエスト（AEON形式） ===")
    print(f"URL: {url}")
    print("リクエストボディ:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))
    
    logger.info(f"リクエストURL: {url}")
    logger.info(f"リクエストボディ: {json.dumps(request_body, ensure_ascii=False)}")
    
    try:
        # リクエスト送信
        logger.info("APIリクエスト送信中...")
        response = requests.post(url, json=request_body, headers=headers)
        
        print(f"\nステータスコード: {response.status_code}")
        print("レスポンス:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        logger.info(f"レスポンスステータスコード: {response.status_code}")
        logger.info(f"レスポンスボディ: {json.dumps(response.json(), ensure_ascii=False)}")
        logger.info("=== AEON決済処理完了 ===")
        
    except requests.exceptions.RequestException as e:
        print(f"\nリクエストエラー: {e}")
        logger.error(f"リクエストエラー: {e}")
    except json.JSONDecodeError:
        print(f"\nレスポンス（非JSON）: {response.text}")
        logger.error(f"JSONデコードエラー。レスポンス: {response.text}")

if __name__ == "__main__":
    test_billing_rollback_aeon()
