# 📁 项目结构说明

项目已完成整理，以下是最新的目录结构和说明。

## 🏗️ 整理后的项目结构

```
arbitrage-system/
├── 📄 README.md                    # 项目主文档
├── 📄 PROJECT_STRUCTURE.md         # 项目结构说明（本文件）
│
├── 🎨 frontend/ (front_demo/)       # 前端应用
│   ├── src/                        # 源代码
│   │   ├── api/                   # API 客户端
│   │   ├── components/            # React 组件
│   │   ├── pages/                 # 页面组件
│   │   └── utils/                 # 工具函数
│   ├── public/                     # 静态资源
│   ├── Dockerfile                  # 前端容器配置
│   ├── nginx.conf                  # Nginx 配置
│   └── package.json                # 依赖管理
│
├── ⚡ backend/                      # 后端服务
│   ├── main.py                     # FastAPI 应用入口
│   ├── models.py                   # 数据库模型
│   ├── crud.py                     # 数据库操作
│   ├── schemas.py                  # API 数据模型
│   ├── database.py                 # 数据库配置
│   ├── hummingbot_integration.py   # Hummingbot 集成
│   ├── init_db.py                  # 数据库初始化
│   ├── mock_hummingbot_api_server.py # Mock API 服务器
│   ├── test_hummingbot_integration.py # 集成测试
│   ├── Dockerfile.simple           # 开发环境容器
│   ├── Dockerfile.production       # 生产环境容器
│   └── requirements.txt            # Python 依赖
│
├── 🤖 hummingbot/                   # Hummingbot 策略引擎
│   ├── conf/                       # 配置文件
│   ├── scripts/                    # 自定义脚本
│   │   └── rest_shim.py           # REST API 桥接
│   ├── controllers/                # 控制器
│   ├── logs/                       # 日志文件
│   └── [其他 Hummingbot 核心文件]
│
├── 📚 docs/                         # 项目文档
│   ├── 📄 README.md                # 文档索引
│   ├── design/                     # 设计文档
│   │   ├── design.md              # 整体设计
│   │   ├── front.md               # 前端设计
│   │   └── back.md                # 后端设计
│   ├── deployment/                 # 部署文档
│   │   ├── PRODUCTION_DEPLOYMENT_GUIDE.md
│   │   ├── CONTAINER_DEPLOYMENT_SUMMARY.md
│   │   ├── DEPLOYMENT_SUCCESS.md
│   │   └── README_DOCKER.md
│   └── operations/                 # 运维文档
│       ├── PROJECT_LIFECYCLE.md
│       ├── CURRENT_TASKS.md
│       └── FINAL_SUMMARY.md
│
├── ⚙️ configs/                      # 配置文件
│   ├── 📄 README.md                # 配置说明
│   ├── production.env              # 生产环境变量
│   ├── redis.conf                  # Redis 配置
│   ├── nginx/                      # Nginx 配置
│   │   └── nginx.conf
│   └── monitoring/                 # 监控配置
│       └── prometheus.yml
│
├── 🛠️ scripts/                      # 脚本工具
│   ├── 📄 README.md                # 脚本说明
│   ├── deployment/                 # 部署脚本
│   │   └── deploy_production.sh
│   └── utils/                      # 工具脚本
│       ├── create_password_verification.py
│       └── stop_local.sh
│
└── 🐳 Docker 配置文件
    ├── docker-compose.simple.yml      # 开发环境
    ├── docker-compose.prod-test.yml   # 生产测试环境
    └── docker-compose.production.yml  # 完整生产环境
```

## 🗂️ 文件整理说明

### ✅ 已删除的文件
以下文件已被清理，因为它们是临时文件、重复文件或无关文件：

#### 临时和无用文件
- `alternative_analysis_algorithm.py` - 无关的分析算法
- `hospital_record_analysis.py` - 无关的医院记录分析
- `docker_daemon_config.json` - 临时 Docker 配置
- `backend/mock_hb_api.out` - 临时输出文件
- `backend/mock_hb_api.pid` - 临时进程文件

#### 重复的配置文件
- `docker-compose.api.yml` - 重复的 API 配置
- `docker-compose.dev.yml` - 重复的开发配置
- `docker-compose.local.yml` - 重复的本地配置
- `docker-compose.yml` - 基础配置（已有专门版本）

#### 过时的部署脚本
- `deploy_backend.sh` - 单独后端部署
- `deploy_hybrid.sh` - 混合部署
- `deploy_local.sh` - 本地部署
- `deploy.sh` - 通用部署
- `fix_docker_network.sh` - 临时网络修复

#### 重复的 Dockerfile
- `backend/Dockerfile.local` - 本地开发版本
- `backend/Dockerfile` - 基础版本

### 📁 新建的目录结构

#### 文档目录 (`docs/`)
- `design/` - 系统设计文档
- `deployment/` - 部署相关文档
- `operations/` - 运维管理文档
- `api/` - API 文档（预留）

#### 配置目录 (`configs/`)
- `nginx/` - Web 服务器配置
- `monitoring/` - 监控系统配置
- 环境变量和服务配置文件

#### 脚本目录 (`scripts/`)
- `deployment/` - 部署自动化脚本
- `utils/` - 工具和辅助脚本

## 🎯 整理后的优势

### 1. 清晰的项目结构
- 按功能模块组织目录
- 分离开发和生产配置
- 文档集中管理

### 2. 减少混乱
- 删除重复和临时文件
- 统一命名规范
- 明确文件用途

### 3. 便于维护
- 文档化的目录结构
- 清晰的依赖关系
- 标准化的配置管理

### 4. 易于扩展
- 模块化的组织方式
- 预留的扩展目录
- 灵活的配置架构

## 📋 使用建议

### 开发者指南
1. **新手入门**: 从 `README.md` 开始
2. **设计了解**: 阅读 `docs/design/` 目录
3. **部署参考**: 查看 `docs/deployment/` 目录
4. **配置修改**: 编辑 `configs/` 目录文件

### 运维指南
1. **日常运维**: 使用 `scripts/` 目录工具
2. **配置管理**: 维护 `configs/` 目录文件
3. **文档更新**: 及时更新 `docs/` 目录内容
4. **版本控制**: 跟踪所有配置变更

### 部署指南
1. **开发环境**: `docker-compose.simple.yml`
2. **测试环境**: `docker-compose.prod-test.yml`
3. **生产环境**: `docker-compose.production.yml`
4. **自动部署**: `scripts/deployment/deploy_production.sh`

---

**📝 维护说明**: 
- 本文档会随项目发展持续更新
- 新增文件时请更新相应说明
- 保持目录结构的一致性和清晰度
