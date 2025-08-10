from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # 策略类型：跨所套利、三角套利等
    status = Column(String(20), default="stopped")  # running, stopped, error
    params = Column(JSON)  # 策略参数
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 交易所名称
    exchange_type = Column(String(50), nullable=False)  # 交易所类型：binance, okx, bybit等
    api_key = Column(String(255), nullable=False)  # API Key
    api_secret = Column(String(255), nullable=True)  # API Secret
    passphrase = Column(String(255), nullable=True)  # API Passphrase（OKX等需要）
    balance = Column(Float, default=0.0)  # 账户余额（缓存值）
    real_time_balance = Column(JSON)  # 实时余额信息
    last_balance_update = Column(DateTime(timezone=True))  # 最后余额更新时间
    position = Column(Text)  # 持仓信息
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, nullable=True)  # 关联策略ID
    account_id = Column(Integer, nullable=False)  # 关联账户ID
    symbol = Column(String(20), nullable=False)  # 交易对
    side = Column(String(10), nullable=False)  # buy, sell
    price = Column(Float, nullable=False)  # 成交价格
    amount = Column(Float, nullable=False)  # 成交数量
    fee = Column(Float, default=0.0)  # 手续费
    order_id = Column(String(100))  # 订单ID
    status = Column(String(20), default="filled")  # filled, pending, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, nullable=True)  # 关联策略ID
    level = Column(String(10), nullable=False)  # INFO, WARN, ERROR
    message = Column(Text, nullable=False)  # 日志消息
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 