import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, message, Alert, Spin, Tag, Card, Row, Col } from 'antd';
import { getStrategies, startStrategy, stopStrategy, deleteStrategy } from '../api/strategy';
import StrategyForm from '../components/StrategyForm';
import { maskApiKey } from '../utils/maskUtils';

const StrategyList: React.FC = () => {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getStrategies();
      setStrategies(data);
    } catch (error: any) {
      console.error('获取策略列表失败:', error);
      setError('无法连接到后端服务，请检查服务是否正常运行');
      message.error('获取策略列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async (id: number) => {
    try {
      await startStrategy(id);
      message.success('策略已启动');
      fetchStrategies();
    } catch (error) {
      message.error('启动策略失败，请检查后端服务状态');
    }
  };

  const handleStop = async (id: number) => {
    try {
      await stopStrategy(id);
      message.success('策略已停止');
      fetchStrategies();
    } catch (error) {
      message.error('停止策略失败，请检查后端服务状态');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteStrategy(id);
      message.success('策略已删除');
      fetchStrategies();
    } catch (error) {
      message.error('删除策略失败，请检查后端服务状态');
    }
  };

  // 渲染策略参数，隐藏敏感信息
  const renderParams = (params: any) => {
    if (!params) return '-';
    
    const maskedParams = { ...params };
    
    // 隐藏可能的敏感字段
    const sensitiveFields = ['api_key', 'secret_key', 'private_key', 'password'];
    sensitiveFields.forEach(field => {
      if (maskedParams[field]) {
        maskedParams[field] = maskApiKey(maskedParams[field]);
      }
    });
    
    return (
      <div>
        {Object.entries(maskedParams).map(([key, value]) => (
          <div key={key} style={{ marginBottom: 4 }}>
            <span style={{ fontWeight: 'bold' }}>{key}:</span> {String(value)}
          </div>
        ))}
      </div>
    );
  };

  // 渲染状态标签
  const renderStatus = (status: string) => {
    const color = status === 'running' ? 'green' : 'red';
    return <Tag color={color}>{status === 'running' ? '运行中' : '已停止'}</Tag>;
  };

  // 渲染策略类型标签
  const renderStrategyType = (type: string) => {
    const typeMap: Record<string, { color: string; name: string }> = {
      'pure_market_making': { color: 'blue', name: '纯做市' },
      'avellaneda_market_making': { color: 'purple', name: 'Avellaneda做市' },
      'cross_exchange_market_making': { color: 'orange', name: '跨交易所做市' },
      'amm_arb': { color: 'cyan', name: 'AMM套利' },
      'spot_perpetual_arbitrage': { color: 'magenta', name: '现货永续套利' },
      'perpetual_market_making': { color: 'geekblue', name: '永续做市' },
      'liquidity_mining': { color: 'lime', name: '流动性挖矿' },
      'twap': { color: 'gold', name: 'TWAP' },
      'hedge': { color: 'volcano', name: '对冲' },
      'cross_exchange_mining': { color: 'green', name: '跨交易所挖矿' }
    };
    
    const typeInfo = typeMap[type] || { color: 'default', name: type };
    return <Tag color={typeInfo.color}>{typeInfo.name}</Tag>;
  };

  const columns = [
    { 
      title: '名称', 
      dataIndex: 'name',
      width: 150
    },
    { 
      title: '类型', 
      dataIndex: 'type',
      width: 120,
      render: (type: string) => renderStrategyType(type)
    },
    { 
      title: '状态', 
      dataIndex: 'status',
      width: 100,
      render: (status: string) => renderStatus(status)
    },
    { 
      title: '参数', 
      dataIndex: 'params',
      render: (params: any) => renderParams(params)
    },
    {
      title: '操作',
      width: 200,
      render: (_: any, record: any) => (
        <>
          <Button 
            onClick={() => handleStart(record.id)} 
            disabled={record.status === 'running'}
            size="small"
            style={{ marginRight: 4 }}
          >
            启动
          </Button>
          <Button 
            onClick={() => handleStop(record.id)} 
            disabled={record.status !== 'running'}
            size="small"
            style={{ marginRight: 4 }}
          >
            停止
          </Button>
          <Button 
            onClick={() => { setEditingStrategy(record); setModalVisible(true); }}
            size="small"
            style={{ marginRight: 4 }}
          >
            编辑
          </Button>
          <Button 
            danger 
            size="small"
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </>
      ),
    },
  ];

  if (error) {
    return (
      <div>
        <Alert
          message="连接错误"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={fetchStrategies}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <Card size="small">
            <Button 
              type="primary" 
              onClick={() => { setEditingStrategy(null); setModalVisible(true); }}
            >
              新建策略
            </Button>
            <span style={{ marginLeft: 16, color: '#666' }}>
              支持 Hummingbot 策略类型：纯做市、Avellaneda做市、跨交易所套利等
            </span>
          </Card>
        </Col>
      </Row>
      
      <Spin spinning={loading}>
        <Table 
          columns={columns} 
          dataSource={strategies} 
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
          }}
        />
      </Spin>
      
      <Modal
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        destroyOnClose
        title={editingStrategy ? '编辑策略' : '新建策略'}
        width={800}
      >
        <StrategyForm
          strategy={editingStrategy}
          onSuccess={() => { setModalVisible(false); fetchStrategies(); }}
        />
      </Modal>
    </div>
  );
};

export default StrategyList; 