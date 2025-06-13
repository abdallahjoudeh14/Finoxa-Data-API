from typing import Annotated

from fastapi import status, Header, Response

from models.user_model import User


async def verfiy_api_key(
    response: Response,
    api_key: str | None = None,
    Authorization: Annotated[str | None, Header()] = None,
) -> bool:

    if not api_key and not Authorization:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "status": False,
            "message": "Unauthorized - No API key provided",
        }

    if api_key:
        api_key = api_key
    elif Authorization and Authorization.startswith("Bearer "):
        api_key = Authorization.split(" ")[1]
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "status": False,
            "message": "Unauthorized - No API key provided",
        }

    user = User.objects(api_key=api_key).first()
    if not user:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "status": False,
            "message": "Unauthorized - Invalid API key",
        }

    return {
        "status": True,
        "message": "API key is valid",
    }
