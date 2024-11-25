from fastapi import Request
import time
from app.core.logging import app_logger
import psutil
import asyncio

async def performance_middleware(request: Request, call_next):
    """性能监控中间件"""
    start_time = time.time()
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    response = await call_next(request)
    
    # 计算性能指标
    execution_time = time.time() - start_time
    memory_used = (process.memory_info().rss / 1024 / 1024) - start_memory
    
    # 记录性能日志
    app_logger.info(
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"Time: {execution_time:.2f}s | "
        f"Memory: {memory_used:.2f}MB"
    )
    
    # 添加性能指标到响应头
    response.headers["X-Execution-Time"] = f"{execution_time:.2f}s"
    
    return response 