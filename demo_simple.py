#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyperliquid资金费率套利系统 - 简单演示版本
"""

import time
import logging
import random
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DemoSystem:
    """演示系统"""
    
    def __init__(self):
        self.trading_pairs = ['BTC', 'ETH', 'SOL', 'MATIC', 'AVAX', 'LINK', 'DOT', 'ADA']
        self.is_running = False
        self.current_position = None
        
    def get_funding_rates(self):
        """获取模拟资金费率"""
        rates = {}
        for pair in self.trading_pairs:
            # 使用时间戳生成可重现的随机数据
            random.seed(int(time.time() / 60) + hash(pair))
            rates[pair] = random.uniform(-0.002, 0.002)
        return rates
    
    def find_best_pair(self):
        """找到最佳套利交易对"""
        rates = self.get_funding_rates()
        best_pair = None
        best_rate = 0.0
        
        for pair, rate in rates.items():
            print(f"{pair}: {rate:.6f}")
            if rate < -0.0001 and rate < best_rate:
                best_rate = rate
                best_pair = pair
        
        return best_pair, best_rate
    
    def execute_strategy(self):
        """执行策略"""
        now = datetime.now()
        
        # 只在整点前后5秒执行
        if now.second < 5 or now.second > 55:
            return
        
        print(f"\n时间: {now.strftime('%H:%M:%S')}")
        
        # 找到最佳交易对
        best_pair, best_rate = self.find_best_pair()
        
        if best_pair:
            print(f"选择交易对: {best_pair}, 资金费率: {best_rate:.6f}")
            
            # 模拟交易
            if now.second < 5 and not self.current_position:
                print(f"执行开仓: {best_pair}")
                self.current_position = {
                    'pair': best_pair,
                    'rate': best_rate,
                    'time': now
                }
            
            elif now.second > 55 and self.current_position:
                print(f"执行平仓: {best_pair}")
                # 模拟收益计算
                profit = random.uniform(-10, 20)
                print(f"收益: {profit:.2f} USDT")
                self.current_position = None
        else:
            print("未找到合适的套利机会")
    
    def start(self):
        """启动系统"""
        self.is_running = True
        print("演示系统已启动")
        print("按 Ctrl+C 停止")
        
        while self.is_running:
            try:
                self.execute_strategy()
                time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self):
        """停止系统"""
        self.is_running = False
        print("\n演示系统已停止")

def main():
    """主函数"""
    print("Hyperliquid资金费率套利系统 - 演示版本")
    print("="*50)
    print("使用模拟数据演示策略逻辑")
    print("="*50)
    
    system = DemoSystem()
    system.start()

if __name__ == "__main__":
    main() 