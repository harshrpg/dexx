from datetime import datetime, timedelta
from typing import Optional
import base58
from eth_account.messages import encode_defunct
from web3 import Web3
import secrets
from fastapi import HTTPException, status
import jwt
from app.core.singleton import Singleton
from app.models.auth import Token, UserInDB, WalletAuth
from app.core.config import settings
from app.services.rate_limiter import RateLimiter
from app.services.session_service import SessionService
import solana.rpc.api as solana
from nacl.signing import VerifyKey

from app.services.utils.constants import AUTH_SIGNATURE_TEXT


class WalletAuthService(metaclass=Singleton):
    def __init__(self):
        self.session_service = SessionService()
        self.rate_limiter = RateLimiter()
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 300
        self.w3 = Web3()
        self.users_db = {}
        self.nonce_db = {}

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def generate_nonce(self, wallet_address: str) -> str:
        """Generate a new nonce for wallet signing"""
        nonce = secrets.token_hex(32)
        self.nonce_db[wallet_address.lower()] = nonce
        return nonce

    async def verify_signature(self, wallet_auth: WalletAuth, chain_type: str) -> bool:
        """Verify the signature based on chain type"""
        try:
            if chain_type == "EVM":
                return self._verify_evm_signature(wallet_auth)
            elif chain_type == "Solana":
                return self._verify_solana_signature(wallet_auth)
            return False
        except Exception as e:
            print(f"Signature verification error: {str(e)}")
            return False

    def _verify_evm_signature(self, wallet_auth: WalletAuth) -> bool:
        """Verify EVM wallet signature"""
        message = f"{AUTH_SIGNATURE_TEXT}{self.nonce_db[wallet_auth.address.lower()]}"
        message_hash = encode_defunct(text=message)

        try:
            recovered_address = self.w3.eth.account.recover_message(
                message_hash, signature=wallet_auth.signature
            )
            return recovered_address.lower() == wallet_auth.address.lower()
        except Exception as e:
            print(f"EVM signature verification error: {str(e)}")
            return False

    def _verify_solana_signature(self, wallet_auth: WalletAuth) -> bool:
        """Verify Solana wallet signature"""
        try:
            public_key = solana.Pubkey.from_string(wallet_auth.address)
            message = (
                f"{AUTH_SIGNATURE_TEXT}{self.nonce_db[wallet_auth.address.lower()]}"
            )
            message_bytes = message.encode("utf-8")

            # Decode the signature from base58
            signature_bytes = base58.b58decode(wallet_auth.signature)
            public_key_bytes = bytes(public_key)

            result = VerifyKey(public_key_bytes).verify(
                smessage=message_bytes, signature=signature_bytes
            )
            if result is not None:
                return True
            return False
        except Exception as e:
            print(f"Solana signature verification error: {str(e)}")
            return False

    async def authenticate_wallet(
        self, wallet_auth: WalletAuth, device_info: Optional[dict] = None
    ) -> Optional[Token]:
        """Authenticate a wallet using signature and create a session"""
        try:
            await self.rate_limiter.check_rate_limit(
                wallet_auth.address.lower(), "auth"
            )

            if not await self.verify_signature(
                wallet_auth, device_info.get("chain_type")
            ):
                return None

            # Get or create user
            user = self.users_db.get(wallet_auth.address.lower())
            if not user:
                user = UserInDB(
                    wallet_address=wallet_auth.address.lower(), nonce=wallet_auth.nonce
                )
                self.users_db[wallet_auth.address.lower()] = user

            token = self.create_access_token({"sub": user.wallet_address})
            # Create session with device info (if provided)
            device_info = device_info or {
                "user_agent": "Unknown",
                "ip_address": "Unknown",
                "device_type": "Unknown",
            }
            session_id = await self.session_service.create_session(
                user.wallet_address, token, device_info
            )
            # Clear used nonce
            self.nonce_db.pop(wallet_auth.address.lower(), None)
            token = Token(
                access_token=token,
                session_id=session_id,
            )
            return token
        except Exception as e:
            # Log the error here
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication failed: {str(e)}",
            )
