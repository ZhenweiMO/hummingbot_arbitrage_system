import React, { useState } from 'react';
import { Form, Input, Button, message, Switch, Select, Typography, Alert } from 'antd';
import { EyeOutlined, EyeInvisibleOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { createAccount, updateAccount } from '../api/account';
import { maskApiKey } from '../utils/maskUtils';

const { Title, Text } = Typography;
const { Option } = Select;

interface AccountFormProps {
  account?: any;
  onSuccess: () => void;
  onCancel: () => void;
}

const AccountForm: React.FC<AccountFormProps> = ({ account, onSuccess, onCancel }) => {
  const [form] = Form.useForm();
  const [showApiKey, setShowApiKey] = useState(false);
  const [showApiSecret, setShowApiSecret] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedExchange, setSelectedExchange] = useState(account?.exchange_type || '');

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

  // 渲染 API Secret 输入框
  const renderApiSecretInput = () => {
    if (account && !showApiSecret) {
      // 编辑模式且隐藏状态，显示掩码后的值
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Input
            value={maskApiKey(account.api_secret || '')}
            disabled
            style={{ flex: 1 }}
          />
          <Switch
            checkedChildren={<EyeOutlined />}
            unCheckedChildren={<EyeInvisibleOutlined />}
            checked={showApiSecret}
            onChange={setShowApiSecret}
          />
        </div>
      );
    }

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Form.Item
          name="api_secret"
          noStyle
          rules={[{ required: true, message: '请输入API Secret' }]}
        >
          <Input.Password
            placeholder="请输入API Secret"
            style={{ flex: 1 }}
          />
        </Form.Item>
        {account && (
          <Switch
            checkedChildren={<EyeOutlined />}
            unCheckedChildren={<EyeInvisibleOutlined />}
            checked={showApiSecret}
            onChange={setShowApiSecret}
          />
        )}
      </div>
    );
  };

  return (
    <div>
      {!account && (
        <Alert
          message="添加交易所账户"
          description="请配置您的交易所 API 密钥以获取实时余额和进行交易。系统将自动获取账户余额，无需手动输入。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Form
        form={form}
        onFinish={handleFinish}
        layout="vertical"
        initialValues={account ? {
          ...account,
          balance: undefined, // 不显示余额，由系统自动获取
          position: undefined // 不显示持仓，由系统自动获取
        } : {}}
      >
        <Form.Item
          name="exchange_type"
          label="交易所类型"
          rules={[{ required: true, message: '请选择交易所类型' }]}
        >
          <Select
            placeholder="请选择交易所"
            onChange={setSelectedExchange}
            disabled={!!account} // 编辑时不允许修改交易所类型
          >
            <Option value="binance">Binance - 全球最大的加密货币交易所</Option>
            <Option value="okx">OKX - 专业的数字资产交易平台</Option>
            <Option value="bybit">Bybit - 专业的衍生品交易平台</Option>
            <Option value="gate_io">Gate.io - 老牌数字资产交易所</Option>
            <Option value="kucoin">KuCoin - 加密货币交易所</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="name"
          label="账户名称"
          rules={[{ required: true, message: '请输入账户名称' }]}
        >
          <Input placeholder="如：我的Binance账户" />
        </Form.Item>

        <Form.Item
          name="api_key"
          label="API Key"
          rules={[{ required: true, message: '请输入API Key' }]}
        >
          {renderApiKeyInput()}
        </Form.Item>

        <Form.Item
          name="api_secret"
          label="API Secret"
          rules={[{ required: true, message: '请输入API Secret' }]}
        >
          {renderApiSecretInput()}
        </Form.Item>

        {selectedExchange === 'okx' && (
          <Form.Item
            name="passphrase"
            label="API Passphrase"
            rules={[{ required: true, message: '请输入API Passphrase' }]}
          >
            <Input.Password placeholder="请输入API Passphrase" />
          </Form.Item>
        )}

        {account && (
          <>
            <Form.Item
              name="balance"
              label="当前余额"
            >
              <Input 
                disabled 
                placeholder="系统自动获取"
                addonAfter="USDT"
              />
            </Form.Item>

            <Form.Item
              name="position"
              label="当前持仓"
            >
              <Input 
                disabled 
                placeholder="系统自动获取"
              />
            </Form.Item>
          </>
        )}

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            style={{ marginRight: 8 }}
            loading={loading}
          >
            {account ? '更新账户' : '添加账户'}
          </Button>
          <Button onClick={onCancel} disabled={loading}>
            取消
          </Button>
        </Form.Item>
      </Form>

      {!account && (
        <div style={{ marginTop: 16, padding: 12, backgroundColor: '#f6f8fa', borderRadius: 6 }}>
          <Title level={5}>
            <InfoCircleOutlined style={{ marginRight: 8 }} />
            如何获取 API 密钥？
          </Title>
          <div style={{ fontSize: 14, lineHeight: 1.6 }}>
            <div style={{ marginBottom: 8 }}>
              <Text strong>Binance:</Text>
              <br />
              <Text type="secondary">登录 Binance → 安全中心 → API 管理 → 创建 API</Text>
            </div>
            <div style={{ marginBottom: 8 }}>
              <Text strong>OKX:</Text>
              <br />
              <Text type="secondary">登录 OKX → 设置 → API 管理 → 创建 API</Text>
            </div>
            <div>
              <Text type="secondary">
                注意：请确保 API 密钥具有交易权限，并设置适当的 IP 白名单。
              </Text>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AccountForm; 