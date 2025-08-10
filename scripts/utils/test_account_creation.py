#!/usr/bin/env python3
"""
账户创建流程测试脚本
验证新建账户时无需手动输入余额和持仓
"""

import requests
import json
import sys
from datetime import datetime

# 配置
BACKEND_URL = "http://localhost:8001"

def test_account_creation_without_balance():
    """测试创建账户时不包含余额和持仓"""
    print("🔍 测试账户创建流程")
    print("=" * 50)
    
    try:
        # 测试数据 - 不包含余额和持仓
        account_data = {
            "name": "测试账户",
            "exchange_type": "binance",
            "api_key": "test_api_key_123",
            "api_secret": "test_api_secret_456"
        }
        
        print("📝 创建账户数据:")
        print(f"   名称: {account_data['name']}")
        print(f"   交易所: {account_data['exchange_type']}")
        print(f"   API Key: {account_data['api_key']}")
        print(f"   API Secret: {account_data['api_secret']}")
        print("   ❌ 不包含余额和持仓字段")
        
        # 创建账户
        response = requests.post(f"{BACKEND_URL}/api/accounts", json=account_data, timeout=10)
        response.raise_for_status()
        account = response.json()
        
        print(f"\n✅ 账户创建成功:")
        print(f"   账户ID: {account.get('id')}")
        print(f"   名称: {account.get('name')}")
        print(f"   交易所: {account.get('exchange_type')}")
        print(f"   余额: {account.get('balance')} (系统自动设置)")
        print(f"   持仓: {account.get('position')} (系统自动设置)")
        print(f"   激活状态: {account.get('is_active')}")
        print(f"   创建时间: {account.get('created_at')}")
        
        # 验证余额和持仓字段
        balance = account.get('balance')
        position = account.get('position')
        
        if balance is not None and balance >= 0:
            print(f"\n✅ 余额字段正确: {balance}")
        else:
            print(f"\n❌ 余额字段异常: {balance}")
            return False
            
        if position is None:
            print(f"✅ 持仓字段正确: {position} (初始为空)")
        else:
            print(f"✅ 持仓字段正确: {position}")
        
        return account.get('id')
        
    except Exception as e:
        print(f"❌ 账户创建失败: {e}")
        return None

def test_account_retrieval(account_id):
    """测试获取账户信息"""
    print(f"\n🔍 测试获取账户信息 (ID: {account_id})")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/accounts", timeout=5)
        response.raise_for_status()
        accounts = response.json()
        
        # 查找刚创建的账户
        target_account = None
        for account in accounts:
            if account.get('id') == account_id:
                target_account = account
                break
        
        if target_account:
            print("✅ 账户信息获取成功:")
            print(f"   名称: {target_account.get('name')}")
            print(f"   交易所: {target_account.get('exchange_type')}")
            print(f"   余额: {target_account.get('balance')}")
            print(f"   持仓: {target_account.get('position')}")
            print(f"   激活状态: {target_account.get('is_active')}")
            return True
        else:
            print("❌ 未找到创建的账户")
            return False
            
    except Exception as e:
        print(f"❌ 获取账户信息失败: {e}")
        return False

def test_account_deletion(account_id):
    """测试删除账户"""
    print(f"\n🔍 测试删除账户 (ID: {account_id})")
    print("=" * 50)
    
    try:
        response = requests.delete(f"{BACKEND_URL}/api/accounts/{account_id}", timeout=5)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == 0:
            print("✅ 账户删除成功")
            return True
        else:
            print(f"❌ 账户删除失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 删除账户失败: {e}")
        return False

def test_schema_validation():
    """测试 schema 验证"""
    print("\n🔍 测试 Schema 验证")
    print("=" * 50)
    
    try:
        # 测试不包含余额和持仓的账户数据
        account_data = {
            "name": "Schema测试账户",
            "exchange_type": "okx",
            "api_key": "test_key",
            "api_secret": "test_secret",
            "passphrase": "test_passphrase"
            # 故意不包含 balance 和 position 字段
        }
        
        print("📝 测试数据 (不包含余额和持仓):")
        for key, value in account_data.items():
            print(f"   {key}: {value}")
        
        response = requests.post(f"{BACKEND_URL}/api/accounts", json=account_data, timeout=10)
        
        if response.status_code == 200:
            account = response.json()
            print(f"\n✅ Schema 验证通过，账户创建成功:")
            print(f"   余额: {account.get('balance')} (自动设置)")
            print(f"   持仓: {account.get('position')} (自动设置)")
            
            # 清理测试数据
            account_id = account.get('id')
            if account_id:
                requests.delete(f"{BACKEND_URL}/api/accounts/{account_id}", timeout=5)
                print(f"✅ 测试数据已清理 (ID: {account_id})")
            
            return True
        else:
            print(f"❌ Schema 验证失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Schema 验证测试失败: {e}")
        return False

def generate_report(results):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("📊 账户创建流程测试报告")
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
        print("🎉 账户创建流程测试全部通过！")
        print("💡 新建账户时无需手动输入余额和持仓，系统会自动处理。")
        return True
    else:
        print("⚠️  部分测试失败，需要进一步检查。")
        return False

def main():
    """主函数"""
    print("🚀 账户创建流程测试")
    print("=" * 60)
    
    results = {}
    
    # 执行各项测试
    account_id = test_account_creation_without_balance()
    results["账户创建测试"] = account_id is not None
    
    if account_id:
        results["账户信息获取测试"] = test_account_retrieval(account_id)
        results["账户删除测试"] = test_account_deletion(account_id)
    else:
        results["账户信息获取测试"] = False
        results["账户删除测试"] = False
    
    results["Schema 验证测试"] = test_schema_validation()
    
    # 生成报告
    success = generate_report(results)
    
    print("\n" + "=" * 60)
    print("🌐 访问地址")
    print("=" * 60)
    print(f"后端 API: {BACKEND_URL}")
    print(f"API 文档: {BACKEND_URL}/docs")
    
    if success:
        print("\n💡 账户创建流程已优化，新用户无需手动输入余额和持仓！")
    else:
        print("\n🔧 请检查失败的测试项并进行修复。")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
