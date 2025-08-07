import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const getHummingbotStrategies = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/hummingbot/strategies`);
    return response.data;
  } catch (error) {
    console.error('获取 Hummingbot 策略列表失败:', error);
    throw error;
  }
};

export const getStrategySchema = async (strategyType: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/hummingbot/strategies/${strategyType}/schema`);
    return response.data;
  } catch (error) {
    console.error('获取策略参数模式失败:', error);
    throw error;
  }
};

export const startHummingbotStrategy = async (strategyId: string, strategyData: any) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/hummingbot/strategies/${strategyId}/start`, strategyData);
    return response.data;
  } catch (error) {
    console.error('启动 Hummingbot 策略失败:', error);
    throw error;
  }
};

export const stopHummingbotStrategy = async (strategyId: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/hummingbot/strategies/${strategyId}/stop`);
    return response.data;
  } catch (error) {
    console.error('停止 Hummingbot 策略失败:', error);
    throw error;
  }
};

export const getHummingbotStrategyStatus = async (strategyId: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/hummingbot/strategies/${strategyId}/status`);
    return response.data;
  } catch (error) {
    console.error('获取 Hummingbot 策略状态失败:', error);
    throw error;
  }
}; 