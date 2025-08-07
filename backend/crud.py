from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import models, schemas

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