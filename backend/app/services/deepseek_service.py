from openai import OpenAI
from typing import Dict, Any
from ..core.config import Config

class DeepSeekService:
    def __init__(self):
        """初始化DeepSeek客户端"""
        print("🚀 开始初始化DeepSeek服务...")
        
        # 调试配置
        Config.debug_print()
        
        # 检查API密钥
        if not Config.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 未设置，请检查 .env 文件")
        
        # 验证API密钥格式
        if not Config.DEEPSEEK_API_KEY.startswith('sk-'):
            raise ValueError(f"API密钥格式错误: {Config.DEEPSEEK_API_KEY[:10]}...")
        
        try:
            # 使用和测试脚本完全相同的方式初始化
            self.client = OpenAI(
                api_key=Config.DEEPSEEK_API_KEY,
                base_url=Config.DEEPSEEK_BASE_URL
            )
            self.model = Config.DEEPSEEK_MODEL
            
            print(f"✅ DeepSeek客户端初始化成功")
            print(f"   使用API密钥: {Config.DEEPSEEK_API_KEY[:10]}...")
            print(f"   Base URL: {Config.DEEPSEEK_BASE_URL}")
            print(f"   Model: {Config.DEEPSEEK_MODEL}")
            
            # 立即测试连接
            self._test_connection()
            
        except Exception as e:
            print(f"❌ DeepSeek客户端初始化失败: {e}")
            raise
    
    def _test_connection(self):
        """在初始化时测试连接"""
        try:
            print("🧪 测试DeepSeek连接...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": "Hi"}
                ],
                max_tokens=10
            )
            content = response.choices[0].message.content
            print(f"✅ 连接测试成功，AI回复: {content}")
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            raise
    
    def generate_cypher_from_text(self, user_input: str) -> Dict[str, Any]:
        """生成Cypher语句 - 使用和测试脚本相同的逻辑"""
        
        system_prompt = """你是一个专业的Neo4j Cypher查询生成助手。根据用户的自然语言描述，生成相应的Cypher语句。

规则：
1. 只返回有效的Cypher语句，不要包含额外的解释
2. 对于学者，使用标签 :Scholar，属性包括 name, affiliation, field 等
3. 对于论文，使用标签 :Paper，属性包括 title, year, citations 等
4. 对于关系，常用的有 AUTHORED, COLLABORATES_WITH, CITES 等
5. 对于学生，使用标签 :Student，属性包括 name, degree等
6. 创建节点时使用MERGE而不是CREATE，避免重复
7. 确保语句语法正确

示例：
输入："添加一个学生张三，是个硕士"
输出：MERGE (s:Student {name: "张三", degree: "master"}) RETURN s
输入："添加一个学者张三，来自清华大学"
输出：MERGE (s:Scholar {name: "张三", affiliation: "清华大学"}) RETURN s"""

        try:
            print(f"🤖 调用DeepSeek API生成Cypher...")
            print(f"   用户输入: {user_input}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            cypher_query = response.choices[0].message.content.strip()
            print(f"✅ 生成的Cypher: {cypher_query}")
            
            # 验证
            if not any(keyword in cypher_query.upper() for keyword in ['MATCH', 'CREATE', 'MERGE', 'RETURN']):
                raise ValueError("生成的不是有效的Cypher语句")
            
            return {
                "success": True,
                "cypher_query": cypher_query,
                "original_input": user_input,
                "model_used": self.model
            }
            
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return {
                "success": False,
                "error": f"生成Cypher语句失败: {str(e)}",
                "original_input": user_input
            }