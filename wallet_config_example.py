#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钱包配置示例
演示如何配置钱包用于Hyperliquid资金费率套利系统
"""

from wallet_simple import SimpleWalletManager

def example_wallet_setup():
    """钱包配置示例"""
    print("="*60)
    print("Hyperliquid资金费率套利系统 - 钱包配置示例")
    print("="*60)
    
    # 创建钱包管理器
    wallet = SimpleWalletManager()
    
    # 示例钱包地址和私钥（请替换为你的真实信息）
    example_address = "0x1234567890123456789012345678901234567890"
    example_private_key = "0x1111111111111111111111111111111111111111111111111111111111111111"
    
    print("📋 配置步骤：")
    print("1. 准备你的钱包地址和私钥")
    print("2. 确保钱包中有足够的USDT余额")
    print("3. 运行配置脚本")
    print()
    
    print("🔧 手动配置方法：")
    print("方法1: 运行配置脚本")
    print("   python setup_wallet.py")
    print()
    
    print("方法2: 在代码中直接配置")
    print("```python")
    print("from wallet_simple import SimpleWalletManager")
    print()
    print("# 创建钱包管理器")
    print("wallet = SimpleWalletManager()")
    print()
    print("# 连接钱包（替换为你的真实信息）")
    print("address = '你的钱包地址'")
    print("private_key = '你的私钥'")
    print("wallet.connect_wallet(address, private_key)")
    print()
    print("# 保存配置")
    print("wallet.save_config()")
    print("```")
    print()
    
    print("方法3: 直接编辑wallet.json文件")
    print("创建wallet.json文件，内容如下：")
    print("```json")
    print("{")
    print('  "address": "你的钱包地址",')
    print('  "private_key": "你的私钥",')
    print('  "balance": 1000.0,')
    print('  "available_margin": 800.0')
    print("}")
    print("```")
    print()
    
    print("⚠️  安全提醒：")
    print("- 私钥非常重要，请妥善保管")
    print("- 不要将私钥分享给任何人")
    print("- 建议使用专门的交易钱包")
    print("- 定期备份钱包配置")
    print()
    
    print("✅ 配置完成后，运行主系统：")
    print("   python hyperliquid_system.py")

def test_wallet_connection():
    """测试钱包连接"""
    print("\n" + "="*40)
    print("测试钱包连接")
    print("="*40)
    
    wallet = SimpleWalletManager()
    
    # 测试连接（使用示例数据）
    test_address = "0x1234567890123456789012345678901234567890"
    test_private_key = "0x1111111111111111111111111111111111111111111111111111111111111111"
    
    if wallet.connect_wallet(test_address, test_private_key):
        print("✅ 钱包连接测试成功")
        
        # 获取余额
        balance, margin = wallet.get_balance()
        print(f"测试余额: {balance} USDT")
        print(f"测试可用保证金: {margin} USDT")
        
        # 保存测试配置
        if wallet.save_config("test_wallet.json"):
            print("✅ 测试配置已保存")
        
        return True
    else:
        print("❌ 钱包连接测试失败")
        return False

if __name__ == "__main__":
    example_wallet_setup()
    
    # 询问是否进行测试
    choice = input("\n是否要测试钱包连接？(y/n): ").strip().lower()
    if choice == 'y':
        test_wallet_connection() 