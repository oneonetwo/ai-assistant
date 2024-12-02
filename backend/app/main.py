from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.database import engine
from app.db.models import Base
from app.api.v1 import context, chat, image_analysis, document_analysis, upload, handbooks, notes, revisions, revision_settings
from app.middleware.upload import validate_upload_size
from app.utils.cache import cache_manager
import uvicorn
import sys
import signal

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

# 添加静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(context.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(image_analysis.router, prefix=settings.API_V1_PREFIX)
app.include_router(document_analysis.router, prefix=settings.API_V1_PREFIX)
app.include_router(upload.router, prefix="/api/v1")
app.include_router(handbooks.router, prefix=settings.API_V1_PREFIX)
app.include_router(notes.router, prefix=settings.API_V1_PREFIX)
app.include_router(revisions.router, prefix=settings.API_V1_PREFIX)
app.include_router(revision_settings.router, prefix=settings.API_V1_PREFIX)

def handle_interrupt(signum, frame):
    print("\nGracefully shutting down...")
    sys.exit(0)

if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_interrupt)
    
    # 配置uvicorn
    config = uvicorn.Config(
        app=app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1,  # 减少worker数量
        loop="asyncio",
        timeout_keep_alive=settings.TIMEOUT,
        access_log=True
    )
    
    server = uvicorn.Server(config)
    server.run()
