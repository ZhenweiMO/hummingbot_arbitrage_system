# Changelog

所有重要的更改都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 计划中
- 支持更多交易所 API
- 添加交易策略回测功能
- 实现实时价格监控
- 添加风险管理模块

## [1.1.0] - 2025-08-10

### Added
- 实时余额获取功能
- 币安 API 连接器
- OKX API 连接器
- 自动余额更新任务
- 版本控制和部署策略
- 账户配置指南
- 部署脚本和工具

### Changed
- 更新账户模型支持实时余额
- 优化前端 API 配置
- 改进错误处理机制
- 重构数据库初始化流程

### Fixed
- 修复前端连接后端问题
- 修复数据库初始化问题
- 修复 API 依赖安装问题
- 修复 Docker 构建缓存问题

### Security
- 添加 API 密钥安全存储
- 实现最小权限原则
- 添加网络安全配置

## [1.0.0] - 2025-08-09

### Added
- 基础套利交易系统
- React 前端界面
- FastAPI 后端服务
- Hummingbot 集成
- Docker 容器化部署
- 基础监控和日志系统
- 策略管理功能
- 账户管理功能
- 交易记录功能

### Technical
- 使用 TypeScript 和 React 构建前端
- 使用 FastAPI 和 SQLAlchemy 构建后端
- 使用 Docker Compose 进行容器编排
- 集成 Prometheus 和 Grafana 监控
- 使用 SQLite 作为数据库
- 实现 RESTful API 设计

---

## 版本说明

### 版本号格式
- **MAJOR**: 不兼容的 API 修改
- **MINOR**: 向下兼容的功能性新增
- **PATCH**: 向下兼容的问题修正

### 发布类型
- **major**: 重大版本更新，可能包含破坏性更改
- **minor**: 功能版本更新，添加新功能
- **patch**: 补丁版本更新，修复问题

### 标签说明
- **Added**: 新功能
- **Changed**: 现有功能的更改
- **Deprecated**: 即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: 问题修复
- **Security**: 安全相关更改
