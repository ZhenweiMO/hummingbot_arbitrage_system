import React, { useState } from 'react';
import { Form, Input, Button, message, Switch } from 'antd';
import { EyeOutlined, EyeInvisibleOutlined } from '@ant-design/icons';
import { createAccount, updateAccount } from '../api/account';
import { maskApiKey } from '../utils/maskUtils';

interface AccountFormProps {
  account?: any;
  onSuccess: () => void;
  onCancel: () => void;
}

const AccountForm: React.FC<AccountFormProps> = ({ account, onSuccess, onCancel }) => {
  const [form] = Form.useForm();
  const [showApiKey, setShowApiKey] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleFinish = async (values: any) => {
    setLoading(true);
    try {
      if (account) {
        // 编辑模式
        await updateAccount(account.id, { ...values, id: account.id });
        message.success('账户更新成功');
      } else {
        // 新增模式
        await createAccount({ ...values, id: Date.now() }); // Temporary client-side ID
        message.success('账户创建成功');
      }
      onSuccess();
    } catch (error) {
      message.error('操作失败');
    } finally {
      setLoading(false);
    }
  };

  // 渲染 API Key 输入框
  const renderApiKeyInput = () => {
    if (account && !showApiKey) {
      // 编辑模式且隐藏状态，显示掩码后的值
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Input
            value={maskApiKey(account.api_key || '')}
            disabled
            style={{ flex: 1 }}
          />
          <Switch
            checkedChildren={<EyeOutlined />}
            unCheckedChildren={<EyeInvisibleOutlined />}
            checked={showApiKey}
            onChange={setShowApiKey}
          />
        </div>
      );
    }

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Form.Item
          name="api_key"
          noStyle
          rules={[{ required: true, message: '请输入API Key' }]}
        >
          <Input.Password
            placeholder="请输入API Key"
            style={{ flex: 1 }}
          />
        </Form.Item>
        {account && (
          <Switch
            checkedChildren={<EyeOutlined />}
            unCheckedChildren={<EyeInvisibleOutlined />}
            checked={showApiKey}
            onChange={setShowApiKey}
          />
        )}
      </div>
    );
  };

  return (
    <Form
      form={form}
      onFinish={handleFinish}
      initialValues={account}
      layout="vertical"
    >
      <Form.Item
        name="name"
        label="交易所名称"
        rules={[{ required: true, message: '请输入交易所名称' }]}
      >
        <Input placeholder="如：Binance" />
      </Form.Item>

      <Form.Item
        name="api_key"
        label="API Key"
        rules={[{ required: true, message: '请输入API Key' }]}
      >
        {renderApiKeyInput()}
      </Form.Item>

      <Form.Item
        name="balance"
        label="余额"
        rules={[{ required: true, message: '请输入余额' }]}
      >
        <Input type="number" placeholder="如：10000" />
      </Form.Item>

      <Form.Item
        name="position"
        label="持仓"
        rules={[{ required: true, message: '请输入持仓信息' }]}
      >
        <Input placeholder="如：BTC: 0.5" />
      </Form.Item>

      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          style={{ marginRight: 8 }}
          loading={loading}
        >
          {account ? '更新' : '创建'}
        </Button>
        <Button onClick={onCancel} disabled={loading}>取消</Button>
      </Form.Item>
    </Form>
  );
};

export default AccountForm; 