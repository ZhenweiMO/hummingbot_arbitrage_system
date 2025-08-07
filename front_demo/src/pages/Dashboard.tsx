import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Alert, Spin, Button, Progress } from 'antd';
import { getOverview } from '../api/overview';

const Dashboard: React.FC = () => {
  const [overview, setOverview] = useState<any>({
    strategy_total: 0,
    strategy_running: 0,
    asset_total: 0,
    profit_today: 0
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOverview();
  }, []);

  const fetchOverview = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getOverview();
      setOverview(data);
    } catch (error: any) {
      console.error('获取总览数据失败:', error);
      setError('无法连接到后端服务，请检查服务是否正常运行');
    } finally {
      setLoading(false);
    }
  };

  // 计算策略运行率
  const strategyRunningRate = overview.strategy_total > 0 
    ? (overview.strategy_running / overview.strategy_total) * 100 
    : 0;

  // 格式化数字
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(num);
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
            <Button size="small" onClick={fetchOverview}>
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
            <Card>
              <Statistic 
                title="策略总数" 
                value={overview.strategy_total}
                suffix="个"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic 
                title="运行中策略" 
                value={overview.strategy_running}
                suffix="个"
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic 
                title="总资产" 
                value={formatNumber(overview.asset_total)}
                suffix="USDT"
                precision={2}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic 
                title="今日盈亏" 
                value={formatNumber(overview.profit_today)}
                suffix="USDT"
                precision={2}
                valueStyle={{ 
                  color: overview.profit_today >= 0 ? '#3f8600' : '#cf1322' 
                }}
              />
            </Card>
          </Col>
        </Row>
        
        <Row gutter={16} style={{ marginTop: 24 }}>
          <Col span={12}>
            <Card title="策略运行状态">
              <div style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span>运行率</span>
                  <span>{strategyRunningRate.toFixed(1)}%</span>
                </div>
                <Progress 
                  percent={strategyRunningRate} 
                  status={strategyRunningRate > 0 ? 'active' : 'exception'}
                />
              </div>
              <div style={{ fontSize: 14, color: '#666' }}>
                <div>运行中: {overview.strategy_running} 个</div>
                <div>已停止: {overview.strategy_total - overview.strategy_running} 个</div>
              </div>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="资产概览">
              <div style={{ fontSize: 14, color: '#666' }}>
                <div style={{ marginBottom: 8 }}>
                  <span style={{ fontWeight: 'bold' }}>总资产:</span> {formatNumber(overview.asset_total)} USDT
                </div>
                <div style={{ marginBottom: 8 }}>
                  <span style={{ fontWeight: 'bold' }}>今日盈亏:</span> 
                  <span style={{ 
                    color: overview.profit_today >= 0 ? '#3f8600' : '#cf1322',
                    marginLeft: 8
                  }}>
                    {overview.profit_today >= 0 ? '+' : ''}{formatNumber(overview.profit_today)} USDT
                  </span>
                </div>
                <div>
                  <span style={{ fontWeight: 'bold' }}>收益率:</span> 
                  <span style={{ 
                    color: overview.profit_today >= 0 ? '#3f8600' : '#cf1322',
                    marginLeft: 8
                  }}>
                    {overview.asset_total > 0 
                      ? `${overview.profit_today >= 0 ? '+' : ''}${((overview.profit_today / overview.asset_total) * 100).toFixed(2)}%`
                      : '0.00%'
                    }
                  </span>
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      </div>
    </Spin>
  );
};

export default Dashboard; 