#!/bin/bash

# 停止本地服务脚本

echo "🛑 停止 Arbitrage System 本地服务"
echo "================================"

# 停止后端服务
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "🛑 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "✅ 后端服务已停止"
    else
        echo "⚠️  后端服务进程不存在"
    fi
    rm -f backend.pid
else
    echo "⚠️  未找到后端服务 PID 文件"
fi

# 停止前端服务
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "🛑 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  前端服务进程不存在"
    fi
    rm -f frontend.pid
else
    echo "⚠️  未找到前端服务 PID 文件"
fi

# 强制停止相关进程
echo "🧹 清理相关进程..."
pkill -f "uvicorn main:app" || true
pkill -f "npm start" || true
pkill -f "react-scripts" || true

echo "✅ 所有服务已停止" 