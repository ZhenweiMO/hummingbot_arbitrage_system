#!/usr/bin/env python3
"""
新用户体验测试脚本
验证系统是否为新用户提供了干净的环境和良好的引导体验
"""

import requests
import json
import sys
from datetime import datetime

# 配置
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:9091"

def test_clean_environment():
    """测试系统是否为干净环境"""
    print("🔍 测试系统环境清洁度")
    print("=" * 50)
    
    try:
        # 测试总览数据
        response = requests.get(f"{BACKEND_URL}/api/overview", timeout=5)
        response.raise_for_status()
        overview = response.json()
        
        print("✅ 总览数据检查:")
        print(f"   策略总数: {overview.get('strategy_total', 0)} (应为 0)")
        print(f"   运行中策略: {overview.get('strategy_running', 0)} (应为 0)")
        print(f"   总资产: {overview.get('asset_total', 0)} (应为 0)")
        print(f"   今日盈亏: {overview.get('profit_today', 0)} (应为 0.0)")
        
        # 测试策略列表
        response = requests.get(f"{BACKEND_URL}/api/strategies", timeout=5)
        response.raise_for_status()
        strategies = response.json()
        
        print(f"✅ 策略列表: {len(strategies)} 个策略 (应为 0)")
        
        # 测试账户列表
        response = requests.get(f"{BACKEND_URL}/api/accounts", timeout=5)
        response.raise_for_status()
        accounts = response.json()
        
        print(f"✅ 账户列表: {len(accounts)} 个账户 (应为 0)")
        
        # 测试日志列表
        response = requests.get(f"{BACKEND_URL}/api/logs", timeout=5)
        response.raise_for_status()
        logs = response.json()
        
        print(f"✅ 日志列表: {len(logs)} 条日志 (应为 0)")
        
        # 测试交易记录
        response = requests.get(f"{BACKEND_URL}/api/trades", timeout=5)
        response.raise_for_status()
        trades = response.json()
        
        print(f"✅ 交易记录: {len(trades)} 条记录 (应为 0)")
        
        # 检查是否为新用户环境
        is_clean = (
            overview.get('strategy_total', 0) == 0 and
            overview.get('strategy_running', 0) == 0 and
            overview.get('asset_total', 0) == 0 and
            overview.get('profit_today', 0) == 0.0 and
            len(strategies) == 0 and
            len(accounts) == 0 and
            len(logs) == 0 and
            len(trades) == 0
        )
        
        if is_clean:
            print("\n🎉 系统环境完全干净，适合新用户使用！")
            return True
        else:
            print("\n⚠️  系统环境不干净，存在示例数据")
            return False
            
    except Exception as e:
        print(f"❌ 环境检查失败: {e}")
        return False

def test_frontend_accessibility():
    """测试前端可访问性"""
    print("\n🔍 测试前端可访问性")
    print("=" * 50)
    
    try:
        # 测试前端页面
        response = requests.get(f"{FRONTEND_URL}", timeout=5)
        response.raise_for_status()
        
        if "React App" in response.text:
            print("✅ 前端页面正常加载")
        else:
            print("⚠️  前端页面内容异常")
        
        # 测试前端代理到后端
        response = requests.get(f"{FRONTEND_URL}/api/overview", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ 前端代理到后端正常")
        print(f"   通过前端获取的数据: {data}")
        
        return True
        
    except Exception as e:
        print(f"❌ 前端访问失败: {e}")
        return False

def test_api_endpoints():
    """测试 API 端点"""
    print("\n🔍 测试 API 端点")
    print("=" * 50)
    
    endpoints = [
        "/api/overview",
        "/api/strategies", 
        "/api/accounts",
        "/api/logs",
        "/api/trades",
        "/api/hummingbot/strategies"
    ]
    
    success_count = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                print(f"✅ {endpoint}: {len(data)} 条记录")
            elif isinstance(data, dict):
                print(f"✅ {endpoint}: 正常响应")
            else:
                print(f"✅ {endpoint}: 正常响应")
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print(f"\n📊 API 端点测试结果: {success_count}/{len(endpoints)} 成功")
    return success_count == len(endpoints)

def test_new_user_flow():
    """测试新用户流程"""
    print("\n🔍 测试新用户流程")
    print("=" * 50)
    
    try:
        # 测试策略创建 API
        strategy_data = {
            "name": "测试策略",
            "type": "pure_market_making",
            "params": {
                "symbol": "BTC/USDT",
                "bid_spread": 0.01,
                "ask_spread": 0.01,
                "order_amount": 0.001
            }
        }
        
        response = requests.post(f"{BACKEND_URL}/api/strategies", json=strategy_data, timeout=5)
        response.raise_for_status()
        strategy = response.json()
        
        print(f"✅ 策略创建成功: {strategy.get('name')}")
        
        # 测试账户创建 API
        account_data = {
            "name": "测试账户",
            "exchange_type": "binance",
            "api_key": "test_api_key",
            "api_secret": "test_api_secret"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/accounts", json=account_data, timeout=5)
        response.raise_for_status()
        account = response.json()
        
        print(f"✅ 账户创建成功: {account.get('name')}")
        
        # 清理测试数据
        requests.delete(f"{BACKEND_URL}/api/strategies/{strategy.get('id')}", timeout=5)
        requests.delete(f"{BACKEND_URL}/api/accounts/{account.get('id')}", timeout=5)
        
        print("✅ 测试数据清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 新用户流程测试失败: {e}")
        return False

def generate_report(results):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("📊 新用户体验测试报告")
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
        print("🎉 新用户体验测试全部通过！系统已为新用户优化。")
        return True
    else:
        print("⚠️  部分测试失败，需要进一步优化。")
        return False

def main():
    """主函数"""
    print("🚀 新用户体验测试")
    print("=" * 60)
    
    results = {}
    
    # 执行各项测试
    results["系统环境清洁度"] = test_clean_environment()
    results["前端可访问性"] = test_frontend_accessibility()
    results["API 端点测试"] = test_api_endpoints()
    results["新用户流程测试"] = test_new_user_flow()
    
    # 生成报告
    success = generate_report(results)
    
    print("\n" + "=" * 60)
    print("🌐 访问地址")
    print("=" * 60)
    print(f"前端界面: {FRONTEND_URL}")
    print(f"后端 API: {BACKEND_URL}")
    print(f"API 文档: {BACKEND_URL}/docs")
    
    if success:
        print("\n💡 系统已为新用户优化，可以开始使用！")
        print("📖 查看新用户指南: docs/user_guide/NEW_USER_GUIDE.md")
    else:
        print("\n🔧 请检查失败的测试项并进行修复。")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
