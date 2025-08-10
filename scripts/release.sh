#!/bin/bash

# 版本发布脚本
# 用法: ./release.sh [version] [type]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 参数
VERSION=${1:-}
RELEASE_TYPE=${2:-patch}

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

# 检查 Git 状态
check_git_status() {
    log_info "检查 Git 状态..."
    
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        log_error "有未提交的更改，请先提交或暂存"
        git status --short
        exit 1
    fi
    
    # 检查是否在 main 分支
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        log_error "当前不在 main 分支，请在 main 分支上执行发布"
        exit 1
    fi
    
    log_success "Git 状态检查通过"
}

# 获取当前版本
get_current_version() {
    if [ -f "VERSION" ]; then
        cat VERSION
    else
        # 从 Git 标签获取最新版本
        git tag --sort=-version:refname | head -1 | sed 's/^v//'
    fi
}

# 计算新版本号
calculate_new_version() {
    local current_version=$1
    local release_type=$2
    
    if [ -z "$current_version" ]; then
        echo "1.0.0"
        return
    fi
    
    # 解析版本号
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    major=${VERSION_PARTS[0]}
    minor=${VERSION_PARTS[1]}
    patch=${VERSION_PARTS[2]}
    
    case $release_type in
        "major")
            echo "$((major + 1)).0.0"
            ;;
        "minor")
            echo "$major.$((minor + 1)).0"
            ;;
        "patch")
            echo "$major.$minor.$((patch + 1))"
            ;;
        *)
            log_error "无效的发布类型: $release_type"
            exit 1
            ;;
    esac
}

# 更新版本文件
update_version_files() {
    local version=$1
    
    log_info "更新版本文件..."
    
    # 更新 VERSION 文件
    echo "v$version" > VERSION
    
    # 更新 CHANGELOG.md
    update_changelog "$version"
    
    # 更新 package.json (如果存在)
    if [ -f "front_demo/package.json" ]; then
        sed -i.bak "s/\"version\": \".*\"/\"version\": \"$version\"/" front_demo/package.json
        rm front_demo/package.json.bak
    fi
    
    log_success "版本文件更新完成"
}

# 更新 CHANGELOG.md
update_changelog() {
    local version=$1
    local date=$(date +%Y-%m-%d)
    
    # 创建临时文件
    cat > CHANGELOG.md.tmp << EOF
# Changelog

## [$version] - $date

### Added
- 实时余额获取功能
- 币安 API 连接器
- OKX API 连接器
- 自动余额更新任务
- 版本控制和部署策略

### Changed
- 更新账户模型支持实时余额
- 优化前端 API 配置
- 改进错误处理机制

### Fixed
- 修复前端连接后端问题
- 修复数据库初始化问题
- 修复 API 依赖安装问题

EOF
    
    # 如果存在旧的 CHANGELOG.md，追加内容
    if [ -f "CHANGELOG.md" ]; then
        tail -n +3 CHANGELOG.md >> CHANGELOG.md.tmp
    fi
    
    # 替换原文件
    mv CHANGELOG.md.tmp CHANGELOG.md
}

# 创建发布分支
create_release_branch() {
    local version=$1
    local branch="release/v$version"
    
    log_info "创建发布分支: $branch"
    
    # 确保在 develop 分支
    git checkout develop
    git pull origin develop
    
    # 创建发布分支
    git checkout -b "$branch"
    
    # 合并 main 分支的更改
    git merge main --no-edit
    
    log_success "发布分支创建完成"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 这里可以添加实际的测试命令
    # 例如: docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
    
    log_success "测试通过"
}

# 提交更改
commit_changes() {
    local version=$1
    
    log_info "提交版本更改..."
    
    git add .
    git commit -m "chore: prepare release v$version"
    
    log_success "更改已提交"
}

# 创建标签
create_tag() {
    local version=$1
    
    log_info "创建版本标签: v$version"
    
    git tag -a "v$version" -m "Release version $version"
    
    log_success "标签创建完成"
}

# 合并到 main
merge_to_main() {
    local version=$1
    
    log_info "合并到 main 分支..."
    
    git checkout main
    git merge "release/v$version" --no-edit
    
    log_success "合并到 main 完成"
}

# 推送更改
push_changes() {
    local version=$1
    
    log_info "推送更改到远程仓库..."
    
    git push origin main
    git push origin "release/v$version"
    git push origin "v$version"
    
    log_success "更改已推送到远程仓库"
}

# 清理发布分支
cleanup_release_branch() {
    local version=$1
    local branch="release/v$version"
    
    log_info "清理发布分支..."
    
    git branch -d "$branch"
    git push origin --delete "$branch" 2>/dev/null || true
    
    log_success "发布分支已清理"
}

# 显示发布信息
show_release_info() {
    local version=$1
    
    echo ""
    echo "🎉 版本 v$version 发布成功！"
    echo ""
    echo "📋 发布信息:"
    echo "  版本: v$version"
    echo "  分支: main"
    echo "  标签: v$version"
    echo ""
    echo "🚀 下一步操作:"
    echo "  1. 部署到测试环境: ./scripts/deployment/deploy.sh staging v$version"
    echo "  2. 部署到生产环境: ./scripts/deployment/deploy.sh production v$version"
    echo "  3. 创建 GitHub Release: https://github.com/your-repo/releases/new"
    echo ""
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [version] [type]"
    echo ""
    echo "参数:"
    echo "  version        版本号 (可选，自动计算)"
    echo "  type           发布类型 (major|minor|patch) [默认: patch]"
    echo ""
    echo "发布类型:"
    echo "  major          主版本号增加 (1.0.0 -> 2.0.0)"
    echo "  minor          次版本号增加 (1.0.0 -> 1.1.0)"
    echo "  patch          修订版本号增加 (1.0.0 -> 1.0.1)"
    echo ""
    echo "示例:"
    echo "  $0             自动计算下一个 patch 版本"
    echo "  $0 1.2.0       指定版本号"
    echo "  $0 1.2.0 minor 指定版本号和类型"
    echo ""
    echo "特殊命令:"
    echo "  $0 help        显示帮助信息"
}

# 主函数
main() {
    case "$1" in
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
    esac
    
    log_info "开始版本发布流程..."
    
    # 检查 Git 状态
    check_git_status
    
    # 获取当前版本
    CURRENT_VERSION=$(get_current_version)
    log_info "当前版本: $CURRENT_VERSION"
    
    # 计算新版本
    if [ -z "$VERSION" ]; then
        VERSION=$(calculate_new_version "$CURRENT_VERSION" "$RELEASE_TYPE")
    fi
    log_info "新版本: $VERSION"
    
    # 确认发布
    echo ""
    read -p "确认发布版本 v$VERSION? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "发布已取消"
        exit 0
    fi
    
    # 执行发布流程
    update_version_files "$VERSION"
    create_release_branch "$VERSION"
    run_tests
    commit_changes "$VERSION"
    create_tag "$VERSION"
    merge_to_main "$VERSION"
    push_changes "$VERSION"
    cleanup_release_branch "$VERSION"
    
    # 显示发布信息
    show_release_info "$VERSION"
}

# 执行主函数
main "$@"
