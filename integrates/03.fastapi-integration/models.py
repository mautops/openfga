"""
Pydantic 数据模型

定义 API 的请求和响应模型
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ==================== 用户模型 ====================

class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    name: str = Field(..., min_length=1, max_length=100, description="用户姓名")


class UserCreate(UserBase):
    """创建用户请求模型"""
    pass


class User(UserBase):
    """用户响应模型"""
    id: str = Field(..., description="用户 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_1",
                "email": "alice@example.com",
                "name": "Alice"
            }
        }


# ==================== 文档模型 ====================

class DocumentBase(BaseModel):
    """文档基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    content: str = Field(..., description="文档内容")


class DocumentCreate(DocumentBase):
    """创建文档请求模型"""

    class Config:
        json_schema_extra = {
            "example": {
                "title": "我的第一个文档",
                "content": "这是文档的内容..."
            }
        }


class DocumentUpdate(BaseModel):
    """更新文档请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "更新后的标题",
                "content": "更新后的内容..."
            }
        }


class Document(DocumentBase):
    """文档响应模型"""
    id: str = Field(..., description="文档 ID")
    owner_id: str = Field(..., description="文档所有者 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_1",
                "title": "我的文档",
                "content": "文档内容...",
                "owner_id": "user_1",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


# ==================== 权限模型 ====================

class PermissionGrant(BaseModel):
    """授予权限请求模型"""
    target_user_id: str = Field(..., description="目标用户 ID")
    relation: str = Field(..., description="权限关系（viewer, editor, owner）")

    class Config:
        json_schema_extra = {
            "example": {
                "target_user_id": "user_2",
                "relation": "viewer"
            }
        }


class PermissionRevoke(BaseModel):
    """撤销权限请求模型"""
    target_user_id: str = Field(..., description="目标用户 ID")
    relation: str = Field(..., description="权限关系")

    class Config:
        json_schema_extra = {
            "example": {
                "target_user_id": "user_2",
                "relation": "viewer"
            }
        }


class PermissionCheck(BaseModel):
    """权限检查请求模型"""
    user_id: str = Field(..., description="用户 ID")
    relation: str = Field(..., description="权限关系")
    object_id: str = Field(..., description="对象 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_1",
                "relation": "viewer",
                "object_id": "document:doc_1"
            }
        }


class PermissionCheckResponse(BaseModel):
    """权限检查响应模型"""
    allowed: bool = Field(..., description="是否有权限")
    user_id: str = Field(..., description="用户 ID")
    relation: str = Field(..., description="权限关系")
    object_id: str = Field(..., description="对象 ID")


# ==================== 认证模型 ====================

class Token(BaseModel):
    """JWT Token 响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Token 中的数据"""
    user_id: str = Field(..., description="用户 ID")
    email: Optional[str] = Field(None, description="用户邮箱")


# ==================== 通用响应模型 ====================

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str = Field(..., description="响应消息")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "操作成功"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    status_code: int = Field(..., description="HTTP 状态码")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "权限被拒绝",
                "status_code": 403
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="应用状态")
    openfga_status: str = Field(..., description="OpenFGA 状态")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "openfga_status": "healthy"
            }
        }


# ==================== 列表响应模型 ====================

class DocumentListResponse(BaseModel):
    """文档列表响应"""
    documents: list[Document] = Field(..., description="文档列表")
    total: int = Field(..., description="文档总数")

    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "id": "doc_1",
                        "title": "文档1",
                        "content": "内容1",
                        "owner_id": "user_1",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                ],
                "total": 1
            }
        }


class UserListResponse(BaseModel):
    """用户列表响应"""
    users: list[User] = Field(..., description="用户列表")
    total: int = Field(..., description="用户总数")
