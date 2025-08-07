import React, { useState, useEffect } from 'react';
import { Table, Tabs, Alert, Spin, Button } from 'antd';
import { getLogs, getTrades } from '../api/log';

const Log: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [logsData, tradesData] = await Promise.all([
        getLogs(),
        getTrades()
      ]);
      setLogs(logsData);
      setTrades(tradesData);
    } catch (error: any) {
      console.error('获取数据失败:', error);
      setError('无法连接到后端服务，请检查服务是否正常运行');
    } finally {
      setLoading(false);
    }
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
            <Button size="small" onClick={fetchData}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <Spin spinning={loading}>
      <Tabs defaultActiveKey="log">
        <Tabs.TabPane tab="运行日志" key="log">
          <Table
            columns={[
              { title: '时间', dataIndex: 'created_at', render: (time: string) => new Date(time).toLocaleString() },
              { title: '级别', dataIndex: 'level' },
              { title: '内容', dataIndex: 'message' },
            ]}
            dataSource={logs}
            rowKey="id"
          />
        </Tabs.TabPane>
        <Tabs.TabPane tab="交易记录" key="trade">
          <Table
            columns={[
              { title: '时间', dataIndex: 'created_at', render: (time: string) => new Date(time).toLocaleString() },
              { title: '交易对', dataIndex: 'symbol' },
              { title: '方向', dataIndex: 'side' },
              { title: '价格', dataIndex: 'price' },
              { title: '数量', dataIndex: 'amount' },
            ]}
            dataSource={trades}
            rowKey="id"
          />
        </Tabs.TabPane>
      </Tabs>
    </Spin>
  );
};

export default Log; 