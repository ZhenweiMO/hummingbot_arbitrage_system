"""
交易所连接器 - 用于实时获取账户余额和交易信息
支持多个交易所的 API 连接
"""

import asyncio
import aiohttp
import hmac
import hashlib
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
import base64

logger = logging.getLogger(__name__)

class ExchangeType(Enum):
    BINANCE = "binance"
    OKX = "okx"
    BYBIT = "bybit"
    GATE_IO = "gate_io"

@dataclass
class Balance:
    asset: str
    free: float
    locked: float
    total: float

@dataclass
class AccountInfo:
    exchange: str
    account_id: str
    balances: List[Balance]
    total_equity: float
    timestamp: float

class ExchangeConnector:
    """交易所连接器基类"""
    
    def __init__(self, api_key: str, api_secret: str, exchange_type: ExchangeType):
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange_type = exchange_type
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_account_balance(self) -> Optional[AccountInfo]:
        """获取账户余额 - 子类需要实现"""
        raise NotImplementedError
    
    def _sign_request(self, params: Dict[str, Any]) -> str:
        """签名请求 - 子类需要实现"""
        raise NotImplementedError

class BinanceConnector(ExchangeConnector):
    """币安交易所连接器"""
    
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret, ExchangeType.BINANCE)
        self.base_url = "https://api.binance.com"
    
    def _sign_request(self, params: Dict[str, Any]) -> str:
        """生成币安 API 签名"""
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def get_account_balance(self) -> Optional[AccountInfo]:
        """获取币安账户余额"""
        try:
            endpoint = "/api/v3/account"
            params = {
                'timestamp': int(time.time() * 1000),
                'recvWindow': 5000
            }
            
            # 添加签名
            params['signature'] = self._sign_request(params)
            
            headers = {
                'X-MBX-APIKEY': self.api_key
            }
            
            async with self.session.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    balances = []
                    total_equity = 0.0
                    
                    for balance in data.get('balances', []):
                        free = float(balance.get('free', 0))
                        locked = float(balance.get('locked', 0))
                        total = free + locked
                        
                        if total > 0:  # 只返回有余额的资产
                            balances.append(Balance(
                                asset=balance['asset'],
                                free=free,
                                locked=locked,
                                total=total
                            ))
                            total_equity += total
                    
                    return AccountInfo(
                        exchange="binance",
                        account_id=data.get('accountType', 'SPOT'),
                        balances=balances,
                        total_equity=total_equity,
                        timestamp=time.time()
                    )
                else:
                    logger.error(f"币安 API 请求失败: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"获取币安账户余额失败: {e}")
            return None

class OKXConnector(ExchangeConnector):
    """OKX 交易所连接器"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str = ""):
        super().__init__(api_key, api_secret, ExchangeType.OKX)
        self.passphrase = passphrase
        self.base_url = "https://www.okx.com"
    
    def _sign_request(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        """生成 OKX API 签名"""
        message = timestamp + method + request_path + body
        return base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode()
    
    async def get_account_balance(self) -> Optional[AccountInfo]:
        """获取 OKX 账户余额"""
        try:
            endpoint = "/api/v5/account/balance"
            timestamp = str(int(time.time()))
            
            headers = {
                'OK-ACCESS-KEY': self.api_key,
                'OK-ACCESS-SIGN': self._sign_request(timestamp, 'GET', endpoint),
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-PASSPHRASE': self.passphrase,
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(
                f"{self.base_url}{endpoint}",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('code') == '0':
                        account_data = data.get('data', [{}])[0]
                        
                        balances = []
                        total_equity = 0.0
                        
                        for balance in account_data.get('details', []):
                            free = float(balance.get('availBal', 0))
                            locked = float(balance.get('frozenBal', 0))
                            total = free + locked
                            
                            if total > 0:
                                balances.append(Balance(
                                    asset=balance['ccy'],
                                    free=free,
                                    locked=locked,
                                    total=total
                                ))
                                total_equity += total
                        
                        return AccountInfo(
                            exchange="okx",
                            account_id=account_data.get('acctId', ''),
                            balances=balances,
                            total_equity=total_equity,
                            timestamp=time.time()
                        )
                    else:
                        logger.error(f"OKX API 错误: {data}")
                        return None
                else:
                    logger.error(f"OKX API 请求失败: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"获取 OKX 账户余额失败: {e}")
            return None

class ExchangeManager:
    """交易所管理器"""
    
    def __init__(self):
        self.connectors: Dict[str, ExchangeConnector] = {}
    
    def add_connector(self, account_id: str, connector: ExchangeConnector):
        """添加交易所连接器"""
        self.connectors[account_id] = connector
    
    async def get_all_accounts_balance(self) -> Dict[str, AccountInfo]:
        """获取所有账户余额"""
        results = {}
        
        for account_id, connector in self.connectors.items():
            try:
                async with connector:
                    balance = await connector.get_account_balance()
                    if balance:
                        results[account_id] = balance
            except Exception as e:
                logger.error(f"获取账户 {account_id} 余额失败: {e}")
        
        return results
    
    async def get_account_balance(self, account_id: str) -> Optional[AccountInfo]:
        """获取指定账户余额"""
        if account_id not in self.connectors:
            return None
        
        try:
            async with self.connectors[account_id]:
                return await self.connectors[account_id].get_account_balance()
        except Exception as e:
            logger.error(f"获取账户 {account_id} 余额失败: {e}")
            return None

# 全局交易所管理器实例
exchange_manager = ExchangeManager()

# 工厂函数
def create_connector(exchange_type: str, api_key: str, api_secret: str, **kwargs) -> ExchangeConnector:
    """创建交易所连接器"""
    if exchange_type.lower() == "binance":
        return BinanceConnector(api_key, api_secret)
    elif exchange_type.lower() == "okx":
        passphrase = kwargs.get('passphrase', '')
        return OKXConnector(api_key, api_secret, passphrase)
    else:
        raise ValueError(f"不支持的交易所类型: {exchange_type}")

# 异步任务：定期更新账户余额
async def update_account_balances_task():
    """定期更新账户余额的任务"""
    while True:
        try:
            balances = await exchange_manager.get_all_accounts_balance()
            logger.info(f"更新了 {len(balances)} 个账户的余额")
            
            # 这里可以将余额信息存储到数据库或缓存中
            # 例如：redis.set('account_balances', json.dumps(balances))
            
        except Exception as e:
            logger.error(f"更新账户余额失败: {e}")
        
        # 每60秒更新一次
        await asyncio.sleep(60)

# 启动余额更新任务
def start_balance_update_task():
    """启动余额更新任务"""
    loop = asyncio.get_event_loop()
    loop.create_task(update_account_balances_task())
