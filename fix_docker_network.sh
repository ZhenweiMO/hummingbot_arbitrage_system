#!/bin/bash

# Docker 网络问题解决脚本

set -e

echo "🔧 解决 Docker Hub 网络连接问题"
echo "================================"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

echo "✅ Docker 正在运行"

# 方案 1: 尝试使用不同的镜像源
echo ""
echo "🌐 方案 1: 测试不同的镜像源..."

# 测试阿里云镜像源
echo "测试阿里云镜像源..."
if docker pull registry.cn-hangzhou.aliyuncs.com/library/python:3.10-slim > /dev/null 2>&1; then
    echo "✅ 阿里云镜像源可用"
    ALIYUN_AVAILABLE=true
else
    echo "❌ 阿里云镜像源不可用"
    ALIYUN_AVAILABLE=false
fi

# 测试腾讯云镜像源
echo "测试腾讯云镜像源..."
if docker pull ccr.ccs.tencentyun.com/library/python:3.10-slim > /dev/null 2>&1; then
    echo "✅ 腾讯云镜像源可用"
    TENCENT_AVAILABLE=true
else
    echo "❌ 腾讯云镜像源不可用"
    TENCENT_AVAILABLE=false
fi

# 方案 2: 使用本地 Python 环境
echo ""
echo "🐍 方案 2: 使用本地 Python 环境..."

# 检查本地 Python 环境
if command -v python3 > /dev/null 2>&1; then
    echo "✅ 本地 Python 环境可用"
    PYTHON_VERSION=$(python3 --version)
    echo "   Python 版本: $PYTHON_VERSION"
    
    # 检查虚拟环境
    if [ -d "backend/venv" ]; then
        echo "✅ 虚拟环境存在"
        LOCAL_PYTHON_AVAILABLE=true
    else
        echo "⚠️  虚拟环境不存在，但可以使用系统 Python"
        LOCAL_PYTHON_AVAILABLE=true
    fi
else
    echo "❌ 本地 Python 环境不可用"
    LOCAL_PYTHON_AVAILABLE=false
fi

# 方案 3: 创建简化的部署方案
echo ""
echo "🚀 方案 3: 创建简化的部署方案..."

# 创建本地开发模式
cat > docker-compose.local.yml << 'EOF'
services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.local
    container_name: arbitrage-backend-local
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend_data:/app/data
      - backend_logs:/app/logs
    environment:
      - DATABASE_URL=sqlite:///./arbitrage_system.db
      - HUMMINGBOT_HOST=localhost
      - HUMMINGBOT_PORT=15888
      - DEBUG=true
    networks:
      - arbitrage-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: arbitrage-redis-local
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - arbitrage-network
    restart: unless-stopped

volumes:
  backend_data:
  backend_logs:
  redis_data:

networks:
  arbitrage-network:
    driver: bridge
EOF

echo "✅ 创建了本地开发模式配置"

# 方案 4: 提供多种解决方案
echo ""
echo "📋 解决方案总结:"
echo "================"

if [ "$ALIYUN_AVAILABLE" = true ] || [ "$TENCENT_AVAILABLE" = true ]; then
    echo "✅ 可以使用国内镜像源"
    echo "   推荐使用: ./deploy_hybrid.sh 选择完整容器化模式"
fi

if [ "$LOCAL_PYTHON_AVAILABLE" = true ]; then
    echo "✅ 可以使用本地 Python 环境"
    echo "   推荐使用: ./deploy_hybrid.sh 选择本地开发模式"
fi

echo ""
echo "🚀 推荐操作:"
echo "==========="

if [ "$LOCAL_PYTHON_AVAILABLE" = true ]; then
    echo "1. 使用本地开发模式 (推荐):"
    echo "   ./deploy_hybrid.sh"
    echo "   选择选项 1: 本地开发模式"
    echo ""
fi

if [ "$ALIYUN_AVAILABLE" = true ] || [ "$TENCENT_AVAILABLE" = true ]; then
    echo "2. 尝试完整容器化模式:"
    echo "   ./deploy_hybrid.sh"
    echo "   选择选项 2: 完整容器化模式"
    echo ""
fi

echo "3. 手动启动服务:"
echo "   后端: cd backend && source venv/bin/activate && python3 -m uvicorn main:app --reload --port 8000"
echo "   前端: cd front_demo && npm start"
echo ""

echo "4. 测试网络连接:"
echo "   curl -s --connect-timeout 5 https://registry-1.docker.io"
echo ""

echo "🔧 如果问题持续存在:"
echo "=================="
echo "1. 检查网络代理设置"
echo "2. 尝试使用 VPN"
echo "3. 联系网络管理员"
echo "4. 使用本地开发模式作为临时解决方案" 