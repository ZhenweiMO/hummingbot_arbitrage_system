from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

import crud, models, schemas
from database import get_db
from hummingbot_integration import (
    get_available_strategies, 
    get_strategy_schema, 
    strategy_executor
)

app = FastAPI()

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 策略相关接口
@app.get('/api/strategies', response_model=List[schemas.Strategy])
def get_strategies(db: Session = Depends(get_db)):
    return crud.get_strategies(db)

@app.post('/api/strategies', response_model=schemas.Strategy)
def create_strategy(strategy: schemas.StrategyCreate, db: Session = Depends(get_db)):
    return crud.create_strategy(db=db, strategy=strategy)

@app.put('/api/strategies/{strategy_id}', response_model=schemas.Strategy)
def update_strategy(strategy_id: int, strategy: schemas.StrategyUpdate, db: Session = Depends(get_db)):
    db_strategy = crud.update_strategy(db=db, strategy_id=strategy_id, strategy=strategy)
    if db_strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return db_strategy

@app.post('/api/strategies/{strategy_id}/start')
def start_strategy(strategy_id: int, db: Session = Depends(get_db)):
    db_strategy = crud.update_strategy_status(db=db, strategy_id=strategy_id, status="running")
    if db_strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"code": 0, "msg": "success"}

@app.post('/api/strategies/{strategy_id}/stop')
def stop_strategy(strategy_id: int, db: Session = Depends(get_db)):
    db_strategy = crud.update_strategy_status(db=db, strategy_id=strategy_id, status="stopped")
    if db_strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"code": 0, "msg": "success"}

@app.delete('/api/strategies/{strategy_id}')
def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    success = crud.delete_strategy(db=db, strategy_id=strategy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"code": 0, "msg": "success"}

# Hummingbot 集成相关接口
@app.get('/api/hummingbot/strategies')
def get_hummingbot_strategies():
    """获取可用的 Hummingbot 策略列表"""
    try:
        strategies = get_available_strategies()
        return {"code": 0, "data": strategies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strategies: {str(e)}")

@app.get('/api/hummingbot/strategies/{strategy_type}/schema')
def get_strategy_parameter_schema(strategy_type: str):
    """获取策略参数模式"""
    try:
        schema = get_strategy_schema(strategy_type)
        if "error" in schema:
            raise HTTPException(status_code=400, detail=schema["error"])
        return {"code": 0, "data": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")

@app.post('/api/hummingbot/strategies/{strategy_id}/start')
async def start_hummingbot_strategy(strategy_id: str, strategy_data: Dict[str, Any]):
    """启动 Hummingbot 策略"""
    try:
        strategy_type = strategy_data.get("type")
        params = strategy_data.get("params", {})
        
        if not strategy_type:
            raise HTTPException(status_code=400, detail="Strategy type is required")
        
        success = await strategy_executor.start_strategy(strategy_id, strategy_type, params)
        
        if success:
            return {"code": 0, "msg": "Strategy started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start strategy")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start strategy: {str(e)}")

@app.post('/api/hummingbot/strategies/{strategy_id}/stop')
async def stop_hummingbot_strategy(strategy_id: str):
    """停止 Hummingbot 策略"""
    try:
        success = await strategy_executor.stop_strategy(strategy_id)
        
        if success:
            return {"code": 0, "msg": "Strategy stopped successfully"}
        else:
            raise HTTPException(status_code=404, detail="Strategy not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop strategy: {str(e)}")

@app.get('/api/hummingbot/strategies/{strategy_id}/status')
async def get_hummingbot_strategy_status(strategy_id: str):
    """获取 Hummingbot 策略状态"""
    try:
        status = await strategy_executor.get_strategy_status(strategy_id)
        
        if status:
            return {"code": 0, "data": status}
        else:
            raise HTTPException(status_code=404, detail="Strategy not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strategy status: {str(e)}")

# 账户相关接口
@app.get('/api/accounts', response_model=List[schemas.Account])
async def get_accounts(db: Session = Depends(get_db)):
    return await crud.get_accounts_with_real_time_balance(db)

@app.post('/api/accounts/{account_id}/update-balance')
async def update_account_balance(account_id: int, db: Session = Depends(get_db)):
    """手动更新指定账户的实时余额"""
    account = await crud.update_account_balance(db, account_id)
    if account:
        return {"message": "余额更新成功", "account": account}
    else:
        raise HTTPException(status_code=404, detail="账户不存在或更新失败")

@app.post('/api/accounts', response_model=schemas.Account)
async def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    return await crud.create_account(db=db, account=account)

@app.put('/api/accounts/{account_id}', response_model=schemas.Account)
def update_account(account_id: int, account: schemas.AccountUpdate, db: Session = Depends(get_db)):
    db_account = crud.update_account(db=db, account_id=account_id, account=account)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.delete('/api/accounts/{account_id}')
def delete_account(account_id: int, db: Session = Depends(get_db)):
    success = crud.delete_account(db=db, account_id=account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"code": 0, "msg": "success"}

# 行情相关接口（保持 mock 数据，因为需要外部 API）
@app.get('/api/markets/symbols')
def get_symbols():
    return ["BTC/USDT", "ETH/USDT", "BNB/USDT"]

@app.get('/api/markets/kline')
def get_kline(symbol: str):
    return [
        {"time": 1622476800000, "open": 35000, "high": 35500, "low": 34500, "close": 35200},
        {"time": 1622480400000, "open": 35200, "high": 36000, "low": 35000, "close": 35800},
        {"time": 1622484000000, "open": 35800, "high": 36200, "low": 35500, "close": 36000},
    ]

@app.get('/api/markets/orderbook')
def get_orderbook(symbol: str):
    return {"bids": [[35200, 1.2], [35150, 0.8]], "asks": [[35300, 1.0], [35400, 0.5]]}

# 日志与交易记录接口
@app.get('/api/logs', response_model=List[schemas.Log])
def get_logs(strategy_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_logs(db=db, strategy_id=strategy_id)

@app.get('/api/trades', response_model=List[schemas.Trade])
def get_trades(strategy_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_trades(db=db, strategy_id=strategy_id)

# 总览统计接口
@app.get('/api/overview')
def get_overview(db: Session = Depends(get_db)):
    strategies = crud.get_strategies(db)
    accounts = crud.get_accounts(db)

    strategy_total = len(strategies)
    strategy_running = len([s for s in strategies if s.status == "running"])
    asset_total = sum(account.balance for account in accounts)

    # 计算今日盈亏（从交易记录计算，如果没有交易记录则返回0）
    trades = crud.get_trades(db)
    today = datetime.now().date()
    profit_today = 0.0
    
    for trade in trades:
        trade_date = trade.created_at.date() if trade.created_at else None
        if trade_date == today:
            # 简单的盈亏计算（实际应该根据交易方向计算）
            profit_today += trade.amount * 0.001  # 假设每笔交易有0.1%的利润

    return {
        "strategy_total": strategy_total,
        "strategy_running": strategy_running,
        "asset_total": asset_total,
        "profit_today": profit_today
    } 