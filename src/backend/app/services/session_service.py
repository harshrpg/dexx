from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any
import json
import redis.asyncio as redis

from app.core.config import settings
from app.core.singleton import Singleton


class SessionService(metaclass=Singleton):
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_UNAME,
            password=settings.REDIS_PWD,
            decode_responses=True,
        )
        self.session_expire_days = 7

    async def create_session(
        self, user_wallet: str, token: str, device_info: Dict[str, Any]
    ) -> str:
        """Create a new session for a user"""
        try:
            session_id = f"session:{user_wallet}:{datetime.now().timestamp()}"

            session_data = self._build_session_data(user_wallet, token, device_info)

            async with self.redis.pipeline() as pipe:
                await pipe.setex(
                    session_id,
                    timedelta(days=self.session_expire_days),
                    json.dumps(session_data),
                ).sadd(user_wallet, session_id).execute()

            return session_id
        except redis.RedisError as e:
            logging.error(f"Redis Error while creating session: {str(e)}")
            raise

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID"""
        session_data = await self.redis.get(session_id)
        if not session_data:
            return None
        return json.loads(session_data)

    async def update_session_activity(self, session_id: str):
        """Update last active timestamp of session"""
        session_data = await self.get_session(session_id)
        if session_data:
            session_data["last_active"] = datetime.now().isoformat()
            await self.redis.setex(
                session_id,
                timedelta(days=self.session_expire_days),
                json.dumps(session_data),
            )

    async def invalidate_session(self, session_id: str):
        """Invalidate a specific session"""
        session_data = await self.get_session(session_id)
        if session_data:
            wallet_address = session_data["wallet_address"]
            await self.redis.srem(wallet_address, session_id)
            await self.redis.delete(session_id)

    async def get_user_sessions(self, wallet_address: str) -> list:
        """Get all active sessions for a user"""
        session_ids = await self.redis.smembers(wallet_address)
        sessions = []
        for session_id in session_ids:
            session_data = await self.get_session(session_id)
            if session_data:
                sessions.append(session_data)
        return sessions

    def _build_session_data(
        self, user_wallet: str, token: str, device_info: Dict[str, Any]
    ) -> Dict:
        return {
            "wallet_address": user_wallet,
            "token": token,
            "device_info": device_info,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "is_active": True,
        }
