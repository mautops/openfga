"""
OpenFGA 客户端初始化和基础操作模块

本模块提供了 OpenFGA 客户端的初始化和基础操作封装，支持两种认证方式：
1. API Token 认证（适用于开发环境）
2. Client Credentials 认证（适用于生产环境）

作者: OpenFGA 集成示例
日期: 2026-02-05
"""

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from openfga_sdk import ClientConfiguration, OpenFgaClient
from openfga_sdk.credentials import Credentials, CredentialConfiguration
from openfga_sdk.client.models import ClientTuple, ClientWriteRequest, ClientCheckRequest
from openfga_sdk.rest import ApiException


class OpenFGAClientWrapper:
    """
    OpenFGA 客户端封装类

    提供了便捷的方法来初始化客户端并执行常见的授权操作。
    支持两种认证方式：API Token 和 Client Credentials。
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        store_id: Optional[str] = None,
        model_id: Optional[str] = None,
        auth_method: Optional[str] = None,
        api_token: Optional[str] = None,
        api_issuer: Optional[str] = None,
        api_audience: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        初始化 OpenFGA 客户端

        Args:
            api_url: OpenFGA API 地址，默认从环境变量 FGA_API_URL 读取
            store_id: Store ID，默认从环境变量 FGA_STORE_ID 读取
            model_id: Authorization Model ID，默认从环境变量 FGA_MODEL_ID 读取
            auth_method: 认证方式 ('api_token' 或 'client_credentials')
            api_token: API Token（当 auth_method='api_token' 时使用）
            api_issuer: Token 颁发者（当 auth_method='client_credentials' 时使用）
            api_audience: API 受众（当 auth_method='client_credentials' 时使用）
            client_id: 客户端 ID（当 auth_method='client_credentials' 时使用）
            client_secret: 客户端密钥（当 auth_method='client_credentials' 时使用）
        """
        # 加载环境变量
        load_dotenv()

        # 从环境变量或参数获取配置
        self.api_url = api_url or os.getenv('FGA_API_URL', 'http://localhost:8080')
        self.store_id = store_id or os.getenv('FGA_STORE_ID')
        self.model_id = model_id or os.getenv('FGA_MODEL_ID')
        self.auth_method = auth_method or os.getenv('FGA_AUTH_METHOD', 'api_token')

        # 验证必需参数
        if not self.store_id:
            raise ValueError("Store ID 是必需的，请通过参数或环境变量 FGA_STORE_ID 提供")

        # 根据认证方式配置凭证
        credentials = None
        if self.auth_method == 'api_token':
            token = api_token or os.getenv('FGA_API_TOKEN')
            if not token:
                raise ValueError("使用 API Token 认证时，必须提供 api_token 或设置环境变量 FGA_API_TOKEN")

            credentials = Credentials(
                method='api_token',
                configuration=CredentialConfiguration(api_token=token)
            )

        elif self.auth_method == 'client_credentials':
            issuer = api_issuer or os.getenv('FGA_API_TOKEN_ISSUER')
            audience = api_audience or os.getenv('FGA_API_AUDIENCE')
            c_id = client_id or os.getenv('FGA_CLIENT_ID')
            c_secret = client_secret or os.getenv('FGA_CLIENT_SECRET')

            if not all([issuer, audience, c_id, c_secret]):
                raise ValueError(
                    "使用 Client Credentials 认证时，必须提供所有必需参数：\n"
                    "api_issuer, api_audience, client_id, client_secret"
                )

            credentials = Credentials(
                method='client_credentials',
                configuration=CredentialConfiguration(
                    api_issuer=issuer,
                    api_audience=audience,
                    client_id=c_id,
                    client_secret=c_secret,
                )
            )
        else:
            raise ValueError(f"不支持的认证方式: {self.auth_method}")

        # 创建客户端配置
        self.configuration = ClientConfiguration(
            api_url=self.api_url,
            store_id=self.store_id,
            authorization_model_id=self.model_id,
            credentials=credentials
        )

        # 客户端实例（将在 async with 中创建）
        self.client: Optional[OpenFgaClient] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.client = OpenFgaClient(self.configuration)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.client:
            await self.client.close()

    async def write_tuples(
        self,
        writes: Optional[List[ClientTuple]] = None,
        deletes: Optional[List[ClientTuple]] = None,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        写入或删除关系元组

        Args:
            writes: 要写入的元组列表
            deletes: 要删除的元组列表
            model_id: 可选的授权模型 ID，覆盖配置中的默认值

        Returns:
            写入操作的响应

        Raises:
            ApiException: 当 API 调用失败时
        """
        if not self.client:
            raise RuntimeError("客户端未初始化，请使用 async with 语句")

        try:
            options = {}
            if model_id:
                options['authorization_model_id'] = model_id

            body = ClientWriteRequest(
                writes=writes or [],
                deletes=deletes or []
            )

            response = await self.client.write(body, options)
            return {
                'success': True,
                'response': response
            }
        except ApiException as e:
            return {
                'success': False,
                'error': str(e),
                'status': e.status,
                'body': e.body
            }

    async def check_permission(
        self,
        user: str,
        relation: str,
        object: str,
        contextual_tuples: Optional[List[ClientTuple]] = None,
        context: Optional[Dict[str, Any]] = None,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        检查用户是否有权限访问对象

        Args:
            user: 用户标识符（如 'user:anne'）
            relation: 关系类型（如 'reader', 'writer'）
            object: 对象标识符（如 'document:budget'）
            contextual_tuples: 上下文元组列表，用于临时授权检查
            context: 上下文数据，用于条件评估
            model_id: 可选的授权模型 ID

        Returns:
            包含检查结果的字典，包括 'allowed' 布尔值

        Raises:
            ApiException: 当 API 调用失败时
        """
        if not self.client:
            raise RuntimeError("客户端未初始化，请使用 async with 语句")

        try:
            options = {}
            if model_id:
                options['authorization_model_id'] = model_id

            body = ClientCheckRequest(
                user=user,
                relation=relation,
                object=object,
                contextual_tuples=contextual_tuples,
                context=context
            )

            response = await self.client.check(body, options)
            return {
                'success': True,
                'allowed': response.allowed,
                'response': response
            }
        except ApiException as e:
            return {
                'success': False,
                'error': str(e),
                'status': e.status,
                'body': e.body
            }

    async def batch_check(
        self,
        checks: List[ClientCheckRequest],
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        批量检查多个权限

        Args:
            checks: ClientCheckRequest 对象列表
            model_id: 可选的授权模型 ID

        Returns:
            包含所有检查结果的字典

        Raises:
            ApiException: 当 API 调用失败时
        """
        if not self.client:
            raise RuntimeError("客户端未初始化，请使用 async with 语句")

        try:
            options = {}
            if model_id:
                options['authorization_model_id'] = model_id

            response = await self.client.batch_check(checks, options)
            return {
                'success': True,
                'responses': response,
                'results': [
                    {
                        'user': check.user,
                        'relation': check.relation,
                        'object': check.object,
                        'allowed': resp.allowed
                    }
                    for check, resp in zip(checks, response)
                ]
            }
        except ApiException as e:
            return {
                'success': False,
                'error': str(e),
                'status': e.status,
                'body': e.body
            }

    async def list_objects(
        self,
        user: str,
        relation: str,
        type: str,
        contextual_tuples: Optional[List[ClientTuple]] = None,
        context: Optional[Dict[str, Any]] = None,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        列出用户有权限访问的所有对象

        Args:
            user: 用户标识符
            relation: 关系类型
            type: 对象类型（如 'document'）
            contextual_tuples: 上下文元组列表
            context: 上下文数据
            model_id: 可选的授权模型 ID

        Returns:
            包含对象列表的字典

        Raises:
            ApiException: 当 API 调用失败时
        """
        if not self.client:
            raise RuntimeError("客户端未初始化，请使用 async with 语句")

        try:
            options = {}
            if model_id:
                options['authorization_model_id'] = model_id

            response = await self.client.list_objects(
                user=user,
                relation=relation,
                type=type,
                contextual_tuples=contextual_tuples,
                context=context,
                options=options
            )

            return {
                'success': True,
                'objects': response.objects if hasattr(response, 'objects') else [],
                'response': response
            }
        except ApiException as e:
            return {
                'success': False,
                'error': str(e),
                'status': e.status,
                'body': e.body
            }

    async def list_users(
        self,
        object: str,
        relation: str,
        user_filters: Optional[List[Dict[str, Any]]] = None,
        contextual_tuples: Optional[List[ClientTuple]] = None,
        context: Optional[Dict[str, Any]] = None,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        列出有权限访问对象的所有用户

        Args:
            object: 对象标识符
            relation: 关系类型
            user_filters: 用户过滤器列表
            contextual_tuples: 上下文元组列表
            context: 上下文数据
            model_id: 可选的授权模型 ID

        Returns:
            包含用户列表的字典

        Raises:
            ApiException: 当 API 调用失败时
        """
        if not self.client:
            raise RuntimeError("客户端未初始化，请使用 async with 语句")

        try:
            options = {}
            if model_id:
                options['authorization_model_id'] = model_id

            response = await self.client.list_users(
                object=object,
                relation=relation,
                user_filters=user_filters or [],
                contextual_tuples=contextual_tuples,
                context=context,
                options=options
            )

            return {
                'success': True,
                'users': response.users if hasattr(response, 'users') else [],
                'response': response
            }
        except ApiException as e:
            return {
                'success': False,
                'error': str(e),
                'status': e.status,
                'body': e.body
            }

    async def read_authorization_models(self) -> Dict[str, Any]:
        """
        读取所有授权模型

        Returns:
            包含授权模型列表的字典

        Raises:
            ApiException: 当 API 调用失败时
        """
        if not self.client:
            raise RuntimeError("客户端未初始化，请使用 async with 语句")

        try:
            response = await self.client.read_authorization_models()
            return {
                'success': True,
                'models': response.authorization_models if hasattr(response, 'authorization_models') else [],
                'response': response
            }
        except ApiException as e:
            return {
                'success': False,
                'error': str(e),
                'status': e.status,
                'body': e.body
            }


def create_client(
    api_url: Optional[str] = None,
    store_id: Optional[str] = None,
    model_id: Optional[str] = None,
    auth_method: Optional[str] = None,
    **kwargs
) -> OpenFGAClientWrapper:
    """
    创建 OpenFGA 客户端的便捷函数

    Args:
        api_url: OpenFGA API 地址
        store_id: Store ID
        model_id: Authorization Model ID
        auth_method: 认证方式
        **kwargs: 其他认证相关参数

    Returns:
        OpenFGAClientWrapper 实例

    Example:
        # 使用 API Token
        async with create_client() as client:
            result = await client.check_permission(
                user='user:anne',
                relation='reader',
                object='document:budget'
            )
            print(result['allowed'])
    """
    return OpenFGAClientWrapper(
        api_url=api_url,
        store_id=store_id,
        model_id=model_id,
        auth_method=auth_method,
        **kwargs
    )
