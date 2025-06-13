import secrets


def get_api_key(length: int = 32) -> str:
    return secrets.token_hex(length)
