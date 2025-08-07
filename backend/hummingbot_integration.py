"""
Hummingbot 集成模块
提供策略参数定义、执行器和参数验证功能
支持容器化部署
"""
import asyncio
import json
import logging
import os
import requests
from decimal import Decimal
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sys

# 获取环境变量
HUMMINGBOT_HOST = os.getenv('HUMMINGBOT_HOST', 'localhost')
HUMMINGBOT_PORT = os.getenv('HUMMINGBOT_PORT', '15888')
HUMMINGBOT_API_URL = f"http://{HUMMINGBOT_HOST}:{HUMMINGBOT_PORT}"

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """策略类型枚举"""
    PURE_MARKET_MAKING = "pure_market_making"
    AVELLANEDA_MARKET_MAKING = "avellaneda_market_making"
    CROSS_EXCHANGE_MARKET_MAKING = "cross_exchange_market_making"
    AMM_ARB = "amm_arb"
    SPOT_PERPETUAL_ARBITRAGE = "spot_perpetual_arbitrage"
    PERPETUAL_MARKET_MAKING = "perpetual_market_making"
    LIQUIDITY_MINING = "liquidity_mining"
    TWAP = "twap"
    HEDGE = "hedge"
    CROSS_EXCHANGE_MINING = "cross_exchange_mining"


@dataclass
class StrategyParameter:
    """策略参数定义"""
    name: str
    type: str  # string, number, boolean, select
    description: str
    required: bool = False
    default: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[List[str]] = None
    unit: Optional[str] = None
    validation_rules: Optional[Dict] = None


class StrategySchema:
    """策略参数模式定义"""
    
    @staticmethod
    def get_pure_market_making_schema() -> Dict[str, StrategyParameter]:
        """获取纯做市策略参数模式"""
        return {
            "exchange": StrategyParameter(
                name="exchange",
                type="select",
                description="交易所名称",
                required=True,
                options=["binance", "okx", "bybit", "gate_io", "kucoin"]
            ),
            "market": StrategyParameter(
                name="market",
                type="string",
                description="交易对 (如: BTC-USDT)",
                required=True
            ),
            "bid_spread": StrategyParameter(
                name="bid_spread",
                type="number",
                description="买单价差百分比",
                required=True,
                min_value=0.01,
                max_value=100,
                unit="%"
            ),
            "ask_spread": StrategyParameter(
                name="ask_spread",
                type="number",
                description="卖单价差百分比",
                required=True,
                min_value=0.01,
                max_value=100,
                unit="%"
            ),
            "order_amount": StrategyParameter(
                name="order_amount",
                type="number",
                description="订单数量",
                required=True,
                min_value=0.001,
                unit="base_asset"
            ),
            "order_refresh_time": StrategyParameter(
                name="order_refresh_time",
                type="number",
                description="订单刷新时间间隔",
                required=True,
                min_value=1,
                max_value=3600,
                unit="秒"
            ),
            "order_levels": StrategyParameter(
                name="order_levels",
                type="number",
                description="订单层级数量",
                default=1,
                min_value=1,
                max_value=10
            ),
            "minimum_spread": StrategyParameter(
                name="minimum_spread",
                type="number",
                description="最小价差",
                default=-100,
                min_value=-100,
                max_value=100,
                unit="%"
            ),
            "price_ceiling": StrategyParameter(
                name="price_ceiling",
                type="number",
                description="价格上限 (-1表示禁用)",
                default=-1
            ),
            "price_floor": StrategyParameter(
                name="price_floor",
                type="number",
                description="价格下限 (-1表示禁用)",
                default=-1
            ),
            "ping_pong_enabled": StrategyParameter(
                name="ping_pong_enabled",
                type="boolean",
                description="启用乒乓模式",
                default=False
            ),
            "inventory_skew_enabled": StrategyParameter(
                name="inventory_skew_enabled",
                type="boolean",
                description="启用库存倾斜",
                default=False
            ),
            "order_optimization_enabled": StrategyParameter(
                name="order_optimization_enabled",
                type="boolean",
                description="启用订单优化",
                default=False
            )
        }
    
    @staticmethod
    def get_avellaneda_market_making_schema() -> Dict[str, StrategyParameter]:
        """获取 Avellaneda 做市策略参数模式"""
        return {
            "exchange": StrategyParameter(
                name="exchange",
                type="select",
                description="交易所名称",
                required=True,
                options=["binance", "okx", "bybit", "gate_io", "kucoin"]
            ),
            "market": StrategyParameter(
                name="market",
                type="string",
                description="交易对 (如: BTC-USDT)",
                required=True
            ),
            "order_amount": StrategyParameter(
                name="order_amount",
                type="number",
                description="订单数量",
                required=True,
                min_value=0.001,
                unit="base_asset"
            ),
            "risk_factor": StrategyParameter(
                name="risk_factor",
                type="number",
                description="风险因子 (γ)",
                default=1.0,
                min_value=0.1,
                max_value=10.0
            ),
            "order_amount_shape_factor": StrategyParameter(
                name="order_amount_shape_factor",
                type="number",
                description="订单数量形状因子 (η)",
                default=0.0,
                min_value=0.0,
                max_value=1.0
            ),
            "min_spread": StrategyParameter(
                name="min_spread",
                type="number",
                description="最小价差",
                default=0.0,
                min_value=0.0,
                unit="%"
            ),
            "order_refresh_time": StrategyParameter(
                name="order_refresh_time",
                type="number",
                description="订单刷新时间间隔",
                required=True,
                min_value=1,
                max_value=3600,
                unit="秒"
            ),
            "inventory_target_base_pct": StrategyParameter(
                name="inventory_target_base_pct",
                type="number",
                description="基础资产库存目标百分比",
                default=50.0,
                min_value=0.0,
                max_value=100.0,
                unit="%"
            ),
            "volatility_buffer_size": StrategyParameter(
                name="volatility_buffer_size",
                type="number",
                description="波动率缓冲区大小",
                default=200,
                min_value=1,
                max_value=10000
            )
        }
    
    @staticmethod
    def get_cross_exchange_arbitrage_schema() -> Dict[str, StrategyParameter]:
        """获取跨交易所套利策略参数模式"""
        return {
            "exchange_1": StrategyParameter(
                name="exchange_1",
                type="select",
                description="交易所1",
                required=True,
                options=["binance", "okx", "bybit", "gate_io", "kucoin"]
            ),
            "exchange_2": StrategyParameter(
                name="exchange_2",
                type="select",
                description="交易所2",
                required=True,
                options=["binance", "okx", "bybit", "gate_io", "kucoin"]
            ),
            "market": StrategyParameter(
                name="market",
                type="string",
                description="交易对 (如: BTC-USDT)",
                required=True
            ),
            "min_profitability": StrategyParameter(
                name="min_profitability",
                type="number",
                description="最小盈利百分比",
                required=True,
                min_value=0.01,
                max_value=100,
                unit="%"
            ),
            "order_amount": StrategyParameter(
                name="order_amount",
                type="number",
                description="订单数量",
                required=True,
                min_value=0.001,
                unit="base_asset"
            ),
            "adjust_order_enabled": StrategyParameter(
                name="adjust_order_enabled",
                type="boolean",
                description="启用订单调整",
                default=True
            )
        }
    
    @staticmethod
    def get_strategy_schema(strategy_type: str) -> Dict[str, StrategyParameter]:
        """根据策略类型获取参数模式"""
        schema_map = {
            StrategyType.PURE_MARKET_MAKING.value: StrategySchema.get_pure_market_making_schema,
            StrategyType.AVELLANEDA_MARKET_MAKING.value: StrategySchema.get_avellaneda_market_making_schema,
            StrategyType.CROSS_EXCHANGE_MARKET_MAKING.value: StrategySchema.get_cross_exchange_arbitrage_schema,
        }
        
        if strategy_type in schema_map:
            return schema_map[strategy_type]()
        else:
            raise ValueError(f"Unsupported strategy type: {strategy_type}")


class ParameterValidator:
    """参数验证器"""
    
    @staticmethod
    def validate_parameters(params: Dict[str, Any], schema: Dict[str, StrategyParameter]) -> Dict[str, Any]:
        """验证策略参数"""
        validated_params = {}
        errors = []
        
        for param_name, param_def in schema.items():
            value = params.get(param_name, param_def.default)
            
            # 检查必需参数
            if param_def.required and value is None:
                errors.append(f"Parameter '{param_name}' is required")
                continue
            
            # 类型验证
            if value is not None:
                try:
                    if param_def.type == "number":
                        value = float(value)
                        if param_def.min_value is not None and value < param_def.min_value:
                            errors.append(f"Parameter '{param_name}' must be >= {param_def.min_value}")
                        if param_def.max_value is not None and value > param_def.max_value:
                            errors.append(f"Parameter '{param_name}' must be <= {param_def.max_value}")
                    elif param_def.type == "boolean":
                        if isinstance(value, str):
                            value = value.lower() in ['true', '1', 'yes', 'on']
                        else:
                            value = bool(value)
                    elif param_def.type == "select":
                        if param_def.options and value not in param_def.options:
                            errors.append(f"Parameter '{param_name}' must be one of {param_def.options}")
                    
                    validated_params[param_name] = value
                except (ValueError, TypeError) as e:
                    errors.append(f"Invalid value for parameter '{param_name}': {e}")
        
        if errors:
            raise ValueError(f"Parameter validation failed: {'; '.join(errors)}")
        
        return validated_params


class HummingbotAPIClient:
    """Hummingbot API 客户端"""
    
    def __init__(self, base_url: str = HUMMINGBOT_API_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """发送 API 请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_strategies(self) -> List[Dict]:
        """获取可用策略列表"""
        return self._make_request('GET', '/strategies')
    
    def start_strategy(self, strategy_id: str, strategy_config: Dict) -> Dict:
        """启动策略"""
        return self._make_request('POST', f'/strategies/{strategy_id}/start', strategy_config)
    
    def stop_strategy(self, strategy_id: str) -> Dict:
        """停止策略"""
        return self._make_request('POST', f'/strategies/{strategy_id}/stop')
    
    def get_strategy_status(self, strategy_id: str) -> Dict:
        """获取策略状态"""
        return self._make_request('GET', f'/strategies/{strategy_id}/status')


class HummingbotStrategyExecutor:
    """Hummingbot 策略执行器"""
    
    def __init__(self):
        self.active_strategies: Dict[str, Any] = {}
        self.api_client = HummingbotAPIClient()
        self.logger = logging.getLogger(__name__)
    
    async def start_strategy(self, strategy_id: str, strategy_type: str, params: Dict[str, Any]) -> bool:
        """启动策略"""
        try:
            # 获取策略参数模式
            schema = StrategySchema.get_strategy_schema(strategy_type)
            
            # 验证参数
            validated_params = ParameterValidator.validate_parameters(params, schema)
            
            # 创建策略配置
            strategy_config = {
                "type": strategy_type,
                "params": validated_params
            }
            
            # 通过 API 启动策略
            result = self.api_client.start_strategy(strategy_id, strategy_config)
            
            if result.get("success", False):
                self.active_strategies[strategy_id] = {
                    "type": strategy_type,
                    "params": validated_params,
                    "status": "running"
                }
                
                self.logger.info(f"Strategy {strategy_id} started successfully")
                return True
            else:
                self.logger.error(f"Failed to start strategy {strategy_id}: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting strategy {strategy_id}: {e}")
            return False
    
    async def stop_strategy(self, strategy_id: str) -> bool:
        """停止策略"""
        try:
            result = self.api_client.stop_strategy(strategy_id)
            
            if result.get("success", False):
                if strategy_id in self.active_strategies:
                    del self.active_strategies[strategy_id]
                
                self.logger.info(f"Strategy {strategy_id} stopped successfully")
                return True
            else:
                self.logger.warning(f"Strategy {strategy_id} not found or already stopped")
                return False
                
        except Exception as e:
            self.logger.error(f"Error stopping strategy {strategy_id}: {e}")
            return False
    
    async def get_strategy_status(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """获取策略状态"""
        try:
            result = self.api_client.get_strategy_status(strategy_id)
            
            if result.get("success", False):
                return {
                    "id": strategy_id,
                    "status": result.get("data", {}).get("status", "unknown"),
                    "type": result.get("data", {}).get("type"),
                    "params": result.get("data", {}).get("params", {})
                }
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting strategy status {strategy_id}: {e}")
            return None


# 全局策略执行器实例
strategy_executor = HummingbotStrategyExecutor()


def get_available_strategies() -> List[Dict[str, Any]]:
    """获取可用的策略列表"""
    return [
        {
            "type": StrategyType.PURE_MARKET_MAKING.value,
            "name": "纯做市策略",
            "description": "在单一交易所进行做市交易",
            "category": "market_making"
        },
        {
            "type": StrategyType.AVELLANEDA_MARKET_MAKING.value,
            "name": "Avellaneda 做市策略",
            "description": "基于 Avellaneda-Stoikov 模型的做市策略",
            "category": "market_making"
        },
        {
            "type": StrategyType.CROSS_EXCHANGE_MARKET_MAKING.value,
            "name": "跨交易所做市策略",
            "description": "在多个交易所之间进行做市交易",
            "category": "market_making"
        },
        {
            "type": StrategyType.AMM_ARB.value,
            "name": "AMM 套利策略",
            "description": "在 AMM 和交易所之间进行套利",
            "category": "arbitrage"
        },
        {
            "type": StrategyType.SPOT_PERPETUAL_ARBITRAGE.value,
            "name": "现货永续套利策略",
            "description": "在现货和永续合约之间进行套利",
            "category": "arbitrage"
        }
    ]


def get_strategy_schema(strategy_type: str) -> Dict[str, Any]:
    """获取策略参数模式（转换为前端友好的格式）"""
    try:
        schema = StrategySchema.get_strategy_schema(strategy_type)
        return {
            name: {
                "name": param.name,
                "type": param.type,
                "description": param.description,
                "required": param.required,
                "default": param.default,
                "min_value": param.min_value,
                "max_value": param.max_value,
                "options": param.options,
                "unit": param.unit
            }
            for name, param in schema.items()
        }
    except ValueError as e:
        return {"error": str(e)} 