from datetime import datetime
import redis.asyncio as redis
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.singleton import Singleton


class RateLimiter(metaclass=Singleton):
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_UNAME,
            password=settings.REDIS_PWD,
            decode_responses=True,
        )
        self.rate_limits = {
            "auth": {"calls": 5, "period": 60},  # 5 calls per minute
            "api": {"calls": 100, "period": 60},  # 100 calls per minute
        }

    async def check_rate_limit(self, wallet_address: str, action_type: str):
        """Check if user has exceeded rate limit"""
        key = f"rate_limit:{action_type}:{wallet_address}"
        current_time = datetime.now().timestamp()
        limit = self.rate_limits[action_type]

        # Clean old records
        await self.redis.zremrangebyscore(key, 0, current_time - limit["period"])

        # Check current count
        count = await self.redis.zcard(key)
        if count >= limit["calls"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        # Add new request
        await self.redis.zadd(key, {str(current_time): current_time})
        await self.redis.expire(key, limit["period"])
