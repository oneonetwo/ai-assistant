from fastapi import HTTPException, status

class ConfigError(HTTPException):
    """配置相关错误"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {detail}"
        )

class DatabaseError(HTTPException):
    """数据库相关错误"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {detail}"
        )

class APIError(HTTPException):
    """API调用相关错误"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"API error: {detail}"
        ) 