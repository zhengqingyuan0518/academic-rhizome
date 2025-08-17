from pydantic import BaseModel, Field
from typing import Optional

class BaseResponseModel(BaseModel):
    """基础响应模型，定义通用返回格式"""
    status: str = "success"
    message: Optional[str] = None

class NLPQueryRequest(BaseModel):
    """自然语言查询的请求体模型"""
    query_text: str = Field(..., min_length=1, description="用户输入的自然语言问题")
    user_id: Optional[str] = Field(None, description="用于追踪会话的用户ID")