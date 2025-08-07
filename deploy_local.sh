#!/bin/bash

# 本地部署脚本 - 不依赖 Docker

set -e

echo "🚀 Arbitrage System 本地部署"
echo "============================"

# 检查必要的工具
echo "🔍 检查环境..."

# 检查 Python
if ! command -v python3 > /dev/null 2>&1; then
    echo "❌ Python3 未安装"
    exit 1
fi
echo "✅ Python3 已安装: $(python3 --version)"

# 检查 Node.js
if ! command -v node > /dev/null 2>&1; then
    echo "❌ Node.js 未安装"
    exit 1
fi
echo "✅ Node.js 已安装: $(node --version)"

# 检查 npm
if ! command -v npm > /dev/null 2>&1; then
    echo "❌ npm 未安装"
    exit 1
fi
echo "✅ npm 已安装: $(npm --version)"

# 检查项目结构
echo ""
echo "📁 检查项目结构..."
if [ ! -d "front_demo" ]; then
    echo "❌ front_demo 目录不存在"
    exit 1
fi
if [ ! -d "backend" ]; then
    echo "❌ backend 目录不存在"
    exit 1
fi
echo "✅ 项目结构完整"

# 停止现有服务
echo ""
echo "🛑 停止现有服务..."
pkill -f "uvicorn main:app" || true
pkill -f "npm start" || true
echo "✅ 已停止现有服务"

# 启动后端服务
echo ""
echo "⚙️ 启动后端服务..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装 Python 依赖..."
pip install -r requirements.txt

# 初始化数据库
echo "🗄️ 初始化数据库..."
python3 init_db.py

# 启动后端服务
echo "🚀 启动后端服务..."
python3 -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 测试后端服务
if curl -s http://localhost:8000/api/overview > /dev/null; then
    echo "✅ 后端服务测试成功"
else
    echo "❌ 后端服务测试失败"
    exit 1
fi

# 启动前端服务
echo ""
echo "🎨 启动前端服务..."
cd ../front_demo

# 安装依赖
echo "📦 安装前端依赖..."
npm install

# 启动前端服务
echo "🚀 启动前端服务..."
npm start &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

# 等待前端启动
sleep 5

# 测试前端服务
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ 前端服务测试成功"
else
    echo "❌ 前端服务测试失败"
    exit 1
fi

# 保存进程 ID
echo $BACKEND_PID > ../backend.pid
echo $FRONTEND_PID > ../frontend.pid

echo ""
echo "🎉 部署完成！"
echo "============="
echo ""
echo "🌐 服务访问地址:"
echo "   前端: http://localhost:3000"
echo "   后端 API: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "📊 服务状态:"
echo "   后端服务 PID: $BACKEND_PID"
echo "   前端服务 PID: $FRONTEND_PID"
echo ""
echo "🔧 管理命令:"
echo "   停止服务: ./stop_local.sh"
echo "   查看日志: tail -f backend/logs/app.log"
echo "   重启后端: kill $BACKEND_PID && cd backend && source venv/bin/activate && python3 -m uvicorn main:app --reload --port 8000 &"
echo "   重启前端: kill $FRONTEND_PID && cd front_demo && npm start &"
echo ""
echo "⚠️  注意事项:"
echo "   - 这是本地开发模式，不包含 Hummingbot 策略执行"
echo "   - 策略管理功能可以正常使用，但策略不会真正执行"
echo "   - 如需完整功能，请解决 Docker 网络问题后使用容器化部署" 