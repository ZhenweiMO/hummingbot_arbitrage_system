#!/usr/bin/env python3
"""
实时余额功能演示脚本
展示如何通过交易所 API 获取实时账户余额
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from exchange_connector import create_connector, ExchangeManager
import json

async def demo_binance_balance():
    """演示币安账户余额获取"""
    print("🔍 演示币安账户余额获取")
    print("=" * 50)
    
    # 注意：这里使用示例 API 密钥，实际使用时需要替换为真实的密钥
    api_key = "your_binance_api_key_here"
    api_secret = "your_binance_api_secret_here"
    
    if api_key == "your_binance_api_key_here":
        print("⚠️  请配置真实的币安 API 密钥")
        print("   1. 登录币安账户")
        print("   2. 进入 API 管理")
        print("   3. 创建 API 密钥（仅读取权限）")
        print("   4. 替换脚本中的 API 密钥")
        return
    
    try:
        connector = create_connector("binance", api_key, api_secret)
        
        async with connector:
            account_info = await connector.get_account_balance()
            
        if account_info:
            print(f"✅ 成功获取币安账户余额")
            print(f"   交易所: {account_info.exchange}")
            print(f"   账户类型: {account_info.account_id}")
            print(f"   总资产: {account_info.total_equity:.2f} USDT")
            print(f"   更新时间: {account_info.timestamp}")
            print("\n   资产详情:")
            
            for balance in account_info.balances:
                print(f"     {balance.asset}:")
                print(f"       可用: {balance.free:.8f}")
                print(f"       冻结: {balance.locked:.8f}")
                print(f"       总计: {balance.total:.8f}")
        else:
            print("❌ 获取币安账户余额失败")
            
    except Exception as e:
        print(f"❌ 币安 API 连接失败: {e}")

async def demo_okx_balance():
    """演示 OKX 账户余额获取"""
    print("\n🔍 演示 OKX 账户余额获取")
    print("=" * 50)
    
    # 注意：这里使用示例 API 密钥，实际使用时需要替换为真实的密钥
    api_key = "your_okx_api_key_here"
    api_secret = "your_okx_api_secret_here"
    passphrase = "your_okx_passphrase_here"
    
    if api_key == "your_okx_api_key_here":
        print("⚠️  请配置真实的 OKX API 密钥")
        print("   1. 登录 OKX 账户")
        print("   2. 进入账户中心 → API 管理")
        print("   3. 创建 API 密钥（仅读取权限）")
        print("   4. 设置 Passphrase")
        print("   5. 替换脚本中的 API 密钥")
        return
    
    try:
        connector = create_connector("okx", api_key, api_secret, passphrase=passphrase)
        
        async with connector:
            account_info = await connector.get_account_balance()
            
        if account_info:
            print(f"✅ 成功获取 OKX 账户余额")
            print(f"   交易所: {account_info.exchange}")
            print(f"   账户ID: {account_info.account_id}")
            print(f"   总资产: {account_info.total_equity:.2f} USDT")
            print(f"   更新时间: {account_info.timestamp}")
            print("\n   资产详情:")
            
            for balance in account_info.balances:
                print(f"     {balance.asset}:")
                print(f"       可用: {balance.free:.8f}")
                print(f"       冻结: {balance.locked:.8f}")
                print(f"       总计: {balance.total:.8f}")
        else:
            print("❌ 获取 OKX 账户余额失败")
            
    except Exception as e:
        print(f"❌ OKX API 连接失败: {e}")

async def demo_exchange_manager():
    """演示交易所管理器"""
    print("\n🔍 演示交易所管理器")
    print("=" * 50)
    
    manager = ExchangeManager()
    
    # 添加多个交易所连接器
    try:
        # 注意：实际使用时需要配置真实的 API 密钥
        binance_connector = create_connector(
            "binance", 
            "your_binance_api_key", 
            "your_binance_api_secret"
        )
        okx_connector = create_connector(
            "okx", 
            "your_okx_api_key", 
            "your_okx_api_secret",
            passphrase="your_okx_passphrase"
        )
        
        manager.add_connector("binance_account", binance_connector)
        manager.add_connector("okx_account", okx_connector)
        
        print(f"✅ 已添加 {len(manager.connectors)} 个交易所连接器")
        
        # 获取所有账户余额
        balances = await manager.get_all_accounts_balance()
        
        print(f"✅ 成功获取 {len(balances)} 个账户的余额")
        
        for account_id, account_info in balances.items():
            print(f"\n   账户: {account_id}")
            print(f"   交易所: {account_info.exchange}")
            print(f"   总资产: {account_info.total_equity:.2f} USDT")
            
    except Exception as e:
        print(f"❌ 交易所管理器演示失败: {e}")
        print("   请配置真实的 API 密钥后重试")

def show_configuration_guide():
    """显示配置指南"""
    print("\n📋 配置指南")
    print("=" * 50)
    print("要使用实时余额功能，请按以下步骤配置：")
    print()
    print("1. 🔑 获取交易所 API 密钥")
    print("   - 币安: https://www.binance.com/cn/my/settings/api-management")
    print("   - OKX: https://www.okx.com/account/my-api")
    print()
    print("2. ⚙️  配置系统账户")
    print("   - 方法一: 通过前端界面配置")
    print("   - 方法二: 直接修改数据库")
    print("   - 方法三: 通过 API 接口配置")
    print()
    print("3. 🔄 测试连接")
    print("   curl http://localhost:8001/api/accounts")
    print()
    print("4. 📊 查看实时余额")
    print("   - 系统会自动每60秒更新一次余额")
    print("   - 也可手动触发更新")
    print()
    print("📖 详细配置文档: docs/operations/ACCOUNT_SETUP_GUIDE.md")

async def main():
    """主函数"""
    print("🚀 实时余额功能演示")
    print("=" * 60)
    print("本演示展示如何通过交易所 API 获取实时账户余额")
    print("注意：需要配置真实的 API 密钥才能正常工作")
    print()
    
    # 演示各个交易所的余额获取
    await demo_binance_balance()
    await demo_okx_balance()
    await demo_exchange_manager()
    
    # 显示配置指南
    show_configuration_guide()
    
    print("\n" + "=" * 60)
    print("🎯 演示完成")
    print("💡 配置真实 API 密钥后，系统将自动获取实时余额")
    print("📖 更多信息请查看配置指南文档")

if __name__ == "__main__":
    asyncio.run(main())
