from loguru import logger
import sys
from pathlib import Path

# 日志文件路径
LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)

# 配置日志格式和输出
def setup_logging():
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )
    
    # 添加文件输出
    logger.add(
        LOG_PATH / "app.log",
        rotation="500 MB",  # 日志文件大小达到500MB时轮转
        retention="10 days",  # 保留10天的日志
        compression="zip",  # 压缩旧日志
        level="INFO"
    )

# 导出logger实例
app_logger = logger 