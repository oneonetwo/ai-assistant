"""服务层异常定义"""
from fastapi import HTTPException, status

class ServiceError(HTTPException):
    """服务基础异常"""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)

class DatabaseError(ServiceError):
    """数据库相关错误"""
    def __init__(self, detail: str):
        super().__init__(
            detail=f"Database error: {detail}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class ValidationError(ServiceError):
    """数据验证错误"""
    def __init__(self, detail: str):
        super().__init__(
            detail=f"Validation error: {detail}",
            status_code=status.HTTP_400_BAD_REQUEST
        )

class NotFoundError(ServiceError):
    """资源不存在错误"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND
        )

class APIError(ServiceError):
    """API调用相关错误"""
    def __init__(self, detail: str):
        super().__init__(
            detail=f"API error: {detail}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        ) 