# app/__init__.py
from flask import Flask
from flask_cors import CORS
from neo4j import GraphDatabase
from .core.config import Config
from .services.graph_service import GraphService
from .services.llm_service import LLMService  # 添加这行导入
from .services.deepseek_service import DeepSeekService
# 导入蓝图和需要初始化的服务实例
from .routes import api as api_routes

def create_app():
    """
    应用工厂函数: 创建并配置Flask应用
    """
    app = Flask(__name__)
    CORS(app) # 为所有路由启用CORS

    # 1. 从config对象加载配置
    app.config.from_object(Config)

    # 2. 初始化数据库驱动
    # 我们在这里创建唯一的driver实例，并传递给服务层
    driver = GraphDatabase.driver(
        app.config['NEO4J_URI'],
        auth=(app.config['NEO4J_USER'], app.config['NEO4J_PASSWORD'])
    )
    driver.close_on_exit = True

    # 3. 初始化所有服务
    # 将driver实例注入到GraphService中
    api_routes.graph_service = GraphService(driver)
    api_routes.llm_service = LLMService() # 重新添加这行
    
    # 初始化DeepSeek服务
    try:
        api_routes.deepseek_service = DeepSeekService()
        print("✅ DeepSeek服务初始化成功")
    except Exception as e:
        print(f"❌ DeepSeek服务初始化失败: {e}")
        print(f"   错误详情: {type(e).__name__}")
        # 创建一个空的服务以避免NoneType错误
        api_routes.deepseek_service = None

    # 4. 注册蓝图
    app.register_blueprint(api_routes.api_blueprint)

    @app.route("/")
    def index():
        return "<h1>欢迎来到科研人脉网络API!</h1><p>请访问 /api/ping 或 /api/db-test 测试服务状态。</p>"

    return app