import os
from typing import Annotated

from fastapi import Header, Response, HTTPException, status, Request


from services.auth_service import decode_jwt_token
from models.user_model import User
from utils import rename_keys


key_map = {
    "_id": "id",
    "apiKey": "api_key",
    "createdAt": "created_at",
    "updatedAt": "updated_at",
}


def protect_route(
    request: Request,
    response: Response,
    Authorization: Annotated[str | None, Header()] = None,
) -> dict:
    if not Authorization or not Authorization.startswith("Bearer "):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "status": False,
            "message": "Unauthorized - No token provided",
        }

    token = Authorization.split(" ")[1]

    if not token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "status": False,
            "message": "Unauthorized - No token provided",
        }

    try:
        payload = decode_jwt_token(token)

    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "status": False,
            "message": str(e),
        }

    try:
        user = User.objects(email=payload["sub"]).first()

        if not user:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {
                "status": False,
                "message": "Unathorized - User not found",
            }

        user_dict: dict = user.to_mongo().to_dict()
        user_dict["_id"] = str(user_dict["_id"])
        user_dict = rename_keys(user_dict, key_map)
        user_dict.pop("password")
        return {
            "data": user_dict,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
