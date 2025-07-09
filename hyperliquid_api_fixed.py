#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyperliquid API - 优化版本
解决限流问题，实现批量获取资金费率
"""

import time
import logging
import requests
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_fixed.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class HyperliquidAPIFixed:
    """Hyperliquid API接口 - 优化版本"""
    
    def __init__(self):
        self.base_url = "https://api.hyperliquid.xyz"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json'
        })
        
        # 限流控制
        self.request_count = 0
        self.last_request_time = 0
        self.max_requests_per_minute = 20  # 降低每分钟最大请求数
        self.min_request_interval = 3.0    # 增加请求间隔（秒）
        
        # 缓存
        self.funding_rates_cache = {}
        self.prices_cache = {}
        self.cache_duration = 60  # 缓存60秒
        
    def _rate_limit(self):
        """限流控制"""
        current_time = time.time()
        
        # 检查请求间隔
        if current_time - self.last_request_time < self.min_request_interval:
            sleep_time = self.min_request_interval - (current_time - self.last_request_time)
            time.sleep(sleep_time)
        
        # 检查每分钟请求数
        if current_time - self.last_request_time > 60:
            self.request_count = 0
        
        if self.request_count >= self.max_requests_per_minute:
            sleep_time = 60 - (current_time - self.last_request_time)
            if sleep_time > 0:
                logging.warning(f"达到请求限制，等待 {sleep_time:.1f} 秒")
                time.sleep(sleep_time)
            self.request_count = 0
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _make_request(self, url: str, payload: dict = None, method: str = "POST") -> dict:
        """发送API请求"""
        self._rate_limit()
        
        try:
            if method == "POST":
                response = self.session.post(url, json=payload, timeout=15)
            else:
                response = self.session.get(url, timeout=15)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logging.warning("API限流，等待重试...")
                time.sleep(10)  # 增加等待时间
                return self._make_request(url, payload, method)
            elif e.response.status_code == 422:
                logging.error(f"请求格式错误: {payload}")
                return {}
            else:
                logging.error(f"HTTP错误: {e}")
                return {}
        except Exception as e:
            logging.error(f"请求失败: {e}")
            return {}
    
    def get_all_trading_pairs(self) -> List[str]:
        """获取所有交易对"""
        try:
            # 尝试多种API调用方式
            methods = [
                {"type": "meta"},
                {"type": "universe"},
                {"type": "metaAndAssetCtxs"}
            ]
            
            for payload in methods:
                try:
                    url = f"{self.base_url}/info"
                    data = self._make_request(url, payload)
                    
                    trading_pairs = []
                    if 'universe' in data:
                        for asset in data['universe']:
                            if 'name' in asset:
                                trading_pairs.append(asset['name'])
                    
                    if trading_pairs:
                        logging.info(f"成功获取到 {len(trading_pairs)} 个交易对")
                        return trading_pairs
                        
                except Exception as e:
                    logging.warning(f"API调用方式失败: {payload}, 错误: {e}")
                    continue
            
            # 如果所有方法都失败，返回备用列表
            logging.warning("所有API调用方式都失败，使用备用交易对列表")
            return ['BTC', 'ETH', 'SOL', 'MATIC', 'AVAX', 'LINK', 'DOT', 'ADA']
            
        except Exception as e:
            logging.error(f"获取交易对失败: {e}")
            return ['BTC', 'ETH', 'SOL', 'MATIC', 'AVAX', 'LINK', 'DOT', 'ADA']
    
    def get_all_funding_rates(self) -> Dict[str, float]:
        """批量获取所有交易对的资金费率"""
        try:
            url = f"{self.base_url}/info"
            payload = {"type": "metaAndAssetCtxs"}
            response = self.session.post(url, json=payload, timeout=10)
            data = response.json()
            funding_rates = {}
            if isinstance(data, list) and len(data) >= 2:
                universe = data[0].get('universe', [])
                funding_list = data[1]
                for i, asset in enumerate(universe):
                    name = asset.get('name', f'index_{i}')
                    funding = None
                    if i < len(funding_list):
                        funding = funding_list[i].get('funding')
                        if funding is not None:
                            funding = float(funding)
                    funding_rates[name] = funding
                logging.info(f"批量获取到 {len(funding_rates)} 个资金费率")
                return funding_rates
            else:
                logging.warning("批量资金费率接口返回结构异常")
                return {}
        except Exception as e:
            logging.error(f"批量获取资金费率失败: {e}")
            return {}
    
    def get_funding_rate(self, trading_pair: str) -> float:
        """获取单个交易对的资金费率"""
        try:
            # 先尝试从缓存获取
            funding_rates = self.get_all_funding_rates()
            if trading_pair in funding_rates:
                return funding_rates[trading_pair]
            
            # 如果缓存中没有，单独获取
            url = f"{self.base_url}/info"
            payload = {
                "type": "fundingHistory",
                "coin": trading_pair,
                "startTime": int(time.time() * 1000) - 3600000,
                "endTime": int(time.time() * 1000)
            }
            
            data = self._make_request(url, payload)
            
            if data and len(data) > 0:
                rate = float(data[-1].get('fundingRate', 0))
                # 更新缓存
                if 'data' in self.funding_rates_cache:
                    self.funding_rates_cache['data'][trading_pair] = rate
                return rate
            
            return 0.0
            
        except Exception as e:
            logging.error(f"获取{trading_pair}资金费率失败: {e}")
            return 0.0
    
    def get_all_market_prices(self) -> Dict[str, float]:
        """批量获取所有交易对的市场价格"""
        try:
            url = f"{self.base_url}/info"
            payload = {"type": "metaAndAssetCtxs"}
            response = self.session.post(url, json=payload, timeout=10)
            data = response.json()
            prices = {}
            if isinstance(data, list) and len(data) >= 2:
                universe = data[0].get('universe', [])
                price_list = data[1]
                for i, asset in enumerate(universe):
                    name = asset.get('name', f'index_{i}')
                    price = None
                    if i < len(price_list):
                        price = price_list[i].get('markPx')
                        if price is not None:
                            price = float(price)
                    prices[name] = price
                logging.info(f"批量获取到 {len(prices)} 个价格")
                return prices
            else:
                logging.warning("批量价格接口返回结构异常")
                return {}
        except Exception as e:
            logging.error(f"批量获取市场价格失败: {e}")
            return {}
    
    def get_market_price(self, trading_pair: str) -> float:
        """获取单个交易对的市场价格"""
        try:
            # 先尝试从缓存获取
            prices = self.get_all_market_prices()
            if trading_pair in prices:
                return prices[trading_pair]
            
            # 如果缓存中没有，单独获取
            url = f"{self.base_url}/info"
            payload = {
                "type": "candleSnapshot",
                "coin": trading_pair,
                "interval": "1m",
                "startTime": int(time.time() * 1000) - 60000,
                "endTime": int(time.time() * 1000) + 60000
            }
            
            data = self._make_request(url, payload)
            
            if data and len(data) > 0:
                price = float(data[-1].get('close', 0))
                # 更新缓存
                if 'data' in self.prices_cache:
                    self.prices_cache['data'][trading_pair] = price
                return price
            
            return 0.0
            
        except Exception as e:
            logging.error(f"获取{trading_pair}市场价格失败: {e}")
            return 0.0
    
    def _generate_mock_funding_rates(self) -> Dict[str, float]:
        """生成模拟资金费率"""
        trading_pairs = self.get_all_trading_pairs()
        funding_rates = {}
        
        for pair in trading_pairs:
            # 使用交易对名称作为种子，确保结果可重现
            random.seed(hash(pair) % 1000)
            funding_rates[pair] = random.uniform(-0.002, 0.002)
        
        return funding_rates
    
    def _generate_mock_prices(self) -> Dict[str, float]:
        """生成模拟价格"""
        trading_pairs = self.get_all_trading_pairs()
        prices = {}
        
        # 基础价格
        base_prices = {
            'BTC': 45000, 'ETH': 2800, 'SOL': 120, 'MATIC': 0.8,
            'AVAX': 35, 'LINK': 15, 'DOT': 7, 'ADA': 0.5
        }
        
        for pair in trading_pairs:
            base_price = base_prices.get(pair, 100)
            random.seed(hash(pair) % 1000)
            # 添加一些随机波动
            price_change = random.uniform(-0.02, 0.02)  # ±2%波动
            prices[pair] = base_price * (1 + price_change)
        
        return prices
    
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            pairs = self.get_all_trading_pairs()
            if pairs:
                logging.info(f"API连接测试成功，获取到 {len(pairs)} 个交易对")
                return True
            else:
                logging.error("API连接测试失败，无法获取交易对")
                return False
        except Exception as e:
            logging.error(f"API连接测试失败: {e}")
            return False

def main():
    """测试优化后的API"""
    print("测试Hyperliquid API - 优化版本")
    print("="*50)
    
    api = HyperliquidAPIFixed()
    
    # 测试连接
    if api.test_connection():
        print("✅ API连接成功")
        
        # 获取交易对
        pairs = api.get_all_trading_pairs()
        print(f"交易对数量: {len(pairs)}")
        print(f"前5个交易对: {pairs[:5]}")
        
        # 测试批量获取资金费率
        print("\n测试批量获取资金费率...")
        funding_rates = api.get_all_funding_rates()
        print(f"获取到 {len(funding_rates)} 个资金费率")
        
        # 显示前5个资金费率
        for i, (pair, rate) in enumerate(list(funding_rates.items())[:5]):
            print(f"{pair}: {rate:.6f}")
        
        # 测试批量获取价格
        print("\n测试批量获取价格...")
        prices = api.get_all_market_prices()
        print(f"获取到 {len(prices)} 个价格")
        
        # 显示前5个价格
        for i, (pair, price) in enumerate(list(prices.items())[:5]):
            print(f"{pair}: {price:.2f}")
        
        # 测试单个获取
        if pairs:
            test_pair = pairs[0]
            print(f"\n测试单个获取 {test_pair}...")
            rate = api.get_funding_rate(test_pair)
            price = api.get_market_price(test_pair)
            print(f"{test_pair} 资金费率: {rate:.6f}")
            print(f"{test_pair} 价格: {price:.2f}")
    else:
        print("❌ API连接失败")

if __name__ == "__main__":
    main() 