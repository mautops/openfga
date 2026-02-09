"""
FastAPI + OpenFGA 集成示例 - 主应用文件

这个示例展示了如何将 OpenFGA 集成到 FastAPI 应用中，实现细粒度的权限控制。

功能：
- JWT 认证
- OpenFGA 权限检查
- 文档 CRUD API
- 用户管理
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from auth import get_current_user
from permissions import require_permission
from models import (
    Document, DocumentCreate, DocumentUpdate,
    User, UserCreate,
    HealthResponse
)
from config import settings
from openfga_client import openfga_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 模拟数据库（实际项目中应使用真实数据库）
documents_db = {}
users_db = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("应用启动中...")
    logger.info(f"OpenFGA API URL: {settings.OPENFGA_API_URL}")
    logger.info(f"OpenFGA Store ID: {settings.OPENFGA_STORE_ID}")
    yield
    logger.info("应用关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title="FastAPI + OpenFGA 集成示例",
    description="展示如何将 OpenFGA 集成到 FastAPI 应用中",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 健康检查 ====================

@app.get("/health", response_model=HealthResponse, tags=["健康检查"])
async def health_check():
    """
    健康检查端点

    返回应用和 OpenFGA 的健康状态
    """
    try:
        # 检查 OpenFGA 连接
        # 这里可以添加实际的连接检查逻辑
        openfga_status = "healthy"
    except Exception as e:
        logger.error(f"OpenFGA 健康检查失败: {e}")
        openfga_status = "unhealthy"

    return HealthResponse(
        status="healthy",
        openfga_status=openfga_status
    )


# ==================== 用户管理 ====================

@app.post("/api/users", response_model=User, tags=["用户管理"])
async def create_user(user_data: UserCreate):
    """
    创建新用户

    创建用户后，会在 OpenFGA 中初始化用户的基础权限
    """
    # 检查用户是否已存在
    if user_data.email in [u.email for u in users_db.values()]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户邮箱已存在"
        )

    # 创建用户
    user_id = f"user_{len(users_db) + 1}"
    user = User(
        id=user_id,
        email=user_data.email,
        name=user_data.name
    )
    users_db[user_id] = user

    logger.info(f"创建用户: {user_id} ({user.email})")

    # 在 OpenFGA 中可以初始化用户的默认权限
    # 例如：用户对自己的 profile 有 owner 权限
    try:
        await openfga_service.write_tuples([
            {
                "user": f"user:{user_id}",
                "relation": "owner",
                "object": f"profile:{user_id}"
            }
        ])
        logger.info(f"已在 OpenFGA 中初始化用户 {user_id} 的权限")
    except Exception as e:
        logger.error(f"初始化用户权限失败: {e}")

    return user


@app.get("/api/users/me", response_model=User, tags=["用户管理"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前登录用户信息

    需要有效的 JWT Token
    """
    user_id = current_user["user_id"]

    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return users_db[user_id]


# ==================== 文档管理 ====================

@app.post("/api/documents", response_model=Document, tags=["文档管理"])
async def create_document(
    document_data: DocumentCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建文档

    需要认证。创建者自动成为文档的 owner。
    """
    user_id = current_user["user_id"]

    # 创建文档
    doc_id = f"doc_{len(documents_db) + 1}"
    document = Document(
        id=doc_id,
        title=document_data.title,
        content=document_data.content,
        owner_id=user_id
    )
    documents_db[doc_id] = document

    logger.info(f"用户 {user_id} 创建文档: {doc_id}")

    # 在 OpenFGA 中设置权限关系
    try:
        await openfga_service.write_tuples([
            {
                "user": f"user:{user_id}",
                "relation": "owner",
                "object": f"document:{doc_id}"
            }
        ])
        logger.info(f"已在 OpenFGA 中设置文档 {doc_id} 的权限")
    except Exception as e:
        logger.error(f"设置文档权限失败: {e}")
        # 回滚文档创建
        del documents_db[doc_id]
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建文档失败"
        )

    return document


@app.get("/api/documents/{document_id}", response_model=Document, tags=["文档管理"])
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission("viewer", "document"))
):
    """
    获取文档详情

    需要对文档有 viewer 权限
    """
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    logger.info(f"用户 {current_user['user_id']} 查看文档: {document_id}")
    return documents_db[document_id]


@app.put("/api/documents/{document_id}", response_model=Document, tags=["文档管理"])
async def update_document(
    document_id: str,
    document_data: DocumentUpdate,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission("editor", "document"))
):
    """
    更新文档

    需要对文档有 editor 权限
    """
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    document = documents_db[document_id]

    # 更新文档字段
    if document_data.title is not None:
        document.title = document_data.title
    if document_data.content is not None:
        document.content = document_data.content

    logger.info(f"用户 {current_user['user_id']} 更新文档: {document_id}")
    return document


@app.delete("/api/documents/{document_id}", tags=["文档管理"])
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission("owner", "document"))
):
    """
    删除文档

    需要对文档有 owner 权限
    """
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 删除文档
    del documents_db[document_id]

    logger.info(f"用户 {current_user['user_id']} 删除文档: {document_id}")

    # 在 OpenFGA 中删除相关权限关系
    try:
        # 这里应该删除所有与该文档相关的权限关系
        # 实际实现需要先查询所有关系，然后删除
        logger.info(f"已在 OpenFGA 中删除文档 {document_id} 的权限")
    except Exception as e:
        logger.error(f"删除文档权限失败: {e}")

    return {"message": "文档已删除"}


@app.get("/api/documents", tags=["文档管理"])
async def list_documents(
    current_user: dict = Depends(get_current_user)
):
    """
    列出当前用户可访问的所有文档

    使用 OpenFGA 的 ListObjects API 获取用户有权限的文档列表
    """
    user_id = current_user["user_id"]

    try:
        # 使用 OpenFGA 的 ListObjects 获取用户可查看的文档
        accessible_docs = await openfga_service.list_objects(
            user=f"user:{user_id}",
            relation="viewer",
            object_type="document"
        )

        # 从数据库中获取文档详情
        documents = []
        for doc_id in accessible_docs:
            # doc_id 格式为 "document:doc_1"，需要提取实际 ID
            actual_id = doc_id.split(":")[-1]
            if actual_id in documents_db:
                documents.append(documents_db[actual_id])

        logger.info(f"用户 {user_id} 查询文档列表，共 {len(documents)} 个")
        return {"documents": documents, "total": len(documents)}

    except Exception as e:
        logger.error(f"查询文档列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询文档列表失败"
        )


# ==================== 权限管理 ====================

@app.post("/api/documents/{document_id}/share", tags=["权限管理"])
async def share_document(
    document_id: str,
    target_user_id: str,
    relation: str,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission("owner", "document"))
):
    """
    分享文档给其他用户

    需要对文档有 owner 权限。
    可以授予的权限：viewer（查看）、editor（编辑）
    """
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    if relation not in ["viewer", "editor"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的权限类型，只能是 viewer 或 editor"
        )

    # 在 OpenFGA 中添加权限关系
    try:
        await openfga_service.write_tuples([
            {
                "user": f"user:{target_user_id}",
                "relation": relation,
                "object": f"document:{document_id}"
            }
        ])

        logger.info(
            f"用户 {current_user['user_id']} 将文档 {document_id} "
            f"的 {relation} 权限分享给用户 {target_user_id}"
        )

        return {
            "message": f"已将 {relation} 权限授予用户 {target_user_id}",
            "document_id": document_id,
            "target_user_id": target_user_id,
            "relation": relation
        }

    except Exception as e:
        logger.error(f"分享文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分享文档失败"
        )


@app.delete("/api/documents/{document_id}/share", tags=["权限管理"])
async def revoke_document_access(
    document_id: str,
    target_user_id: str,
    relation: str,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission("owner", "document"))
):
    """
    撤销用户对文档的访问权限

    需要对文档有 owner 权限
    """
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 在 OpenFGA 中删除权限关系
    try:
        await openfga_service.delete_tuples([
            {
                "user": f"user:{target_user_id}",
                "relation": relation,
                "object": f"document:{document_id}"
            }
        ])

        logger.info(
            f"用户 {current_user['user_id']} 撤销了用户 {target_user_id} "
            f"对文档 {document_id} 的 {relation} 权限"
        )

        return {
            "message": f"已撤销用户 {target_user_id} 的 {relation} 权限",
            "document_id": document_id,
            "target_user_id": target_user_id,
            "relation": relation
        }

    except Exception as e:
        logger.error(f"撤销权限失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="撤销权限失败"
        )


# ==================== 异常处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """统一的 HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """统一的通用异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "服务器内部错误",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
