# app/routes/api.py
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from ..models.schemas import NLPQueryRequest, BaseResponseModel
# 注意，我们从.services导入具体的服务类
from ..services.graph_service import GraphService
from ..services.llm_service import LLMService
from ..services.deepseek_service import DeepSeekService
from ..services.deepseek_service import DeepSeekService

# 使用 Flask 的 "蓝图" (Blueprint) 来组织路由，实现模块化
api_blueprint = Blueprint('api', __name__, url_prefix='/api')

# 全局服务实例，将在应用工厂中被初始化
graph_service: GraphService = None
llm_service: LLMService = None
deepseek_service: DeepSeekService = None

@api_blueprint.route('/ping', methods=['GET'])
def ping():
    """一个简单的测试端点"""
    return jsonify(BaseResponseModel(message="pong!").model_dump())

@api_blueprint.route('/db-test', methods=['GET'])
def db_test():
    """测试数据库连接和获取节点总数"""
    node_count = graph_service.get_node_count()
    if node_count >= 0:
        return jsonify(BaseResponseModel(message=f"成功连接到Neo4j，数据库中共有 {node_count} 个节点。").model_dump())
    else:
        return jsonify(BaseResponseModel(status="error", message="数据库连接失败").model_dump()), 500

@api_blueprint.route('/query', methods=['POST'])
def query_handler():
    """处理自然语言查询的端点"""
    try:
        query_request = NLPQueryRequest(**request.json)
        # 1. 调用LLM服务解析实体
        entities = llm_service.parse_text_to_entities(query_request.query_text)
        # 2. (未来) 调用Graph服务进行图查询或更新
        # graph_service.process_entities(entities)
        return jsonify(entities)
    except ValidationError as e:
        return jsonify(BaseResponseModel(status="error", message=f"请求体校验失败: {e.errors()}").model_dump()), 400
    except Exception as e:
        return jsonify(BaseResponseModel(status="error", message=f"处理请求时发生错误: {str(e)}").model_dump()), 500
    
@api_blueprint.route('/graph-data', methods=['GET'])
def get_graph_data():
    """从Neo4j获取真实数据并返回给前端"""
    # 从服务层调用函数获取ECharts格式的数据
    data = graph_service.get_graph_for_echarts(node_limit=50) # 可以调整查询数量
    return jsonify(data)

@api_blueprint.route('/cypher', methods=['POST'])
def execute_cypher():
    """执行Cypher查询语句"""
    try:
        request_data = request.json
        cypher_query = request_data.get('query', '').strip()
        parameters = request_data.get('parameters', {})
        
        if not cypher_query:
            return jsonify({
                "success": False,
                "error": "Cypher查询语句不能为空",
                "data": [],
                "summary": {}
            }), 400
        
        # 执行查询
        result = graph_service.execute_cypher_query(cypher_query, parameters)
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"执行Cypher查询时发生错误: {str(e)}",
            "data": [],
            "summary": {}
        }), 500

@api_blueprint.route('/ai-cypher', methods=['POST'])
def ai_generate_and_execute_cypher():
    """AI生成Cypher语句并执行"""
    try:
        print("🚀 收到AI-Cypher请求")
        
        request_data = request.json
        user_input = request_data.get('user_input', '').strip()
        
        print(f"📝 用户输入: {user_input}")
        
        if not user_input:
            return jsonify({
                "success": False,
                "error": "用户输入不能为空",
                "step": "validation"
            }), 400
        
        # 检查DeepSeek服务
        print(f"🔍 检查DeepSeek服务状态: {deepseek_service is not None}")
        
        if deepseek_service is None:
            return jsonify({
                "success": False,
                "error": "DeepSeek服务未初始化，请检查API密钥配置",
                "step": "service_check"
            }), 500
        
        print("🤖 调用DeepSeek服务...")
        ai_result = deepseek_service.generate_cypher_from_text(user_input)
        
        print(f"📊 AI结果: {ai_result}")
        
        if not ai_result["success"]:
            return jsonify({
                "success": False,
                "error": ai_result["error"],
                "step": "ai_generation",
                "user_input": user_input
            }), 400
        
        cypher_query = ai_result["cypher_query"]
        
        # 步骤2：执行生成的Cypher语句
        execution_result = graph_service.execute_cypher_query(cypher_query)
        
        # 返回完整结果
        return jsonify({
            "success": execution_result["success"],
            "user_input": user_input,
            "generated_cypher": cypher_query,
            "execution_result": execution_result,
            "ai_model": ai_result.get("model_used", "unknown")
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"处理请求时发生错误: {str(e)}",
            "step": "general_error"
        }), 500
