# 🐳 Arbitrage System 容器化部署指南

## 📋 概述

本项目采用 Docker 容器化部署，包含以下服务：
- **前端**: React + TypeScript + Ant Design
- **后端**: FastAPI + SQLAlchemy + SQLite
- **Hummingbot**: 策略执行引擎
- **Redis**: 缓存和消息队列

## 🚀 快速开始

### 1. 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 2. 一键部署

```bash
# 克隆项目
git clone <repository-url>
cd web3_projects

# 给部署脚本执行权限
chmod +x deploy.sh

# 一键部署
./deploy.sh
```

### 3. 手动部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 🌐 服务访问

部署完成后，可以通过以下地址访问服务：

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:3000 | Web 界面 |
| 后端 API | http://localhost:8000 | REST API |
| Hummingbot API | http://localhost:15888 | 策略管理 API |
| Gateway | http://localhost:8080 | DEX 网关 |
| Redis | localhost:6379 | 缓存服务 |

## 📁 项目结构

```
web3_projects/
├── docker-compose.yml          # Docker Compose 配置
├── deploy.sh                   # 部署脚本
├── front_demo/                 # 前端项目
│   ├── Dockerfile             # 前端 Dockerfile
│   ├── nginx.conf             # Nginx 配置
│   └── .dockerignore          # Docker 忽略文件
├── backend/                    # 后端项目
│   ├── Dockerfile             # 后端 Dockerfile
│   ├── requirements.txt       # Python 依赖
│   └── .dockerignore          # Docker 忽略文件
└── hummingbot/                 # Hummingbot 项目
    ├── conf/                   # 配置文件
    │   └── arbitrage_config.py # 主配置文件
    ├── logs/                   # 日志目录
    ├── data/                   # 数据目录
    └── certs/                  # 证书目录
```

## 🔧 配置说明

### 环境变量

可以通过 `.env` 文件或环境变量配置：

```bash
# 数据库配置
DATABASE_URL=sqlite:///./arbitrage_system.db

# Hummingbot 配置
HUMMINGBOT_HOST=hummingbot
HUMMINGBOT_PORT=15888
CONFIG_PASSWORD=arbitrage123

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379
```

### Hummingbot 配置

编辑 `hummingbot/conf/arbitrage_config.py` 文件：

```python
# 交易所配置
exchanges = {
    "binance": {
        "api_key": "your_api_key",
        "secret_key": "your_secret_key",
        "sandbox_mode": True,  # 测试模式
    }
}

# 策略配置
strategy_templates = {
    "pure_market_making": {
        "exchange": "binance",
        "market": "BTC-USDT",
        "bid_spread": Decimal("0.5"),
        "ask_spread": Decimal("0.5"),
        "order_amount": Decimal("0.01"),
    }
}
```

## 📊 监控和管理

### 查看服务状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f hummingbot
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 更新部署

```bash
# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

## 🔍 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :3000
   lsof -i :8000
   lsof -i :15888
   
   # 停止占用进程
   kill -9 <PID>
   ```

2. **容器启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs <service_name>
   
   # 重新构建镜像
   docker-compose build --no-cache <service_name>
   ```

3. **数据库初始化失败**
   ```bash
   # 手动初始化数据库
   docker-compose exec backend python3 init_db.py
   ```

### 日志位置

- 后端日志: `backend/logs/`
- Hummingbot 日志: `hummingbot/logs/`
- 容器日志: `docker-compose logs -f`

## 🔒 安全配置

### 生产环境部署

1. **修改默认密码**
   ```bash
   # 修改 CONFIG_PASSWORD
   export CONFIG_PASSWORD=your_secure_password
   ```

2. **配置 SSL 证书**
   ```bash
   # 将证书文件放入 hummingbot/certs/
   cp your_cert.pem hummingbot/certs/
   cp your_key.pem hummingbot/certs/
   ```

3. **限制网络访问**
   ```yaml
   # 在 docker-compose.yml 中配置
   networks:
     arbitrage-network:
       driver: bridge
       ipam:
         config:
           - subnet: 172.20.0.0/16
   ```

## 📈 性能优化

### 资源限制

```yaml
# 在 docker-compose.yml 中配置
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

### 缓存配置

```yaml
# Redis 持久化配置
redis:
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

## 🆘 支持

如果遇到问题，请：

1. 查看日志文件
2. 检查配置文件
3. 确认环境要求
4. 提交 Issue 到项目仓库

## 📝 更新日志

- **v1.0.0**: 初始容器化部署版本
- 支持前端、后端、Hummingbot 服务
- 集成 Redis 缓存
- 提供完整的部署脚本 