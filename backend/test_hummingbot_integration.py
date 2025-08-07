#!/usr/bin/env python3
"""
Hummingbot 集成测试脚本
"""
import sys
import os
import asyncio
from typing import Dict, Any

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

from hummingbot_integration import (
    get_available_strategies,
    get_strategy_schema,
    strategy_executor,
    StrategyType
)

def test_get_available_strategies():
    """测试获取可用策略列表"""
    print("=== 测试获取可用策略列表 ===")
    try:
        strategies = get_available_strategies()
        print(f"✅ 成功获取 {len(strategies)} 个策略:")
        for strategy in strategies:
            print(f"  - {strategy['name']} ({strategy['type']}) - {strategy['description']}")
        return True
    except Exception as e:
        print(f"❌ 获取策略列表失败: {e}")
        return False

def test_get_strategy_schema():
    """测试获取策略参数模式"""
    print("\n=== 测试获取策略参数模式 ===")
    try:
        # 测试纯做市策略
        schema = get_strategy_schema(StrategyType.PURE_MARKET_MAKING.value)
        print(f"✅ 成功获取纯做市策略参数模式，包含 {len(schema)} 个参数:")
        for param_name, param_info in schema.items():
            print(f"  - {param_name}: {param_info['type']} ({'必需' if param_info['required'] else '可选'})")
        
        # 测试 Avellaneda 做市策略
        schema = get_strategy_schema(StrategyType.AVELLANEDA_MARKET_MAKING.value)
        print(f"✅ 成功获取 Avellaneda 做市策略参数模式，包含 {len(schema)} 个参数:")
        for param_name, param_info in schema.items():
            print(f"  - {param_name}: {param_info['type']} ({'必需' if param_info['required'] else '可选'})")
        
        return True
    except Exception as e:
        print(f"❌ 获取策略参数模式失败: {e}")
        return False

async def test_strategy_executor():
    """测试策略执行器"""
    print("\n=== 测试策略执行器 ===")
    try:
        # 测试启动策略
        strategy_id = "test_strategy_001"
        strategy_type = StrategyType.PURE_MARKET_MAKING.value
        params = {
            "exchange": "binance",
            "market": "BTC-USDT",
            "bid_spread": 1.0,
            "ask_spread": 1.0,
            "order_amount": 0.001,
            "order_refresh_time": 30
        }
        
        success = await strategy_executor.start_strategy(strategy_id, strategy_type, params)
        if success:
            print(f"✅ 成功启动策略 {strategy_id}")
            
            # 测试获取策略状态
            status = await strategy_executor.get_strategy_status(strategy_id)
            if status:
                print(f"✅ 成功获取策略状态: {status}")
            
            # 测试停止策略
            success = await strategy_executor.stop_strategy(strategy_id)
            if success:
                print(f"✅ 成功停止策略 {strategy_id}")
            else:
                print(f"❌ 停止策略失败")
        else:
            print(f"❌ 启动策略失败")
        
        return True
    except Exception as e:
        print(f"❌ 策略执行器测试失败: {e}")
        return False

def test_parameter_validation():
    """测试参数验证"""
    print("\n=== 测试参数验证 ===")
    try:
        from hummingbot_integration import ParameterValidator, StrategySchema
        
        # 测试有效参数
        valid_params = {
            "exchange": "binance",
            "market": "BTC-USDT",
            "bid_spread": 1.0,
            "ask_spread": 1.0,
            "order_amount": 0.001,
            "order_refresh_time": 30
        }
        
        schema = StrategySchema.get_pure_market_making_schema()
        validated_params = ParameterValidator.validate_parameters(valid_params, schema)
        print(f"✅ 参数验证成功: {len(validated_params)} 个参数")
        
        # 测试无效参数
        invalid_params = {
            "exchange": "invalid_exchange",
            "bid_spread": -1.0,  # 无效的价差
            "order_amount": -0.001  # 无效的数量
        }
        
        try:
            validated_params = ParameterValidator.validate_parameters(invalid_params, schema)
            print("❌ 应该验证失败但通过了")
            return False
        except ValueError as e:
            print(f"✅ 参数验证正确捕获错误: {e}")
        
        return True
    except Exception as e:
        print(f"❌ 参数验证测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始 Hummingbot 集成测试...\n")
    
    tests = [
        ("获取可用策略列表", test_get_available_strategies),
        ("获取策略参数模式", test_get_strategy_schema),
        ("策略执行器", test_strategy_executor),
        ("参数验证", test_parameter_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            print()
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}\n")
    
    print("=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！Hummingbot 集成功能正常。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    asyncio.run(main()) 