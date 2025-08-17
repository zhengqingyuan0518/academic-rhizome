<template>
  <div class="cypher-console">
    <div class="console-header">
      <h3>Cypher 控制台</h3>
      <div class="header-actions">
        <button @click="clearQuery" class="btn btn-secondary btn-sm">清空</button>
        <button @click="clearResults" class="btn btn-secondary btn-sm">清空结果</button>
      </div>
    </div>
    
    <!-- 查询输入区域 -->
    <div class="query-section">
      <div class="query-input">
        <textarea
          v-model="cypherQuery"
          placeholder="输入Cypher查询语句..."
          rows="4"
          class="form-control"
          @keydown.ctrl.enter="executeQuery"
        ></textarea>
      </div>
      
      <!-- 参数输入 -->
      <div class="parameters-section" v-if="showParameters">
        <label>参数 (JSON格式):</label>
        <textarea
          v-model="parametersJson"
          placeholder='{"param1": "value1", "param2": 123}'
          rows="2"
          class="form-control"
        ></textarea>
      </div>
      
      <div class="query-actions">
        <button @click="executeQuery" :disabled="isExecuting" class="btn btn-primary">
          <span v-if="isExecuting">执行中...</span>
          <span v-else>执行 (Ctrl+Enter)</span>
        </button>
        <button @click="showParameters = !showParameters" class="btn btn-secondary">
          {{ showParameters ? '隐藏参数' : '显示参数' }}
        </button>
      </div>
    </div>
    
    <!-- 结果显示区域 -->
    <div class="results-section">
      <div class="results-header">
        <h4>查询结果</h4>
        <div class="result-stats" v-if="lastResult">
          <span class="badge badge-info">{{ lastResult.summary.records_count }} 条记录</span>
          <span class="badge badge-secondary">{{ lastResult.summary.query_type }}</span>
        </div>
      </div>
      
      <!-- 错误信息 -->
      <div v-if="error" class="error-message">
        <div class="alert alert-danger">
          <strong>错误:</strong> {{ error }}
        </div>
      </div>
      
      <!-- 成功结果 -->
      <div v-if="lastResult && lastResult.success" class="results-content">
        <!-- 操作统计 -->
        <div v-if="lastResult.summary.counters && Object.keys(lastResult.summary.counters).length > 0" 
             class="operation-stats">
          <div class="stats-grid">
            <div v-for="(value, key) in lastResult.summary.counters" :key="key" class="stat-item">
              <span class="stat-label">{{ formatCounterKey(key) }}:</span>
              <span class="stat-value">{{ value }}</span>
            </div>
          </div>
        </div>
        
        <!-- 数据表格 -->
        <div v-if="lastResult.data.length > 0" class="data-table">
          <table class="table table-striped table-sm">
            <thead>
              <tr>
                <th v-for="key in lastResult.summary.keys" :key="key">{{ key }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in lastResult.data" :key="index">
                <td v-for="key in lastResult.summary.keys" :key="key">
                  <div class="cell-content">
                    {{ formatCellValue(row[key]) }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- 无数据提示 -->
        <div v-else class="no-data">
          <p class="text-muted">查询执行成功，但没有返回数据。</p>
        </div>
      </div>
    </div>
    
    <!-- 常用查询示例 -->
    <div class="examples-section">
      <details>
        <summary>常用查询示例</summary>
        <div class="examples-grid">
          <div class="example-item" @click="useExample(example)" v-for="example in queryExamples" :key="example.name">
            <div class="example-name">{{ example.name }}</div>
            <div class="example-query">{{ example.query }}</div>
          </div>
        </div>
      </details>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import axios from 'axios'

export default {
  name: 'CypherConsole',
  setup() {
    const cypherQuery = ref('')
    const parametersJson = ref('{}')
    const showParameters = ref(false)
    const isExecuting = ref(false)
    const lastResult = ref(null)
    const error = ref('')
    
    const queryExamples = reactive([
      {
        name: '查看所有节点类型',
        query: 'MATCH (n) RETURN DISTINCT labels(n) as labels, count(n) as count'
      },
      {
        name: '查看所有关系类型',
        query: 'MATCH ()-[r]->() RETURN DISTINCT type(r) as relationship_type, count(r) as count'
      },
      {
        name: '查看前10个节点',
        query: 'MATCH (n) RETURN n LIMIT 10'
      },
      {
        name: '创建测试节点',
        query: 'CREATE (n:TestNode {name: "测试节点", created: datetime()}) RETURN n'
      },
      {
        name: '删除测试节点',
        query: 'MATCH (n:TestNode) DELETE n'
      },
      {
        name: '查看数据库统计',
        query: 'CALL db.stats.retrieve("GRAPH COUNTS")'
      }
    ])
    
    const executeQuery = async () => {
      if (!cypherQuery.value.trim()) {
        error.value = '请输入Cypher查询语句'
        return
      }
      
      isExecuting.value = true
      error.value = ''
      
      try {
        let parameters = {}
        if (showParameters.value && parametersJson.value.trim()) {
          try {
            parameters = JSON.parse(parametersJson.value)
          } catch (e) {
            error.value = '参数JSON格式错误'
            isExecuting.value = false
            return
          }
        }
        
        const response = await axios.post('/api/cypher', {
          query: cypherQuery.value,
          parameters: parameters
        })
        
        lastResult.value = response.data
        
      } catch (err) {
        if (err.response && err.response.data) {
          error.value = err.response.data.error || '查询执行失败'
        } else {
          error.value = '网络错误或服务器无响应'
        }
        lastResult.value = null
      } finally {
        isExecuting.value = false
      }
    }
    
    const clearQuery = () => {
      cypherQuery.value = ''
      parametersJson.value = '{}'
    }
    
    const clearResults = () => {
      lastResult.value = null
      error.value = ''
    }
    
    const useExample = (example) => {
      cypherQuery.value = example.query
    }
    
    const formatCellValue = (value) => {
      if (value === null || value === undefined) {
        return 'null'
      }
      
      if (typeof value === 'object') {
        if (value.type === 'node') {
          return `节点[${value.labels.join(', ')}]: ${JSON.stringify(value.properties)}`
        } else if (value.type === 'relationship') {
          return `关系[${value.type_name}]: ${JSON.stringify(value.properties)}`
        }
        return JSON.stringify(value, null, 2)
      }
      
      return String(value)
    }
    
    const formatCounterKey = (key) => {
      const keyMap = {
        'nodes_created': '创建节点',
        'nodes_deleted': '删除节点',
        'relationships_created': '创建关系',
        'relationships_deleted': '删除关系',
        'properties_set': '设置属性',
        'labels_added': '添加标签',
        'labels_removed': '移除标签'
      }
      return keyMap[key] || key
    }
    
    return {
      cypherQuery,
      parametersJson,
      showParameters,
      isExecuting,
      lastResult,
      error,
      queryExamples,
      executeQuery,
      clearQuery,
      clearResults,
      useExample,
      formatCellValue,
      formatCounterKey
    }
  }
}
</script>

<style scoped>
.cypher-console {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.console-header {
  background: #343a40;
  color: white;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.console-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.query-section {
  padding: 16px;
  border-bottom: 1px solid #dee2e6;
}

.query-input {
  margin-bottom: 12px;
}

.query-input textarea {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  resize: vertical;
  min-height: 80px;
}

.parameters-section {
  margin-bottom: 12px;
}

.parameters-section label {
  font-weight: 600;
  margin-bottom: 4px;
  display: block;
}

.parameters-section textarea {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
}

.query-actions {
  display: flex;
  gap: 8px;
}

.results-section {
  flex: 1;
  padding: 16px;
  overflow: auto;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.results-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.result-stats {
  display: flex;
  gap: 8px;
}

.operation-stats {
  background: #e3f2fd;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
}

.stat-label {
  font-weight: 600;
}

.stat-value {
  color: #1976d2;
  font-weight: 600;
}

.data-table {
  max-height: 400px;
  overflow: auto;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.table {
  margin: 0;
  font-size: 12px;
}

.table th {
  background: #f8f9fa;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
}

.cell-content {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.error-message {
  margin-bottom: 16px;
}

.no-data {
  text-align: center;
  padding: 32px;
}

.examples-section {
  border-top: 1px solid #dee2e6;
  padding: 16px;
}

.examples-section summary {
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 12px;
}

.examples-grid {
  display: grid;
  gap: 8px;
}

.example-item {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.example-item:hover {
  background: #f8f9fa;
  border-color: #007bff;
}

.example-name {
  font-weight: 600;
  font-size: 12px;
  color: #495057;
  margin-bottom: 4px;
}

.example-query {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 11px;
  color: #6c757d;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Bootstrap-like classes */
.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 13px;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.alert {
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.alert-danger {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.badge-info {
  background: #17a2b8;
  color: white;
}

.badge-secondary {
  background: #6c757d;
  color: white;
}

.text-muted {
  color: #6c757d;
}
</style>
