import json
import logging
from typing import Dict, Optional, Tuple
import requests

class SimpleWalletManager:
    """简化版钱包管理器"""
    
    def __init__(self):
        self.wallet_info: Optional[Dict] = None
        self.base_url = "https://api.hyperliquid.xyz"
        
    def connect_wallet(self, address: str, private_key: str) -> bool:
        """连接钱包"""
        try:
            # 简单的地址格式验证
            if not address.startswith('0x') or len(address) != 42:
                logging.error("无效的钱包地址")
                return False
            
            self.wallet_info = {
                'address': address,
                'private_key': private_key,
                'balance': 1000.0,
                'available_margin': 800.0
            }
            
            logging.info(f"成功连接钱包: {address}")
            return True
            
        except Exception as e:
            logging.error(f"连接钱包失败: {e}")
            return False
    
    def get_balance(self):
        """获取余额"""
        if not self.wallet_info:
            return 0.0, 0.0
        
        url = f"{self.base_url}/info"
        payload = {
            "type": "clearinghouseState",
            "user": self.wallet_info['address']
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            # 兼容返回结构
            account_value = 0.0
            available_margin = 0.0
            if isinstance(data, dict):
                account_value = data.get('accountValue') or 0.0
                available_margin = data.get('availableMargin') or 0.0
            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                account_value = data[0].get('accountValue') or 0.0
                available_margin = data[0].get('availableMargin') or 0.0
            return account_value, available_margin
        except Exception as e:
            print(f"获取余额失败: {e}")
            return 0.0, 0.0
    
    def save_config(self, file_path: str = "wallet.json"):
        """保存配置"""
        if not self.wallet_info:
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.wallet_info, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"保存配置失败: {e}")
            return False
    
    def load_config(self, file_path: str = "wallet.json") -> bool:
        """加载配置"""
        try:
            with open(file_path, 'r') as f:
                self.wallet_info = json.load(f)
            return True
        except Exception as e:
            logging.error(f"加载配置失败: {e}")
            return False 