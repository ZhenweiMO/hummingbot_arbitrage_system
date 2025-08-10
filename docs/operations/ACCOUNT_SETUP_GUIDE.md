# 🔐 账户配置指南

## 📋 概述

本系统支持通过交易所 API 实时获取账户余额，无需手动设置。您需要配置真实的交易所 API 密钥来启用此功能。

## 🎯 支持的交易所

| 交易所 | 状态 | API 文档 |
|--------|------|----------|
| **Binance** | ✅ 支持 | [币安 API](https://binance-docs.github.io/apidocs/spot/en/) |
| **OKX** | ✅ 支持 | [OKX API](https://www.okx.com/docs-v5/en/) |
| **Bybit** | 🔄 开发中 | [Bybit API](https://bybit-exchange.github.io/docs/v5/intro) |
| **Gate.io** | 🔄 开发中 | [Gate.io API](https://www.gate.io/docs/developers/apiv4) |

## 🔧 配置步骤

### 1. 获取交易所 API 密钥

#### Binance API 配置
1. 登录 [Binance](https://www.binance.com)
2. 进入 **API 管理** → **创建 API**
3. 设置 API 权限：
   - ✅ **读取信息** (必需)
   - ❌ **交易** (可选，仅用于交易功能)
   - ❌ **提现** (不推荐)
4. 保存 **API Key** 和 **Secret Key**

#### OKX API 配置
1. 登录 [OKX](https://www.okx.com)
2. 进入 **账户中心** → **API 管理** → **创建 API**
3. 设置 API 权限：
   - ✅ **读取** (必需)
   - ❌ **交易** (可选)
   - ❌ **提现** (不推荐)
4. 设置 **Passphrase** (API 密码)
5. 保存 **API Key**、**Secret Key** 和 **Passphrase**

### 2. 配置系统账户

#### 方法一：通过前端界面
1. 访问系统前端：http://localhost:9091
2. 进入 **账户管理** 页面
3. 编辑现有账户或创建新账户
4. 填入真实的 API 密钥信息
5. 保存配置

#### 方法二：直接修改数据库
```sql
-- 更新 Binance 账户
UPDATE accounts 
SET api_key = 'your_real_binance_api_key',
    api_secret = 'your_real_binance_api_secret'
WHERE name = 'Binance';

-- 更新 OKX 账户
UPDATE accounts 
SET api_key = 'your_real_okx_api_key',
    api_secret = 'your_real_okx_api_secret',
    passphrase = 'your_real_okx_passphrase'
WHERE name = 'OKX';
```

#### 方法三：通过 API 接口
```bash
# 更新账户配置
curl -X PUT http://localhost:8001/api/accounts/1 \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_real_api_key",
    "api_secret": "your_real_api_secret"
  }'

# 手动更新余额
curl -X POST http://localhost:8001/api/accounts/1/update-balance
```

### 3. 验证配置

#### 检查 API 连接
```bash
# 测试账户余额获取
curl http://localhost:8001/api/accounts
```

#### 预期响应
```json
[
  {
    "id": 1,
    "name": "Binance",
    "exchange_type": "binance",
    "balance": 12345.67,
    "real_time_balance": {
      "total_equity": 12345.67,
      "balances": [
        {
          "asset": "USDT",
          "free": 10000.0,
          "locked": 0.0,
          "total": 10000.0
        },
        {
          "asset": "BTC",
          "free": 0.5,
          "locked": 0.0,
          "total": 0.5
        }
      ],
      "timestamp": 1640995200.0
    },
    "last_balance_update": "2025-08-10T05:30:00Z"
  }
]
```

## 🔒 安全注意事项

### API 密钥安全
- 🔐 **加密存储**: API 密钥在数据库中加密存储
- 🚫 **最小权限**: 只授予读取权限，避免交易和提现权限
- 🔄 **定期轮换**: 建议定期更换 API 密钥
- 📧 **IP 白名单**: 在交易所设置 API 访问 IP 白名单

### 网络安全
- 🌐 **HTTPS**: 所有 API 通信使用 HTTPS
- 🔒 **防火墙**: 限制服务器网络访问
- 📊 **监控**: 监控 API 调用频率和异常活动
- 🚨 **告警**: 设置异常访问告警

## 🔄 自动余额更新

### 更新频率
- **自动更新**: 每 60 秒自动更新所有账户余额
- **手动更新**: 可通过 API 手动触发更新
- **实时更新**: 交易后立即更新余额

### 更新机制
```python
# 自动更新任务
async def update_account_balances_task():
    while True:
        balances = await exchange_manager.get_all_accounts_balance()
        # 更新数据库
        await asyncio.sleep(60)
```

## 🛠️ 故障排除

### 常见问题

#### 1. API 连接失败
**错误**: `币安 API 请求失败: 401`
**解决**: 检查 API 密钥是否正确，确认 API 权限设置

#### 2. 余额获取失败
**错误**: `获取账户余额失败: Network error`
**解决**: 检查网络连接，确认交易所 API 服务正常

#### 3. 权限不足
**错误**: `币安 API 错误: -2015`
**解决**: 确认 API 密钥有读取权限，检查 IP 白名单设置

### 调试方法
```bash
# 查看详细日志
docker-compose -f docker-compose.production.yml logs backend | grep "exchange"

# 测试单个账户连接
curl -X POST http://localhost:8001/api/accounts/1/update-balance
```

## 📈 性能优化

### 缓存策略
- **Redis 缓存**: 余额信息缓存 30 秒
- **数据库缓存**: 最后更新时间记录
- **批量更新**: 并发更新多个账户

### 监控指标
- **API 响应时间**: 监控各交易所 API 响应速度
- **更新成功率**: 跟踪余额更新成功率
- **错误率**: 监控 API 错误频率

## 🎯 最佳实践

### 1. 账户管理
- 📝 **命名规范**: 使用清晰的账户名称
- 🔄 **定期检查**: 定期验证 API 密钥有效性
- 📊 **余额监控**: 设置余额变化告警

### 2. 安全配置
- 🛡️ **最小权限**: 只授予必要的 API 权限
- 🔐 **密钥管理**: 使用安全的密钥管理方案
- 📍 **IP 限制**: 设置 API 访问 IP 白名单

### 3. 监控告警
- 📊 **实时监控**: 监控账户余额变化
- 🚨 **异常告警**: 设置异常交易告警
- 📈 **性能监控**: 监控 API 调用性能

---

**💡 提示**: 配置完成后，系统将自动获取实时余额，无需手动更新。建议定期检查 API 密钥的有效性和权限设置。
