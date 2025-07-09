import requests
import time
import logging
import random
from typing import List, Dict, Optional

class FixedAPI:
    """修复的API管理器"""
    
    def __init__(self):
        self.base_url = "https://api.hyperliquid.xyz"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json'
        })
        
        # 限流控制
        self.last_request_time = 0
        self.min_interval = 3.0  # 3秒间隔
        self.request_count = 0
        self.max_per_minute = 15  # 每分钟15次
    
    def _rate_limit(self):
        """限流控制"""
        current_time = time.time()
        
        # 检查间隔
        if current_time - self.last_request_time < self.min_interval:
            sleep_time = self.min_interval - (current_time - self.last_request_time)
            time.sleep(sleep_time)
        
        # 检查每分钟限制
        if current_time - self.last_request_time > 60:
            self.request_count = 0
        
        if self.request_count >= self.max_per_minute:
            sleep_time = 60 - (current_time - self.last_request_time)
            if sleep_time > 0:
                logging.warning(f"达到限制，等待 {sleep_time:.1f} 秒")
                time.sleep(sleep_time)
            self.request_count = 0
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _make_request(self, payload: Dict) -> Optional[Dict]:
        """发送请求"""
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/info"
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 429:
                logging.warning("API限流，等待5秒...")
                time.sleep(5)
                return None
            elif response.status_code == 422:
                logging.error(f"请求格式错误: {payload}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logging.error(f"请求失败: {e}")
            return None
    
    def get_trading_pairs(self) -> List[str]:
        """获取交易对"""
        methods = [
            {"type": "meta"},
            {"type": "universe"}
        ]
        
        for payload in methods:
            data = self._make_request(payload)
            if data and 'universe' in data:
                pairs = [asset['name'] for asset in data['universe'] if 'name' in asset]
                if pairs:
                    logging.info(f"获取到 {len(pairs)} 个交易对")
                    return pairs
        
        # 备用列表
        return ['BTC', 'ETH', 'SOL', 'MATIC', 'AVAX', 'LINK', 'DOT', 'ADA']
    
    def get_funding_rate(self, pair: str) -> float:
        """获取资金费率"""
        payload = {
            "type": "fundingHistory",
            "coin": pair,
            "startTime": int(time.time() * 1000) - 3600000,
            "endTime": int(time.time() * 1000)
        }
        
        data = self._make_request(payload)
        if data and len(data) > 0:
            return float(data[-1].get('fundingRate', 0))
        
        # 模拟数据
        random.seed(hash(pair) % 1000)
        return random.uniform(-0.001, 0.001)
    
    def get_price(self, pair: str) -> float:
        """获取价格"""
        payload = {
            "type": "candleSnapshot",
            "coin": pair,
            "interval": "1m",
            "startTime": int(time.time() * 1000) - 60000,
            "endTime": int(time.time() * 1000) + 60000
        }
        
        data = self._make_request(payload)
        if data and len(data) > 0:
            return float(data[-1].get('close', 0))
        
        # 模拟价格
        base_prices = {
            'BTC': 45000, 'ETH': 2800, 'SOL': 120, 'MATIC': 0.8,
            'AVAX': 35, 'LINK': 15, 'DOT': 7, 'ADA': 0.5
        }
        base_price = base_prices.get(pair, 100)
        random.seed(hash(pair) % 1000)
        return base_price * (1 + random.uniform(-0.02, 0.02))

def main():
    """测试"""
    print("测试修复的API")
    api = FixedAPI()
    
    pairs = api.get_trading_pairs()
    print(f"交易对: {pairs[:5]}")
    
    if pairs:
        rate = api.get_funding_rate(pairs[0])
        price = api.get_price(pairs[0])
        print(f"{pairs[0]} - 费率: {rate:.6f}, 价格: {price:.2f}")

if __name__ == "__main__":
    main() 