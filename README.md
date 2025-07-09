# Hyperliquid资金费率套利系统

## 项目简介

这是一个完整的Hyperliquid资金费率套利系统，支持自动化交易、实时监控、资金管理和风险控制。

## 核心功能

### 1. 钱包认证系统
- 支持MetaMask等主流钱包登录
- 本地加密存储钱包私钥/助记词
- 自动检测钱包网络连接状态
- 安全的私钥管理

### 2. 实时数据监控
- 每分钟扫描所有交易对资金费率
- 识别负费率且绝对值最低的交易对
- 获取实时标记价格和深度数据
- 自动记录历史数据

### 3. 自动化套利引擎
- 在整点前a秒执行策略
- 市价开b倍多单(投入c USDT)
- 整点后a秒市价平仓
- 自动计算并记录每轮收益

### 4. 资金管理系统
- 实时监控钱包余额
- 自动计算可用保证金
- 记录每次操作后的余额变化
- 风险控制机制

### 5. 日志与报表系统
- 详细记录每笔交易参数
- 生成收益曲线图
- 输出风险指标分析
- 数据库存储和查询

## 文件结构

```
web3_projects/
├── hyperliquid_system.py      # 主系统文件
├── wallet_simple.py           # 简化版钱包管理器
├── requirements.txt           # 依赖包
├── README.md                  # 项目说明
├── arbitrage_system.db        # SQLite数据库
├── arbitrage_system.log       # 系统日志
└── wallet.json               # 钱包配置
```

## 安装和配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置钱包
```python
from wallet_simple import SimpleWalletManager

# 创建钱包管理器
wallet = SimpleWalletManager()

# 连接钱包（替换为真实地址和私钥）
address = "0x1234567890123456789012345678901234567890"
private_key = "your_private_key_here"

if wallet.connect_wallet(address, private_key):
    print("钱包连接成功")
    wallet.save_config()  # 保存配置
```

### 3. 运行系统
```bash
python hyperliquid_system.py
```

## 策略参数配置

在 `hyperliquid_system.py` 中的 `TradingConfig` 类可以调整以下参数：

```python
class TradingConfig:
    leverage = 10                    # 杠杆倍数
    investment_amount = 100.0        # 投资金额(USDT)
    pre_execution_seconds = 5        # 整点前执行秒数
    post_execution_seconds = 5       # 整点后执行秒数
    min_funding_rate_threshold = -0.0001  # 最小资金费率阈值
```

## 策略逻辑

### 核心算法
1. **时间点选择**：每个整点的前一分钟
2. **交易对选择**：选择资金费率最低的交易对
3. **入场时机**：整点前5秒
4. **出场时机**：整点后5秒
5. **收益计算**：
   - 价格差 = 买入价格 - 卖出价格
   - 资金费率收益 = 买入价格 × (资金费率 / 8)
   - 总收益 = 价格差 + 资金费率收益

### 风险控制
- 只选择资金费率最低的交易对
- 严格的时间控制（前后5秒）
- 资金费率除以8作为收益计算
- 实时监控钱包余额
- 自动止损机制

## 系统监控

### 实时监控
- 系统运行状态
- 网络连接状态
- 钱包余额变化
- 交易执行情况

### 日志记录
- 详细的交易日志
- 错误和异常记录
- 系统性能指标
- 资金费率变化

## 报表分析

### 性能指标
- 总交易次数
- 盈利次数/亏损次数
- 胜率
- 总收益/平均收益
- 最大单次收益/亏损
- 夏普比率
- 最大回撤

### 可视化图表
1. **累计收益曲线** - 显示策略的累计收益变化
2. **单次收益分布** - 显示单次交易的收益分布
3. **资金费率变化** - 显示所选交易对的资金费率变化
4. **交易对选择分布** - 显示不同交易对被选择的频率

## 数据库结构

### trades表（交易记录）
- id: 主键
- timestamp: 时间戳
- datetime: 日期时间
- trading_pair: 交易对
- action: 操作类型（open/close）
- price: 价格
- amount: 数量
- leverage: 杠杆
- funding_rate: 资金费率
- profit: 收益
- balance_before: 操作前余额
- balance_after: 操作后余额
- status: 状态

### funding_rates表（资金费率记录）
- id: 主键
- timestamp: 时间戳
- datetime: 日期时间
- trading_pair: 交易对
- funding_rate: 资金费率

## 安全注意事项

1. **私钥安全**：私钥应妥善保管，不要泄露给他人
2. **网络安全**：确保网络连接安全，避免中间人攻击
3. **API限制**：注意API调用频率限制
4. **资金安全**：建议先使用小额资金测试
5. **风险控制**：设置合理的止损和仓位管理

## 故障排除

### 常见问题
1. **网络连接失败**：检查网络连接和API地址
2. **钱包连接失败**：验证地址和私钥格式
3. **交易执行失败**：检查余额和权限
4. **数据获取失败**：检查API状态和参数

### 日志查看
```bash
tail -f arbitrage_system.log
```

## 免责声明

本系统仅用于学习和研究目的，不构成投资建议。实际交易存在风险，请谨慎使用。作者不对使用本系统造成的任何损失承担责任。

## 技术支持

如有问题或建议，请通过以下方式联系：
- 提交Issue到项目仓库
- 发送邮件至项目维护者

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的资金费率套利策略
- 包含钱包管理、实时监控、自动化交易功能
- 完整的日志和报表系统 