from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Strategy schemas
class StrategyBase(BaseModel):
    name: str
    type: str
    params: Dict[str, Any]

class StrategyCreate(StrategyBase):
    pass

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

class Strategy(StrategyBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Account schemas
class AccountBase(BaseModel):
    name: str
    exchange_type: str
    api_key: str
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    balance: float = 0.0
    position: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    exchange_type: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    balance: Optional[float] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None

class Account(AccountBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Trade schemas
class TradeBase(BaseModel):
    account_id: int
    symbol: str
    side: str
    price: float
    amount: float
    fee: float = 0.0
    order_id: Optional[str] = None

class TradeCreate(TradeBase):
    strategy_id: Optional[int] = None

class Trade(TradeBase):
    id: int
    strategy_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Log schemas
class LogBase(BaseModel):
    level: str
    message: str

class LogCreate(LogBase):
    strategy_id: Optional[int] = None

class Log(LogBase):
    id: int
    strategy_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True 