# 后端设计思路

## 技术选型建议

- 框架：FastAPI（推荐，异步、文档友好）、Flask（同步，简单易用）
- 数据库：SQLite（开发测试）、PostgreSQL/MySQL（生产）
- 任务调度/异步：Celery + Redis（如需策略异步运行）
- hummingbot：作为策略执行引擎，二次封装

## 目录结构建议

```
backend/
  app/
    main.py                # FastAPI/Flask 启动入口
    api/
      strategy.py          # 策略相关接口
      account.py           # 账户相关接口
      market.py            # 行情相关接口
      log.py               # 日志与交易记录接口
    core/
      strategy_base.py     # 策略基类
      strategy_loader.py   # 策略加载与管理
      hummingbot_wrapper.py# hummingbot 封装
    models/
      strategy.py
      account.py
      trade.py
      log.py
    db/
      database.py
      ...
    utils/
      ...
  requirements.txt
```

## 主要接口设计（与前端功能点一一对应）

### 1. 策略管理
- `GET /api/strategies`  获取策略列表
- `POST /api/strategies`  新建策略
- `PUT /api/strategies/{id}`  编辑策略
- `DELETE /api/strategies/{id}`  删除策略
- `POST /api/strategies/{id}/start`  启动策略
- `POST /api/strategies/{id}/stop`  停止策略
- `GET /api/strategies/{id}`  获取策略详情（含参数、状态、日志、盈亏等）

### 2. 账户管理
- `GET /api/accounts`  获取账户列表
- `POST /api/accounts`  新增账户（API Key）
- `PUT /api/accounts/{id}`  编辑账户
- `DELETE /api/accounts/{id}`  删除账户
- `POST /api/accounts/{id}/transfer`  资金划转

### 3. 行情与订单簿
- `GET /api/markets/symbols`  获取支持的交易对列表
- `GET /api/markets/kline?symbol=BTC/USDT`  获取K线数据
- `GET /api/markets/orderbook?symbol=BTC/USDT`  获取订单簿深度
- `GET /api/markets/ticker?symbol=BTC/USDT`  获取最新行情

### 4. 日志与交易记录
- `GET /api/logs?strategy_id=xxx`  获取策略运行日志
- `GET /api/trades?strategy_id=xxx`  获取策略交易明细

### 5. 总览统计
- `GET /api/overview`  获取策略总数、运行中数量、总资产、今日盈亏等统计数据

## 开发建议

1. 接口返回格式统一，推荐：
   ```json
   {
     "code": 0,
     "msg": "success",
     "data": { ... }
   }
   ```
2. 策略插件化，每个策略为独立 Python 类，继承基类，便于扩展
3. 异步任务与状态管理，策略运行建议用异步任务（如 Celery），并记录状态
4. 行情与订单簿可直接调用 hummingbot 或第三方行情接口，支持 WebSocket 推送实时行情（可选）
5. 初期可用 mock 数据，接口联调后逐步接入真实数据

## FastAPI 路由片段示例

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

class Strategy(BaseModel):
    id: str
    name: str
    type: str
    status: str
    params: Dict

@app.get('/api/strategies', response_model=List[Strategy])
def get_strategies():
    # TODO: 从数据库获取
    return [
        {"id": "1", "name": "套利策略1", "type": "跨所套利", "status": "stopped", "params": {"symbol": "BTC/USDT", "threshold": 0.5}},
        {"id": "2", "name": "套利策略2", "type": "三角套利", "status": "running", "params": {"symbol": "ETH/USDT", "threshold": 0.3}},
    ]

@app.post('/api/strategies/{id}/start')
def start_strategy(id: str):
    # TODO: 启动策略逻辑
    return {"code": 0, "msg": "success"}
```

## 后续开发建议

- 先实现 mock 数据接口，保证前后端联调顺畅
- 再逐步接入数据库、hummingbot、真实行情与交易
- 日志、交易明细等可用定时任务或异步写入
- 代码结构清晰，便于后续扩展新策略、新交易所 