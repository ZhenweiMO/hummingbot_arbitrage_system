import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Alert, Spin, Button, Progress, Empty, Typography } from 'antd';
import { PlusOutlined, SettingOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { getOverview } from '../api/overview';

const { Title, Paragraph, Text } = Typography;

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

  // 检查是否为新用户（没有策略和资产）
  const isNewUser = overview.strategy_total === 0 && overview.asset_total === 0;

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

  // 新用户欢迎界面
  if (isNewUser && !loading) {
    return (
      <div>
        <Card style={{ marginBottom: 24 }}>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Title level={2}>欢迎使用套利交易系统</Title>
            <Paragraph style={{ fontSize: 16, color: '#666', marginBottom: 32 }}>
              这是一个专业的加密货币套利交易平台，支持多种套利策略和实时监控
            </Paragraph>
            
            <Row gutter={24} justify="center">
              <Col>
                <Card 
                  size="small" 
                  style={{ width: 200, textAlign: 'center' }}
                  hoverable
                  onClick={() => window.location.href = '/accounts'}
                >
                  <SettingOutlined style={{ fontSize: 32, color: '#1890ff', marginBottom: 16 }} />
                  <Title level={4}>配置账户</Title>
                  <Text type="secondary">添加交易所 API 密钥</Text>
                </Card>
              </Col>
              <Col>
                <Card 
                  size="small" 
                  style={{ width: 200, textAlign: 'center' }}
                  hoverable
                  onClick={() => window.location.href = '/strategies'}
                >
                  <PlusOutlined style={{ fontSize: 32, color: '#52c41a', marginBottom: 16 }} />
                  <Title level={4}>创建策略</Title>
                  <Text type="secondary">选择套利策略类型</Text>
                </Card>
              </Col>
              <Col>
                <Card 
                  size="small" 
                  style={{ width: 200, textAlign: 'center' }}
                  hoverable
                  onClick={() => window.location.href = '/hummingbot-test'}
                >
                  <PlayCircleOutlined style={{ fontSize: 32, color: '#722ed1', marginBottom: 16 }} />
                  <Title level={4}>策略测试</Title>
                  <Text type="secondary">查看可用策略类型</Text>
                </Card>
              </Col>
            </Row>
          </div>
        </Card>

        <Row gutter={16}>
          <Col span={12}>
            <Card title="快速开始指南" size="small">
              <div style={{ fontSize: 14, lineHeight: 1.8 }}>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>1. 配置交易所账户</Text>
                  <br />
                  <Text type="secondary">在"账户管理"页面添加您的交易所 API 密钥</Text>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>2. 创建套利策略</Text>
                  <br />
                  <Text type="secondary">选择适合的套利策略类型并配置参数</Text>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>3. 启动策略</Text>
                  <br />
                  <Text type="secondary">启动策略后系统将自动执行套利交易</Text>
                </div>
                <div>
                  <Text strong>4. 监控收益</Text>
                  <br />
                  <Text type="secondary">在仪表板查看实时收益和策略状态</Text>
                </div>
              </div>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="支持的功能" size="small">
              <div style={{ fontSize: 14, lineHeight: 1.8 }}>
                <div style={{ marginBottom: 8 }}>
                  <Text strong>• 多种套利策略</Text>
                  <br />
                  <Text type="secondary">纯做市、跨交易所套利、AMM套利等</Text>
                </div>
                <div style={{ marginBottom: 8 }}>
                  <Text strong>• 实时余额监控</Text>
                  <br />
                  <Text type="secondary">自动获取交易所账户余额</Text>
                </div>
                <div style={{ marginBottom: 8 }}>
                  <Text strong>• 交易日志记录</Text>
                  <br />
                  <Text type="secondary">完整的交易历史和日志追踪</Text>
                </div>
                <div>
                  <Text strong>• 性能监控</Text>
                  <br />
                  <Text type="secondary">实时监控策略性能和收益</Text>
                </div>
              </div>
            </Card>
          </Col>
        </Row>
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