from typing import Optional
from pydantic import BaseModel, Field

from app.models.thread import ChatThread


class User(BaseModel):
    """
    User model representing a user in the system.
    """

    wallet_address: Optional[str] = Field(
        default=None, description="User's wallet address"
    )
    email: Optional[str] = Field(default=None, description="User's email address")
    session_id: str = Field(description="Unique session identifier for the user")
    thread: Optional[ChatThread] = Field(
        default=None, description="Thread identifier for conversation tracking"
    )

    class Config:
        from_attributes = True
