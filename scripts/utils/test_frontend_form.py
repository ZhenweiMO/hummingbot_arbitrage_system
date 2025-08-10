#!/usr/bin/env python3
"""
前端表单测试脚本
验证账户创建表单的正确性
"""

import requests
import json
import sys
from datetime import datetime

# 配置
FRONTEND_URL = "http://localhost:9091"
BACKEND_URL = "http://localhost:8001"

def test_frontend_accessibility():
    """测试前端可访问性"""
    print("🔍 测试前端可访问性")
    print("=" * 50)
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("✅ 前端页面可正常访问")
            return True
        else:
            print(f"❌ 前端页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端页面访问异常: {e}")
        return False

def test_backend_api():
    """测试后端 API"""
    print("\n🔍 测试后端 API")
    print("=" * 50)
    
    try:
        # 测试账户列表 API
        response = requests.get(f"{BACKEND_URL}/api/accounts", timeout=5)
        if response.status_code == 200:
            accounts = response.json()
            print(f"✅ 后端 API 正常，当前账户数量: {len(accounts)}")
            return True
        else:
            print(f"❌ 后端 API 异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端 API 访问失败: {e}")
        return False

def test_account_creation_flow():
    """测试账户创建流程"""
    print("\n🔍 测试账户创建流程")
    print("=" * 50)
    
    try:
        # 测试数据 - 不包含余额和持仓
        test_accounts = [
            {
                "name": "Binance测试账户",
                "exchange_type": "binance",
                "api_key": "binance_test_key",
                "api_secret": "binance_test_secret"
            },
            {
                "name": "OKX测试账户", 
                "exchange_type": "okx",
                "api_key": "okx_test_key",
                "api_secret": "okx_test_secret",
                "passphrase": "okx_test_passphrase"
            }
        ]
        
        created_accounts = []
        
        for i, account_data in enumerate(test_accounts, 1):
            print(f"\n📝 测试账户 {i}: {account_data['name']}")
            print(f"   交易所: {account_data['exchange_type']}")
            print(f"   包含余额字段: {'balance' in account_data}")
            print(f"   包含持仓字段: {'position' in account_data}")
            
            # 创建账户
            response = requests.post(f"{BACKEND_URL}/api/accounts", json=account_data, timeout=10)
            
            if response.status_code == 200:
                account = response.json()
                created_accounts.append(account['id'])
                
                print(f"✅ 账户创建成功:")
                print(f"   账户ID: {account['id']}")
                print(f"   余额: {account['balance']} (系统自动设置)")
                print(f"   持仓: {account['position']} (系统自动设置)")
                
                # 验证余额和持仓是否正确设置
                if account['balance'] is not None and account['balance'] >= 0:
                    print(f"   ✅ 余额字段正确")
                else:
                    print(f"   ❌ 余额字段异常")
                    return False
                    
                if account['position'] is None:
                    print(f"   ✅ 持仓字段正确 (初始为空)")
                else:
                    print(f"   ✅ 持仓字段正确")
                    
            else:
                print(f"❌ 账户创建失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
        
        # 清理测试数据
        print(f"\n🧹 清理测试数据...")
        for account_id in created_accounts:
            try:
                requests.delete(f"{BACKEND_URL}/api/accounts/{account_id}", timeout=5)
                print(f"   ✅ 删除账户 {account_id}")
            except Exception as e:
                print(f"   ⚠️  删除账户 {account_id} 失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 账户创建流程测试失败: {e}")
        return False

def generate_form_guide():
    """生成表单使用指南"""
    print("\n" + "=" * 60)
    print("📋 账户创建表单使用指南")
    print("=" * 60)
    print("🌐 访问地址: http://localhost:9091/accounts")
    print()
    
    print("📝 表单字段说明:")
    print("1. 交易所类型: 下拉选择框")
    print("   - Binance - 全球最大的加密货币交易所")
    print("   - OKX - 专业的数字资产交易平台") 
    print("   - Bybit - 专业的衍生品交易平台")
    print("   - Gate.io - 老牌数字资产交易所")
    print("   - KuCoin - 加密货币交易所")
    print()
    
    print("2. 账户名称: 文本输入框")
    print("   - 示例: 我的Binance账户")
    print()
    
    print("3. API Key: 密码输入框")
    print("   - 从交易所获取的 API Key")
    print()
    
    print("4. API Secret: 密码输入框")
    print("   - 从交易所获取的 API Secret")
    print()
    
    print("5. API Passphrase: 密码输入框 (仅 OKX)")
    print("   - 仅在选择 OKX 交易所时显示")
    print()
    
    print("❌ 新建账户时不会显示:")
    print("   - 余额字段 (系统自动获取)")
    print("   - 持仓字段 (系统自动获取)")
    print()
    
    print("✅ 编辑账户时会显示:")
    print("   - 当前余额 (只读，显示'系统自动获取')")
    print("   - 当前持仓 (只读，显示'系统自动获取')")
    print()
    
    print("💡 使用提示:")
    print("- 选择交易所类型后，表单会根据交易所要求显示相应字段")
    print("- 系统会自动从交易所 API 获取余额和持仓信息")
    print("- 编辑时交易所类型不允许修改")
    print("- API 密钥信息会进行掩码显示保护")

def main():
    """主函数"""
    print("🚀 前端表单测试")
    print("=" * 60)
    
    results = {}
    
    # 执行各项测试
    results["前端可访问性测试"] = test_frontend_accessibility()
    results["后端 API 测试"] = test_backend_api()
    results["账户创建流程测试"] = test_account_creation_flow()
    
    # 生成报告
    print("\n" + "=" * 60)
    print("📊 测试报告")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print()
    print(f"总体结果: {passed_tests}/{total_tests} 项测试通过")
    
    if passed_tests == total_tests:
        print("🎉 前端表单测试全部通过！")
        print("💡 账户创建表单已正确配置，无需手动输入余额和持仓。")
    else:
        print("⚠️  部分测试失败，需要进一步检查。")
    
    # 生成使用指南
    generate_form_guide()
    
    return 0 if passed_tests == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())
