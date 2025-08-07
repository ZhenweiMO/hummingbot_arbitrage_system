import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Select, InputNumber, Switch, message, Card, Divider, Spin, Alert } from 'antd';
import { createStrategy, updateStrategy } from '../api/strategy';
import { getHummingbotStrategies, getStrategySchema } from '../api/hummingbot';

const { Option } = Select;

interface StrategyFormProps {
  strategy?: any;
  onSuccess: () => void;
}

interface ParameterSchema {
  name: string;
  type: string;
  description: string;
  required: boolean;
  default: any;
  min_value?: number;
  max_value?: number;
  options?: string[];
  unit?: string;
}

const StrategyForm: React.FC<StrategyFormProps> = ({ strategy, onSuccess }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [availableStrategies, setAvailableStrategies] = useState<any[]>([]);
  const [selectedStrategyType, setSelectedStrategyType] = useState<string>('');
  const [parameterSchema, setParameterSchema] = useState<Record<string, ParameterSchema>>({});
  const [schemaLoading, setSchemaLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAvailableStrategies();
  }, []);

  useEffect(() => {
    if (strategy) {
      setSelectedStrategyType(strategy.type);
      form.setFieldsValue({
        name: strategy.name,
        type: strategy.type,
        params: strategy.params
      });
    }
  }, [strategy, form]);

  useEffect(() => {
    if (selectedStrategyType) {
      fetchStrategySchema(selectedStrategyType);
    }
  }, [selectedStrategyType]);

  const fetchAvailableStrategies = async () => {
    try {
      const response = await getHummingbotStrategies();
      setAvailableStrategies(response.data || []);
    } catch (error) {
      console.error('获取可用策略失败:', error);
      setError('无法获取可用策略列表');
    }
  };

  const fetchStrategySchema = async (strategyType: string) => {
    setSchemaLoading(true);
    setError(null);
    try {
      const response = await getStrategySchema(strategyType);
      setParameterSchema(response.data || {});
    } catch (error) {
      console.error('获取策略参数模式失败:', error);
      setError('无法获取策略参数模式');
    } finally {
      setSchemaLoading(false);
    }
  };

  const handleFinish = async (values: any) => {
    setLoading(true);
    try {
      const strategyData = {
        name: values.name,
        type: values.type,
        params: values.params || {}
      };

      if (strategy) {
        await updateStrategy(strategy.id, strategyData);
        message.success('策略更新成功');
      } else {
        await createStrategy(strategyData);
        message.success('策略创建成功');
      }
      onSuccess();
    } catch (error) {
      message.error('操作失败');
    } finally {
      setLoading(false);
    }
  };

  const renderParameterField = (paramName: string, paramSchema: ParameterSchema) => {
    const { type, description, required, min_value, max_value, options, unit } = paramSchema;

    switch (type) {
      case 'string':
        return (
          <Form.Item
            key={paramName}
            name={['params', paramName]}
            label={paramName}
            rules={[{ required, message: `${paramName} 是必需的` }]}
            tooltip={description}
          >
            <Input placeholder={`请输入 ${paramName}`} />
          </Form.Item>
        );

      case 'number':
        return (
          <Form.Item
            key={paramName}
            name={['params', paramName]}
            label={paramName}
            rules={[{ required, message: `${paramName} 是必需的` }]}
            tooltip={description}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={min_value}
              max={max_value}
              placeholder={`请输入 ${paramName}`}
              addonAfter={unit}
            />
          </Form.Item>
        );

      case 'boolean':
        return (
          <Form.Item
            key={paramName}
            name={['params', paramName]}
            label={paramName}
            valuePropName="checked"
            tooltip={description}
          >
            <Switch />
          </Form.Item>
        );

      case 'select':
        return (
          <Form.Item
            key={paramName}
            name={['params', paramName]}
            label={paramName}
            rules={[{ required, message: `${paramName} 是必需的` }]}
            tooltip={description}
          >
            <Select placeholder={`请选择 ${paramName}`}>
              {options?.map(option => (
                <Option key={option} value={option}>
                  {option}
                </Option>
              ))}
            </Select>
          </Form.Item>
        );

      default:
        return (
          <Form.Item
            key={paramName}
            name={['params', paramName]}
            label={paramName}
            tooltip={description}
          >
            <Input placeholder={`请输入 ${paramName}`} />
          </Form.Item>
        );
    }
  };

  if (error) {
    return (
      <Alert
        message="加载错误"
        description={error}
        type="error"
        showIcon
        action={
          <Button size="small" onClick={fetchAvailableStrategies}>
            重试
          </Button>
        }
      />
    );
  }

  return (
    <div>
      <Form
        form={form}
        onFinish={handleFinish}
        layout="vertical"
        initialValues={{
          type: selectedStrategyType,
          params: {}
        }}
      >
        <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
          <Form.Item
            name="name"
            label="策略名称"
            rules={[{ required: true, message: '请输入策略名称' }]}
          >
            <Input placeholder="请输入策略名称" />
          </Form.Item>

          <Form.Item
            name="type"
            label="策略类型"
            rules={[{ required: true, message: '请选择策略类型' }]}
          >
            <Select
              placeholder="请选择策略类型"
              onChange={setSelectedStrategyType}
              showSearch
              filterOption={(input, option) => 
                String(option?.children || '').toLowerCase().includes(input.toLowerCase())
              }
            >
              {availableStrategies.map(strategy => (
                <Option key={strategy.type} value={strategy.type}>
                  {strategy.name} - {strategy.description}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Card>

        {selectedStrategyType && (
          <Card title="策略参数" size="small">
            <Spin spinning={schemaLoading}>
              {Object.entries(parameterSchema).map(([paramName, paramSchema]) => 
                renderParameterField(paramName, paramSchema)
              )}
            </Spin>
          </Card>
        )}

        <Divider />

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            style={{ marginRight: 8 }}
          >
            {strategy ? '更新' : '创建'}
          </Button>
          <Button onClick={() => form.resetFields()}>
            重置
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default StrategyForm; 