import json
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel
from redis import Redis
from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class RedisService(Generic[T]):
    def __init__(self, model_class: type[T]):
        self.redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_UNAME,
            password=settings.REDIS_PWD,
            decode_responses=True,
        )
        self.model_class = model_class
        self.prefix = model_class.__name__.lower()

    def _get_key(self, id: str) -> str:
        """Generate Redis key with model prefix"""
        return f"{self.prefix}:{id}"

    async def create(self, id: str, data: T) -> None:
        """Create a new record"""
        key = self._get_key(id)
        json_data = data.model_dump_json()
        self.redis_client.set(key, json_data)

    async def get(self, id: str) -> Optional[T]:
        """Retrieve a record by ID"""
        key = self._get_key(id)
        data = self.redis_client.get(key)
        if not data:
            return None
        return self.model_class.model_validate_json(data)

    async def update(self, id: str, data: T) -> None:
        """Update an existing record"""
        key = self._get_key(id)
        json_data = data.model_dump_json()
        self.redis_client.set(key, json_data)

    async def delete(self, id: str) -> bool:
        """Delete a record by ID"""
        key = self._get_key(id)
        return bool(self.redis_client.delete(key))

    async def exists(self, id: str) -> bool:
        """Check if a record exists"""
        key = self._get_key(id)
        return bool(self.redis_client.exists(key))
