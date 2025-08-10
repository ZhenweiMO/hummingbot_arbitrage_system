# 🌍 环境对比说明

## 📊 当前部署状态

### 🧪 **生产测试环境** (已停止)
- **配置文件**: `docker-compose.prod-test.yml`
- **状态**: 已停止，可随时重启
- **用途**: 功能验证和开发测试

### 🚀 **完整生产环境** (运行中)
- **配置文件**: `docker-compose.production.yml`
- **状态**: 正常运行
- **用途**: 企业级生产部署

## 🔍 详细对比

| 特性 | 生产测试环境 | 完整生产环境 |
|------|-------------|-------------|
| **容器命名** | `arbitrage-*-prod-test` | `arbitrage-*-prod` |
| **前端端口** | 3000 | 9091 |
| **后端端口** | 8000 | 8001 |
| **Hummingbot端口** | 15888 | 15889 |
| **Redis端口** | 6379 | 6380 |
| **监控系统** | ❌ | ✅ Prometheus + Grafana |
| **反向代理** | ❌ | ✅ Nginx |
| **健康检查** | 基础 | 完整 |
| **资源限制** | ❌ | ✅ |
| **日志聚合** | ❌ | ✅ |
| **安全配置** | 基础 | 高级 |

## 🌐 访问地址

### 生产测试环境 (当前停止)
```bash
# 启动测试环境
docker-compose -f docker-compose.prod-test.yml up -d

# 访问地址
前端: http://localhost:3000
后端: http://localhost:8000
Hummingbot: http://localhost:15888
Redis: localhost:6379
```

### 完整生产环境 (当前运行)
```bash
# 访问地址
前端: http://localhost:9091
后端: http://localhost:8001
API文档: http://localhost:8001/docs
Hummingbot: http://localhost:15889
Redis: localhost:6380
监控面板: http://localhost:3001 (Grafana)
指标收集: http://localhost:9090 (Prometheus)
```

## 🔧 环境管理

### 启动生产测试环境
```bash
# 停止生产环境
docker-compose -f docker-compose.production.yml down

# 启动测试环境
docker-compose -f docker-compose.prod-test.yml up -d
```

### 启动完整生产环境
```bash
# 停止测试环境
docker-compose -f docker-compose.prod-test.yml down

# 启动生产环境
docker-compose -f docker-compose.production.yml --env-file configs/production.env.local up -d
```

### 同时运行两个环境
```bash
# 测试环境使用默认端口
docker-compose -f docker-compose.prod-test.yml up -d

# 生产环境使用不同端口
docker-compose -f docker-compose.production.yml --env-file configs/production.env.local up -d
```

## 📈 生产环境特性

### 监控系统
- **Prometheus**: 指标收集和存储
- **Grafana**: 可视化监控面板
- **健康检查**: 自动故障检测
- **告警系统**: 异常情况通知

### 性能优化
- **负载均衡**: Nginx 反向代理
- **缓存策略**: Redis 数据缓存
- **资源限制**: 容器资源管理
- **并发处理**: 多 worker 配置

### 安全加固
- **网络隔离**: Docker 网络安全
- **访问控制**: API 限流和认证
- **数据加密**: 敏感信息保护
- **审计日志**: 操作记录追踪

## 🎯 使用建议

### 开发阶段
- 使用 **生产测试环境**
- 快速迭代和调试
- 功能验证和测试

### 生产部署
- 使用 **完整生产环境**
- 企业级监控和运维
- 高可用性和安全性

### 并行开发
- 可以同时运行两个环境
- 不同端口避免冲突
- 独立的数据和配置

## 📋 环境检查清单

### 生产测试环境
- [ ] 前端服务正常 (端口 3000)
- [ ] 后端 API 正常 (端口 8000)
- [ ] Hummingbot 连接正常 (端口 15888)
- [ ] Redis 服务正常 (端口 6379)
- [ ] 数据库初始化完成

### 完整生产环境
- [ ] 前端服务正常 (端口 9091)
- [ ] 后端 API 正常 (端口 8001)
- [ ] Hummingbot 连接正常 (端口 15889)
- [ ] Redis 服务正常 (端口 6380)
- [ ] Prometheus 监控正常 (端口 9090)
- [ ] Grafana 面板正常 (端口 3001)
- [ ] Nginx 代理正常 (端口 80/443)
- [ ] 健康检查通过
- [ ] 数据库初始化完成

---

**💡 提示**: 根据您的需求选择合适的环境。开发时使用测试环境，正式部署时使用完整生产环境。
