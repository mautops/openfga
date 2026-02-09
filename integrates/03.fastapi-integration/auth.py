"""
JWT 认证中间件

提供基于 JWT Token 的用户认证功能
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import logging

from config import settings

logger = logging.getLogger(__name__)

# HTTP Bearer Token 认证方案
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT Access Token

    Args:
        data: 要编码到 token 中的数据（通常包含 user_id）
        expires_delta: token 过期时间，默认为配置的过期时间

    Returns:
        编码后的 JWT token 字符串
    """
    to_encode = data.copy()

    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # 编码 JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    验证并解码 JWT Token

    Args:
        token: JWT token 字符串

    Returns:
        解码后的 payload 字典

    Raises:
        HTTPException: token 无效或过期时抛出
    """
    try:
        # 解码 JWT
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # 提取用户 ID
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 中缺少用户 ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        logger.error(f"JWT 验证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    从请求中提取并验证当前用户

    这是一个 FastAPI 依赖函数，可以在路由中使用 Depends(get_current_user)
    来获取当前认证的用户信息。

    Args:
        credentials: HTTP Bearer 认证凭证

    Returns:
        包含用户信息的字典，至少包含 user_id 字段

    Raises:
        HTTPException: 认证失败时抛出 401 错误

    使用示例:
        @app.get("/api/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            user_id = current_user["user_id"]
            return {"message": f"Hello, {user_id}"}
    """
    token = credentials.credentials

    # 验证 token
    payload = verify_token(token)

    logger.debug(f"用户 {payload.get('user_id')} 通过认证")

    return payload


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    可选的用户认证

    如果提供了 token 则验证，否则返回 None。
    适用于某些端点既支持认证用户也支持匿名用户的场景。

    Args:
        credentials: HTTP Bearer 认证凭证（可选）

    Returns:
        包含用户信息的字典，或 None（未认证）
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token)
        return payload
    except HTTPException:
        return None


# ==================== 用于测试的辅助函数 ====================

def generate_test_token(user_id: str, email: str = "test@example.com") -> str:
    """
    生成测试用的 JWT Token

    仅用于开发和测试环境！

    Args:
        user_id: 用户 ID
        email: 用户邮箱

    Returns:
        JWT token 字符串

    使用示例:
        # 生成测试 token
        token = generate_test_token("user_1", "alice@example.com")

        # 在请求中使用
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/api/documents", headers=headers)
    """
    token_data = {
        "user_id": user_id,
        "email": email
    }
    return create_access_token(token_data)


if __name__ == "__main__":
    # 测试代码：生成一些测试 token
    print("生成测试 Token:")
    print("-" * 60)

    users = [
        ("user_1", "alice@example.com"),
        ("user_2", "bob@example.com"),
        ("user_3", "charlie@example.com"),
    ]

    for user_id, email in users:
        token = generate_test_token(user_id, email)
        print(f"\n用户: {user_id} ({email})")
        print(f"Token: {token}")

    print("\n" + "-" * 60)
    print("使用方式:")
    print('curl -H "Authorization: Bearer <token>" http://localhost:8000/api/documents')
