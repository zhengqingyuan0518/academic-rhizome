# app/routes/api.py
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from ..models.schemas import NLPQueryRequest, BaseResponseModel
# 注意，我们从.services导入具体的服务类
from ..services.graph_service import GraphService
from ..services.llm_service import LLMService

# 使用 Flask 的 "蓝图" (Blueprint) 来组织路由，实现模块化
api_blueprint = Blueprint('api', __name__, url_prefix='/api')

# 全局服务实例，将在应用工厂中被初始化
graph_service: GraphService = None
llm_service: LLMService = None

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