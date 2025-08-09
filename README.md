# 🚀 Arbitrage System - 套利交易系统

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 项目概述

一个基于 Hummingbot 的智能套利交易系统，提供完整的前端界面、后端 API 和策略管理功能。

### 🎯 主要特性

- **🎨 现代化前端**: React + TypeScript + Ant Design
- **⚡ 高性能后端**: FastAPI + SQLAlchemy + SQLite
- **🤖 策略引擎**: 集成 Hummingbot 交易策略
- **🐳 容器化部署**: Docker + Docker Compose
- **📊 实时监控**: Prometheus + Grafana
- **🔒 生产就绪**: 完整的安全和监控配置

## 🏗️ 项目架构

```
arbitrage-system/
├── frontend/          # React 前端应用
├── backend/           # FastAPI 后端服务
├── hummingbot/        # Hummingbot 策略引擎
├── docs/              # 项目文档
├── configs/           # 配置文件
└── scripts/           # 部署和工具脚本
```

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose v2.0+
- 4GB+ 内存
- 20GB+ 存储空间

### 开发环境部署

```bash
# 克隆项目
git clone <repository-url>
cd arbitrage-system

# 启动开发环境
docker-compose -f docker-compose.simple.yml up -d

# 访问应用
open http://localhost:3000
```

### 生产环境部署

```bash
# 配置环境变量
cp configs/production.env.example configs/production.env
nano configs/production.env

# 执行自动部署
./scripts/deployment/deploy_production.sh

# 或手动部署
docker-compose -f docker-compose.production.yml up -d
```

## 📖 文档

- **[设计文档](docs/design/)**: 系统架构和设计说明
- **[部署指南](docs/deployment/)**: 详细的部署和配置说明
- **[运维手册](docs/operations/)**: 监控、维护和故障处理
- **[API 文档](http://localhost:8000/docs)**: 在线 API 文档

## 🎛️ 服务访问

| 服务 | 地址 | 描述 |
|------|------|------|
| 前端界面 | http://localhost:3000 | React 用户界面 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| API 文档 | http://localhost:8000/docs | Swagger 文档 |
| Hummingbot | http://localhost:15888 | 策略引擎 API |
| 监控面板 | http://localhost:3001 | Grafana 仪表板 |

## 🔧 核心功能

### 策略管理
- ✅ 策略创建和配置
- ✅ 实时启动和停止
- ✅ 状态监控和日志
- ✅ 参数验证和优化

### 账户管理
- ✅ 多交易所账户配置
- ✅ 余额查询和管理
- ✅ API 密钥安全存储

### 交易监控
- ✅ 实时交易数据
- ✅ 收益分析和统计
- ✅ 风险控制和预警

## 🛠️ 开发

### 项目结构

```
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── components/      # React 组件
│   │   ├── pages/          # 页面组件
│   │   └── api/            # API 客户端
│   └── Dockerfile          # 前端容器配置
│
├── backend/                 # 后端项目
│   ├── main.py             # FastAPI 应用入口
│   ├── models.py           # 数据库模型
│   ├── crud.py             # 数据库操作
│   └── hummingbot_integration.py  # Hummingbot 集成
│
├── hummingbot/             # Hummingbot 配置
│   ├── conf/               # 策略配置
│   ├── scripts/            # 自定义脚本
│   └── rest_shim.py        # REST API 桥接
│
├── docs/                   # 文档目录
│   ├── design/             # 设计文档
│   ├── deployment/         # 部署文档
│   └── operations/         # 运维文档
│
├── configs/                # 配置文件
│   ├── nginx/              # Nginx 配置
│   ├── monitoring/         # 监控配置
│   └── production.env      # 生产环境变量
│
└── scripts/                # 脚本目录
    ├── deployment/         # 部署脚本
    └── utils/              # 工具脚本
```

### 本地开发

```bash
# 后端开发
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# 前端开发
cd frontend
npm install
npm start
```

## 📊 测试

### 功能测试
```bash
# 运行集成测试
./scripts/utils/integration_test.sh

# 检查服务状态
docker-compose ps
curl http://localhost:8000/api/overview
```

### 性能测试
```bash
# 并发测试
ab -n 1000 -c 10 http://localhost:8000/api/strategies

# 资源监控
docker stats
```

## 📈 监控

### 系统监控
- **Prometheus**: 指标收集 (http://localhost:9090)
- **Grafana**: 可视化面板 (http://localhost:3001)
- **健康检查**: 自动故障检测和恢复

### 应用监控
- **日志聚合**: 集中式日志收集
- **性能指标**: API 响应时间和吞吐量
- **业务指标**: 交易量、收益和风险指标

## 🔒 安全

### 安全特性
- **密码加密**: 所有密码加密存储
- **API 限流**: 防止恶意请求
- **网络隔离**: Docker 网络安全隔离
- **HTTPS 支持**: SSL/TLS 加密传输

### 安全配置
```bash
# 修改默认密码
nano configs/production.env

# 生成 SSL 证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout configs/nginx/ssl/key.pem \
  -out configs/nginx/ssl/cert.pem
```

## 🚀 部署

### Docker Compose 配置

- **`docker-compose.simple.yml`**: 开发和测试环境
- **`docker-compose.prod-test.yml`**: 生产测试环境
- **`docker-compose.production.yml`**: 完整生产环境（含监控）

### 环境要求

| 环境 | CPU | 内存 | 存储 | 网络 |
|------|-----|------|------|------|
| 开发 | 2核 | 4GB | 10GB | 1Mbps |
| 测试 | 2核 | 8GB | 20GB | 10Mbps |
| 生产 | 4核 | 16GB | 100GB | 100Mbps |

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests！

### 开发流程
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📞 支持

- **文档**: 查看 [docs/](docs/) 目录
- **Issues**: 提交到 GitHub Issues
- **邮件**: support@example.com

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🎉 鸣谢

- [Hummingbot](https://hummingbot.io/) - 核心交易引擎
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [React](https://reactjs.org/) - 用户界面库
- [Ant Design](https://ant.design/) - 企业级 UI 设计语言

---

**⭐ 如果这个项目对您有帮助，请给一个 Star！**
