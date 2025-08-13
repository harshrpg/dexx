import fakeredis
import pytest
from fastapi.testclient import TestClient
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from datetime import datetime

from app.main import app
from app.services.auth_service import WalletAuthService
from app.services.session_service import SessionService
from app.services.utils.constants import AUTH_SIGNATURE_TEXT


@pytest.fixture
def mock_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def mock_rate_limiter(mock_redis):
    from app.services.rate_limiter import RateLimiter

    rate_limiter = RateLimiter()
    rate_limiter.redis = mock_redis
    return rate_limiter


@pytest.fixture
def mock_session_service(mock_redis):
    from app.services.session_service import SessionService

    session_service = SessionService()
    session_service.redis = mock_redis
    return session_service


@pytest.fixture
def auth_service(mock_rate_limiter, mock_session_service):
    from app.services.auth_service import WalletAuthService

    service = WalletAuthService()
    service.rate_limiter = mock_rate_limiter
    service.session_service = mock_session_service
    return service


@pytest.fixture
def session_service(mock_redis):
    service = SessionService()
    service.redis = mock_redis
    return service


@pytest.fixture
def mock_device_info():
    return {
        "user_agent": "Mozilla/5.0 (Test Browser)",
        "ip_address": "127.0.0.1",
        "device_type": "Test Device",
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_session_data(test_wallet, mock_device_info):
    return {
        "wallet_address": test_wallet["address"].lower(),
        "device_info": mock_device_info,
        "created_at": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat(),
        "is_active": True,
    }


@pytest.fixture
def test_client(auth_service):
    # Override dependency
    async def get_auth_service():
        return auth_service

    app.dependency_overrides = {WalletAuthService: get_auth_service}

    with TestClient(app) as client:
        yield client

    # Clean up
    app.dependency_overrides = {}


@pytest.fixture
def auth_service():
    return WalletAuthService()


@pytest.fixture
def test_wallet():
    """Create a test ethereum account"""

    account = Account.create()
    return {
        "address": account.address,
        "private_key": account.key.hex(),
        "account": account,
    }


@pytest.fixture
def web3():
    return Web3()


@pytest.fixture
async def signed_message(test_wallet, mock_redis):
    """Create a properly signed message for testing"""
    # Generate a test nonce
    nonce = "test_nonce_123"

    # Create the message that would be signed
    message = f"{AUTH_SIGNATURE_TEXT}{nonce}"
    message_hash = encode_defunct(text=message)

    # Sign with the test wallet
    signed = test_wallet["account"].sign_message(message_hash)

    return {"signature": signed.signature.hex(), "nonce": nonce, "message": message}
