from typing import Optional, List, Tuple
from uuid import uuid4

from app.models.user import User
from app.models.thread import ChatThread
from app.services.data_access.redis_service import RedisService
from app.services.thread_service import ThreadService


class UserService:
    def __init__(self):
        self.redis_service = RedisService[User](User)
        self.thread_service = ThreadService()

    async def handle_user_prompt(
        self,
        wallet_address: str,
        session_id: str,
        prompt: str,
        thread_id: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[User, str]:
        """
        Handle a user prompt, creating or updating user and thread as needed.

        Args:
            wallet_address: User's wallet address
            prompt: User's prompt message
            thread_id: Optional existing thread ID
            email: Optional user email

        Returns:
            Tuple[User, str]: The user object and thread ID
        """
        # Get or create user
        user = await self.get_user(wallet_address)
        if not user:
            user = await self.create_user(
                wallet_address=wallet_address, email=email, session_id=session_id
            )

        # Handle thread
        if not thread_id:
            # Create new thread
            thread_id = self.thread_service.create_thread(
                user_id=wallet_address, initial_message=prompt
            )
            # Create ChatThread object and update user
            chat_thread = ChatThread(thread_id=thread_id, last_response_id=None)
            user.thread = chat_thread
            await self.update_user(user)
        else:
            # Add message to existing thread
            self.thread_service.add_message(thread_id, "user", prompt)

        return user, thread_id

    async def update_thread_response(
        self, wallet_address: str, thread_id: str, response_id: str
    ) -> Optional[User]:
        """
        Update the last_response_id in the user's ChatThread.

        Args:
            wallet_address: User's wallet address
            thread_id: Thread ID
            response_id: Response ID to update

        Returns:
            Optional[User]: Updated user object if found, None otherwise
        """
        user = await self.get_user(wallet_address)
        if user and user.thread and user.thread.thread_id == thread_id:
            user.thread.last_response_id = response_id
            await self.update_user(user)
        return user

    async def create_user(
        self,
        wallet_address: str,
        session_id: str,
        email: Optional[str] = None,
        thread: Optional[ChatThread] = None,
    ) -> User:
        """
        Create a new user with the given wallet address.

        Args:
            wallet_address: User's wallet address (primary key)
            email: Optional email address
            thread: Optional ChatThread object

        Returns:
            User: The created user object
        """
        user = User(
            session_id=session_id,
            wallet_address=wallet_address,
            email=email,
            thread=thread,
        )
        await self.redis_service.create(wallet_address, user)
        return user

    async def add_message_to_thread(
        self, wallet_address: str, thread_id: str, role: str, content: str
    ) -> Optional[User]:
        """Add a message to an existing thread."""
        user = await self.get_user(wallet_address)
        if user and user.thread and user.thread.thread_id == thread_id:
            self.thread_service.add_message(thread_id, role, content)
            return user
        return None

    async def get_user(self, wallet_address: str) -> Optional[User]:
        """
        Retrieve a user by their wallet address.

        Args:
            wallet_address: The user's wallet address

        Returns:
            Optional[User]: The user object if found, None otherwise
        """
        return await self.redis_service.get(wallet_address)

    async def update_user(self, user: User) -> None:
        """
        Update an existing user.

        Args:
            user: The updated user object
        """
        if not user.wallet_address:
            raise ValueError("User must have a wallet address")
        await self.redis_service.update(user.wallet_address, user)

    async def delete_user(self, wallet_address: str) -> bool:
        """
        Delete a user by their wallet address.

        Args:
            wallet_address: The user's wallet address

        Returns:
            bool: True if the user was deleted, False otherwise
        """
        return await self.redis_service.delete(wallet_address)

    async def user_exists(self, wallet_address: str) -> bool:
        """
        Check if a user exists by their wallet address.

        Args:
            wallet_address: The user's wallet address

        Returns:
            bool: True if the user exists, False otherwise
        """
        return await self.redis_service.exists(wallet_address)

    async def update_user_thread(
        self, wallet_address: str, thread: ChatThread
    ) -> Optional[User]:
        """
        Update a user's thread.

        Args:
            wallet_address: The user's wallet address
            thread: The new ChatThread object

        Returns:
            Optional[User]: The updated user object if found, None otherwise
        """
        user = await self.get_user(wallet_address)
        if user:
            user.thread = thread
            await self.update_user(user)
        return user

    async def update_user_email(
        self, wallet_address: str, email: str
    ) -> Optional[User]:
        """
        Update a user's email address.

        Args:
            wallet_address: The user's wallet address
            email: The new email address

        Returns:
            Optional[User]: The updated user object if found, None otherwise
        """
        user = await self.get_user(wallet_address)
        if user:
            user.email = email
            await self.update_user(user)
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        Note: This is less efficient as it requires scanning all users.

        Args:
            email: The user's email address

        Returns:
            Optional[User]: The user object if found, None otherwise
        """
        # Note: This is a simplified implementation. In a production environment,
        # you might want to maintain a separate index for email lookups
        all_keys = self.redis_service.redis_client.keys(
            f"{self.redis_service.prefix}:*"
        )
        for key in all_keys:
            user = await self.redis_service.get(key.split(":")[-1])
            if user and user.email == email:
                return user
        return None

    async def get_user_thread(
        self, wallet_address: str, thread_id: str
    ) -> Optional[ChatThread]:
        """
        Get a user's ChatThread by thread ID.

        Args:
            wallet_address: The user's wallet address
            thread_id: The thread ID to look for

        Returns:
            Optional[ChatThread]: The ChatThread if found, None otherwise
        """
        user = await self.get_user(wallet_address)
        if user and user.thread and user.thread.thread_id == thread_id:
            return user.thread
        return None
