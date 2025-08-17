<template>
  <div class="home-page">
    <h1>💖 Academic Rhizome</h1>
    <div class="main-layout">
      <!-- 左侧图谱区域 -->
      <div class="graph-section">
        <div v-if="loading" class="loading">正在从后端加载图谱数据...</div>
        <div v-if="error" class="error">加载失败: {{ error.message }}</div>
        <GraphVisualizer
          v-if="graphData.nodes.length > 0"
          class="graph-container"
          :nodes="graphData.nodes"
          :links="graphData.links"
          :categories="graphData.categories"
          @graph-updated="refreshGraph"
        />
      </div>

      
      <!-- 右上：AI助手 -->
      <!-- <div class="right-panel">
        <div class="ai-section">
          <AIChatBot @graph-updated="refreshGraph" />
        </div>
        <div class="cypher-section" v-if="showCypherConsole">
          <CypherConsole />
        </div>
      </div> -->


    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import GraphVisualizer from '../components/GraphVisualizer.vue';
import CypherConsole from '../components/CypherConsole.vue';
import AIChatBot from '../components/AIChatBot.vue';
import { getGraphData } from '../api/graph.js'; // 导入我们的API函数

// 创建响应式变量来存储数据、加载状态和错误信息
const loading = ref(true);
const error = ref(null);
const graphData = ref({ nodes: [], links: [], categories: [] });
const showCypherConsole = ref(true); // 控制Cypher控制台的显示与隐藏

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

// 刷新图谱的函数
function refreshGraph() {
  loading.value = true;
  error.value = null;
  getGraphData()
    .then(data => {
      graphData.value = data;
    })
    .catch(err => {
      error.value = err;
    })
    .finally(() => {
      loading.value = false;
    });
}
</script>

<style scoped>
.home-page {
  text-align: center;
  padding: 20px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.home-page h1 {
  margin: 0 0 20px 0;
  flex-shrink: 0;
}

.main-layout {
  flex: 1;
  display: flex;
  gap: 10px;
  height: calc(100vh - 120px);
  min-height: 500px;
}

.graph-section {
  flex: 7; /* 占据7/8的宽度 */
  display: flex;
  flex-direction: column;
}

.right-panel {
  flex: 1; /* 占据1/8的宽度 */
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
}

.cypher-section {
  flex: 1; /* 占据1/8的宽度 */
  min-width: 300px; /* 设置最小宽度确保可用性 */
  max-width: 400px; /* 设置最大宽度避免过宽 */
}

.graph-container {
  width: 100%;
  height: 100%;
  flex: 1;
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