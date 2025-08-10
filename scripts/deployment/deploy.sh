#!/bin/bash

# 部署脚本 - 支持多环境部署
# 用法: ./deploy.sh [environment] [version]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认参数
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境
check_environment() {
    log_info "检查部署环境..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 检查 compose 文件
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Compose 文件不存在: $COMPOSE_FILE"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 备份当前版本
backup_current() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "备份当前版本..."
        
        # 创建备份目录
        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # 备份数据库
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "backend"; then
            docker-compose -f "$COMPOSE_FILE" exec -T backend sqlite3 data/arbitrage_system.db ".backup $BACKUP_DIR/database.db"
            log_success "数据库已备份到 $BACKUP_DIR/database.db"
        fi
        
        # 备份配置文件
        cp "$COMPOSE_FILE" "$BACKUP_DIR/"
        cp -r configs/ "$BACKUP_DIR/" 2>/dev/null || true
        
        log_success "备份完成: $BACKUP_DIR"
    fi
}

# 拉取最新代码
pull_latest_code() {
    log_info "拉取最新代码..."
    
    # 检查 Git 状态
    if [ -d ".git" ]; then
        git fetch origin
        git checkout main
        git pull origin main
        
        # 如果指定了版本，切换到对应标签
        if [ "$VERSION" != "latest" ]; then
            git checkout "$VERSION"
        fi
        
        log_success "代码更新完成"
    else
        log_warning "非 Git 仓库，跳过代码更新"
    fi
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    # 构建所有服务
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    log_success "镜像构建完成"
}

# 部署服务
deploy_services() {
    log_info "部署服务到 $ENVIRONMENT 环境..."
    
    # 停止现有服务
    docker-compose -f "$COMPOSE_FILE" down
    
    # 启动新服务
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_success "服务部署完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务启动
    sleep 10
    
    # 检查服务状态
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log_success "所有服务运行正常"
    else
        log_error "部分服务启动失败"
        docker-compose -f "$COMPOSE_FILE" ps
        exit 1
    fi
    
    # 检查 API 健康状态
    if [ "$ENVIRONMENT" = "production" ]; then
        if curl -f -s http://localhost:8001/api/overview > /dev/null; then
            log_success "API 健康检查通过"
        else
            log_error "API 健康检查失败"
            exit 1
        fi
    fi
}

# 回滚函数
rollback() {
    log_warning "开始回滚..."
    
    # 停止当前服务
    docker-compose -f "$COMPOSE_FILE" down
    
    # 恢复备份
    if [ -d "backups" ]; then
        LATEST_BACKUP=$(ls -t backups/ | head -1)
        if [ -n "$LATEST_BACKUP" ]; then
            log_info "恢复备份: $LATEST_BACKUP"
            
            # 恢复数据库
            if [ -f "backups/$LATEST_BACKUP/database.db" ]; then
                docker-compose -f "$COMPOSE_FILE" up -d backend
                sleep 5
                docker-compose -f "$COMPOSE_FILE" exec -T backend sqlite3 data/arbitrage_system.db ".restore backups/$LATEST_BACKUP/database.db"
            fi
            
            # 恢复配置文件
            if [ -f "backups/$LATEST_BACKUP/$COMPOSE_FILE" ]; then
                cp "backups/$LATEST_BACKUP/$COMPOSE_FILE" .
            fi
            
            # 重新部署
            docker-compose -f "$COMPOSE_FILE" up -d
            log_success "回滚完成"
        else
            log_error "没有找到可用的备份"
            exit 1
        fi
    else
        log_error "没有备份目录"
        exit 1
    fi
}

# 清理函数
cleanup() {
    log_info "清理旧镜像..."
    
    # 删除未使用的镜像
    docker image prune -f
    
    # 删除未使用的容器
    docker container prune -f
    
    log_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [environment] [version]"
    echo ""
    echo "参数:"
    echo "  environment    部署环境 (development|staging|production) [默认: production]"
    echo "  version        版本号或标签 [默认: latest]"
    echo ""
    echo "示例:"
    echo "  $0 production v1.1.0"
    echo "  $0 staging"
    echo "  $0 development latest"
    echo ""
    echo "特殊命令:"
    echo "  $0 rollback    回滚到上一个版本"
    echo "  $0 cleanup     清理 Docker 资源"
}

# 主函数
main() {
    case "$1" in
        "rollback")
            rollback
            exit 0
            ;;
        "cleanup")
            cleanup
            exit 0
            ;;
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
    esac
    
    log_info "开始部署到 $ENVIRONMENT 环境，版本: $VERSION"
    
    # 执行部署步骤
    check_environment
    backup_current
    pull_latest_code
    build_images
    deploy_services
    health_check
    cleanup
    
    log_success "部署完成！"
    
    # 显示访问信息
    case "$ENVIRONMENT" in
        "production")
            echo ""
            echo "🌐 访问地址:"
            echo "  前端: http://localhost:9091"
            echo "  后端 API: http://localhost:8001"
            echo "  API 文档: http://localhost:8001/docs"
            echo "  监控面板: http://localhost:3001"
            ;;
        "staging")
            echo ""
            echo "🌐 访问地址:"
            echo "  前端: http://localhost:9092"
            echo "  后端 API: http://localhost:8002"
            echo "  API 文档: http://localhost:8002/docs"
            ;;
        "development")
            echo ""
            echo "🌐 访问地址:"
            echo "  前端: http://localhost:3000"
            echo "  后端 API: http://localhost:8000"
            echo "  API 文档: http://localhost:8000/docs"
            ;;
    esac
}

# 执行主函数
main "$@"
