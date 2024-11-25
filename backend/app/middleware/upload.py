from fastapi import Request, HTTPException
from app.core.config import settings
import functools

async def validate_upload_size(request: Request, call_next):
    """验证上传文件大小的中间件"""
    if request.method == "POST" and "multipart/form-data" in request.headers.get("content-type", ""):
        if request.headers.get("content-length"):
            content_length = int(request.headers["content-length"])
            if content_length > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"文件大小超过限制: {settings.MAX_UPLOAD_SIZE} bytes"
                )
    
    return await call_next(request)

def require_file_type(*allowed_types):
    """文件类型验证装饰器"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            file = kwargs.get('file')
            if not file:
                raise HTTPException(
                    status_code=400,
                    detail="未找到上传文件"
                )
                
            content_type = magic.from_buffer(await file.read(1024), mime=True)
            await file.seek(0)
            
            if content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件类型: {content_type}"
                )
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator 