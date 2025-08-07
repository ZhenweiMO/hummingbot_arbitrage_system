#!/bin/bash

# 简化部署脚本 - 只部署后端服务

set -e

echo "🚀 开始部署后端服务..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down --remove-orphans

# 只构建后端
echo "🔨 构建后端镜像..."
docker-compose build backend

# 启动后端服务
echo "🚀 启动后端服务..."
docker-compose up -d backend

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

echo "✅ 后端部署完成！"
echo ""
echo "🌐 服务访问地址："
echo "  后端 API: http://localhost:8000"
echo ""
echo "📊 查看日志："
echo "  docker-compose logs -f backend" 