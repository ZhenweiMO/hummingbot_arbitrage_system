import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

export const getSymbols = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/markets/symbols`);
    return response.data;
  } catch (error) {
    console.error('获取交易对列表失败:', error);
    throw error; // 抛出错误而不是返回 mock 数据
  }
};

export const getKline = async (symbol: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/markets/kline`, {
      params: { symbol }
    });
    return response.data;
  } catch (error) {
    console.error('获取K线数据失败:', error);
    throw error; // 抛出错误而不是返回 mock 数据
  }
};

export const getOrderBook = async (symbol: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/markets/orderbook`, {
      params: { symbol }
    });
    return response.data;
  } catch (error) {
    console.error('获取订单簿失败:', error);
    throw error; // 抛出错误而不是返回 mock 数据
  }
}; 