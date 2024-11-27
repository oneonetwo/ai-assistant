from pydantic_settings import BaseSettings
from typing import Optional, List
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
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"
    DB_NAME: str = "ai_assistant"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_PREFIX: str

    # 通义千问API配置
    QWEN_API_KEY: str
    QWEN_API_URL: str
    QWEN_API_TIMEOUT: int

    # 上下文配置
    MAX_CONTEXT_TURNS: int = 10
    MAX_TOKEN_LENGTH: int

    # 文件存储配置
    UPLOAD_DIR: Path = Path("static/uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_DOCUMENT_TYPES: set = {
        "text/plain", "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/epub+zip", "text/markdown"
    }
    ALLOWED_IMAGE_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/bmp",
        "image/tiff",
        "application/octet-stream"  # 临时添加，用于处理某些客户端的图片上传
    ]

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