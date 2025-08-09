#!/bin/bash

set -e

echo "🚀 开始生产环境部署..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查必要的文件
check_requirements() {
    echo -e "${BLUE}📋 检查部署要求...${NC}"
    
    if [ ! -f "docker-compose.production.yml" ]; then
        echo -e "${RED}❌ docker-compose.production.yml 文件不存在${NC}"
        exit 1
    fi
    
    if [ ! -f "production.env" ]; then
        echo -e "${RED}❌ production.env 文件不存在${NC}"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker 未安装${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose 未安装${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 所有要求检查通过${NC}"
}

# 环境变量检查
check_env_vars() {
    echo -e "${BLUE}🔐 检查环境变量...${NC}"
    
    if grep -q "your-super-secret-key-change-this-in-production" production.env; then
        echo -e "${YELLOW}⚠️  警告: 请在生产环境中修改默认的 SECRET_KEY${NC}"
    fi
    
    if grep -q "secure-production-password-123" production.env; then
        echo -e "${YELLOW}⚠️  警告: 请在生产环境中修改默认的密码${NC}"
    fi
    
    echo -e "${GREEN}✅ 环境变量检查完成${NC}"
}

# 创建必要的目录
create_directories() {
    echo -e "${BLUE}📁 创建必要的目录...${NC}"
    
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p logs
    mkdir -p backups
    
    echo -e "${GREEN}✅ 目录创建完成${NC}"
}

# 备份现有数据
backup_data() {
    echo -e "${BLUE}💾 备份现有数据...${NC}"
    
    if [ -f "backend/arbitrage_system.db" ]; then
        timestamp=$(date +%Y%m%d_%H%M%S)
        cp backend/arbitrage_system.db "backups/arbitrage_system_${timestamp}.db"
        echo -e "${GREEN}✅ 数据库已备份到 backups/arbitrage_system_${timestamp}.db${NC}"
    fi
}

# 构建镜像
build_images() {
    echo -e "${BLUE}🔨 构建 Docker 镜像...${NC}"
    
    # 停止现有服务
    echo "停止现有服务..."
    docker-compose -f docker-compose.simple.yml down --remove-orphans 2>/dev/null || true
    
    # 构建生产镜像
    echo "构建生产镜像..."
    docker-compose -f docker-compose.production.yml build --no-cache
    
    echo -e "${GREEN}✅ 镜像构建完成${NC}"
}

# 启动服务
start_services() {
    echo -e "${BLUE}🚀 启动生产服务...${NC}"
    
    # 加载环境变量并启动服务
    docker-compose -f docker-compose.production.yml --env-file production.env up -d
    
    echo -e "${GREEN}✅ 服务启动完成${NC}"
}

# 健康检查
health_check() {
    echo -e "${BLUE}🏥 执行健康检查...${NC}"
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    services=("arbitrage-frontend-prod" "arbitrage-backend-prod" "arbitrage-hummingbot-prod" "arbitrage-redis-prod")
    
    for service in "${services[@]}"; do
        if docker ps --filter "name=$service" --filter "status=running" --quiet | grep -q .; then
            echo -e "${GREEN}✅ $service 运行正常${NC}"
        else
            echo -e "${RED}❌ $service 运行异常${NC}"
            docker logs "$service" --tail 20
        fi
    done
    
    # API 健康检查
    echo "检查 API 健康状态..."
    for i in {1..10}; do
        if curl -f -s http://localhost:8000/api/overview > /dev/null; then
            echo -e "${GREEN}✅ 后端 API 响应正常${NC}"
            break
        else
            echo "等待 API 响应... (尝试 $i/10)"
            sleep 5
        fi
    done
    
    # 前端健康检查
    echo "检查前端服务..."
    if curl -f -s http://localhost > /dev/null; then
        echo -e "${GREEN}✅ 前端服务响应正常${NC}"
    else
        echo -e "${YELLOW}⚠️  前端服务可能需要更多时间启动${NC}"
    fi
}

# 显示部署信息
show_deployment_info() {
    echo -e "${BLUE}📊 部署信息${NC}"
    echo "=================================="
    echo -e "${GREEN}🌐 前端服务: http://localhost${NC}"
    echo -e "${GREEN}🔗 后端 API: http://localhost:8000${NC}"
    echo -e "${GREEN}📖 API 文档: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}🤖 Hummingbot: http://localhost:15888${NC}"
    echo -e "${GREEN}📊 监控面板: http://localhost:3001${NC}"
    echo -e "${GREEN}📈 Prometheus: http://localhost:9090${NC}"
    echo "=================================="
    echo ""
    echo -e "${YELLOW}💡 提示:${NC}"
    echo "- 查看服务状态: docker-compose -f docker-compose.production.yml ps"
    echo "- 查看日志: docker-compose -f docker-compose.production.yml logs [service_name]"
    echo "- 停止服务: docker-compose -f docker-compose.production.yml down"
}

# 主函数
main() {
    echo -e "${GREEN}🚀 Arbitrage System 生产环境部署脚本${NC}"
    echo "=================================================="
    
    check_requirements
    check_env_vars
    create_directories
    backup_data
    build_images
    start_services
    health_check
    show_deployment_info
    
    echo -e "${GREEN}🎉 生产环境部署完成！${NC}"
}

# 错误处理
trap 'echo -e "${RED}❌ 部署过程中发生错误${NC}"; exit 1' ERR

# 检查是否以 root 权限运行 (可选)
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}⚠️  警告: 正在以 root 权限运行${NC}"
fi

# 执行主函数
main "$@"

