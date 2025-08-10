from database import engine
import models
import crud, schemas
from database import SessionLocal

def init_db():
    # 创建所有表
    models.Base.metadata.create_all(bind=engine)
    
    # 创建初始数据
    db = SessionLocal()
    try:
        # 检查是否已有数据
        existing_strategies = crud.get_strategies(db)
        if not existing_strategies:
            # 创建示例策略
            strategy1 = schemas.StrategyCreate(
                name="套利策略1",
                type="跨所套利",
                params={"symbol": "BTC/USDT", "threshold": 0.5}
            )
            strategy2 = schemas.StrategyCreate(
                name="套利策略2", 
                type="三角套利",
                params={"symbol": "ETH/USDT", "threshold": 0.3}
            )
            crud.create_strategy(db, strategy1)
            crud.create_strategy(db, strategy2)
            print("✅ 示例策略已创建")

        existing_accounts = crud.get_accounts(db)
        if not existing_accounts:
            # 创建示例账户（需要用户配置真实的 API 密钥）
            account1 = schemas.AccountCreate(
                name="Binance",
                exchange_type="binance",
                api_key="your_binance_api_key_here",  # 需要用户替换为真实的 API 密钥
                api_secret="your_binance_api_secret_here",
                balance=0.0,  # 初始为0，将通过 API 获取真实余额
                position=""
            )
            account2 = schemas.AccountCreate(
                name="OKX",
                exchange_type="okx", 
                api_key="your_okx_api_key_here",  # 需要用户替换为真实的 API 密钥
                api_secret="your_okx_api_secret_here",
                passphrase="your_okx_passphrase_here",
                balance=0.0,  # 初始为0，将通过 API 获取真实余额
                position=""
            )
            crud.create_account(db, account1)
            crud.create_account(db, account2)
            print("✅ 示例账户已创建")
            print("⚠️  请配置真实的交易所 API 密钥以获取实时余额")

        # 创建示例日志
        log1 = schemas.LogCreate(
            level="INFO",
            message="系统启动完成"
        )
        log2 = schemas.LogCreate(
            level="INFO", 
            message="策略引擎初始化成功"
        )
        crud.create_log(db, log1)
        crud.create_log(db, log2)
        print("✅ 示例日志已创建")

    except Exception as e:
        print(f"❌ 初始化数据库失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 开始初始化数据库...")
    init_db()
    print("✅ 数据库初始化完成！") 