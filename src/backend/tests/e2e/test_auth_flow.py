from eth_account.messages import encode_defunct
from fastapi import status

from app.services.utils.constants import AUTH_SIGNATURE_TEXT


def test_complete_auth_flow(test_client, test_wallet, web3):
    # Step 1: Get nonce
    nonce_response = test_client.get(f"/auth/nonce/{test_wallet['address']}")
    assert nonce_response.status_code == status.HTTP_200_OK
    nonce = nonce_response.json()["nonce"]

    # Step 2: Sign message
    message = f"{AUTH_SIGNATURE_TEXT}{nonce}"
    message_hash = encode_defunct(text=message)
    signed_message = web3.eth.account.sign_message(
        message_hash, private_key=test_wallet["private_key"]
    )

    # Step 3: Verify wallet and get token
    verify_response = test_client.post(
        "/auth/verify-wallet",
        json={
            "address": test_wallet["address"],
            "signature": signed_message.signature.hex(),
            "nonce": nonce,
        },
    )
    assert verify_response.status_code == status.HTTP_200_OK
    token = verify_response.json()["access_token"]

    # Step 4: Access protected route
    me_response = test_client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()["wallet_address"] == test_wallet["address"]
