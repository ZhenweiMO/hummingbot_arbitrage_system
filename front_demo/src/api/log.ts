import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const getLogs = async (strategyId?: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/logs`, {
      params: { strategy_id: strategyId }
    });
    return response.data;
  } catch (error) {
    console.error('获取日志失败:', error);
    throw error; // 抛出错误而不是返回 mock 数据
  }
};

export const getTrades = async (strategyId?: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/trades`, {
      params: { strategy_id: strategyId }
    });
    return response.data;
  } catch (error) {
    console.error('获取交易记录失败:', error);
    throw error; // 抛出错误而不是返回 mock 数据
  }
}; 