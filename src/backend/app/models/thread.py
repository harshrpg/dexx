from typing import Optional
from pydantic import BaseModel


class ChatThread(BaseModel):
    thread_id: Optional[str]
    last_response_id: Optional[str]
