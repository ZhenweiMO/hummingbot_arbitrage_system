# 🛠️ 脚本工具

本目录包含项目的部署脚本和工具脚本，用于自动化各种操作任务。

## 📁 目录结构

```
scripts/
├── deployment/           # 部署相关脚本
│   └── deploy_production.sh
└── utils/               # 工具脚本
    ├── create_password_verification.py
    └── stop_local.sh
```

## 🚀 部署脚本 (`deployment/`)

### `deploy_production.sh`
**功能**: 自动化生产环境部署脚本

**特性**:
- ✅ 自动环境检查
- ✅ 依赖项验证
- ✅ 镜像构建和部署
- ✅ 健康检查
- ✅ 部署状态报告

**使用方法**:
```bash
# 赋予执行权限
chmod +x scripts/deployment/deploy_production.sh

# 执行部署
./scripts/deployment/deploy_production.sh
```

**部署流程**:
1. 检查 Docker 环境
2. 验证配置文件
3. 备份现有数据
4. 构建镜像
5. 启动服务
6. 健康检查
7. 显示部署信息

**输出示例**:
```
🚀 开始生产环境部署...
📋 检查部署要求...
✅ 所有要求检查通过
🔐 检查环境变量...
✅ 环境变量检查完成
...
🎉 生产环境部署完成！
```

## 🔧 工具脚本 (`utils/`)

### `create_password_verification.py`
**功能**: 为 Hummingbot 创建密码验证文件

**用途**:
- 生成 Hummingbot 所需的 `.password_verification` 文件
- 支持自定义密码配置
- 适用于 Docker 容器环境

**使用方法**:
```bash
# 直接运行（使用默认密码）
python scripts/utils/create_password_verification.py

# 在 Docker 容器中运行
docker run --rm -v ./hummingbot/conf:/app/conf python:3.9-slim python -c "
import os, hashlib
password = 'your-password'
hashed = hashlib.sha256(password.encode()).hexdigest()
with open('/app/conf/.password_verification', 'w') as f:
    f.write(hashed)
"
```

### `stop_local.sh`
**功能**: 停止本地开发环境服务

**用途**:
- 快速停止所有开发环境容器
- 清理临时资源
- 重置开发环境

**使用方法**:
```bash
# 赋予执行权限
chmod +x scripts/utils/stop_local.sh

# 停止服务
./scripts/utils/stop_local.sh
```

## 📋 脚本使用指南

### 开发环境管理
```bash
# 启动开发环境
docker-compose -f docker-compose.simple.yml up -d

# 停止开发环境
./scripts/utils/stop_local.sh

# 重启开发环境
./scripts/utils/stop_local.sh && docker-compose -f docker-compose.simple.yml up -d
```

### 生产环境管理
```bash
# 首次部署
./scripts/deployment/deploy_production.sh

# 更新部署
docker-compose -f docker-compose.production.yml pull
./scripts/deployment/deploy_production.sh

# 停止生产环境
docker-compose -f docker-compose.production.yml down
```

### 密码管理
```bash
# 生成新的密码验证文件
python scripts/utils/create_password_verification.py

# 验证密码文件
ls -la hummingbot/conf/.password_verification
```

## 🔒 安全考虑

### 脚本权限
```bash
# 设置正确的执行权限
chmod +x scripts/deployment/*.sh
chmod +x scripts/utils/*.sh

# 设置 Python 脚本权限
chmod +r scripts/utils/*.py
```

### 敏感信息处理
- ❌ 不要在脚本中硬编码密码
- ✅ 使用环境变量或配置文件
- ✅ 确保脚本输出不包含敏感信息

### 执行环境
- ✅ 在隔离环境中测试脚本
- ✅ 验证脚本的幂等性
- ✅ 准备回滚方案

## 🛠️ 自定义脚本

### 创建新脚本
1. 选择合适的目录（`deployment/` 或 `utils/`）
2. 创建脚本文件
3. 添加执行权限
4. 更新此 README 文档

### 脚本模板
```bash
#!/bin/bash

set -e  # 遇到错误时退出

echo "🚀 脚本开始执行..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 错误处理
trap 'echo -e "${RED}❌ 脚本执行失败${NC}"; exit 1' ERR

# 主要逻辑
main() {
    echo -e "${GREEN}✅ 脚本执行成功${NC}"
}

# 执行主函数
main "$@"
```

## 📊 脚本监控

### 执行日志
```bash
# 查看部署日志
tail -f /var/log/deployment.log

# 查看脚本执行历史
grep "deploy_production" /var/log/auth.log
```

### 性能监控
```bash
# 监控脚本执行时间
time ./scripts/deployment/deploy_production.sh

# 监控资源使用
top -p $(pgrep -f deploy_production)
```

## 🔄 脚本维护

### 定期检查
- [ ] 脚本功能正常
- [ ] 依赖项可用
- [ ] 权限设置正确
- [ ] 文档保持更新

### 版本管理
- 使用 Git 管理脚本版本
- 记录重要变更
- 保留历史版本备份

### 测试策略
```bash
# 在测试环境验证
export ENVIRONMENT=test
./scripts/deployment/deploy_production.sh

# 干运行测试
DRY_RUN=true ./scripts/deployment/deploy_production.sh
```

---

**💡 提示**: 在执行任何脚本前，建议先在测试环境中验证其功能和安全性。
