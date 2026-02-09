"""
OAuth 认证处理模块

支持多种 OAuth 提供商：
- Google
- GitHub
- 自定义 OAuth 2.0 服务器

功能：
- OAuth 登录流程
- Token 验证
- 用户信息提取
- Session 管理
"""

from flask import Blueprint, redirect, url_for, session, jsonify, request
from authlib.integrations.flask_client import OAuth
from functools import wraps
import os
import jwt
from datetime import datetime, timedelta

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

# OAuth 客户端
oauth = OAuth()


def init_oauth(app):
    """初始化 OAuth 配置"""
    oauth.init_app(app)

    # 配置 Google OAuth
    if os.getenv('GOOGLE_CLIENT_ID'):
        oauth.register(
            name='google',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )

    # 配置 GitHub OAuth
    if os.getenv('GITHUB_CLIENT_ID'):
        oauth.register(
            name='github',
            client_id=os.getenv('GITHUB_CLIENT_ID'),
            client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
            access_token_url='https://github.com/login/oauth/access_token',
            access_token_params=None,
            authorize_url='https://github.com/login/oauth/authorize',
            authorize_params=None,
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'},
        )

    # 配置自定义 OAuth 服务器（可选）
    if os.getenv('OAUTH_CLIENT_ID'):
        oauth.register(
            name='custom',
            client_id=os.getenv('OAUTH_CLIENT_ID'),
            client_secret=os.getenv('OAUTH_CLIENT_SECRET'),
            server_metadata_url=os.getenv('OAUTH_SERVER_METADATA_URL'),
            client_kwargs={
                'scope': 'openid profile email'
            }
        )


def require_auth(f):
    """
    认证装饰器 - 要求用户已登录

    使用方法:
        @require_auth
        def protected_route():
            user_id = session.get('user_id')
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Please login first'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    获取当前登录用户信息

    返回:
        dict: 用户信息字典，包含 user_id, email, name 等
        None: 如果用户未登录
    """
    if 'user_id' not in session:
        return None

    return {
        'user_id': session.get('user_id'),
        'email': session.get('email'),
        'name': session.get('name'),
        'picture': session.get('picture'),
        'provider': session.get('provider')
    }


def create_jwt_token(user_info):
    """
    创建 JWT Token

    参数:
        user_info: 用户信息字典

    返回:
        str: JWT Token
    """
    payload = {
        'user_id': user_info['user_id'],
        'email': user_info['email'],
        'name': user_info.get('name'),
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }

    secret_key = os.getenv('JWT_SECRET_KEY', os.getenv('SECRET_KEY'))
    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return token


def verify_jwt_token(token):
    """
    验证 JWT Token

    参数:
        token: JWT Token 字符串

    返回:
        dict: Token payload
        None: 如果 Token 无效
    """
    try:
        secret_key = os.getenv('JWT_SECRET_KEY', os.getenv('SECRET_KEY'))
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@auth_bp.route('/login')
def login():
    """
    OAuth 登录入口

    查询参数:
        provider: OAuth 提供商 (google, github, custom)

    示例:
        GET /auth/login?provider=google
    """
    provider = request.args.get('provider', 'google')

    if provider not in ['google', 'github', 'custom']:
        return jsonify({
            'error': 'Invalid provider',
            'message': f'Provider "{provider}" is not supported'
        }), 400

    # 检查提供商是否已配置
    if provider == 'google' and not os.getenv('GOOGLE_CLIENT_ID'):
        return jsonify({
            'error': 'Provider not configured',
            'message': 'Google OAuth is not configured'
        }), 400

    if provider == 'github' and not os.getenv('GITHUB_CLIENT_ID'):
        return jsonify({
            'error': 'Provider not configured',
            'message': 'GitHub OAuth is not configured'
        }), 400

    if provider == 'custom' and not os.getenv('OAUTH_CLIENT_ID'):
        return jsonify({
            'error': 'Provider not configured',
            'message': 'Custom OAuth is not configured'
        }), 400

    # 保存提供商到 session
    session['oauth_provider'] = provider

    # 重定向到 OAuth 授权页面
    redirect_uri = url_for('auth.callback', _external=True)
    return getattr(oauth, provider).authorize_redirect(redirect_uri)


@auth_bp.route('/callback')
def callback():
    """
    OAuth 回调处理

    处理 OAuth 提供商的回调，获取用户信息并创建 session
    """
    provider = session.get('oauth_provider', 'google')

    try:
        # 获取 access token
        token = getattr(oauth, provider).authorize_access_token()

        # 获取用户信息
        if provider == 'google':
            user_info = token.get('userinfo')
            if not user_info:
                resp = getattr(oauth, provider).get('userinfo')
                user_info = resp.json()

            user_data = {
                'user_id': user_info['sub'],
                'email': user_info['email'],
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'provider': 'google'
            }

        elif provider == 'github':
            resp = getattr(oauth, provider).get('user')
            user_info = resp.json()

            # GitHub 需要额外请求获取邮箱
            email_resp = getattr(oauth, provider).get('user/emails')
            emails = email_resp.json()
            primary_email = next((e['email'] for e in emails if e['primary']), None)

            user_data = {
                'user_id': str(user_info['id']),
                'email': primary_email or user_info.get('email'),
                'name': user_info.get('name') or user_info.get('login'),
                'picture': user_info.get('avatar_url'),
                'provider': 'github'
            }

        elif provider == 'custom':
            user_info = token.get('userinfo')
            if not user_info:
                resp = getattr(oauth, provider).get('userinfo')
                user_info = resp.json()

            user_data = {
                'user_id': user_info['sub'],
                'email': user_info['email'],
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'provider': 'custom'
            }

        # 保存用户信息到 session
        session['user_id'] = user_data['user_id']
        session['email'] = user_data['email']
        session['name'] = user_data['name']
        session['picture'] = user_data['picture']
        session['provider'] = user_data['provider']

        # 创建 JWT Token（可选，用于 API 访问）
        jwt_token = create_jwt_token(user_data)
        session['jwt_token'] = jwt_token

        # 重定向到前端应用（或返回 JSON）
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}?token={jwt_token}")

    except Exception as e:
        return jsonify({
            'error': 'Authentication failed',
            'message': str(e)
        }), 400


@auth_bp.route('/logout')
def logout():
    """
    登出

    清除 session 中的用户信息
    """
    session.clear()
    return jsonify({
        'message': 'Logged out successfully'
    })


@auth_bp.route('/user')
@require_auth
def get_user():
    """
    获取当前用户信息

    需要认证

    返回:
        用户信息 JSON
    """
    user = get_current_user()
    return jsonify(user)


@auth_bp.route('/token/verify', methods=['POST'])
def verify_token():
    """
    验证 JWT Token

    请求体:
        {
            "token": "jwt_token_string"
        }

    返回:
        Token payload 或错误信息
    """
    data = request.get_json()
    token = data.get('token')

    if not token:
        return jsonify({
            'error': 'Missing token',
            'message': 'Token is required'
        }), 400

    payload = verify_jwt_token(token)

    if not payload:
        return jsonify({
            'error': 'Invalid token',
            'message': 'Token is invalid or expired'
        }), 401

    return jsonify({
        'valid': True,
        'payload': payload
    })
