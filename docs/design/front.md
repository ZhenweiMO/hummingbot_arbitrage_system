# 前端设计思路

## 目录结构建议

```
frontend/
  src/
    api/                # 封装后端接口
      strategy.ts
      account.ts
      market.ts
      ...
    components/         # 通用组件
      StrategyForm.tsx
      StrategyTable.tsx
      AccountTable.tsx
      MarketDepth.tsx
      LogViewer.tsx
      ...
    pages/              # 页面
      Dashboard.tsx
      StrategyList.tsx
      StrategyDetail.tsx
      Account.tsx
      Market.tsx
      Log.tsx
      ...
    App.tsx             # 路由与布局
    index.tsx
  package.json
```

## 主要页面与功能点

1. 策略管理页（StrategyList.tsx & StrategyDetail.tsx）
   - 策略列表（表格展示，含启停、编辑、删除按钮）
   - 新建/编辑策略（弹窗或独立页面，动态表单）
   - 策略详情（运行状态、参数、实时日志、盈亏统计、手动下单等）
2. 账户管理页（Account.tsx）
   - 账户列表（API Key、余额、持仓、资金划转按钮）
   - 新增/编辑/删除 API Key
3. 行情与订单簿页（Market.tsx）
   - 实时行情（K线、最新价、涨跌幅等）
   - 订单簿深度（买卖盘可视化）
   - 交易对选择
4. 交易记录与日志页（Log.tsx）
   - 交易记录（表格，支持筛选）
   - 策略运行日志（实时滚动）
5. 总览页（Dashboard.tsx）
   - 策略数量、运行中数量、总资产、今日盈亏等统计卡片
   - 主要策略和账户的状态一览

## 页面示意（Ant Design 组件为例）

- Table 展示策略/账户/交易记录等
- Modal 弹窗用于新建/编辑
- Tabs 切换日志与交易明细
- Select 选择交易对
- K线图用 echarts-for-react
- Card/Statistic 展示统计信息

## 信息展示建议

- 策略状态、盈亏、运行日志、交易明细等均可通过表格、卡片、图表等方式直观展示
- 实时数据（如行情、订单簿、日志）建议用 WebSocket 推送
- 重要操作（如启停、删除）需二次确认，防止误操作

## 扩展性说明

- 策略参数表单、策略类型、账户类型等均可通过后端 schema 动态生成，便于后续扩展
- 页面和组件解耦，便于新增功能和维护 