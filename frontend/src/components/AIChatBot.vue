<template>
  <div class="ai-chatbot">
    <div class="chat-header">
      <h3>🤖 AI 图谱助手</h3>
      <div class="status-indicator" :class="{ 'connected': isConnected }">
        {{ isConnected ? '已连接' : '未连接' }}
      </div>
    </div>
    
    <!-- 对话历史 -->
    <div class="chat-history" ref="chatHistoryRef">
      <div 
        v-for="(message, index) in chatHistory" 
        :key="index" 
        class="message"
        :class="message.type"
      >
        <div class="message-content">
          <div class="message-text">{{ message.text }}</div>
          
          <!-- 显示生成的Cypher语句 -->
          <div v-if="message.cypher" class="generated-cypher">
            <label>生成的Cypher语句：</label>
            <code>{{ message.cypher }}</code>
          </div>
          
          <!-- 显示执行结果 -->
          <div v-if="message.result" class="execution-result">
            <label>执行结果：</label>
            <div class="result-summary">
              {{ message.result.success ? 
                `✅ 成功处理 ${message.result.records_count} 条记录` : 
                `❌ ${message.result.error}` 
              }}
            </div>
          </div>
        </div>
        <div class="message-time">{{ message.timestamp }}</div>
      </div>
    </div>
    
    <!-- 输入框 -->
    <div class="chat-input">
      <div class="input-group">
        <input
          v-model="currentInput"
          @keyup.enter="sendMessage"
          :disabled="isProcessing"
          placeholder="描述您想要进行的图谱操作，例如：添加一个教授..."
          class="form-control"
        />
        <button 
          @click="sendMessage" 
          :disabled="isProcessing || !currentInput.trim()"
          class="btn btn-primary"
        >
          {{ isProcessing ? '处理中...' : '发送' }}
        </button>
      </div>
    </div>
    
    <!-- 示例提示 -->
    <div class="examples" v-if="chatHistory.length === 0">
      <p>💡 试试这些示例：</p>
      <div class="example-list">
        <div 
          v-for="example in examples" 
          :key="example"
          @click="useExample(example)"
          class="example-item"
        >
          {{ example }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, nextTick, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'AIChatBot',
  emits: ['graph-updated'], // 通知父组件刷新图谱
  setup(props, { emit }) {
    const currentInput = ref('')
    const isProcessing = ref(false)
    const isConnected = ref(false)
    const chatHistoryRef = ref(null)
    
    const chatHistory = reactive([])
    
    const examples = [
      "添加一个教授，姓名是任民，任教于北京邮电大学",
      "创建一篇论文，标题是《深度学习在图像识别中的应用》",
      "建立张三教授和李四教授的合作关系",
      "查询所有来自清华大学的学者",
      "删除名为张三的学者节点"
    ]
    
    // 检查连接状态
    const checkConnection = async () => {
      try {
        await axios.get('/api/ping')
        isConnected.value = true
      } catch {
        isConnected.value = false
      }
    }
    
    // 发送消息
    const sendMessage = async () => {
      if (!currentInput.value.trim() || isProcessing.value) return
      
      const userMessage = currentInput.value.trim()
      
      // 添加用户消息到历史
      addMessage('user', userMessage)
      currentInput.value = ''
      isProcessing.value = true
      
      try {
        const response = await axios.post('/api/ai-cypher', {
          user_input: userMessage
        })
        
        const result = response.data
        
        // 添加AI回复到历史
        addMessage('assistant', 
          result.success ? '操作已完成！' : `操作失败: ${result.error}`,
          result.generated_cypher,
          result.execution_result
        )
        
        // 如果成功，通知父组件刷新图谱
        if (result.success) {
          emit('graph-updated')
        }
        
      } catch (error) {
        addMessage('assistant', 
          `处理失败: ${error.response?.data?.error || '网络错误'}`
        )
      } finally {
        isProcessing.value = false
        scrollToBottom()
      }
    }
    
    // 添加消息到历史
    const addMessage = (type, text, cypher = null, result = null) => {
      chatHistory.push({
        type,
        text,
        cypher,
        result,
        timestamp: new Date().toLocaleTimeString()
      })
    }
    
    // 使用示例
    const useExample = (example) => {
      currentInput.value = example
    }
    
    // 滚动到底部
    const scrollToBottom = async () => {
      await nextTick()
      if (chatHistoryRef.value) {
        chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
      }
    }
    
    onMounted(() => {
      checkConnection()
    })
    
    return {
      currentInput,
      isProcessing,
      isConnected,
      chatHistory,
      chatHistoryRef,
      examples,
      sendMessage,
      useExample
    }
  }
}
</script>

<style scoped>
.ai-chatbot {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8px 8px 0 0;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
}

.status-indicator {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  background: rgba(255,255,255,0.2);
}

.status-indicator.connected {
  background: rgba(76, 175, 80, 0.8);
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  max-height: 400px;
}

.message {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
  max-width: 90%;
}

.message.user {
  background: #e3f2fd;
  margin-left: auto;
  border-bottom-right-radius: 4px;
}

.message.assistant {
  background: #f5f5f5;
  margin-right: auto;
  border-bottom-left-radius: 4px;
}

.message-text {
  margin-bottom: 8px;
}

.generated-cypher {
  margin-top: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-left: 3px solid #007bff;
  border-radius: 4px;
}

.generated-cypher label {
  font-weight: 600;
  font-size: 12px;
  color: #495057;
  display: block;
  margin-bottom: 4px;
}

.generated-cypher code {
  font-family: 'Consolas', monospace;
  font-size: 13px;
  word-break: break-all;
}

.execution-result {
  margin-top: 8px;
  padding: 8px;
  border-radius: 4px;
}

.execution-result label {
  font-weight: 600;
  font-size: 12px;
  display: block;
  margin-bottom: 4px;
}

.result-summary {
  font-size: 13px;
}

.message-time {
  font-size: 11px;
  color: #666;
  margin-top: 4px;
  text-align: right;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #eee;
}

.input-group {
  display: flex;
  gap: 8px;
}

.input-group input {
  flex: 1;
}

.examples {
  padding: 16px;
  border-top: 1px solid #eee;
  background: #fafafa;
}

.examples p {
  margin: 0 0 12px 0;
  font-weight: 600;
  color: #495057;
}

.example-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.example-item {
  padding: 8px 12px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.example-item:hover {
  background: #e3f2fd;
  border-color: #2196f3;
}

/* 通用样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
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

.form-control {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}
</style>