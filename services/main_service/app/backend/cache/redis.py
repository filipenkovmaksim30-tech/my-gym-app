import json
from typing import Optional, Any
import redis.asyncio as aioredis
from app.backend.auth.config import settings


class RedisCacheBackend:

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def set_cache(self, key:str , value: Any, expire_seconds: int = 3600):
        if not self.redis:
            return None

        return await self.redis.set(name=key, value=json.dumps(value, default=str), ex=expire_seconds)

    async def get_cache(self, key: str):

        if not self.redis:
            return None
    
        data = await self.redis.get(key)
        if not data:
            return None
        
        try:
            if isinstance(data, bytes): 
                data = data.decode("utf-8")
            return json.loads(data)
        
        except (json.JSONDecodeError, TypeError):

            return data

    async def delete_cache(self, key: str):
        if self.redis:
            await self.redis.delete(key)
    
    async def delete_by_pattern(self, pattern: str):
        if not self.redis:
            return
        
        keys = await self.redis.keys(pattern)
        
        if keys:
            await self.redis.delete(*keys)

cache_backend = RedisCacheBackend()