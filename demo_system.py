#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyperliquid资金费率套利系统 - 演示版本
使用模拟数据，避免API连接问题
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

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('demo_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class DemoConfig:
    """演示配置"""
    def __init__(self):
        self.leverage = 10  # 杠杆倍数
        self.investment_amount = 100.0  # 投资金额(USDT)
        self.pre_execution_seconds = 5  # 整点前执行秒数
        self.post_execution_seconds = 5  # 整点后执行秒数
        self.min_funding_rate_threshold = -0.0001  # 最小资金费率阈值

class DemoDatabase:
    """演示数据库"""
    
    def __init__(self, db_path: str = "demo_system.db"):
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

class DemoDataGenerator:
    """演示数据生成器"""
    
    def __init__(self):
        self.trading_pairs = ['BTC', 'ETH', 'SOL', 'MATIC', 'AVAX', 'LINK', 'DOT', 'ADA']
        self.base_prices = {
            'BTC': 45000, 'ETH': 2800, 'SOL': 120, 'MATIC': 0.8,
            'AVAX': 35, 'LINK': 15, 'DOT': 7, 'ADA': 0.5
        }
    
    def get_all_trading_pairs(self) -> List[str]:
        """获取所有交易对"""
        return self.trading_pairs
    
    def get_funding_rate(self, trading_pair: str) -> float:
        """获取模拟资金费率"""
        # 使用时间戳和交易对名称生成可重现的随机数据
        seed = int(time.time() / 60) + hash(trading_pair)  # 每分钟变化一次
        np.random.seed(seed)
        return np.random.uniform(-0.002, 0.002)  # -0.2% 到 0.2%
    
    def get_market_price(self, trading_pair: str) -> float:
        """获取模拟市场价格"""
        base_price = self.base_prices.get(trading_pair, 100)
        seed = int(time.time() / 10) + hash(trading_pair)  # 每10秒变化一次
        np.random.seed(seed)
        price_change = np.random.uniform(-0.01, 0.01)  # ±1%波动
        return base_price * (1 + price_change)

class DemoArbitrageEngine:
    """演示套利引擎"""
    
    def __init__(self, config: DemoConfig, data_gen: DemoDataGenerator, db: DemoDatabase):
        self.config = config
        self.data_gen = data_gen
        self.db = db
        self.is_running = False
        self.current_position = None
        
    def find_best_arbitrage_pair(self) -> Optional[Tuple[str, float]]:
        """找到最佳套利交易对"""
        try:
            trading_pairs = self.data_gen.get_all_trading_pairs()
            best_pair = None
            best_rate = 0.0
            
            for pair in trading_pairs:
                rate = self.data_gen.get_funding_rate(pair)
                self.db.save_funding_rate(pair, rate)
                
                # 寻找负费率且绝对值最低的交易对
                if rate < self.config.min_funding_rate_threshold and rate < best_rate:
                    best_rate = rate
                    best_pair = pair
            
            if best_pair:
                return best_pair, best_rate
            else:
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
                logging.info("未找到合适的套利机会")
                return
            
            best_pair, best_rate = result
            logging.info(f"找到套利机会: {best_pair}, 资金费率: {best_rate:.6f}")
            
            # 获取当前价格
            current_price = self.data_gen.get_market_price(best_pair)
            if current_price <= 0:
                logging.error("获取价格失败")
                return
            
            # 计算开仓数量
            position_size = (self.config.investment_amount * self.config.leverage) / current_price
            
            # 执行开仓
            if now.second < self.config.pre_execution_seconds and not self.current_position:
                logging.info(f"执行开仓: {best_pair}, 数量: {position_size:.6f}")
                
                self.current_position = {
                    'pair': best_pair,
                    'size': position_size,
                    'entry_price': current_price,
                    'funding_rate': best_rate,
                    'entry_time': now
                }
                
                # 保存交易记录
                self.db.save_trade({
                    'timestamp': int(time.time() * 1000),
                    'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'trading_pair': best_pair,
                    'action': 'open',
                    'price': current_price,
                    'amount': position_size,
                    'leverage': self.config.leverage,
                    'funding_rate': best_rate,
                    'profit': 0.0,
                    'balance_before': 1000.0,
                    'balance_after': 900.0,
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
                self.db.save_trade({
                    'timestamp': int(time.time() * 1000),
                    'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'trading_pair': best_pair,
                    'action': 'close',
                    'price': current_price,
                    'amount': self.current_position['size'],
                    'leverage': self.config.leverage,
                    'funding_rate': self.current_position['funding_rate'],
                    'profit': total_profit,
                    'balance_before': 900.0,
                    'balance_after': 900.0 + total_profit,
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
        logging.info("演示套利引擎已启动")
        
        # 每分钟执行一次策略
        schedule.every().minute.do(self.execute_arbitrage_strategy)
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """停止套利引擎"""
        self.is_running = False
        logging.info("演示套利引擎已停止")

class DemoReportGenerator:
    """演示报表生成器"""
    
    def __init__(self, db: DemoDatabase):
        self.db = db
    
    def generate_performance_report(self) -> Dict:
        """生成性能报告"""
        conn = sqlite3.connect(self.db.db_path)
        
        # 获取交易数据
        trades_df = pd.read_sql_query("SELECT * FROM trades WHERE action='close'", conn)
        
        if trades_df.empty:
            conn.close()
            return {}
        
        # 计算性能指标
        total_trades = len(trades_df)
        profitable_trades = len(trades_df[trades_df['profit'] > 0])
        total_profit = trades_df['profit'].sum()
        avg_profit = trades_df['profit'].mean()
        max_profit = trades_df['profit'].max()
        max_loss = trades_df['profit'].min()
        win_rate = profitable_trades / total_trades * 100
        
        # 计算夏普比率
        if trades_df['profit'].std() > 0:
            sharpe_ratio = avg_profit / trades_df['profit'].std()
        else:
            sharpe_ratio = 0
        
        conn.close()
        
        return {
            '总交易次数': total_trades,
            '盈利交易次数': profitable_trades,
            '胜率': win_rate,
            '总收益': total_profit,
            '平均收益': avg_profit,
            '最大单次收益': max_profit,
            '最大单次亏损': max_loss,
            '夏普比率': sharpe_ratio
        }
    
    def plot_performance_charts(self):
        """绘制性能图表"""
        conn = sqlite3.connect(self.db.db_path)
        
        # 获取交易数据
        trades_df = pd.read_sql_query("SELECT * FROM trades WHERE action='close'", conn)
        funding_rates_df = pd.read_sql_query("SELECT * FROM funding_rates", conn)
        
        conn.close()
        
        if trades_df.empty:
            print("没有交易数据可以绘制")
            return
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Hyperliquid资金费率套利系统演示版 - 性能报告', fontsize=16, fontweight='bold')
        
        # 1. 累计收益曲线
        cumulative_profit = trades_df['profit'].cumsum()
        axes[0, 0].plot(pd.to_datetime(trades_df['datetime']), cumulative_profit, linewidth=2, color='blue')
        axes[0, 0].set_title('累计收益曲线')
        axes[0, 0].set_xlabel('时间')
        axes[0, 0].set_ylabel('累计收益 (USDT)')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. 单次收益分布
        axes[0, 1].hist(trades_df['profit'], bins=20, alpha=0.7, color='green', edgecolor='black')
        axes[0, 1].set_title('单次收益分布')
        axes[0, 1].set_xlabel('收益 (USDT)')
        axes[0, 1].set_ylabel('频次')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].axvline(x=0, color='red', linestyle='--', alpha=0.7)
        
        # 3. 资金费率变化
        if not funding_rates_df.empty:
            axes[1, 0].scatter(pd.to_datetime(funding_rates_df['datetime']), 
                             funding_rates_df['funding_rate'], alpha=0.6, color='orange')
            axes[1, 0].set_title('资金费率变化')
            axes[1, 0].set_xlabel('时间')
            axes[1, 0].set_ylabel('资金费率')
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].tick_params(axis='x', rotation=45)
            axes[1, 0].axhline(y=0, color='red', linestyle='--', alpha=0.7)
        
        # 4. 交易对分布
        pair_counts = trades_df['trading_pair'].value_counts()
        axes[1, 1].pie(pair_counts.values, labels=pair_counts.index, autopct='%1.1f%%')
        axes[1, 1].set_title('交易对选择分布')
        
        plt.tight_layout()
        plt.show()

def main():
    """主函数"""
    print("Hyperliquid资金费率套利系统 - 演示版本")
    print("="*60)
    print("注意：此版本使用模拟数据，仅用于演示策略逻辑")
    print("="*60)
    
    # 创建组件
    config = DemoConfig()
    db = DemoDatabase()
    data_gen = DemoDataGenerator()
    arbitrage_engine = DemoArbitrageEngine(config, data_gen, db)
    report_generator = DemoReportGenerator(db)
    
    # 启动演示系统
    logging.info("启动演示资金费率套利系统...")
    
    # 在后台线程中运行套利引擎
    engine_thread = threading.Thread(target=arbitrage_engine.start)
    engine_thread.daemon = True
    engine_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("收到停止信号，正在关闭系统...")
        arbitrage_engine.stop()
        
        # 生成报告
        report = report_generator.generate_performance_report()
        
        print("\n" + "="*50)
        print("演示系统性能报告")
        print("="*50)
        
        for key, value in report.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
        
        # 绘制图表
        report_generator.plot_performance_charts()

if __name__ == "__main__":
    main() 