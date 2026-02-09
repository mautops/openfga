"""
应用配置

使用 Pydantic Settings 管理环境变量配置
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""

    # ==================== 应用配置 ====================
    APP_NAME: str = "FastAPI + OpenFGA 集成示例"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ==================== JWT 配置 ====================
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时

    # ==================== OpenFGA 配置 ====================
    OPENFGA_API_URL: str = "http://localhost:8080"
    OPENFGA_STORE_ID: str = ""
    OPENFGA_MODEL_ID: Optional[str] = None

    # ==================== 数据库配置（可选）====================
    # 如果使用真实数据库，可以添加数据库配置
    # DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # ==================== CORS 配置 ====================
    CORS_ORIGINS: list[str] = ["*"]

    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"

    class Config:
        # 从 .env 文件读取配置
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()


# ==================== 配置验证 ====================

def validate_settings():
    """验证必需的配置项"""
    errors = []

    if not settings.OPENFGA_STORE_ID:
        errors.append("OPENFGA_STORE_ID 未配置")

    if settings.JWT_SECRET_KEY == "your-secret-key-change-this-in-production":
        errors.append("警告: JWT_SECRET_KEY 使用默认值，生产环境请修改")

    if errors:
        print("配置错误:")
        for error in errors:
            print(f"  - {error}")

    return len(errors) == 0


# 应用启动时验证配置
if __name__ == "__main__":
    print("当前配置:")
    print(f"  APP_NAME: {settings.APP_NAME}")
    print(f"  OPENFGA_API_URL: {settings.OPENFGA_API_URL}")
    print(f"  OPENFGA_STORE_ID: {settings.OPENFGA_STORE_ID}")
    print(f"  OPENFGA_MODEL_ID: {settings.OPENFGA_MODEL_ID}")
    print(f"  JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
    print(f"  ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
    print()

    if validate_settings():
        print("✓ 配置验证通过")
    else:
        print("✗ 配置验证失败")
