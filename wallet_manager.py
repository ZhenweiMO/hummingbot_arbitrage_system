import json
import logging
from typing import Dict, Optional, List
from cryptography.fernet import Fernet
from web3 import Web3
import requests
import time
from eth_account import Account
from eth_account.messages import encode_defunct

class WalletManager:
    """钱包管理器：只负责连接和本地私钥管理，不再管理余额和保证金"""
    def __init__(self, encryption_key: bytes = None):
        if encryption_key is None:
            encryption_key = Fernet.generate_key()
        self.encryption_key = encryption_key
        self.cipher = Fernet(self.encryption_key)
        self.wallet_info: Optional[Dict] = None
        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_KEY'))

    def encrypt_private_key(self, private_key: str) -> str:
        """加密私钥"""
        return self.cipher.encrypt(private_key.encode()).decode()

    def decrypt_private_key(self, encrypted_key: str) -> str:
        """解密私钥"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()

    def connect_wallet(self, address: str, private_key: str) -> bool:
        """连接钱包，仅验证地址和私钥匹配"""
        try:
            if not self.w3.is_address(address):
                logging.error("无效的钱包地址")
                return False
            account = self.w3.eth.account.from_key(private_key)
            if account.address.lower() != address.lower():
                logging.error("私钥与地址不匹配")
                return False
            encrypted_key = self.encrypt_private_key(private_key)
            self.wallet_info = {
                'address': address,
                'private_key': encrypted_key
            }
            logging.info(f"成功连接钱包: {address}")
            return True
        except Exception as e:
            logging.error(f"连接钱包失败: {e}")
            return False

    def save_wallet_config(self, file_path: str = "wallet_config.json"):
        """保存钱包配置，只保存地址和加密私钥"""
        if not self.wallet_info:
            logging.error("没有钱包信息可保存")
            return False
        try:
            enc_key = self.encryption_key.decode() if isinstance(self.encryption_key, bytes) else (self.encryption_key or "")
            config_data = {
                'address': self.wallet_info['address'],
                'encrypted_private_key': self.wallet_info['private_key'],
                'encryption_key': enc_key
            }
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            logging.info(f"钱包配置已保存到: {file_path}")
            return True
        except Exception as e:
            logging.error(f"保存钱包配置失败: {e}")
            return False

    def load_wallet_config(self, file_path: str = "wallet_config.json") -> bool:
        """加载钱包配置，只加载地址和加密私钥"""
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            enc_key = config_data.get('encryption_key', None)
            if enc_key is None:
                enc_key = Fernet.generate_key()
                logging.warning("wallet.json 缺少 encryption_key，已自动生成新密钥。建议重新保存配置文件！")
            elif isinstance(enc_key, str):
                enc_key = enc_key.encode()
            self.encryption_key = enc_key
            self.cipher = Fernet(self.encryption_key)
            self.wallet_info = {
                'address': config_data['address'],
                'private_key': config_data['encrypted_private_key']
            }
            logging.info(f"钱包配置已从 {file_path} 加载")
            return True
        except Exception as e:
            logging.error(f"加载钱包配置失败: {e}")
            return False

class HyperliquidWalletAPI:
    """Hyperliquid钱包API接口"""
    
    def __init__(self, wallet_manager: WalletManager):
        self.wallet_manager = wallet_manager
        self.base_url = "https://api.hyperliquid.xyz"
        self.session = requests.Session()
    
    def get_account_info(self) -> Dict:
        """获取账户信息（通过 Hyperliquid API 实时查询）"""
        try:
            if not self.wallet_manager.wallet_info:
                return {}
            address = self.wallet_manager.wallet_info['address']
            url = f"{self.base_url}/info"
            payload = {
                "type": "clearinghouseState",
                "user": address
            }
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            # 解析返回数据，提取余额和可用保证金
            # 兼容返回结构
            account_value = 0.0
            available_margin = 0.0
            if isinstance(data, dict):
                account_value = data.get('accountValue', 0.0)
                available_margin = data.get('availableMargin', 0.0)
            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                account_value = data[0].get('accountValue', 0.0)
                available_margin = data[0].get('availableMargin', 0.0)
            return {
                'address': address,
                'balance': account_value,
                'available_margin': available_margin,
                'raw': data
            }
        except Exception as e:
            logging.error(f"获取账户信息失败: {e}")
            return {}
    
    def place_order(self, trading_pair: str, side: str, amount: float, price: float = None, order_type: str = "market") -> Dict:
        """真实下单接口，EVM私钥签名"""
        try:
            if not self.wallet_manager.wallet_info:
                return {'status': 'failed', 'error': '钱包未连接'}
            address = self.wallet_manager.wallet_info['address']
            private_key = self.wallet_manager.decrypt_private_key(self.wallet_manager.wallet_info['private_key'])
            nonce = int(time.time() * 1000)
            is_buy = side.lower() == 'buy'
            # 构造 order_type 字段
            if order_type == "market":
                order_type_obj = {"market": {}}
            else:
                order_type_obj = {"limit": {"tif": "Gtc"}}
            # 币对自动补全
            if not trading_pair.endswith('-PERP'):
                trading_pair = trading_pair + '-PERP'
            investment_amount = amount  # 保证金
            leverage = 1.0  # 假设杠杆为1倍
            current_price = price if price else 0.0  # 实时获取
            notional = investment_amount * leverage
            sz = notional / current_price
            payload = {
                "coin": trading_pair,
                "is_buy": is_buy,
                "sz": sz,
                "order_type": order_type_obj,
                "reduce_only": False,
                "nonce": nonce,
                "address": address
            }
            if order_type != "market" and price is not None:
                payload["limit_px"] = price
            logging.info(f"下单payload: {json.dumps(payload, ensure_ascii=False)}")
            # 签名
            message = json.dumps(payload, separators=(',', ':'), sort_keys=True)
            sign_msg = encode_defunct(text=message)
            signature = Account.sign_message(sign_msg, private_key=private_key).signature.hex()
            payload["signature"] = signature
            url = f"{self.base_url}/exchange"
            headers = {"Content-Type": "application/json"}
            resp = self.session.post(url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if 'status' in data and data['status'] == 'failed':
                logging.error(f"下单失败: {data}")
            return data
        except Exception as e:
            logging.error(f"下单失败: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        try:
            # 这里需要实现实际的取消订单接口
            logging.info(f"订单已取消: {order_id}")
            return True
            
        except Exception as e:
            logging.error(f"取消订单失败: {e}")
            return False
    
    def get_open_orders(self) -> List[Dict]:
        """获取未成交订单"""
        try:
            # 这里需要实现实际的API调用
            # 暂时返回空列表
            return []
            
        except Exception as e:
            logging.error(f"获取未成交订单失败: {e}")
            return []
    
    def get_position_history(self, trading_pair: str = None) -> List[Dict]:
        """获取持仓历史"""
        try:
            # 这里需要实现实际的API调用
            # 暂时返回模拟数据
            return [
                {
                    'trading_pair': 'BTC',
                    'side': 'long',
                    'size': 0.1,
                    'entry_price': 45000.0,
                    'current_price': 45100.0,
                    'pnl': 10.0,
                    'funding_rate': -0.0001
                }
            ]
            
        except Exception as e:
            logging.error(f"获取持仓历史失败: {e}")
            return []

def main():
    """测试钱包管理器"""
    print("钱包管理器测试")
    print("="*30)
    
    # 创建钱包管理器
    wallet_manager = WalletManager()
    
    # 测试钱包连接（使用示例数据）
    address = "0x1234567890123456789012345678901234567890"
    private_key = "0x" + "1" * 64  # 示例私钥
    
    if wallet_manager.connect_wallet(address, private_key):
        print("钱包连接成功")
        
        # 保存配置
        wallet_manager.save_wallet_config()
        
    else:
        print("钱包连接失败")

if __name__ == "__main__":
    main() 