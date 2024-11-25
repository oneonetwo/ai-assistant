from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # API配置
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI聊天助手"
    DEBUG: bool = True
    VERSION: str = "0.1.0"

    # 安全配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # 数据库配置
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Redis配置
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: Optional[str] = None
    REDIS_PREFIX: str

    # 通义千问API配置
    QWEN_API_KEY: str
    QWEN_API_URL: str
    QWEN_API_TIMEOUT: int

    # 上下文配置
    MAX_CONTEXT_TURNS: int
    MAX_TOKEN_LENGTH: int

    # 文件存储配置
    UPLOAD_DIR: Path = Path("static/uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_DOCUMENT_TYPES: set = {
        "text/plain", "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/epub+zip", "text/markdown"
    }
    ALLOWED_IMAGE_TYPES: set = {
        "image/jpeg", "image/png", "image/webp", "image/gif"
    }

    def get_database_url(self, async_url: bool = True) -> str:
        """获取数据库URL
        
        Args:
            async_url: 是否返回异步数据库URL，默认为True
        """
        driver = "aiomysql" if async_url else "pymysql"
        return f"mysql+{driver}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保上传目录存在
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        (self.UPLOAD_DIR / "documents").mkdir(exist_ok=True)
        (self.UPLOAD_DIR / "images").mkdir(exist_ok=True)

    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局设置实例
settings = Settings()