import React, { useState, useEffect } from 'react';
import { Card, Select, Row, Col, Alert, Spin, Button } from 'antd';
import ReactECharts from 'echarts-for-react';
import { getSymbols, getKline, getOrderBook } from '../api/market';

const { Option } = Select;

const Market: React.FC = () => {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [symbol, setSymbol] = useState<string>('');
  const [klineData, setKlineData] = useState<any[]>([]);
  const [orderBookData, setOrderBookData] = useState<any>({ bids: [], asks: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSymbols();
  }, []);

  useEffect(() => {
    if (symbol) {
      fetchKlineData();
      fetchOrderBookData();
    }
  }, [symbol]);

  const fetchSymbols = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getSymbols();
      setSymbols(data);
      if (data.length > 0) {
        setSymbol(data[0]);
      }
    } catch (error: any) {
      console.error('获取交易对失败:', error);
      setError('无法连接到后端服务，请检查服务是否正常运行');
    } finally {
      setLoading(false);
    }
  };

  const fetchKlineData = async () => {
    try {
      const data = await getKline(symbol);
      setKlineData(data);
    } catch (error) {
      console.error('获取K线数据失败:', error);
    }
  };

  const fetchOrderBookData = async () => {
    try {
      const data = await getOrderBook(symbol);
      setOrderBookData(data);
    } catch (error) {
      console.error('获取订单簿失败:', error);
    }
  };

  const klineOption = {
    xAxis: { type: 'category', data: klineData.map((item) => new Date(item.time).toLocaleTimeString()) },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'candlestick',
        data: klineData.map(item => [item.open, item.high, item.low, item.close]),
      },
    ],
  };

  if (error) {
    return (
      <div>
        <Alert
          message="连接错误"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={fetchSymbols}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <Spin spinning={loading}>
      <div>
        <Row gutter={16}>
          <Col span={6}>
            <Card title="交易对选择">
              <Select value={symbol} onChange={setSymbol} style={{ width: '100%' }}>
                {symbols.map(s => <Option key={s} value={s}>{s}</Option>)}
              </Select>
            </Card>
            <Card title="订单簿深度" style={{ marginTop: 16 }}>
              <div>买盘：</div>
              {orderBookData.bids.map(([price, amount]: [number, number], idx: number) => (
                <div key={idx}>价格: {price} 数量: {amount}</div>
              ))}
              <div>卖盘：</div>
              {orderBookData.asks.map(([price, amount]: [number, number], idx: number) => (
                <div key={idx}>价格: {price} 数量: {amount}</div>
              ))}
            </Card>
          </Col>
          <Col span={18}>
            <Card title="K线图">
              <ReactECharts option={klineOption} style={{ height: 400 }} />
            </Card>
          </Col>
        </Row>
      </div>
    </Spin>
  );
};

export default Market; 