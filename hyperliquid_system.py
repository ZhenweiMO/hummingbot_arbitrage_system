import asyncio
import json
import time
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import sqlite3
import threading
import schedule

# 导入优化后的API
from hyperliquid_api_fixed import HyperliquidAPIFixed
from wallet_manager import WalletManager, HyperliquidWalletAPI

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

class ArbitrageEngine:
    """套利引擎 - 优化版本"""
    
    def __init__(self, config: TradingConfig, wallet_manager, wallet_api, api: HyperliquidAPIFixed, db_manager: DatabaseManager):
        self.config = config
        self.wallet_manager = wallet_manager
        self.wallet_api = wallet_api
        self.api = api
        self.db_manager = db_manager
        self.is_running = False
        self.current_position = None
        self.total_profit = 0.0
        self.trade_count = 0
        # 拉取所有合约最大杠杆
        self.max_leverage_map = self.fetch_max_leverage_map()
        # 拉取所有合约 minSz 和 tickSz
        self.asset_meta_map = self.fetch_asset_meta_map()
        
    def fetch_max_leverage_map(self):
        """通过API获取所有合约最大杠杆"""
        try:
            url = "https://api.hyperliquid.xyz/info"
            payload = {"type": "metaAndAssetCtxs"}
            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()
            max_leverage_map = {}
            if isinstance(data, list) and len(data) >= 2:
                universe = data[0].get('universe', [])
                for asset in universe:
                    name = asset.get('name')
                    margin_tiers = asset.get('marginTiers', [])
                    if margin_tiers:
                        # 取第一个tier的maxLeverage
                        max_leverage = float(margin_tiers[0].get('maxLeverage', 1))
                        max_leverage_map[name] = max_leverage
            return max_leverage_map
        except Exception as e:
            logging.error(f"获取最大杠杆失败: {e}")
            return {}
    
    def fetch_asset_meta_map(self):
        try:
            url = "https://api.hyperliquid.xyz/info"
            payload = {"type": "metaAndAssetCtxs"}
            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()
            asset_meta_map = {}
            if isinstance(data, list) and len(data) >= 2:
                universe = data[0].get('universe', [])
                for asset in universe:
                    name = asset.get('name')
                    min_sz = float(asset.get('minSz', 0.0))
                    # 优先用 asset['tickSz']，否则用 szDecimals 计算
                    tick_sz = float(asset.get('tickSz', 0.0)) if 'tickSz' in asset else None
                    sz_decimals = int(asset.get('szDecimals', 0))
                    if tick_sz is None or tick_sz == 0.0:
                        tick_sz = 10 ** (-sz_decimals) if sz_decimals > 0 else 1.0
                    asset_meta_map[name] = {
                        "minSz": min_sz,
                        "tickSz": tick_sz
                    }
                    if name == "SOPH-PERP":
                        logging.info(f"SOPH-PERP asset meta: {json.dumps(asset, ensure_ascii=False)}")
            return asset_meta_map
        except Exception as e:
            logging.error(f"获取合约元数据失败: {e}")
            return {}
    
    def find_best_arbitrage_pair(self) -> Tuple[Optional[str], float]:
        """找到最佳套利交易对（批量获取资金费率）"""
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
            
        except Exception as e:
            logging.error(f"寻找套利交易对失败: {e}")
            return None, 0.0
    
    def execute_arbitrage_strategy(self):
        """执行套利策略"""
        try:
            # 策略执行前记录余额
            self.log_platform_balance('策略执行前')
            # 获取当前时间
            now = datetime.now()
            
            # 检查是否接近整点
            if now.second < self.config.pre_execution_seconds or now.second > (60 - self.config.post_execution_seconds):
                return
            
            # 找到最佳套利交易对
            best_pair, best_rate = self.find_best_arbitrage_pair()
            
            if best_pair is None:
                logging.info("未找到合适的套利机会")
                return
            
            # 获取当前价格
            current_price = self.api.get_market_price(best_pair)
            if current_price <= 0:
                logging.error("获取价格失败")
                return
            
            # 资金管理：直接通过 Hyperliquid API 查询余额
            address = self.wallet_manager.wallet_info['address'] if self.wallet_manager.wallet_info else None
            if not address:
                logging.error("未检测到钱包地址，无法查询余额")
                return
            url = "https://api.hyperliquid.xyz/info"
            payload = {"type": "clearinghouseState", "user": address}
            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()
            margin_summary = data.get("marginSummary")
            if not margin_summary:
                logging.error("未获取到平台账户余额信息")
                return
            balance = margin_summary.get("accountValue", 0.0)
            if balance is None:
                balance = 0.0
            balance = float(balance)
            used_margin = margin_summary.get("totalMarginUsed", 0.0)
            if used_margin is None:
                used_margin = 0.0
            used_margin = float(used_margin)
            available_margin = balance - used_margin
            logging.info(f"[策略执行中] 平台账户余额: {balance} USDC, 可用保证金: {available_margin} USDC")
            # 优化：每次投入总金额的90%，但不超过100 USDC
            invest_amount = min(available_margin * 0.9, 100.0)
            if invest_amount < 1e-6:
                logging.warning(f"可用保证金不足: {available_margin}")
                return
            
            # === 计算 sz，自动适配最大杠杆、minSz、tickSz ===
            pair_key = best_pair if best_pair.endswith('-PERP') else best_pair + '-PERP'
            max_leverage = self.max_leverage_map.get(pair_key, self.config.leverage)
            leverage = min(self.config.leverage, max_leverage)
            if self.config.leverage > max_leverage:
                logging.warning(f"{pair_key} 杠杆上限为 {max_leverage}，已自动降为 {max_leverage}")
            notional = available_margin * leverage
            sz = notional / current_price
            # 适配 minSz 和 tickSz
            meta = self.asset_meta_map.get(pair_key, {})
            min_sz = meta.get("minSz", 0.0)
            tick_sz = meta.get("tickSz", 1.0)
            logging.info(f"{pair_key} minSz: {min_sz}, tickSz: {tick_sz}, 计算后 sz: {sz}")
            # 强制用 minSz 测试
            sz = min_sz
            # 向下取整到 tickSz 精度
            sz = (sz // tick_sz) * tick_sz
            logging.info(f"最终用于下单的 sz: {sz}")
            
            # === 新增真实下单 ===
            # 仅在无持仓时开仓
            if not self.current_position:
                order_result = self.wallet_api.place_order(
                    trading_pair=best_pair,
                    side='buy',
                    amount=1.0,  # 你可以根据实际策略调整数量
                    price=current_price,
                    order_type="market"
                )
                logging.info(f"下单结果: {order_result}")
                if order_result.get('status') != 'success':
                    logging.error(f"下单失败: {order_result}")
                    return
                # 记录持仓
                self.current_position = {
                    'pair': best_pair,
                    'size': 1.0,
                    'entry_price': current_price,
                    'funding_rate': best_rate,
                    'entry_time': now
                }
            
            # 平仓逻辑（如有持仓且到达平仓时间）
            elif self.current_position and now.second > (60 - self.config.post_execution_seconds):
                order_result = self.wallet_api.place_order(
                    trading_pair=best_pair,
                    side='sell',
                    amount=self.current_position['size'],
                    price=current_price,
                    order_type="market"
                )
                logging.info(f"平仓下单结果: {order_result}")
                if order_result.get('status') != 'success':
                    logging.error(f"平仓下单失败: {order_result}")
                    return
                # 清空持仓
                self.current_position = None
            
            # 策略执行后记录余额
            self.log_platform_balance('策略执行后')
            
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
        logging.info(f"最终统计 - 总收益: {self.total_profit:.6f} USDT, 交易次数: {self.trade_count}")

    def log_platform_balance(self, tag=''):  # 新增方法
        address = self.wallet_manager.wallet_info['address'] if self.wallet_manager.wallet_info else None
        if not address:
            logging.warning(f"[{tag}] 未检测到钱包地址，无法查询平台余额")
            return
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "clearinghouseState", "user": address}
        try:
            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()
            margin_summary = data.get("marginSummary")
            if not margin_summary:
                logging.warning(f"[{tag}] 未获取到平台账户余额信息")
                return
            balance = margin_summary.get("accountValue", 0.0)
            if balance is None:
                balance = 0.0
            balance = float(balance)
            used_margin = margin_summary.get("totalMarginUsed", 0.0)
            if used_margin is None:
                used_margin = 0.0
            used_margin = float(used_margin)
            available_margin = balance - used_margin
            logging.info(f"[{tag}] 平台账户余额: {balance} USDC, 可用保证金: {available_margin} USDC")
        except Exception as e:
            logging.error(f"[{tag}] 查询平台余额失败: {e}")

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
        conn = sqlite3.connect(self.db_manager.db_path)
        
        # 获取交易数据
        trades_df = pd.read_sql_query("SELECT * FROM trades WHERE action='close'", conn)
        funding_rates_df = pd.read_sql_query("SELECT * FROM funding_rates", conn)
        
        conn.close()
        
        if trades_df.empty:
            print("没有交易数据可以绘制")
            return
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Hyperliquid资金费率套利系统性能报告', fontsize=16, fontweight='bold')
        
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

class ArbitrageSystem:
    def __init__(self):
        self.config = TradingConfig()
        self.db_manager = DatabaseManager()
        self.wallet_manager = WalletManager()
        self.wallet_api = HyperliquidWalletAPI(self.wallet_manager)
        self.api = HyperliquidAPIFixed()
        self.arbitrage_engine = ArbitrageEngine(
            self.config, self.wallet_manager, self.wallet_api, self.api, self.db_manager
        )
        self.report_generator = ReportGenerator(self.db_manager)
        self.wallet_manager.load_wallet_config('wallet.json')
        self.log_platform_balance('系统启动')

    def setup_wallet(self, address, private_key):
        """兼容旧接口，实际已自动加载 wallet.json"""
        # 可选：如需覆盖 wallet.json，可在此处实现
        pass

    def log_platform_balance(self, tag=''):  # 新增方法
        address = self.wallet_manager.wallet_info['address'] if self.wallet_manager.wallet_info else None
        if not address:
            logging.warning(f"[{tag}] 未检测到钱包地址，无法查询平台余额")
            return
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "clearinghouseState", "user": address}
        try:
            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()
            margin_summary = data.get("marginSummary")
            if not margin_summary:
                logging.warning(f"[{tag}] 未获取到平台账户余额信息")
                return
            balance = margin_summary.get("accountValue", 0.0)
            if balance is None:
                balance = 0.0
            balance = float(balance)
            used_margin = margin_summary.get("totalMarginUsed", 0.0)
            if used_margin is None:
                used_margin = 0.0
            used_margin = float(used_margin)
            available_margin = balance - used_margin
            logging.info(f"[{tag}] 平台账户余额: {balance} USDC, 可用保证金: {available_margin} USDC")
        except Exception as e:
            logging.error(f"[{tag}] 查询平台余额失败: {e}")

def main():
    """主函数"""
    print("Hyperliquid资金费率套利系统 - 优化版本")
    print("="*50)
    print("使用批量API调用，解决限流问题")
    print("="*50)
    # 创建系统实例
    system = ArbitrageSystem()
    print('[DEBUG MAIN] 钱包信息:', system.wallet_manager.wallet_info)

    # 启动套利系统（用系统自带的 engine）
    logging.info("启动资金费率套利系统...")

    engine_thread = threading.Thread(target=system.arbitrage_engine.start)
    engine_thread.daemon = True
    engine_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("收到停止信号，正在关闭系统...")
        system.arbitrage_engine.stop()

        # 生成报告
        report = system.report_generator.generate_performance_report()

        print("\n" + "="*50)
        print("资金费率套利系统性能报告")
        print("="*50)

        for key, value in report.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")

        # 绘制图表
        system.report_generator.plot_performance_charts()

if __name__ == "__main__":
    main() 