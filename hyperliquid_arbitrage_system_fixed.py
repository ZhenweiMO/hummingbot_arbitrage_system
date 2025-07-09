#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyperliquid资金费率套利系统 - 优化版本
使用批量API调用解决限流问题
"""

import time
import logging
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import schedule

# 导入优化版本的API
from hyperliquid_api_fixed import HyperliquidAPIFixed

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage_system_fixed.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class TradingConfig:
    """交易配置"""
    def __init__(self):
        self.leverage = 10  # 杠杆倍数
        self.investment_amount = 100.0  # 投资金额(USDT)
        self.pre_execution_seconds = 5  # 整点前执行秒数
        self.post_execution_seconds = 5  # 整点后执行秒数
        self.min_funding_rate_threshold = -0.0001  # 最小资金费率阈值

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "arbitrage_system_fixed.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                datetime TEXT,
                trading_pair TEXT,
                action TEXT,
                price REAL,
                amount REAL,
                leverage INTEGER,
                funding_rate REAL,
                profit REAL,
                balance_before REAL,
                balance_after REAL,
                status TEXT
            )
        ''')
        
        # 创建资金费率记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funding_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                datetime TEXT,
                trading_pair TEXT,
                funding_rate REAL
            )
        ''')
        
        # 创建钱包余额记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet_balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                datetime TEXT,
                balance REAL,
                available_margin REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_trade(self, trade_data: Dict):
        """保存交易记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                timestamp, datetime, trading_pair, action, price, amount,
                leverage, funding_rate, profit, balance_before, balance_after, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data['timestamp'],
            trade_data['datetime'],
            trade_data['trading_pair'],
            trade_data['action'],
            trade_data['price'],
            trade_data['amount'],
            trade_data['leverage'],
            trade_data['funding_rate'],
            trade_data['profit'],
            trade_data['balance_before'],
            trade_data['balance_after'],
            trade_data['status']
        ))
        
        conn.commit()
        conn.close()
    
    def save_funding_rate(self, pair: str, rate: float):
        """保存资金费率"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = int(time.time() * 1000)
        datetime_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO funding_rates (timestamp, datetime, trading_pair, funding_rate)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, datetime_str, pair, rate))
        
        conn.commit()
        conn.close()
    
    def save_funding_rates_batch(self, funding_rates: Dict[str, float]):
        """批量保存资金费率"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = int(time.time() * 1000)
        datetime_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        
        for pair, rate in funding_rates.items():
            cursor.execute('''
                INSERT INTO funding_rates (timestamp, datetime, trading_pair, funding_rate)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, datetime_str, pair, rate))
        
        conn.commit()
        conn.close()
    
    def save_wallet_balance(self, balance: float, available_margin: float):
        """保存钱包余额"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = int(time.time() * 1000)
        datetime_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO wallet_balances (timestamp, datetime, balance, available_margin)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, datetime_str, balance, available_margin))
        
        conn.commit()
        conn.close()

class WalletManager:
    """钱包管理器"""
    
    def __init__(self):
        self.wallet_info = None
    
    def connect_metamask(self, address: str, private_key: str) -> bool:
        """连接MetaMask钱包"""
        try:
            # 这里应该实现实际的MetaMask连接逻辑
            # 暂时使用模拟数据
            self.wallet_info = {
                'address': address,
                'private_key': private_key,
                'balance': 1000.0,
                'available_margin': 900.0
            }
            logging.info(f"钱包连接成功: {address}")
            return True
        except Exception as e:
            logging.error(f"钱包连接失败: {e}")
            return False
    
    def get_wallet_balance(self) -> Tuple[float, float]:
        """获取钱包余额"""
        if self.wallet_info:
            return self.wallet_info['balance'], self.wallet_info['available_margin']
        return 0.0, 0.0

class ArbitrageEngine:
    """套利引擎 - 优化版本"""
    
    def __init__(self, config: TradingConfig, wallet_manager: WalletManager, 
                 api: HyperliquidAPIFixed, db_manager: DatabaseManager):
        self.config = config
        self.wallet_manager = wallet_manager
        self.api = api
        self.db_manager = db_manager
        self.is_running = False
        self.current_position = None
        
    def find_best_arbitrage_pair(self) -> Optional[Tuple[str, float]]:
        """找到最佳套利交易对 - 使用批量API"""
        try:
            # 批量获取所有资金费率
            funding_rates = self.api.get_all_funding_rates()
            
            if not funding_rates:
                logging.warning("无法获取资金费率数据")
                return None, 0.0
            
            # 保存所有资金费率到数据库
            self.db_manager.save_funding_rates_batch(funding_rates)
            
            best_pair = None
            best_rate = 0.0
            
            # 寻找最佳套利机会
            for pair, rate in funding_rates.items():
                # 寻找负费率且绝对值最低的交易对
                if rate < self.config.min_funding_rate_threshold and rate < best_rate:
                    best_rate = rate
                    best_pair = pair
            
            if best_pair:
                logging.info(f"找到套利机会: {best_pair}, 资金费率: {best_rate:.6f}")
                return best_pair, best_rate
            else:
                logging.info("未找到合适的套利机会")
                return None, 0.0
            
        except Exception as e:
            logging.error(f"寻找套利交易对失败: {e}")
            return None, 0.0
    
    def execute_arbitrage_strategy(self):
        """执行套利策略"""
        try:
            # 获取当前时间
            now = datetime.now()
            
            # 检查是否接近整点
            if now.second < self.config.pre_execution_seconds or now.second > (60 - self.config.post_execution_seconds):
                return
            
            # 找到最佳套利交易对
            result = self.find_best_arbitrage_pair()
            if result[0] is None:
                return
            
            best_pair, best_rate = result
            
            # 获取钱包余额
            balance, available_margin = self.wallet_manager.get_wallet_balance()
            self.db_manager.save_wallet_balance(balance, available_margin)
            
            if available_margin < self.config.investment_amount:
                logging.warning(f"可用保证金不足: {available_margin} < {self.config.investment_amount}")
                return
            
            # 获取当前价格
            current_price = self.api.get_market_price(best_pair)
            if current_price <= 0:
                logging.error("获取价格失败")
                return
            
            # 计算开仓数量
            position_size = (self.config.investment_amount * self.config.leverage) / current_price
            
            # 执行开仓
            if not self.current_position and now.second < self.config.pre_execution_seconds:
                logging.info(f"执行开仓: {best_pair}, 价格: {current_price:.4f}, 数量: {position_size:.4f}")
                
                # 记录开仓前余额
                balance_before = available_margin
                
                # 模拟开仓
                self.current_position = {
                    'pair': best_pair,
                    'entry_price': current_price,
                    'size': position_size,
                    'funding_rate': best_rate,
                    'entry_time': now
                }
                
                # 保存交易记录
                self.db_manager.save_trade({
                    'timestamp': int(time.time() * 1000),
                    'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'trading_pair': best_pair,
                    'action': 'open',
                    'price': current_price,
                    'amount': position_size,
                    'leverage': self.config.leverage,
                    'funding_rate': best_rate,
                    'profit': 0.0,
                    'balance_before': balance_before,
                    'balance_after': balance_before,
                    'status': 'success'
                })
            
            # 执行平仓
            elif self.current_position and now.second > (60 - self.config.post_execution_seconds):
                logging.info(f"执行平仓: {best_pair}")
                
                # 计算收益
                price_diff = self.current_position['entry_price'] - current_price
                funding_profit = self.current_position['entry_price'] * (self.current_position['funding_rate'] / 8)
                total_profit = price_diff * self.current_position['size'] + funding_profit
                
                # 保存交易记录
                self.db_manager.save_trade({
                    'timestamp': int(time.time() * 1000),
                    'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'trading_pair': best_pair,
                    'action': 'close',
                    'price': current_price,
                    'amount': self.current_position['size'],
                    'leverage': self.config.leverage,
                    'funding_rate': self.current_position['funding_rate'],
                    'profit': total_profit,
                    'balance_before': balance,
                    'balance_after': balance + total_profit,
                    'status': 'success'
                })
                
                logging.info(f"平仓完成，收益: {total_profit:.6f} USDT")
                
                # 清空当前持仓
                self.current_position = None
            
        except Exception as e:
            logging.error(f"执行套利策略失败: {e}")
    
    def start(self):
        """启动套利引擎"""
        self.is_running = True
        logging.info("套利引擎已启动")
        
        # 每分钟执行一次策略
        schedule.every().minute.do(self.execute_arbitrage_strategy)
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """停止套利引擎"""
        self.is_running = False
        logging.info("套利引擎已停止")

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def generate_performance_report(self) -> Dict:
        """生成性能报告"""
        conn = sqlite3.connect(self.db_manager.db_path)
        
        # 获取交易统计
        trades_df = pd.read_sql_query("SELECT * FROM trades", conn)
        
        if trades_df.empty:
            return {
                '总交易次数': 0,
                '总收益': 0.0,
                '平均收益': 0.0,
                '胜率': 0.0,
                '最大单笔收益': 0.0,
                '最大单笔亏损': 0.0
            }
        
        # 计算统计指标
        total_trades = len(trades_df)
        total_profit = trades_df['profit'].sum()
        avg_profit = trades_df['profit'].mean()
        win_rate = len(trades_df[trades_df['profit'] > 0]) / total_trades * 100
        max_profit = trades_df['profit'].max()
        max_loss = trades_df['profit'].min()
        
        conn.close()
        
        return {
            '总交易次数': total_trades,
            '总收益': total_profit,
            '平均收益': avg_profit,
            '胜率': win_rate,
            '最大单笔收益': max_profit,
            '最大单笔亏损': max_loss
        }
    
    def plot_performance_charts(self):
        """绘制性能图表"""
        conn = sqlite3.connect(self.db_manager.db_path)
        
        # 获取交易数据
        trades_df = pd.read_sql_query("SELECT * FROM trades", conn)
        funding_rates_df = pd.read_sql_query("SELECT * FROM funding_rates", conn)
        
        if not trades_df.empty:
            # 创建图表
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # 收益曲线
            trades_df['cumulative_profit'] = trades_df['profit'].cumsum()
            axes[0, 0].plot(trades_df['datetime'], trades_df['cumulative_profit'])
            axes[0, 0].set_title('累计收益曲线')
            axes[0, 0].set_xlabel('时间')
            axes[0, 0].set_ylabel('收益 (USDT)')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 单笔收益分布
            axes[0, 1].hist(trades_df['profit'], bins=20, alpha=0.7)
            axes[0, 1].set_title('单笔收益分布')
            axes[0, 1].set_xlabel('收益 (USDT)')
            axes[0, 1].set_ylabel('频次')
            
            # 资金费率分布
            if not funding_rates_df.empty:
                axes[1, 0].hist(funding_rates_df['funding_rate'], bins=30, alpha=0.7)
                axes[1, 0].set_title('资金费率分布')
                axes[1, 0].set_xlabel('资金费率')
                axes[1, 0].set_ylabel('频次')
            
            # 交易对分布
            pair_counts = trades_df['trading_pair'].value_counts()
            axes[1, 1].pie(pair_counts.values, labels=pair_counts.index, autopct='%1.1f%%')
            axes[1, 1].set_title('交易对分布')
            
            plt.tight_layout()
            plt.savefig('performance_charts.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        conn.close()

class ArbitrageSystem:
    """资金费率套利系统主类 - 优化版本"""
    
    def __init__(self):
        self.config = TradingConfig()
        self.db_manager = DatabaseManager()
        self.wallet_manager = WalletManager()
        self.api = HyperliquidAPIFixed()
        self.arbitrage_engine = ArbitrageEngine(
            self.config, self.wallet_manager, self.api, self.db_manager
        )
        self.report_generator = ReportGenerator(self.db_manager)
    
    def setup_wallet(self, address: str, private_key: str) -> bool:
        """设置钱包"""
        return self.wallet_manager.connect_metamask(address, private_key)
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def start_arbitrage(self):
        """启动套利系统"""
        if not self.wallet_manager.wallet_info:
            logging.error("请先设置钱包")
            return
        
        logging.info("启动资金费率套利系统...")
        
        # 在后台线程中运行套利引擎
        engine_thread = threading.Thread(target=self.arbitrage_engine.start)
        engine_thread.daemon = True
        engine_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("收到停止信号，正在关闭系统...")
            self.arbitrage_engine.stop()
    
    def generate_report(self):
        """生成报告"""
        report = self.report_generator.generate_performance_report()
        
        print("\n" + "="*50)
        print("资金费率套利系统性能报告")
        print("="*50)
        
        for key, value in report.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
        
        # 绘制图表
        self.report_generator.plot_performance_charts()

def main():
    """主函数"""
    print("Hyperliquid资金费率套利系统 - 优化版本")
    print("="*50)
    print("使用批量API调用，解决限流问题")
    print("="*50)
    
    # 创建系统实例
    system = ArbitrageSystem()
    
    # 设置钱包（示例）
    # 注意：实际使用时请替换为真实的钱包地址和私钥
    wallet_address = "0x1234567890123456789012345678901234567890"
    private_key = "your_private_key_here"
    
    if system.setup_wallet(wallet_address, private_key):
        print("钱包设置成功")
        
        # 更新配置（可选）
        system.update_config(
            leverage=10,
            investment_amount=100.0,
            pre_execution_seconds=5,
            post_execution_seconds=5
        )
        
        # 启动套利系统
        system.start_arbitrage()
    else:
        print("钱包设置失败")

if __name__ == "__main__":
    main() 