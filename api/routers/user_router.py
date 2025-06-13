from typing import Annotated

# pip modules
from fastapi import APIRouter, Depends, Response, status

from models.user_model import User
from dependencies.auth_dependency import protect_route
from dependencies.user_dependency import verfiy_api_key
from services.user_service import get_api_key

router = APIRouter()


@router.get("")
async def get_user(data: Annotated[dict, Depends(protect_route)]):

    return {
        "status": True,
        **data,
    }


@router.put("/generate-apikey")
async def generate_api_key(
    data: Annotated[dict, Depends(protect_route)], response: Response
):
    email = data["data"]["email"]
    api_key = get_api_key()
    user = User.objects(email=email).first()
    user.api_key = api_key
    user.save()

    response.status_code = status.HTTP_200_OK

    return {
        "status": True,
        "data": {
            "api_key": user.api_key,
        },
    }


@router.delete("/delete-apikey")
async def delete_api_key(
    data: Annotated[dict, Depends(protect_route)], response: Response
):
    email = data["data"]["email"]
    user = User.objects(email=email).first()
    user.api_key = ""
    user.save()

    response.status_code = status.HTTP_200_OK
    return {
        "status": True,
        "message": "API key deleted successfully",
    }


@router.get("/verify-apikey")
async def verify_api_key(
    api_key: Annotated[str, Depends(verfiy_api_key)],
):
    if not api_key["status"]:
        return api_key

    return {
        "status": True,
        "message": "API key verified",
    }
