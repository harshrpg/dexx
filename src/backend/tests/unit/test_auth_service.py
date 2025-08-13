import jwt


def test_generate_nonce(auth_service, test_wallet):
    nonce = auth_service.generate_nonce(test_wallet["address"])
    assert isinstance(nonce, str)
    assert len(nonce) == 64  # 32 bytes hex

    # Test nonce is stored
    assert test_wallet["address"].lower() in auth_service.nonce_db
    assert auth_service.nonce_db[test_wallet["address"].lower()] == nonce


def test_create_access_token(auth_service, test_wallet):
    data = {"sub": test_wallet["address"]}
    token = auth_service.create_access_token(data)

    # Verify token
    payload = jwt.decode(
        token, auth_service.secret_key, algorithms=[auth_service.algorithm]
    )

    assert payload["sub"] == test_wallet["address"]
    assert "exp" in payload


def test_verify_signature(auth_service, test_wallet, signed_message, web3):
    # Test valid signature
    auth_data = {
        "address": test_wallet["address"],
        "signature": signed_message["signature"],
        "nonce": signed_message["nonce"],
    }

    d = auth_service.verify_signature(auth_data)
    print(d)
    assert d is True
    # Test invalid signature
    invalid_auth = auth_data.copy()
    invalid_auth["signature"] = "0x" + "1" * 130
    assert auth_service.verify_signature(invalid_auth) is False
