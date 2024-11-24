from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.database import engine
from app.db.models import Base
from app.api.v1 import context, chat, image_analysis, document_analysis
from app.middleware.upload import validate_upload_size
from app.utils.cache import cache_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    # 初始化缓存
    await cache_manager.init()
    
    # 初始化数据库
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # 清理资源
    await cache_manager.close()
    await engine.dispose()

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# 设置日志
setup_logging()

# 添加中间件
app.middleware("http")(validate_upload_size)

# 注册路由
app.include_router(context.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(image_analysis.router, prefix=settings.API_V1_PREFIX)
app.include_router(document_analysis.router, prefix=settings.API_V1_PREFIX)
