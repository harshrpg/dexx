import pytest
from fastapi import status

from app.services.utils.constants import AUTH_SIGNATURE_TEXT


async def test_complete_session_lifecycle(
    test_client, test_wallet, web3, mock_device_info
):
    # 1. Get nonce
    nonce_response = test_client.get(f"/auth/nonce/{test_wallet['address']}")
    nonce = nonce_response.json()["nonce"]

    # 2. Sign message and create session
    message = f"{AUTH_SIGNATURE_TEXT}{nonce}"
    message_hash = encode_defunct(text=message)
    signed_message = web3.eth.account.sign_message(
        message_hash, private_key=test_wallet["private_key"]
    )

    auth_response = test_client.post(
        "/auth/verify-wallet",
        json={
            "address": test_wallet["address"],
            "signature": signed_message.signature.hex(),
            "nonce": nonce,
        },
        headers={"User-Agent": mock_device_info["user_agent"]},
    )

    auth_data = auth_response.json()
    token = auth_data["access_token"]
    session_id = auth_data["session_id"]

    # 3. Use session to access protected route
    me_response = test_client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == status.HTTP_200_OK

    # 4. Check session info
    sessions_response = test_client.get(
        "/auth/sessions", headers={"Authorization": f"Bearer {token}"}
    )
    assert sessions_response.status_code == status.HTTP_200_OK

    # 5. Revoke session
    revoke_response = test_client.post(
        f"/auth/sessions/{session_id}/revoke",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert revoke_response.status_code == status.HTTP_200_OK

    # 6. Verify session is revoked
    me_response = test_client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == status.HTTP_401_UNAUTHORIZED
