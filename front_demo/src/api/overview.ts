import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const getOverview = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/overview`);
    return response.data;
  } catch (error) {
    console.error('获取总览数据失败:', error);
    throw error; // 抛出错误而不是返回 mock 数据
  }
}; 