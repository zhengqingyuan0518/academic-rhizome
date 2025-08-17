// frontend/src/api/graph.js
import axios from 'axios';

// 基础URL不再需要IP和端口了！
const apiClient = axios.create({
  baseURL: '/', // 或者直接留空
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getGraphData = async () => {
  try {
    // 请求的地址直接写 /api/graph-data 即可
    const response = await apiClient.get('/api/graph-data');
    // 在控制台打印返回的数据，方便调试
    console.log('从后端获取的图谱数据:', response.data);
    return response.data;
  } catch (error) {
    console.error('获取图谱数据失败:', error);
    throw error;
  }
};