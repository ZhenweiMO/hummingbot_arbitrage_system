import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

export const getStrategies = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/strategies`);
    return response.data;
  } catch (error) {
    console.error('获取策略列表失败:', error);
    throw error; // 抛出错误而不是返回 mock 数据
  }
};

export const createStrategy = async (strategy: any) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/strategies`, strategy);
    return response.data;
  } catch (error) {
    console.error('创建策略失败:', error);
    throw error;
  }
};

export const updateStrategy = async (id: number, strategy: any) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/strategies/${id}`, strategy);
    return response.data;
  } catch (error) {
    console.error('更新策略失败:', error);
    throw error;
  }
};

export const startStrategy = async (id: number) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/strategies/${id}/start`);
    return response.data;
  } catch (error) {
    console.error('启动策略失败:', error);
    throw error;
  }
};

export const stopStrategy = async (id: number) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/strategies/${id}/stop`);
    return response.data;
  } catch (error) {
    console.error('停止策略失败:', error);
    throw error;
  }
};

export const deleteStrategy = async (id: number) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/strategies/${id}`);
    return response.data;
  } catch (error) {
    console.error('删除策略失败:', error);
    throw error;
  }
}; 