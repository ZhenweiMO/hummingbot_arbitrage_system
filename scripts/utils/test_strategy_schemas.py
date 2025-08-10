#!/usr/bin/env python3
"""
策略参数模式测试脚本
验证所有策略的参数模式是否正确返回
"""

import requests
import json
import sys

# API 基础 URL
API_BASE_URL = "http://localhost:8001/api"

def test_available_strategies():
    """测试获取可用策略列表"""
    print("🔍 测试获取可用策略列表")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/hummingbot/strategies")
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0:
            strategies = data.get("data", [])
            print(f"✅ 成功获取 {len(strategies)} 个策略")
            
            for strategy in strategies:
                print(f"   📋 {strategy['name']}")
                print(f"      类型: {strategy['type']}")
                print(f"      描述: {strategy['description']}")
                print(f"      分类: {strategy['category']}")
                print()
            
            return [s['type'] for s in strategies]
        else:
            print(f"❌ API 返回错误: {data}")
            return []
            
    except Exception as e:
        print(f"❌ 获取策略列表失败: {e}")
        return []

def test_strategy_schema(strategy_type):
    """测试获取策略参数模式"""
    print(f"🔍 测试策略参数模式: {strategy_type}")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_BASE_URL}/hummingbot/strategies/{strategy_type}/schema")
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0:
            schema = data.get("data", {})
            print(f"✅ 成功获取参数模式，包含 {len(schema)} 个参数")
            
            for param_name, param_info in schema.items():
                print(f"   📝 {param_name}")
                print(f"      类型: {param_info['type']}")
                print(f"      描述: {param_info['description']}")
                print(f"      必需: {param_info['required']}")
                
                if param_info.get('default') is not None:
                    print(f"      默认值: {param_info['default']}")
                
                if param_info.get('min_value') is not None:
                    print(f"      最小值: {param_info['min_value']}")
                
                if param_info.get('max_value') is not None:
                    print(f"      最大值: {param_info['max_value']}")
                
                if param_info.get('options'):
                    print(f"      选项: {', '.join(param_info['options'])}")
                
                if param_info.get('unit'):
                    print(f"      单位: {param_info['unit']}")
                
                print()
            
            return True
        else:
            print(f"❌ API 返回错误: {data}")
            return False
            
    except Exception as e:
        print(f"❌ 获取参数模式失败: {e}")
        return False

def test_frontend_api():
    """测试前端 API 调用"""
    print("🔍 测试前端 API 调用")
    print("=" * 50)
    
    try:
        # 测试策略列表
        response = requests.get(f"{API_BASE_URL}/hummingbot/strategies")
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0:
            strategies = data.get("data", [])
            print(f"✅ 前端 API 策略列表正常，包含 {len(strategies)} 个策略")
            
            # 测试第一个策略的参数模式
            if strategies:
                first_strategy = strategies[0]
                strategy_type = first_strategy['type']
                
                response = requests.get(f"{API_BASE_URL}/hummingbot/strategies/{strategy_type}/schema")
                response.raise_for_status()
                schema_data = response.json()
                
                if schema_data.get("code") == 0:
                    print(f"✅ 前端 API 参数模式正常，策略 {strategy_type} 包含 {len(schema_data.get('data', {}))} 个参数")
                else:
                    print(f"❌ 前端 API 参数模式异常: {schema_data}")
            else:
                print("⚠️  没有可用的策略")
        else:
            print(f"❌ 前端 API 策略列表异常: {data}")
            
    except Exception as e:
        print(f"❌ 前端 API 测试失败: {e}")

def main():
    """主函数"""
    print("🚀 策略参数模式测试")
    print("=" * 60)
    
    # 测试可用策略列表
    strategy_types = test_available_strategies()
    
    if not strategy_types:
        print("❌ 无法获取策略列表，测试终止")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🔍 测试各策略的参数模式")
    print("=" * 60)
    
    # 测试每个策略的参数模式
    success_count = 0
    total_count = len(strategy_types)
    
    for strategy_type in strategy_types:
        if test_strategy_schema(strategy_type):
            success_count += 1
        print()
    
    print("=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    print(f"总策略数: {total_count}")
    print(f"成功获取参数模式: {success_count}")
    print(f"失败数量: {total_count - success_count}")
    
    if success_count == total_count:
        print("🎉 所有策略参数模式测试通过！")
    else:
        print("⚠️  部分策略参数模式获取失败")
    
    print("\n" + "=" * 60)
    print("🔍 前端 API 测试")
    print("=" * 60)
    
    # 测试前端 API
    test_frontend_api()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("💡 现在可以在前端创建 AMM 套利和现货永续套利策略了")

if __name__ == "__main__":
    main()
