#!/usr/bin/env python3
"""
系统连接性测试脚本
验证前端、后端、数据库等各组件的连接状态
"""

import requests
import json
import sys
from datetime import datetime

# 配置
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:9091"
HUMMINGBOT_URL = "http://localhost:15889"

def test_backend_connectivity():
    """测试后端连接性"""
    print("🔍 测试后端连接性")
    print("=" * 50)
    
    try:
        # 测试基础 API
        response = requests.get(f"{BACKEND_URL}/api/overview", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ 后端 API 正常")
        print(f"   策略总数: {data.get('strategy_total', 0)}")
        print(f"   运行中策略: {data.get('strategy_running', 0)}")
        print(f"   总资产: {data.get('asset_total', 0)}")
        print(f"   今日盈亏: {data.get('profit_today', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_frontend_connectivity():
    """测试前端连接性"""
    print("\n🔍 测试前端连接性")
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
        print(f"❌ 前端连接失败: {e}")
        return False

def test_hummingbot_connectivity():
    """测试 Hummingbot 连接性"""
    print("\n🔍 测试 Hummingbot 连接性")
    print("=" * 50)
    
    try:
        # 测试 Hummingbot 健康检查
        response = requests.get(f"{HUMMINGBOT_URL}/health", timeout=5)
        response.raise_for_status()
        
        print("✅ Hummingbot API 正常")
        return True
        
    except Exception as e:
        print(f"❌ Hummingbot 连接失败: {e}")
        return False

def test_strategy_apis():
    """测试策略相关 API"""
    print("\n🔍 测试策略相关 API")
    print("=" * 50)
    
    try:
        # 测试策略列表
        response = requests.get(f"{BACKEND_URL}/api/hummingbot/strategies", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0:
            strategies = data.get("data", [])
            print(f"✅ 策略列表 API 正常，包含 {len(strategies)} 个策略")
            
            # 测试每个策略的参数模式
            success_count = 0
            for strategy in strategies:
                strategy_type = strategy['type']
                try:
                    response = requests.get(f"{BACKEND_URL}/api/hummingbot/strategies/{strategy_type}/schema", timeout=5)
                    response.raise_for_status()
                    schema_data = response.json()
                    
                    if schema_data.get("code") == 0:
                        schema = schema_data.get("data", {})
                        print(f"   ✅ {strategy['name']}: {len(schema)} 个参数")
                        success_count += 1
                    else:
                        print(f"   ❌ {strategy['name']}: 参数模式获取失败")
                        
                except Exception as e:
                    print(f"   ❌ {strategy['name']}: {e}")
            
            print(f"\n📊 策略参数模式测试结果: {success_count}/{len(strategies)} 成功")
            return success_count == len(strategies)
        else:
            print(f"❌ 策略列表 API 异常: {data}")
            return False
            
    except Exception as e:
        print(f"❌ 策略 API 测试失败: {e}")
        return False

def test_database_connectivity():
    """测试数据库连接性"""
    print("\n🔍 测试数据库连接性")
    print("=" * 50)
    
    try:
        # 通过 API 测试数据库连接
        response = requests.get(f"{BACKEND_URL}/api/strategies", timeout=5)
        response.raise_for_status()
        strategies = response.json()
        
        print(f"✅ 数据库连接正常")
        print(f"   数据库中的策略数量: {len(strategies)}")
        
        # 测试账户 API
        response = requests.get(f"{BACKEND_URL}/api/accounts", timeout=5)
        response.raise_for_status()
        accounts = response.json()
        
        print(f"   数据库中的账户数量: {len(accounts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def generate_report(results):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("📊 连接性测试报告")
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
        print("🎉 所有测试通过！系统连接正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关服务。")
        return False

def main():
    """主函数"""
    print("🚀 系统连接性测试")
    print("=" * 60)
    
    results = {}
    
    # 执行各项测试
    results["后端连接性"] = test_backend_connectivity()
    results["前端连接性"] = test_frontend_connectivity()
    results["Hummingbot 连接性"] = test_hummingbot_connectivity()
    results["策略 API"] = test_strategy_apis()
    results["数据库连接性"] = test_database_connectivity()
    
    # 生成报告
    success = generate_report(results)
    
    print("\n" + "=" * 60)
    print("🌐 访问地址")
    print("=" * 60)
    print(f"前端界面: {FRONTEND_URL}")
    print(f"后端 API: {BACKEND_URL}")
    print(f"API 文档: {BACKEND_URL}/docs")
    print(f"监控面板: http://localhost:3001")
    print(f"Prometheus: http://localhost:9090")
    
    if success:
        print("\n💡 系统运行正常，可以开始使用套利交易系统了！")
    else:
        print("\n🔧 请检查失败的服务并重新启动。")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
