"""
Flask + OAuth + OpenFGA 集成示例 - 主应用文件

这个示例展示了如何将 Flask、OAuth 2.0 认证和 OpenFGA 授权集成在一起。

功能特性：
- OAuth 2.0 认证（支持 Google、GitHub 等）
- JWT Token 处理
- OpenFGA 权限检查
- 文档 CRUD API
- Session 管理
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_session import Session
import os
from dotenv import load_dotenv

from auth import auth_bp, init_oauth
from views import api_bp
from models import init_db

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# 初始化扩展
CORS(app, supports_credentials=True)
Session(app)

# 初始化 OAuth
init_oauth(app)

# 初始化数据库
init_db()

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(api_bp, url_prefix='/api')


@app.route('/')
def index():
    """首页"""
    return jsonify({
        'message': 'Flask + OAuth + OpenFGA 集成示例',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'login': '/auth/login',
                'callback': '/auth/callback',
                'logout': '/auth/logout',
                'user': '/auth/user'
            },
            'api': {
                'documents': '/api/documents',
                'document_detail': '/api/documents/<id>',
                'share_document': '/api/documents/<id>/share'
            }
        }
    })


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'flask-oauth-openfga'
    })


@app.errorhandler(400)
def bad_request(error):
    """400 错误处理"""
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    """401 错误处理"""
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required'
    }), 401


@app.errorhandler(403)
def forbidden(error):
    """403 错误处理"""
    return jsonify({
        'error': 'Forbidden',
        'message': 'Permission denied'
    }), 403


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'error': 'Not Found',
        'message': 'Resource not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    # 开发环境运行
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'

    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║  Flask + OAuth + OpenFGA 集成示例                        ║
    ╠══════════════════════════════════════════════════════════╣
    ║  服务地址: http://localhost:{port}                        ║
    ║  健康检查: http://localhost:{port}/health                 ║
    ║  API 文档: 查看 README.md                                ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
