#!/bin/bash

# Arbitrage System 容器化部署脚本
# 一键启动前端、后端和 Hummingbot 服务

set -e

echo "🚀 开始部署 Arbitrage System..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查必要的目录是否存在
echo "📁 检查项目结构..."
if [ ! -d "front_demo" ]; then
    echo "❌ front_demo 目录不存在"
    exit 1
fi

if [ ! -d "backend" ]; then
    echo "❌ backend 目录不存在"
    exit 1
fi

if [ ! -d "hummingbot" ]; then
    echo "❌ hummingbot 目录不存在"
    exit 1
fi

# 创建必要的目录
echo "📂 创建必要的目录..."
mkdir -p hummingbot/conf/connectors
mkdir -p hummingbot/conf/strategies
mkdir -p hummingbot/conf/controllers
mkdir -p hummingbot/conf/scripts
mkdir -p hummingbot/logs
mkdir -p hummingbot/data
mkdir -p hummingbot/certs

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down --remove-orphans

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 初始化数据库
echo "🗄️ 初始化数据库..."
docker-compose exec backend python3 init_db.py

echo "✅ 部署完成！"
echo ""
echo "🌐 服务访问地址："
echo "  前端: http://localhost:3000"
echo "  后端 API: http://localhost:8000"
echo "  Hummingbot API: http://localhost:15888"
echo "  Gateway: http://localhost:8080"
echo ""
echo "📊 查看日志："
echo "  docker-compose logs -f"
echo ""
echo "🛑 停止服务："
echo "  docker-compose down"
echo ""
echo "🔄 重启服务："
echo "  docker-compose restart" 