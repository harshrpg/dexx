from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# from eth_typing import Address


class WalletAuth(BaseModel):
    address: str = Field(..., description="Ethereum wallet address")
    signature: str = Field(..., description="Signed message signature")
    nonce: str = Field(..., description="Nonce used for signing")
    chain_type: Optional[str] = None


class UserInDB(BaseModel):
    wallet_address: str
    nonce: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    session_id: str


class TokenData(BaseModel):
    wallet_address: Optional[str] = None
