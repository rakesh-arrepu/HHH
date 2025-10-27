"""REST v1 auth endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from core.security import create_access_token, create_refresh_token, set_auth_cookies, clear_auth_cookies, decode_token, get_current_user
from services.auth import authenticate_user, create_user
from models.user import User


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


from core.security import set_csrf_cookie

@router.get("/health")
def health(response: Response):
    set_csrf_cookie(response)
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


# --- 2FA Endpoints ---

import pyotp
from fastapi import Request

@router.post("/2fa/enable")
def enable_2fa(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Begin 2FA setup for a Super Admin user and return TOTP QR provisioning URI."""
    if not hasattr(user, "role") or (getattr(user.role, "name", None) != "SUPER_ADMIN"):
        raise HTTPException(status_code=403, detail="Only Super Admin can enable 2FA")

    # Load the same user within this DB session to avoid cross-session assignment issues
    db_user: User | None = db.query(User).filter_by(id=str(user.id)).first()  # type: ignore
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if getattr(db_user, "is_2fa_enabled", False) and getattr(db_user, "totp_secret", None):
        raise HTTPException(status_code=409, detail="2FA already enabled")

    # Generate new secret and save
    totp_secret = pyotp.random_base32()
    db_user.totp_secret = totp_secret
    db_user.is_2fa_enabled = False
    db.commit()
    provisioning_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(db_user.email, issuer_name="DailyTracker")
    return {"provisioning_uri": provisioning_uri}

from pydantic import BaseModel

class TotpVerifyRequest(BaseModel):
    totp_code: str

@router.post("/2fa/verify")
def verify_2fa(
    payload: TotpVerifyRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Verify TOTP code to enable 2FA for Super Admin users."""
    if not hasattr(user, "role") or (getattr(user.role, "name", None) != "SUPER_ADMIN"):
        raise HTTPException(status_code=403, detail="Only Super Admin can verify 2FA")

    # Load user in this DB session
    db_user: User | None = db.query(User).filter_by(id=str(user.id)).first()  # type: ignore
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not getattr(db_user, "totp_secret", None):
        raise HTTPException(status_code=400, detail="2FA not initialized")

    totp = pyotp.TOTP(db_user.totp_secret)  # type: ignore
    if not totp.verify(payload.totp_code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")

    db_user.is_2fa_enabled = True
    db.commit()
    return {"2fa_enabled": True}
