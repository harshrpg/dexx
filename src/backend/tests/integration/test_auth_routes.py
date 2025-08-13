from fastapi import status


def test_get_nonce(test_client, test_wallet):
    response = test_client.get(f"/auth/nonce/{test_wallet['address']}")
    assert response.status_code == status.HTTP_200_OK
    assert "nonce" in response.json()
    assert isinstance(response.json()["nonce"], str)


def test_get_nonce_invalid_address(test_client):
    response = test_client.get("/auth/nonce/0xinvalid")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid wallet address" in response.json()["detail"]


def test_verify_wallet(test_client, test_wallet, signed_message):
    # First get nonce
    response = test_client.post(
        "/auth/verify-wallet",
        json={
            "address": test_wallet["address"],
            "signature": signed_message["signature"],
            "nonce": signed_message["nonce"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_verify_wallet_invalid_signature(test_client, test_wallet, signed_message):
    response = test_client.post(
        "/auth/verify-wallet",
        json={
            "address": test_wallet["address"],
            "signature": "0x" + "1" * 130,
            "nonce": signed_message["nonce"],
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_route(test_client, test_wallet, signed_message):
    # First get token
    auth_response = test_client.post(
        "/auth/verify-wallet",
        json={
            "address": test_wallet["address"],
            "signature": signed_message["signature"],
            "nonce": signed_message["nonce"],
        },
    )

    token = auth_response.json()["access_token"]

    # Test protected route
    response = test_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["wallet_address"] == test_wallet["address"]
