"""REST v1 auth endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from core.security import create_access_token, create_refresh_token, set_auth_cookies, clear_auth_cookies, decode_token
from services.auth import authenticate_user, create_user


router = APIRouter()


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str

    @classmethod
    def from_orm_user(cls, user: Any) -> "UserOut":
        return cls(id=user.id, email=user.email, name=user.name)


class AuthUserResponse(BaseModel):
    user: UserOut


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post(
    "/register", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    try:
        user = create_user(
            db, email=payload.email, password=payload.password, name=payload.name
        )
    except ValueError as e:
        # Email already registered or integrity error
        detail = str(e)
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
                if "already" in detail.lower()
                else status.HTTP_400_BAD_REQUEST
            ),
            detail=detail,
        )

    # Issue session cookies (access + refresh)
    access = create_access_token({"sub": user.id, "email": user.email})
    refresh = create_refresh_token({"sub": user.id, "email": user.email})
    set_auth_cookies(response, access, refresh)
    return AuthUserResponse(user=UserOut.from_orm_user(user))


@router.post("/login", response_model=AuthUserResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    try:
        user, access = authenticate_user(
            db, email=payload.email, password=payload.password
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    refresh = create_refresh_token({"sub": user.id, "email": user.email})
    set_auth_cookies(response, access, refresh)
    return AuthUserResponse(user=UserOut.from_orm_user(user))


@router.post("/refresh")
def refresh(request: Request, response: Response):
    token = request.cookies.get(settings.refresh_cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    sub = payload.get("sub")
    email = payload.get("email")
    access = create_access_token({"sub": sub, "email": email})
    refresh_new = create_refresh_token({"sub": sub, "email": email})
    set_auth_cookies(response, access, refresh_new)
    return {"status": "ok"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    clear_auth_cookies(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
