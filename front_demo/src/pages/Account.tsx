import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, message, Popconfirm, Alert, Spin } from 'antd';
import { getAccounts, deleteAccount } from '../api/account';
import AccountForm from '../components/AccountForm';
import { maskApiKey } from '../utils/maskUtils';

const Account: React.FC = () => {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingAccount, setEditingAccount] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAccounts();
      setAccounts(data);
    } catch (error: any) {
      console.error('获取账户列表失败:', error);
      setError('无法连接到后端服务，请检查服务是否正常运行');
      message.error('获取账户列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteAccount(id);
      message.success('账户已删除');
      fetchAccounts(); // 重新获取列表
    } catch (error) {
      message.error('删除账户失败，请检查后端服务状态');
    }
  };

  const handleSuccess = () => {
    setModalVisible(false);
    setEditingAccount(null);
    fetchAccounts(); // 重新获取列表
  };

  const handleCancel = () => {
    setModalVisible(false);
    setEditingAccount(null);
  };

  const columns = [
    { title: '交易所', dataIndex: 'name' },
    { 
      title: 'API Key', 
      dataIndex: 'api_key',
      render: (apiKey: string) => maskApiKey(apiKey)
    },
    { title: '余额', dataIndex: 'balance' },
    { title: '持仓', dataIndex: 'position' },
    {
      title: '操作',
      render: (_: any, record: any) => (
        <>
          <Button 
            onClick={() => { 
              setEditingAccount(record); 
              setModalVisible(true); 
            }}
            style={{ marginRight: 8 }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个账户吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button danger>删除</Button>
          </Popconfirm>
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
            <Button size="small" onClick={fetchAccounts}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div>
      <Button 
        type="primary" 
        onClick={() => { 
          setEditingAccount(null); 
          setModalVisible(true); 
        }}
        style={{ marginBottom: 16 }}
      >
        新增账户
      </Button>
      <Spin spinning={loading}>
        <Table columns={columns} dataSource={accounts} rowKey="id" />
      </Spin>
      <Modal
        open={modalVisible}
        onCancel={handleCancel}
        footer={null}
        destroyOnClose
        title={editingAccount ? '编辑账户' : '新增账户'}
        width={600}
      >
        <AccountForm
          account={editingAccount}
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      </Modal>
    </div>
  );
};

export default Account; 