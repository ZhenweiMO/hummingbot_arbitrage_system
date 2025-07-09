import asyncio
import json
import time
import hmac
import hashlib
import base64
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import sqlite3
import os
from cryptography.fernet import Fernet
from web3 import Web3
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
        logging.FileHandler('arbitrage_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

@dataclass
class TradingConfig:
    """交易配置"""
    leverage: int = 10  # 杠杆倍数
    investment_amount: float = 100.0  # 投资金额(USDT)
    pre_execution_seconds: int = 5  # 整点前执行秒数
    post_execution_seconds: int = 5  # 整点后执行秒数
    min_funding_rate_threshold: float = -0.0001  # 最小资金费率阈值

@dataclass
class WalletInfo:
    """钱包信息"""
    address: str
    private_key: str
    balance: float = 0.0
    available_margin: float = 0.0

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "arbitrage_system.db"):
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
    
    def __init__(self, encryption_key: str = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.wallet_info: Optional[WalletInfo] = None
        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_KEY'))
    
    def encrypt_private_key(self, private_key: str) -> str:
        """加密私钥"""
        return self.cipher.encrypt(private_key.encode()).decode()
    
    def decrypt_private_key(self, encrypted_key: str) -> str:
        """解密私钥"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
    
    def connect_metamask(self, address: str, private_key: str) -> bool:
        """连接MetaMask钱包"""
        try:
            # 验证地址格式
            if not self.w3.is_address(address):
                logging.error("无效的钱包地址")
                return False
            
            # 验证私钥
            account = self.w3.eth.account.from_key(private_key)
            if account.address.lower() != address.lower():
                logging.error("私钥与地址不匹配")
                return False
            
            # 加密存储私钥
            encrypted_key = self.encrypt_private_key(private_key)
            
            self.wallet_info = WalletInfo(
                address=address,
                private_key=encrypted_key
            )
            
            logging.info(f"成功连接钱包: {address}")
            return True
            
        except Exception as e:
            logging.error(f"连接钱包失败: {e}")
            return False
    
    def get_wallet_balance(self) -> Tuple[float, float]:
        """获取钱包余额和可用保证金"""
        if not self.wallet_info:
            return 0.0, 0.0
        
        try:
            # 这里需要调用Hyperliquid API获取实际余额
            # 暂时返回模拟数据
            balance = 1000.0  # 总余额
            available_margin = 800.0  # 可用保证金
            
            self.wallet_info.balance = balance
            self.wallet_info.available_margin = available_margin
            
            return balance, available_margin
            
        except Exception as e:
            logging.error(f"获取钱包余额失败: {e}")
            return 0.0, 0.0

class HyperliquidAPI:
    """Hyperliquid API接口"""
    
    def __init__(self):
        self.base_url = "https://api.hyperliquid.xyz"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_all_trading_pairs(self) -> List[str]:
        """获取所有交易对"""
        try:
            url = f"{self.base_url}/info"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            trading_pairs = []
            if 'universe' in data:
                for asset in data['universe']:
                    if 'name' in asset:
                        trading_pairs.append(asset['name'])
            
            return trading_pairs
        except Exception as e:
            logging.error(f"获取交易对失败: {e}")
            return ['BTC', 'ETH', 'SOL', 'MATIC', 'AVAX', 'LINK', 'DOT', 'ADA']
    
    def get_funding_rate(self, trading_pair: str) -> float:
        """获取资金费率"""
        try:
            url = f"{self.base_url}/info"
            payload = {
                "type": "fundingHistory",
                "coin": trading_pair,
                "startTime": int(time.time() * 1000) - 3600000,
                "endTime": int(time.time() * 1000)
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return float(data[-1].get('fundingRate', 0))
            return 0.0
            
        except Exception as e:
            logging.error(f"获取{trading_pair}资金费率失败: {e}")
            return 0.0
    
    def get_market_price(self, trading_pair: str) -> float:
        """获取市场价格"""
        try:
            url = f"{self.base_url}/info"
            payload = {
                "type": "candleSnapshot",
                "coin": trading_pair,
                "interval": "1m",
                "startTime": int(time.time() * 1000) - 60000,
                "endTime": int(time.time() * 1000) + 60000
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return float(data[-1].get('close', 0))
            return 0.0
            
        except Exception as e:
            logging.error(f"获取{trading_pair}市场价格失败: {e}")
            return 0.0
    
    def place_order(self, trading_pair: str, side: str, amount: float, price: float = None) -> Dict:
        """下单"""
        try:
            # 这里需要实现实际的订单接口
            # 暂时返回模拟数据
            order_id = f"order_{int(time.time() * 1000)}"
            
            return {
                'order_id': order_id,
                'status': 'filled',
                'filled_price': price or self.get_market_price(trading_pair),
                'filled_amount': amount
            }
            
        except Exception as e:
            logging.error(f"下单失败: {e}")
            return {'status': 'failed', 'error': str(e)}

class ArbitrageEngine:
    """套利引擎"""
    
    def __init__(self, config: TradingConfig, wallet_manager: WalletManager, 
                 api: HyperliquidAPI, db_manager: DatabaseManager):
        self.config = config
        self.wallet_manager = wallet_manager
        self.api = api
        self.db_manager = db_manager
        self.is_running = False
        self.current_position = None
        
    def find_best_arbitrage_pair(self) -> Optional[Tuple[str, float]]:
        """找到最佳套利交易对"""
        try:
            trading_pairs = self.api.get_all_trading_pairs()
            best_pair = None
            best_rate = 0.0
            
            for pair in trading_pairs:
                rate = self.api.get_funding_rate(pair)
                self.db_manager.save_funding_rate(pair, rate)
                
                # 寻找负费率且绝对值最低的交易对
                if rate < self.config.min_funding_rate_threshold and rate < best_rate:
                    best_rate = rate
                    best_pair = pair
            
            return best_pair, best_rate if best_pair else (None, 0.0)
            
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
            best_pair, best_rate = self.find_best_arbitrage_pair()
            
            if not best_pair:
                logging.info("未找到合适的套利机会")
                return
            
            logging.info(f"找到套利机会: {best_pair}, 资金费率: {best_rate:.6f}")
            
            # 获取钱包余额
            balance, available_margin = self.wallet_manager.get_wallet_balance()
            self.db_manager.save_wallet_balance(balance, available_margin)
            
            if available_margin < self.config.investment_amount:
                logging.warning(f"可用保证金不足: {available_margin} < {self.config.investment_amount}")
                return
            
            # 计算开仓数量
            current_price = self.api.get_market_price(best_pair)
            if current_price <= 0:
                logging.error("获取价格失败")
                return
            
            position_size = (self.config.investment_amount * self.config.leverage) / current_price
            
            # 记录开仓前余额
            balance_before = available_margin
            
            # 执行开仓
            if now.second < self.config.pre_execution_seconds:
                logging.info(f"执行开仓: {best_pair}, 数量: {position_size:.6f}")
                
                order_result = self.api.place_order(
                    trading_pair=best_pair,
                    side='buy',
                    amount=position_size,
                    price=current_price
                )
                
                if order_result['status'] == 'filled':
                    self.current_position = {
                        'pair': best_pair,
                        'size': position_size,
                        'entry_price': order_result['filled_price'],
                        'funding_rate': best_rate,
                        'entry_time': now
                    }
                    
                    # 保存交易记录
                    self.db_manager.save_trade({
                        'timestamp': int(time.time() * 1000),
                        'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
                        'trading_pair': best_pair,
                        'action': 'open',
                        'price': order_result['filled_price'],
                        'amount': position_size,
                        'leverage': self.config.leverage,
                        'funding_rate': best_rate,
                        'profit': 0.0,
                        'balance_before': balance_before,
                        'balance_after': balance_before - self.config.investment_amount,
                        'status': 'success'
                    })
            
            # 执行平仓
            elif self.current_position and now.second > (60 - self.config.post_execution_seconds):
                logging.info(f"执行平仓: {best_pair}")
                
                order_result = self.api.place_order(
                    trading_pair=best_pair,
                    side='sell',
                    amount=self.current_position['size'],
                    price=current_price
                )
                
                if order_result['status'] == 'filled':
                    # 计算收益
                    price_diff = self.current_position['entry_price'] - order_result['filled_price']
                    funding_profit = self.current_position['entry_price'] * (self.current_position['funding_rate'] / 8)
                    total_profit = price_diff * self.current_position['size'] + funding_profit
                    
                    # 更新余额
                    balance_after = balance_before + total_profit
                    
                    # 保存交易记录
                    self.db_manager.save_trade({
                        'timestamp': int(time.time() * 1000),
                        'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
                        'trading_pair': best_pair,
                        'action': 'close',
                        'price': order_result['filled_price'],
                        'amount': self.current_position['size'],
                        'leverage': self.config.leverage,
                        'funding_rate': self.current_position['funding_rate'],
                        'profit': total_profit,
                        'balance_before': balance_before,
                        'balance_after': balance_after,
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
    """报表生成器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def generate_performance_report(self) -> Dict:
        """生成性能报告"""
        conn = sqlite3.connect(self.db_manager.db_path)
        
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
        
        # 计算最大回撤
        cumulative_profit = trades_df['profit'].cumsum()
        peak = cumulative_profit.expanding().max()
        drawdown = (cumulative_profit - peak) / peak
        max_drawdown = drawdown.min()
        
        conn.close()
        
        return {
            '总交易次数': total_trades,
            '盈利交易次数': profitable_trades,
            '胜率': win_rate,
            '总收益': total_profit,
            '平均收益': avg_profit,
            '最大单次收益': max_profit,
            '最大单次亏损': max_loss,
            '夏普比率': sharpe_ratio,
            '最大回撤': max_drawdown
        }
    
    def plot_performance_charts(self):
        """绘制性能图表"""
        conn = sqlite3.connect(self.db_manager.db_path)
        
        # 获取交易数据
        trades_df = pd.read_sql_query("SELECT * FROM trades WHERE action='close'", conn)
        funding_rates_df = pd.read_sql_query("SELECT * FROM funding_rates", conn)
        balances_df = pd.read_sql_query("SELECT * FROM wallet_balances", conn)
        
        conn.close()
        
        if trades_df.empty:
            print("没有交易数据可以绘制")
            return
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Hyperliquid资金费率套利系统性能报告', fontsize=16, fontweight='bold')
        
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
        
        # 4. 钱包余额变化
        if not balances_df.empty:
            axes[1, 1].plot(pd.to_datetime(balances_df['datetime']), 
                           balances_df['balance'], linewidth=2, color='purple')
            axes[1, 1].set_title('钱包余额变化')
            axes[1, 1].set_xlabel('时间')
            axes[1, 1].set_ylabel('余额 (USDT)')
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()

class ArbitrageSystem:
    """资金费率套利系统主类"""
    
    def __init__(self):
        self.config = TradingConfig()
        self.db_manager = DatabaseManager()
        self.wallet_manager = WalletManager()
        self.api = HyperliquidAPI()
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
    print("Hyperliquid资金费率套利系统")
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