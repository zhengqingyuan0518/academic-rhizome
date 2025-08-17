import os

class Config:
    """存放所有配置"""
    # Neo4j 配置
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "neo4j12345678")

    # OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_key")