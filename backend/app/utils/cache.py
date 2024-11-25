from typing import Optional
import redis.asyncio as aioredis
from loguru import logger
from app.core.config import settings

class CacheManager:
    _redis: Optional[aioredis.Redis] = None
    
    @property
    def redis(self) -> aioredis.Redis:
        if not self._redis:
            raise RuntimeError("Redis client not initialized")
        return self._redis
    
    def get_cache(self, prefix: str) -> 'RedisCache':
        """获取指定前缀的缓存实例"""
        return RedisCache(self, prefix)
    
    async def init(self):
        try:
            self._redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD or None,
                encoding="utf-8",
                decode_responses=True
            )
            await self._redis.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            raise
    
    async def close(self):
        if self._redis:
            await self._redis.close()
            logger.info("Redis连接已关闭")

class RedisCache:
    def __init__(self, manager: CacheManager, prefix: str):
        self._manager = manager
        self._prefix = prefix
    
    def _make_key(self, key: str) -> str:
        """生成带前缀的键名"""
        return f"{settings.REDIS_PREFIX}{self._prefix}:{key}"
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        return await self._manager.redis.get(self._make_key(key))
    
    async def set(self, key: str, value: str, expire: int = None):
        """设置缓存值"""
        await self._manager.redis.set(self._make_key(key), value, ex=expire)
    
    async def delete(self, key: str):
        """删除缓存值"""
        await self._manager.redis.delete(self._make_key(key))

cache_manager = CacheManager() 