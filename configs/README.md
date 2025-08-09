# ⚙️ 配置文件

本目录包含项目的所有配置文件，用于不同环境的部署和运行。

## 📁 目录结构

```
configs/
├── production.env          # 生产环境变量
├── redis.conf             # Redis 配置
├── nginx/                 # Nginx 配置
│   └── nginx.conf
└── monitoring/            # 监控配置
    └── prometheus.yml
```

## 🔧 配置文件说明

### 环境变量 (`production.env`)
生产环境的环境变量配置，包含：
- 应用密钥和密码
- 数据库连接配置
- 监控服务配置
- 安全设置

**⚠️ 重要**: 在生产环境中必须修改所有默认密码！

```bash
# 示例配置
SECRET_KEY=your-super-secret-key-here
HUMMINGBOT_PASSWORD=secure-production-password
GRAFANA_PASSWORD=secure-grafana-password
```

### Redis 配置 (`redis.conf`)
Redis 数据库的生产环境配置：
- 内存优化设置
- 持久化配置
- 安全配置
- 性能调优

### Nginx 配置 (`nginx/nginx.conf`)
反向代理和负载均衡配置：
- 前端静态文件服务
- API 路由代理
- 限流和安全设置
- SSL/HTTPS 配置（可选）

### 监控配置 (`monitoring/prometheus.yml`)
Prometheus 监控指标收集配置：
- 应用服务监控
- 容器资源监控
- 数据库监控
- 自定义业务指标

## 🚀 使用方法

### 开发环境
开发环境使用默认配置，无需额外设置：
```bash
docker-compose -f docker-compose.simple.yml up -d
```

### 生产环境
1. 复制并编辑生产配置：
```bash
cp configs/production.env.example configs/production.env
nano configs/production.env
```

2. 修改必要的配置项：
```bash
# 必须修改的配置
SECRET_KEY=your-unique-secret-key
HUMMINGBOT_PASSWORD=your-secure-password
GRAFANA_PASSWORD=your-grafana-password
```

3. 启动生产环境：
```bash
docker-compose -f docker-compose.production.yml --env-file configs/production.env up -d
```

## 🔒 安全注意事项

### 密码安全
- ✅ 使用强密码（至少 12 位字符）
- ✅ 包含大小写字母、数字和特殊字符
- ✅ 定期更换密码
- ❌ 不要在代码中硬编码密码

### 文件权限
```bash
# 设置配置文件权限
chmod 600 configs/production.env
chmod 644 configs/redis.conf
chmod 644 configs/nginx/nginx.conf
```

### 访问控制
- 限制配置文件的访问权限
- 使用环境变量管理敏感信息
- 定期审查配置变更

## 🛠️ 配置优化

### 性能优化
1. **Redis 配置优化**:
   - 调整最大内存限制
   - 配置合适的持久化策略
   - 优化连接池设置

2. **Nginx 配置优化**:
   - 启用 Gzip 压缩
   - 配置静态文件缓存
   - 调整工作进程数量

3. **监控配置优化**:
   - 设置合理的采集间隔
   - 配置告警阈值
   - 清理历史数据

### 扩展性配置
```yaml
# docker-compose.yml 中的资源限制
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## 🔄 配置更新

### 热更新支持
- **Nginx**: 支持配置热重载
- **Redis**: 部分配置支持运行时修改
- **应用配置**: 需要重启容器

### 更新流程
1. 备份当前配置
2. 修改配置文件
3. 验证配置语法
4. 应用新配置
5. 验证服务状态

```bash
# 示例：更新 Nginx 配置
docker exec arbitrage-nginx nginx -t  # 验证配置
docker exec arbitrage-nginx nginx -s reload  # 重载配置
```

## 📋 配置检查清单

### 部署前检查
- [ ] 所有密码已修改
- [ ] SSL 证书已配置（如需要）
- [ ] 资源限制已设置
- [ ] 监控配置已启用
- [ ] 备份策略已配置

### 运行时检查
- [ ] 服务状态正常
- [ ] 配置文件权限正确
- [ ] 日志输出正常
- [ ] 监控指标正常
- [ ] 性能指标达标

---

**💡 提示**: 在修改配置文件前，建议先备份原文件，并在测试环境中验证配置的正确性。
