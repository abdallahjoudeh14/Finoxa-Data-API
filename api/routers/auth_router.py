from typing import Annotated

# pip modules
from fastapi import APIRouter, Response, Depends, status


from models.user_model import User
from schemas.auth_schema import LoginUserSchema, SigninUserSchema
from services.auth_service import (
    generate_jwt_token,
    hash_password,
    verify_password,
)
from dependencies.auth_dependency import protect_route
from utils import rename_keys


router = APIRouter()

key_map = {
    "_id": "id",
    "apiKey": "api_key",
    "createdAt": "created_at",
    "updatedAt": "updated_at",
}


@router.post("/signup")
async def signup(
    user_data: SigninUserSchema,
    response: Response,
):
    # Check if user already exists
    if User.objects(email=user_data.email).first():
        response.status_code = status.HTTP_400_BAD_REQUEST

        return {
            "status": False,
            "message": "User is already exists",
        }

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create a new user
    user = User(name=user_data.name, email=user_data.email, password=hashed_password)
    user.save()

    # Generate JWT access token
    access_token = generate_jwt_token(data={"sub": user.email})

    user_dict: dict = user.to_mongo().to_dict()
    user_dict["_id"] = str(user_dict["_id"])
    user_dict = rename_keys(user_dict, key_map)
    user_dict.pop("password")

    return {
        "status": True,
        "access_token": access_token,
        "data": user_dict,
    }


@router.post("/login")
async def login(
    user_data: LoginUserSchema,
    response: Response,
):
    # Check if user exists and verify password
    user = User.objects(email=user_data.email).first()
    if not user or not verify_password(user_data.password, user.password):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "status": False,
            "message": "Invalid credentials",
        }

    # Generate JWT access token
    access_token = generate_jwt_token(data={"sub": user.email})

    user_dict: dict = user.to_mongo().to_dict()
    user_dict["_id"] = str(user_dict["_id"])
    user_dict = rename_keys(user_dict, key_map)
    user_dict.pop("password")

    return {
        "status": True,
        "access_token": access_token,
        "data": user_dict,
    }


@router.get("/logout")
async def logout():
    return {
        "status": True,
        "message": "Logged out successfully",
    }


@router.get("/me")
async def check_auth(data: Annotated[dict, Depends(protect_route)]):

    return {
        "status": True,
        **data,
    }
