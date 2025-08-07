import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const getAccounts = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/accounts`);
    return response.data;
  } catch (error) {
    console.error('获取账户列表失败:', error);
    throw error; // 抛出错误而不是返回 mock 数据
  }
};

export const createAccount = async (account: any) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/accounts`, account);
    return response.data;
  } catch (error) {
    console.error('创建账户失败:', error);
    throw error;
  }
};

export const updateAccount = async (id: number, account: any) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/accounts/${id}`, account);
    return response.data;
  } catch (error) {
    console.error('更新账户失败:', error);
    throw error;
  }
};

export const deleteAccount = async (id: number) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/accounts/${id}`);
    return response.data;
  } catch (error) {
    console.error('删除账户失败:', error);
    throw error;
  }
}; 