import pytest
from fastapi import status
from eth_account.messages import encode_defunct

from app.services.utils.constants import AUTH_SIGNATURE_TEXT


@pytest.mark.asyncio
async def test_session_creation_on_login(
    test_client,
    test_wallet,
    signed_message,
    mock_device_info,
    auth_service,
    mock_redis,  # Add this to ensure Redis is mocked
):
    # First get nonce
    nonce_response = test_client.get(f"/auth/nonce/{test_wallet['address']}")
    assert nonce_response.status_code == status.HTTP_200_OK
    nonce = nonce_response.json()["nonce"]

    # Create signed message with actual nonce
    message = f"{AUTH_SIGNATURE_TEXT}{nonce}"
    message_hash = encode_defunct(text=message)
    signed = test_wallet["account"].sign_message(message_hash)

    try:
        # Verify wallet and create session
        response = test_client.post(
            "/auth/verify-wallet",
            json={
                "address": test_wallet["address"],
                "signature": signed.signature.hex(),
                "nonce": nonce,
            },
            headers={"User-Agent": mock_device_info["user_agent"]},
        )

        print("Response:", response.status_code, response.json())  # Debug print

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "session_id" in data

        # Verify session was created
        session_response = test_client.get(
            "/auth/sessions",
            headers={"Authorization": f"Bearer {data['access_token']}"},
        )

        assert session_response.status_code == status.HTTP_200_OK
        sessions = session_response.json()["sessions"]
        assert len(sessions) == 1
        assert (
            sessions[0]["device_info"]["user_agent"] == mock_device_info["user_agent"]
        )

    except Exception as e:
        print("Test error:", str(e))  # Debug print
        raise

    # async def test_session_revocation(test_client, test_wallet, signed_message):
    #     # First login and create session
    #     auth_response = test_client.post(
    #         "/auth/verify-wallet",
    #         json={
    #             "address": test_wallet["address"],
    #             "signature": signed_message["signature"],
    #             "nonce": signed_message["nonce"],
    #         },
    #     )

    #     auth_data = auth_response.json()
    #     session_id = auth_data["session_id"]
    #     token = auth_data["access_token"]

    #     # Revoke session
    #     revoke_response = test_client.post(
    #         f"/auth/sessions/{session_id}/revoke",
    #         headers={"Authorization": f"Bearer {token}"},
    #     )

    #     assert revoke_response.status_code == status.HTTP_200_OK

    #     # Try to use the revoked session
    #     me_response = test_client.get(
    #         "/auth/me", headers={"Authorization": f"Bearer {token}"}
    #     )

    #     assert me_response.status_code == status.HTTP_401_UNAUTHORIZED

    # async def test_multiple_sessions(test_client, test_wallet, signed_message):
    # Create multiple sessions
    sessions = []
    for _ in range(3):
        response = test_client.post(
            "/auth/verify-wallet",
            json={
                "address": test_wallet["address"],
                "signature": signed_message["signature"],
                "nonce": signed_message["nonce"],
            },
        )
        sessions.append(response.json())

    # Get all sessions
    sessions_response = test_client.get(
        "/auth/sessions",
        headers={"Authorization": f"Bearer {sessions[0]['access_token']}"},
    )

    assert sessions_response.status_code == status.HTTP_200_OK
    active_sessions = sessions_response.json()["sessions"]
    assert len(active_sessions) == 3
