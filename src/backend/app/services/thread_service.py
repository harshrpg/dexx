from typing import Dict, List, Optional
import json
import uuid
from datetime import datetime
import redis
from app.config.agent_lore import SYSTEM_PROMPT
from app.core.config import settings
from app.core.singleton import Singleton


class ThreadService(metaclass=Singleton):
    """Service for managing user threads and chat history in Redis.

    This service handles:
    - Creating and managing chat threads per user
    - Storing and retrieving chat messages
    - Managing thread metadata (title, creation time, etc.)
    """

    def __init__(self):
        """Initialize Redis connection."""
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_UNAME,
            password=settings.REDIS_PWD,
            decode_responses=True,
        )

    def create_thread(self, user_id: str, initial_message: Optional[str] = None) -> str:
        """Create a new thread for a user.

        Args:
            user_id: The authenticated user's ID
            initial_message: Optional initial message to start the thread

        Returns:
            The newly created thread ID
        """
        thread_id = str(uuid.uuid4())
        thread_data = {
            "id": thread_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "title": initial_message[:50] + "..." if initial_message else "New Chat",
            "message_count": 0,
        }

        # Store thread metadata
        self.redis.hset(f"thread:{thread_id}", mapping=thread_data)

        # Add thread to user's thread list
        self.redis.sadd(f"user:{user_id}:threads", thread_id)

        # Store initial message if provided
        if initial_message:
            self.add_message(thread_id, "user", initial_message)

        return thread_id

    def add_message(self, thread_id: str, role: str, content: str) -> None:
        """Add a message to a thread.

        Args:
            thread_id: The thread ID
            role: The role of the message sender ('user' or 'assistant')
            content: The message content
        """
        message = {
            "id": str(uuid.uuid4()),
            "thread_id": thread_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store message
        self.redis.rpush(f"thread:{thread_id}:messages", json.dumps(message))

        # Update thread metadata
        self.redis.hincrby(f"thread:{thread_id}", "message_count", 1)
        self.redis.hset(
            f"thread:{thread_id}", "updated_at", datetime.utcnow().isoformat()
        )

    def get_thread(self, thread_id: str) -> Optional[Dict]:
        """Get thread metadata and messages.

        Args:
            thread_id: The thread ID

        Returns:
            Dictionary containing thread metadata and messages, or None if not found
        """
        # Get thread metadata
        thread_data = self.redis.hgetall(f"thread:{thread_id}")
        if not thread_data:
            return None

        # Get messages
        messages = self.redis.lrange(f"thread:{thread_id}:messages", 0, -1)
        thread_data["messages"] = [json.loads(msg) for msg in messages]

        return thread_data

    def get_user_threads(self, user_id: str) -> List[Dict]:
        """Get all threads for a user.

        Args:
            user_id: The user ID

        Returns:
            List of thread metadata dictionaries
        """
        thread_ids = self.redis.smembers(f"user:{user_id}:threads")
        threads = []

        for thread_id in thread_ids:
            thread_data = self.redis.hgetall(f"thread:{thread_id}")
            if thread_data:
                threads.append(thread_data)

        return threads

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all its messages.

        Args:
            thread_id: The thread ID

        Returns:
            True if thread was deleted, False if not found
        """
        # Get thread metadata to find user_id
        thread_data = self.redis.hgetall(f"thread:{thread_id}")
        if not thread_data:
            return False

        # Remove thread from user's thread list
        self.redis.srem(f"user:{thread_data['user_id']}:threads", thread_id)

        # Delete thread metadata and messages
        self.redis.delete(f"thread:{thread_id}")
        self.redis.delete(f"thread:{thread_id}:messages")

        return True

    def update_thread_title(self, thread_id: str, title: str) -> bool:
        """Update a thread's title.

        Args:
            thread_id: The thread ID
            title: New title

        Returns:
            True if title was updated, False if thread not found
        """
        if not self.redis.exists(f"thread:{thread_id}"):
            return False

        self.redis.hset(f"thread:{thread_id}", "title", title)
        return True

    def get_thread_messages(self, thread_id: str) -> dict:
        """
        Fetch only the role and content of a thread
        """
        if not self.redis.exists(f"thread:{thread_id}"):
            return None
        thread_messages = self.get_thread(thread_id=thread_id)
        return [
            {"role": i["role"], "content": i["content"]}
            for i in thread_messages.get("messages")
        ]
