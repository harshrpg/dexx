from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class Message(BaseModel):
    content: str
    role: str
    timestamp: datetime = datetime.now()
    metadata: Optional[Dict] = None


class MessageHistory(BaseModel):
    wallet_address: str
    messages: List[Message]
    last_updated: datetime = datetime.now()
