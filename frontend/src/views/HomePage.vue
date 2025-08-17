<template>
  <div class="home-page">
    <h1>💖 Academic Rhizome</h1>
    <div v-if="loading" class="loading">正在从后端加载图谱数据...</div>
    <div v-if="error" class="error">加载失败: {{ error.message }}</div>
    <GraphVisualizer
      v-if="graphData.nodes.length > 0"
      class="graph-container"
      :nodes="graphData.nodes"
      :links="graphData.links"
      :categories="graphData.categories"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import GraphVisualizer from '../components/GraphVisualizer.vue';
import { getGraphData } from '../api/graph.js'; // 导入我们的API函数

// 创建响应式变量来存储数据、加载状态和错误信息
const loading = ref(true);
const error = ref(null);
const graphData = ref({ nodes: [], links: [], categories: [] });

// 在组件挂载后，执行获取数据的操作
onMounted(async () => {
  try {
    const data = await getGraphData(); // 调用API
    graphData.value = data; // 更新数据
  } catch (err) {
    error.value = err; // 记录错误
  } finally {
    loading.value = false; // 结束加载状态
  }
});
</script>

<style scoped>
.home-page {
  text-align: center;
  padding: 5px;
  height: 100vh; /* 使用全屏高度 */
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.home-page h1 {
  margin: 0 0 20px 0; /* 减少标题的上下边距 */
  flex-shrink: 0; /* 防止标题被压缩 */
}

/* 控制 GraphVisualizer 组件的容器大小 */
.graph-container {
  width: 100%; /* 使用全宽 */
  height: calc(100vh - 120px); /* 总高度减去标题和padding的高度 */
  max-height: 800px; /* 设置最大高度，避免过高 */
  min-height: 500px; /* 设置最小高度 */
  margin: 0 auto; /* 居中显示 */
}

.loading, .error {
  margin-top: 20px;
  font-size: 1.2em;
  color: #666;
}
.error {
  color: red;
}
</style>