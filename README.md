# Hyperliquid资金费率套利系统

## 项目简介
本系统为Hyperliquid平台的资金费率套利自动化系统，支持实盘自动下单、实时资金管理、参数合规适配与详细日志追踪。所有资金与仓位均以平台API为准，系统不再本地管理余额，确保安全、透明、自动化。

---

## 目录结构
```
web3_projects/
├── hyperliquid_system.py           # 主系统入口，策略与资金管理
├── wallet_manager.py               # 钱包连接与签名，集成真实下单API
├── hyperliquid_api_fixed.py        # Hyperliquid API适配与参数合规
├── requirements.txt                # 依赖包
├── setup_wallet.py                 # 钱包配置脚本
├── wallet.json                     # 钱包配置文件（私钥加密存储）
├── arbitrage_system.db             # 交易与资金数据库
├── arbitrage_system.log            # 系统运行日志
├── README.md                       # 项目说明
```

---

## 环境与依赖安装
建议使用Python 3.10+，推荐虚拟环境隔离依赖：
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
依赖包（requirements.txt）：
```
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
schedule>=1.2.0
```
如遇`cryptography`、`web3`等依赖缺失，请手动安装：
```bash
pip install cryptography web3 eth-account
```

---

## 钱包配置与安全说明
### 1. 推荐方式：脚本配置
```bash
python setup_wallet.py
```
按提示输入钱包地址与私钥，配置将自动加密保存到wallet.json。

### 2. 手动配置wallet.json
```json
{
  "address": "你的钱包地址",
  "private_key": "你的私钥"
}
```

### 3. 钱包安全建议
- 私钥仅本地加密存储，严禁泄露
- 建议专用小额钱包，勿用主钱包
- 定期备份wallet.json
- 钱包仅用于签名与身份校验，资金全部以平台API为准

---

## 资金管理与主系统运行
- 系统启动、每次策略执行前后，均通过API实时查询平台余额与可用保证金，自动记录日志
- 本地不再维护余额，所有资金以Hyperliquid平台为准
- 日志详细记录每次资金变动、下单参数、API响应，便于溯源与排查

### 启动主系统
```bash
python hyperliquid_system.py
```

---

## 真实下单接口与参数自动适配
- 所有下单均通过`wallet_manager.py`的`place_order`方法，调用Hyperliquid官方/exchange接口，EVM私钥签名，支持市价单/限价单
- 下单参数自动适配：
  - 启动时拉取所有合约meta，自动对齐minSz、tickSz、最大杠杆
  - sz（下单数量）= 余额90% × 杠杆 / 当前价格，自动向下取整到tickSz，且不低于minSz
  - SOPH-PERP等合约参数自动合规，避免422错误
- 日志输出每次下单payload、参数适配过程、合约meta字典，便于定位问题

---

## 日志与常见问题排查
- 所有运行、资金、下单、异常均记录于arbitrage_system.log
- 实时查看日志：
```bash
tail -f arbitrage_system.log
```
- 常见问题：
  - 钱包连接失败：检查地址/私钥格式与网络
  - 下单422：检查sz、tickSz、minSz、杠杆参数，查看日志payload与meta
  - 余额异常：以平台API为准，重启系统同步

---

## 免责声明与安全建议
- 本系统仅供学习与研究，不构成投资建议
- 实盘交易有风险，建议小额测试，严格风控
- 私钥安全自负，建议专用钱包
- 如遇问题请先查阅日志与本说明

---

## 更新日志
- 资金管理重构：所有余额/保证金实时API同步
- 集成真实下单接口，参数自动适配平台限制
- 日志与排查机制完善
- 钱包配置与安全加固 