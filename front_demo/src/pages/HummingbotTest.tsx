import React, { useState, useEffect } from 'react';
import { Card, Button, Select, message, Alert, Spin, Descriptions, Tag, Divider } from 'antd';
import { getHummingbotStrategies, getStrategySchema } from '../api/hummingbot';

const { Option } = Select;

const HummingbotTest: React.FC = () => {
  const [availableStrategies, setAvailableStrategies] = useState<any[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [strategySchema, setStrategySchema] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [schemaLoading, setSchemaLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAvailableStrategies();
  }, []);

  useEffect(() => {
    if (selectedStrategy) {
      fetchStrategySchema(selectedStrategy);
    }
  }, [selectedStrategy]);

  const fetchAvailableStrategies = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getHummingbotStrategies();
      setAvailableStrategies(response.data || []);
    } catch (error) {
      console.error('获取可用策略失败:', error);
      setError('无法获取可用策略列表');
    } finally {
      setLoading(false);
    }
  };

  const fetchStrategySchema = async (strategyType: string) => {
    setSchemaLoading(true);
    try {
      const response = await getStrategySchema(strategyType);
      setStrategySchema(response.data || {});
    } catch (error) {
      console.error('获取策略参数模式失败:', error);
      message.error('获取策略参数模式失败');
    } finally {
      setSchemaLoading(false);
    }
  };

  const renderParameterInfo = (paramName: string, paramInfo: any) => {
    return (
      <Descriptions.Item key={paramName} label={paramName}>
        <div>
          <div><strong>类型:</strong> {paramInfo.type}</div>
          <div><strong>描述:</strong> {paramInfo.description}</div>
          <div><strong>必需:</strong> {paramInfo.required ? '是' : '否'}</div>
          {paramInfo.default !== undefined && (
            <div><strong>默认值:</strong> {String(paramInfo.default)}</div>
          )}
          {paramInfo.min_value !== undefined && (
            <div><strong>最小值:</strong> {paramInfo.min_value}</div>
          )}
          {paramInfo.max_value !== undefined && (
            <div><strong>最大值:</strong> {paramInfo.max_value}</div>
          )}
          {paramInfo.unit && (
            <div><strong>单位:</strong> {paramInfo.unit}</div>
          )}
          {paramInfo.options && (
            <div>
              <strong>选项:</strong>
              <div style={{ marginTop: 4 }}>
                                 {paramInfo.options.map((option: string) => (
                   <Tag key={option} style={{ margin: 2 }}>
                     {option}
                   </Tag>
                 ))}
              </div>
            </div>
          )}
        </div>
      </Descriptions.Item>
    );
  };

  const getCategoryColor = (category: string) => {
    const colorMap: Record<string, string> = {
      'market_making': 'blue',
      'arbitrage': 'green',
      'liquidity_mining': 'orange',
      'directional': 'purple'
    };
    return colorMap[category] || 'default';
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
            <Button size="small" onClick={fetchAvailableStrategies}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div>
      <Card title="Hummingbot 集成测试" style={{ marginBottom: 16 }}>
        <p>此页面用于测试 Hummingbot 策略集成功能，包括策略列表获取和参数模式解析。</p>
      </Card>

      <Card title="可用策略列表" style={{ marginBottom: 16 }}>
        <Spin spinning={loading}>
          <div style={{ marginBottom: 16 }}>
            <Button onClick={fetchAvailableStrategies} loading={loading}>
              刷新策略列表
            </Button>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
            {availableStrategies.map(strategy => (
              <Card 
                key={strategy.type} 
                size="small" 
                title={
                  <div>
                    <Tag color={getCategoryColor(strategy.category)}>{strategy.category}</Tag>
                    {strategy.name}
                  </div>
                }
                extra={
                  <Button 
                    size="small" 
                    type={selectedStrategy === strategy.type ? 'primary' : 'default'}
                    onClick={() => setSelectedStrategy(strategy.type)}
                  >
                    查看参数
                  </Button>
                }
              >
                <p>{strategy.description}</p>
                <div>
                  <strong>类型:</strong> <code>{strategy.type}</code>
                </div>
              </Card>
            ))}
          </div>
        </Spin>
      </Card>

      {selectedStrategy && (
        <Card title={`${selectedStrategy} 策略参数模式`}>
          <Spin spinning={schemaLoading}>
            <Descriptions 
              bordered 
              column={1} 
              size="small"
              labelStyle={{ fontWeight: 'bold', width: '150px' }}
            >
              {Object.entries(strategySchema).map(([paramName, paramInfo]) => 
                renderParameterInfo(paramName, paramInfo)
              )}
            </Descriptions>
            
            <Divider />
            
            <div>
              <strong>参数总数:</strong> {Object.keys(strategySchema).length}
              <br />
              <strong>必需参数:</strong> {Object.values(strategySchema).filter((p: any) => p.required).length}
              <br />
              <strong>可选参数:</strong> {Object.values(strategySchema).filter((p: any) => !p.required).length}
            </div>
          </Spin>
        </Card>
      )}
    </div>
  );
};

export default HummingbotTest; 