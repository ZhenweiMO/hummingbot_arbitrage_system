#!/bin/bash

# 混合部署脚本 - 支持本地开发和容器化部署

set -e

echo "🚀 Arbitrage System 混合部署脚本"
echo "请选择部署模式："
echo "1) 本地开发模式 (前端本地 + 后端容器 + Redis容器)"
echo "2) 完整容器化模式 (所有服务容器化)"
echo "3) 仅后端容器化"
echo "4) 退出"

read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "🔧 启动本地开发模式..."
        
        # 检查 Docker
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker 未安装"
            exit 1
        fi
        
        # 停止现有容器
        docker-compose -f docker-compose.dev.yml down --remove-orphans
        
        # 构建后端
        echo "🔨 构建后端容器..."
        docker-compose -f docker-compose.dev.yml build backend
        
        # 启动后端和Redis
        echo "🚀 启动后端和Redis服务..."
        docker-compose -f docker-compose.dev.yml up -d
        
        # 等待服务启动
        sleep 5
        
        # 初始化数据库
        echo "🗄️ 初始化数据库..."
        docker-compose -f docker-compose.dev.yml exec backend python3 init_db.py
        
        echo "✅ 本地开发模式启动完成！"
        echo ""
        echo "🌐 服务访问地址："
        echo "  后端 API: http://localhost:8000"
        echo "  Redis: localhost:6379"
        echo ""
        echo "📝 前端启动命令："
        echo "  cd front_demo && npm start"
        echo ""
        echo "📊 查看后端日志："
        echo "  docker-compose -f docker-compose.dev.yml logs -f backend"
        ;;
        
    2)
        echo "🐳 启动完整容器化模式..."
        
        # 检查项目结构
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
        mkdir -p hummingbot/conf/connectors hummingbot/conf/strategies hummingbot/conf/controllers hummingbot/conf/scripts hummingbot/logs hummingbot/data hummingbot/certs
        
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
        
        echo "✅ 完整容器化模式启动完成！"
        echo ""
        echo "🌐 服务访问地址："
        echo "  前端: http://localhost:3000"
        echo "  后端 API: http://localhost:8000"
        echo "  Hummingbot API: http://localhost:15888"
        echo "  Gateway: http://localhost:8080"
        echo "  Redis: localhost:6379"
        echo ""
        echo "📊 查看服务日志："
        echo "  docker-compose logs -f"
        ;;
        
    3)
        echo "🔧 启动仅后端容器化模式..."
        
        # 使用后端部署脚本
        ./deploy_backend.sh
        ;;
        
    4)
        echo "👋 退出部署"
        exit 0
        ;;
        
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac 