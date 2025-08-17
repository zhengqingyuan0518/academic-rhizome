import os
from typing import Optional

# 调试：打印当前工作目录和环境变量
print(f"🔍 当前工作目录: {os.getcwd()}")
print(f"🔍 环境变量中的DEEPSEEK_API_KEY: {bool(os.getenv('DEEPSEEK_API_KEY'))}")

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    
    # 明确指定.env文件路径
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    print(f"🔍 尝试加载.env文件: {env_path}")
    print(f"🔍 .env文件是否存在: {os.path.exists(env_path)}")
    
    load_dotenv(env_path)
    print("✅ .env 文件加载成功")
    
    # 再次检查环境变量
    print(f"🔍 加载后的DEEPSEEK_API_KEY: {bool(os.getenv('DEEPSEEK_API_KEY'))}")
    
except ImportError:
    print("⚠️  python-dotenv 未安装，将使用系统环境变量")

class Config:
    """存放所有配置"""
    # Neo4j 配置
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "neo4j12345678")

    # DeepSeek API 配置
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    @classmethod
    def debug_print(cls):
        """调试打印所有配置"""
        print("🔍 当前配置状态:")
        print(f"   DEEPSEEK_API_KEY: {'已设置' if cls.DEEPSEEK_API_KEY else '❌ 未设置'}")
        if cls.DEEPSEEK_API_KEY:
            print(f"   API密钥前缀: {cls.DEEPSEEK_API_KEY[:10]}...")
        print(f"   DEEPSEEK_BASE_URL: {cls.DEEPSEEK_BASE_URL}")
        print(f"   DEEPSEEK_MODEL: {cls.DEEPSEEK_MODEL}")

    @classmethod
    def validate_config(cls):
        cls.debug_print()
        if not cls.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")