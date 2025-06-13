from pydantic import BaseModel, EmailStr


class SigninUserSchema(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str
