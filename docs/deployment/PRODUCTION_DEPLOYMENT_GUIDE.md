# 🚀 生产环境部署指南

## 📋 部署概述

本文档详细说明了 Arbitrage System 生产环境的部署流程、配置要求和运维指南。

## ✅ 部署测试结果

### 测试状态 (2025-08-08)
- **整体成功率**: 91.6% (11/12 项测试通过)
- **核心功能**: ✅ 全部正常
- **服务健康**: ✅ 所有容器运行正常
- **API 响应**: ✅ 所有端点正常响应
- **策略生命周期**: ✅ 启动/停止/状态查询正常

### 服务状态
| 服务 | 状态 | 健康检查 | 端口 |
|------|------|----------|------|
| 前端服务 | ✅ 运行中 | healthy | 3000 |
| 后端 API | ✅ 运行中 | healthy | 8000 |
| Hummingbot | ✅ 运行中 | - | 15888 |
| Redis | ✅ 运行中 | healthy | 6379 |

## 🔧 生产环境配置

### 系统要求
- **操作系统**: Linux (推荐 Ubuntu 20.04+)
- **Docker**: 20.10+
- **Docker Compose**: v2.0+
- **内存**: 最低 4GB，推荐 8GB+
- **存储**: 最低 20GB 可用空间
- **网络**: 稳定的互联网连接

### 核心配置文件
```
├── docker-compose.production.yml  # 完整生产配置
├── docker-compose.prod-test.yml   # 简化测试配置
├── production.env                 # 环境变量
├── nginx/nginx.conf               # 反向代理配置
├── redis.conf                     # Redis 配置
├── monitoring/prometheus.yml      # 监控配置
└── deploy_production.sh          # 自动部署脚本
```

## 🚀 快速部署

### 1. 环境准备
```bash
# 克隆代码
git clone <repository-url>
cd arbitrage-system

# 检查 Docker 环境
docker --version
docker-compose --version
```

### 2. 配置环境变量
```bash
# 复制并编辑生产配置
cp production.env.example production.env
nano production.env

# 必须修改的配置项:
SECRET_KEY=your-super-secret-key-here
HUMMINGBOT_PASSWORD=your-secure-password
GRAFANA_PASSWORD=your-grafana-password
```

### 3. 执行部署
```bash
# 使用自动部署脚本
./deploy_production.sh

# 或手动部署
docker-compose -f docker-compose.production.yml up -d --build
```

### 4. 验证部署
```bash
# 运行生产测试
./production_test.sh

# 检查服务状态
docker-compose -f docker-compose.production.yml ps
```

## 📊 监控和日志

### 访问地址
- **前端界面**: http://localhost
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **监控面板**: http://localhost:3001 (Grafana)
- **指标收集**: http://localhost:9090 (Prometheus)

### 日志查看
```bash
# 查看所有服务日志
docker-compose -f docker-compose.production.yml logs

# 查看特定服务日志
docker-compose -f docker-compose.production.yml logs backend
docker-compose -f docker-compose.production.yml logs hummingbot

# 实时跟踪日志
docker-compose -f docker-compose.production.yml logs -f
```

## 🔒 安全配置

### 必要的安全措施
1. **修改默认密码**: 更改所有默认密码
2. **启用 HTTPS**: 配置 SSL 证书
3. **防火墙设置**: 限制不必要的端口访问
4. **定期备份**: 配置自动备份策略
5. **更新维护**: 定期更新依赖包

### SSL 配置 (可选)
```bash
# 生成自签名证书 (测试用)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem

# 编辑 nginx.conf 启用 HTTPS 配置块
```

## 💾 备份和恢复

### 数据备份
```bash
# 备份数据库
docker exec arbitrage-backend-prod cp /app/data/arbitrage_system.db /app/backups/

# 备份配置文件
tar -czf config-backup-$(date +%Y%m%d).tar.gz \
  hummingbot/conf/ production.env nginx/

# 备份 Docker 卷
docker run --rm -v web3_projects_backend_data_prod:/data \
  -v $(pwd)/backups:/backup alpine \
  tar czf /backup/backend-data-$(date +%Y%m%d).tar.gz -C /data .
```

### 数据恢复
```bash
# 恢复数据库
docker exec arbitrage-backend-prod cp /app/backups/arbitrage_system.db /app/data/

# 恢复配置
tar -xzf config-backup-YYYYMMDD.tar.gz

# 重启服务
docker-compose -f docker-compose.production.yml restart
```

## 🔧 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 检查容器状态
docker-compose -f docker-compose.production.yml ps

# 查看错误日志
docker-compose -f docker-compose.production.yml logs [service_name]

# 重新构建镜像
docker-compose -f docker-compose.production.yml build --no-cache
```

#### 2. Hummingbot 连接问题
```bash
# 检查密码验证文件
ls -la hummingbot/conf/.password_verification

# 重新生成密码验证
python create_password_verification.py

# 重启 Hummingbot 服务
docker-compose -f docker-compose.production.yml restart hummingbot
```

#### 3. 数据库错误
```bash
# 初始化数据库
docker-compose -f docker-compose.production.yml exec backend python init_db.py

# 检查数据库文件权限
docker-compose -f docker-compose.production.yml exec backend ls -la /app/data/
```

### 性能优化

#### 1. 资源限制
```yaml
# 在 docker-compose.yml 中添加资源限制
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

#### 2. 数据库优化
```bash
# 定期清理旧日志
docker-compose -f docker-compose.production.yml exec backend \
  python -c "
from database import SessionLocal
from models import Log
from datetime import datetime, timedelta
db = SessionLocal()
cutoff = datetime.now() - timedelta(days=30)
db.query(Log).filter(Log.created_at < cutoff).delete()
db.commit()
"
```

## 📈 扩展和升级

### 水平扩展
```bash
# 扩展后端服务
docker-compose -f docker-compose.production.yml up -d --scale backend=3

# 使用负载均衡器
# 在 nginx.conf 中配置多个后端实例
```

### 版本升级
```bash
# 1. 备份当前环境
./backup.sh

# 2. 拉取新版本
git pull origin main

# 3. 更新镜像
docker-compose -f docker-compose.production.yml pull

# 4. 重新部署
docker-compose -f docker-compose.production.yml up -d
```

## 📞 运维联系方式

### 支持信息
- **文档**: 查看 `README_DOCKER.md` 获取更多信息
- **日志**: 查看 `/var/log/` 目录下的应用日志
- **监控**: 访问 Grafana 面板查看系统状态

### 紧急处理
```bash
# 紧急停止所有服务
docker-compose -f docker-compose.production.yml down

# 快速重启
docker-compose -f docker-compose.production.yml restart

# 查看资源使用情况
docker stats
```

---

## 📝 变更日志

### v1.0.0 (2025-08-08)
- ✅ 完成生产环境配置
- ✅ 通过功能测试 (91.6% 成功率)
- ✅ 添加健康检查和监控
- ✅ 创建自动部署脚本

---

**注意**: 在生产环境中部署前，请务必修改所有默认密码和安全配置！

