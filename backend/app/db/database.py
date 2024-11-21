from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 构建数据库URL
DATABASE_URL = settings.get_database_url(async_url=True)

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # 在调试模式下打印SQL语句
    pool_pre_ping=True,  # 连接池健康检查
    pool_size=5,  # 连接池大小
    max_overflow=10  # 最大连接数
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 获取数据库会话的依赖函数
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 