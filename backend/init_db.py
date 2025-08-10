from database import engine
import models
import crud, schemas
from database import SessionLocal

def init_db():
    """初始化数据库 - 生产环境版本，不创建示例数据"""
    # 创建所有表
    models.Base.metadata.create_all(bind=engine)
    
    # 创建初始数据
    db = SessionLocal()
    try:
        # 检查是否已有数据
        existing_strategies = crud.get_strategies(db)
        existing_accounts = crud.get_accounts(db)
        
        if not existing_strategies and not existing_accounts:
            print("✅ 数据库表结构已创建")
            print("📝 提示：")
            print("   - 请先添加交易所账户以获取实时余额")
            print("   - 然后创建套利策略开始交易")
            print("   - 系统将自动记录交易日志和性能数据")
        else:
            print("✅ 数据库已存在数据，跳过初始化")
            
    except Exception as e:
        print(f"❌ 初始化数据库失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 开始初始化数据库...")
    init_db()
    print("✅ 数据库初始化完成！") 