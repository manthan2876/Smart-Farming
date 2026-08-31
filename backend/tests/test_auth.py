from __future__ import annotations

from app.api import (
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_round_trip() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert password_hash != "correct horse battery staple"
    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("wrong password", password_hash)


def test_access_and_refresh_tokens_have_separate_types() -> None:
    tokens = create_token_pair("farmer-1")

    assert decode_token(tokens["access_token"]) == "farmer-1"
    assert decode_token(tokens["refresh_token"], expected_type="refresh") == "farmer-1"

    try:
        decode_token(tokens["refresh_token"])
    except ValueError:
        pass
    else:
        raise AssertionError(
            "A refresh token must not authenticate as an access token."
        )


def test_decode_invalid_token() -> None:
    try:
        decode_token("invalid.token.payload")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid token should raise ValueError.")

