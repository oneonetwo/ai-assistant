from pydantic_settings import BaseSettings
from typing import Optional

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

    def get_database_url(self, async_url: bool = True) -> str:
        """获取数据库URL
        
        Args:
            async_url: 是否返回异步数据库URL，默认为True
        """
        driver = "aiomysql" if async_url else "pymysql"
        return f"mysql+{driver}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局设置实例
settings = Settings()