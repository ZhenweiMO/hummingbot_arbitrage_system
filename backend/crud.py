from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
import asyncio
import logging
import models, schemas

logger = logging.getLogger(__name__)

# Strategy CRUD operations
def get_strategies(db: Session, skip: int = 0, limit: int = 100) -> List[models.Strategy]:
    return db.query(models.Strategy).offset(skip).limit(limit).all()

def get_strategy(db: Session, strategy_id: int) -> Optional[models.Strategy]:
    return db.query(models.Strategy).filter(models.Strategy.id == strategy_id).first()

def create_strategy(db: Session, strategy: schemas.StrategyCreate) -> models.Strategy:
    db_strategy = models.Strategy(**strategy.dict())
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy

def update_strategy(db: Session, strategy_id: int, strategy: schemas.StrategyUpdate) -> Optional[models.Strategy]:
    db_strategy = get_strategy(db, strategy_id)
    if db_strategy:
        update_data = strategy.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_strategy, field, value)
        db.commit()
        db.refresh(db_strategy)
    return db_strategy

def delete_strategy(db: Session, strategy_id: int) -> bool:
    db_strategy = get_strategy(db, strategy_id)
    if db_strategy:
        db.delete(db_strategy)
        db.commit()
        return True
    return False

def update_strategy_status(db: Session, strategy_id: int, status: str) -> Optional[models.Strategy]:
    db_strategy = get_strategy(db, strategy_id)
    if db_strategy:
        db_strategy.status = status
        db.commit()
        db.refresh(db_strategy)
    return db_strategy

# Account CRUD operations
def get_accounts(db: Session, skip: int = 0, limit: int = 100) -> List[models.Account]:
    return db.query(models.Account).filter(models.Account.is_active == True).offset(skip).limit(limit).all()

def get_account(db: Session, account_id: int) -> Optional[models.Account]:
    return db.query(models.Account).filter(models.Account.id == account_id).first()

def create_account(db: Session, account: schemas.AccountCreate) -> models.Account:
    db_account = models.Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

async def update_account_balance(db: Session, account_id: int) -> Optional[models.Account]:
    """更新账户实时余额"""
    from exchange_connector import exchange_manager, create_connector
    
    db_account = get_account(db, account_id)
    if not db_account or not db_account.is_active:
        return None
    
    try:
        # 创建交易所连接器
        connector = create_connector(
            exchange_type=db_account.exchange_type,
            api_key=db_account.api_key,
            api_secret=db_account.api_secret,
            passphrase=db_account.passphrase
        )
        
        # 获取实时余额
        async with connector:
            account_info = await connector.get_account_balance()
            
        if account_info:
            # 更新数据库中的余额信息
            db_account.real_time_balance = {
                'total_equity': account_info.total_equity,
                'balances': [
                    {
                        'asset': b.asset,
                        'free': b.free,
                        'locked': b.locked,
                        'total': b.total
                    } for b in account_info.balances
                ],
                'timestamp': account_info.timestamp
            }
            db_account.balance = account_info.total_equity
            db_account.last_balance_update = func.now()
            
            db.commit()
            db.refresh(db_account)
            
        return db_account
        
    except Exception as e:
        logger.error(f"更新账户 {account_id} 余额失败: {e}")
        return None

async def get_accounts_with_real_time_balance(db: Session, skip: int = 0, limit: int = 100) -> List[models.Account]:
    """获取账户列表并更新实时余额"""
    accounts = get_accounts(db, skip, limit)
    
    # 异步更新所有账户的余额
    update_tasks = []
    for account in accounts:
        if account.is_active:
            update_tasks.append(update_account_balance(db, account.id))
    
    if update_tasks:
        await asyncio.gather(*update_tasks, return_exceptions=True)
    
    return get_accounts(db, skip, limit)

def update_account(db: Session, account_id: int, account: schemas.AccountUpdate) -> Optional[models.Account]:
    db_account = get_account(db, account_id)
    if db_account:
        update_data = account.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_account, field, value)
        db.commit()
        db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: int) -> bool:
    db_account = get_account(db, account_id)
    if db_account:
        db_account.is_active = False  # 软删除
        db.commit()
        return True
    return False

# Trade CRUD operations
def get_trades(db: Session, strategy_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[models.Trade]:
    query = db.query(models.Trade)
    if strategy_id:
        query = query.filter(models.Trade.strategy_id == strategy_id)
    return query.order_by(desc(models.Trade.created_at)).offset(skip).limit(limit).all()

def create_trade(db: Session, trade: schemas.TradeCreate) -> models.Trade:
    db_trade = models.Trade(**trade.dict())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

# Log CRUD operations
def get_logs(db: Session, strategy_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[models.Log]:
    query = db.query(models.Log)
    if strategy_id:
        query = query.filter(models.Log.strategy_id == strategy_id)
    return query.order_by(desc(models.Log.created_at)).offset(skip).limit(limit).all()

def create_log(db: Session, log: schemas.LogCreate) -> models.Log:
    db_log = models.Log(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log 