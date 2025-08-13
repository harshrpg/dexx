import asyncio
import pytest
from datetime import datetime, timedelta
import json
from fastapi import status
from app.models.response import ResponseType


@pytest.mark.asyncio
async def test_create_session(session_service, test_wallet, mock_device_info):
    token = "test_token"
    session_id = await session_service.create_session(
        test_wallet["address"], token, mock_device_info
    )

    # Verify session was created
    assert session_id.startswith("session:")

    # Verify session data
    session_data = await session_service.get_session(session_id)
    assert session_data is not None
    assert session_data["wallet_address"] == test_wallet["address"]
    assert session_data["token"] == token
    assert session_data["device_info"] == mock_device_info
    assert session_data["is_active"] is True


@pytest.mark.asyncio
async def test_get_session(session_service, sample_session_data):
    # Create a test session
    session_id = (
        f"session:{sample_session_data['wallet_address']}:{datetime.now().timestamp()}"
    )
    await session_service.redis.setex(
        session_id, timedelta(days=7), json.dumps(sample_session_data)
    )

    # Get and verify session
    session = await session_service.get_session(session_id)
    assert session is not None
    assert session["wallet_address"] == sample_session_data["wallet_address"]
    assert session["device_info"] == sample_session_data["device_info"]


@pytest.mark.asyncio
async def test_update_session_activity(session_service, sample_session_data):
    session_id = (
        f"session:{sample_session_data['wallet_address']}:{datetime.now().timestamp()}"
    )
    await session_service.redis.setex(
        session_id, timedelta(days=7), json.dumps(sample_session_data)
    )

    # Get original last_active time
    original_session = await session_service.get_session(session_id)
    original_last_active = original_session["last_active"]

    # Wait a moment
    await asyncio.sleep(1)

    # Update activity
    await session_service.update_session_activity(session_id)

    # Verify last_active was updated
    updated_session = await session_service.get_session(session_id)
    assert updated_session["last_active"] > original_last_active


@pytest.mark.asyncio
async def test_invalidate_session(session_service, sample_session_data):
    session_id = (
        f"session:{sample_session_data['wallet_address']}:{datetime.now().timestamp()}"
    )
    await session_service.redis.setex(
        session_id, timedelta(days=7), json.dumps(sample_session_data)
    )

    # Invalidate session
    await session_service.invalidate_session(session_id)

    # Verify session was removed
    assert await session_service.get_session(session_id) is None


@pytest.mark.asyncio
async def test_get_user_sessions(session_service, test_wallet, mock_device_info):
    # Create multiple sessions
    session_ids = []
    for i in range(3):
        session_id = await session_service.create_session(
            test_wallet["address"], f"token_{i}", mock_device_info
        )
        session_ids.append(session_id)

    # Get user sessions
    sessions = await session_service.get_user_sessions(test_wallet["address"])

    assert len(sessions) == 3
    assert all(s["wallet_address"] == test_wallet["address"] for s in sessions)


@pytest.mark.asyncio
async def test_tokenmetrics_success(async_client, mock_fetch_metadata, mock_metadata):
    mock_fetch_metadata.return_value = mock_metadata

    response = await async_client.get("/tokenmetrics/WBTC")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["type"] == ResponseType.SUCCESS
    assert data["message"] == "Metadata and chart rebuilt for WBTC"
    assert data["symbol"] == "WBTC"
    assert "metadata" in data
    assert data["metadata"]["symbol"] == "WBTC"


@pytest.mark.asyncio
async def test_tokenmetrics_not_found(async_client, mock_fetch_metadata):
    mock_fetch_metadata.return_value = None

    response = await async_client.get("/tokenmetrics/TRKW")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "No metadata found for TRKW"


@pytest.mark.asyncio
async def test_tokenmetrics_exception(async_client, mock_fetch_metadata):
    mock_fetch_metadata.side_effect = Exception("Unexpected Error")

    response = await async_client.get("/tokenmetrics/WBTC")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Unexpected Error"


