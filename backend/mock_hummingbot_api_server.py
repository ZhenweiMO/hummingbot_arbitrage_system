#!/usr/bin/env python3
"""
模拟 Hummingbot API 服务器
"""

import asyncio
import json
import logging
from typing import Dict, Any
from aiohttp import web, ClientSession
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockHummingbotAPIServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 15888):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.running_strategies = {}
        self.setup_routes()
        
    def setup_routes(self):
        """设置 API 路由"""
        self.app.router.add_get('/strategies', self.get_strategies)
        self.app.router.add_get('/strategies/{strategy_id}', self.get_strategy)
        self.app.router.add_post('/strategies/{strategy_id}/start', self.start_strategy)
        self.app.router.add_post('/strategies/{strategy_id}/stop', self.stop_strategy)
        self.app.router.add_get('/strategies/{strategy_id}/status', self.get_strategy_status)
        self.app.router.add_get('/health', self.health_check)
        
    async def get_strategies(self, request):
        """获取策略列表"""
        strategies = [
            {
                "id": "pure_market_making",
                "name": "纯做市策略",
                "description": "在单一交易所进行做市交易",
                "category": "market_making",
                "status": "available"
            },
            {
                "id": "avellaneda_market_making", 
                "name": "Avellaneda 做市策略",
                "description": "基于 Avellaneda-Stoikov 模型的做市策略",
                "category": "market_making",
                "status": "available"
            },
            {
                "id": "cross_exchange_market_making",
                "name": "跨交易所做市策略", 
                "description": "在多个交易所之间进行做市交易",
                "category": "market_making",
                "status": "available"
            },
            {
                "id": "amm_arb",
                "name": "AMM 套利策略",
                "description": "在 AMM 和交易所之间进行套利",
                "category": "arbitrage",
                "status": "available"
            },
            {
                "id": "spot_perpetual_arbitrage",
                "name": "现货永续套利策略",
                "description": "在现货和永续合约之间进行套利", 
                "category": "arbitrage",
                "status": "available"
            }
        ]
        return web.json_response({"success": True, "data": strategies})
        
    async def get_strategy(self, request):
        """获取策略详情"""
        strategy_id = request.match_info['strategy_id']
        strategy = {
            "id": strategy_id,
            "name": f"{strategy_id} 策略",
            "description": f"{strategy_id} 策略描述",
            "category": "market_making",
            "status": "available"
        }
        return web.json_response({"success": True, "data": strategy})
        
    async def start_strategy(self, request):
        """启动策略"""
        strategy_id = request.match_info['strategy_id']
        try:
            data = await request.json()
            strategy_type = data.get('type')
            params = data.get('params', {})
            
            # 模拟策略启动
            self.running_strategies[strategy_id] = {
                "id": strategy_id,
                "type": strategy_type,
                "params": params,
                "status": "running",
                "started_at": datetime.now().isoformat(),
                "trades": [],
                "pnl": 0.0
            }
            
            logger.info(f"Strategy {strategy_id} started successfully")
            return web.json_response({
                "success": True,
                "message": f"Strategy {strategy_id} started successfully",
                "data": self.running_strategies[strategy_id]
            })
        except Exception as e:
            logger.error(f"Failed to start strategy {strategy_id}: {e}")
            return web.json_response({
                "success": False,
                "error": f"Failed to start strategy: {str(e)}"
            }, status=500)
            
    async def stop_strategy(self, request):
        """停止策略"""
        strategy_id = request.match_info['strategy_id']
        
        if strategy_id in self.running_strategies:
            strategy = self.running_strategies.pop(strategy_id)
            strategy["status"] = "stopped"
            strategy["stopped_at"] = datetime.now().isoformat()
            
            logger.info(f"Strategy {strategy_id} stopped successfully")
            return web.json_response({
                "success": True,
                "message": f"Strategy {strategy_id} stopped successfully",
                "data": strategy
            })
        else:
            return web.json_response({
                "success": False,
                "error": f"Strategy {strategy_id} not found"
            }, status=404)
            
    async def get_strategy_status(self, request):
        """获取策略状态"""
        strategy_id = request.match_info['strategy_id']
        
        if strategy_id in self.running_strategies:
            return web.json_response({
                "success": True,
                "data": self.running_strategies[strategy_id]
            })
        else:
            return web.json_response({
                "success": False,
                "error": f"Strategy {strategy_id} not found"
            }, status=404)
            
    async def health_check(self, request):
        """健康检查"""
        return web.json_response({
            "success": True,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "running_strategies": len(self.running_strategies)
        })
        
    async def start(self):
        """启动服务器"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"Mock Hummingbot API Server started on {self.host}:{self.port}")
        
        try:
            await asyncio.Future()  # 保持服务器运行
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
        finally:
            await runner.cleanup()

async def main():
    """主函数"""
    server = MockHummingbotAPIServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main()) 