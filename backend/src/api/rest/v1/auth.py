# REST v1 auth endpoints
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Any

from core.database import get_db
from services.auth import create_user, authenticate_user
=======
from typing import Any

from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from services.auth import authenticate_user, create_user
from sqlalchemy.orm import Session
>>>>>>> origin/chore/collect-modified-2025-10-11

router = APIRouter()


class UserOut(BaseModel):
    """REST v1 auth endpoints (merged).

    This file was reconstructed to remove merge markers and keep the best of both
    branch changes: consistent import ordering, readable multiline calls, and
    preserve functionality.
    """

    from typing import Any

    from fastapi import APIRouter, Depends, HTTPException, status
    from pydantic import BaseModel, EmailStr, Field
    from sqlalchemy.orm import Session

    from core.database import get_db
    from services.auth import authenticate_user, create_user


    router = APIRouter()


    class UserOut(BaseModel):
        id: str
        email: EmailStr
        name: str

        @classmethod
        def from_orm_user(cls, user: Any) -> "UserOut":
            return cls(id=user.id, email=user.email, name=user.name)


    class AuthResponse(BaseModel):
        token: str
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
        "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
    )
    def register(payload: RegisterRequest, db: Session = Depends(get_db)):
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

        # Auto-login after registration
        from core.security import create_access_token

        token = create_access_token({"sub": user.id, "email": user.email})
        return AuthResponse(token=token, user=UserOut.from_orm_user(user))


    @router.post("/login", response_model=AuthResponse)
    def login(payload: LoginRequest, db: Session = Depends(get_db)):
        try:
            user, token = authenticate_user(
                db, email=payload.email, password=payload.password
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        return AuthResponse(token=token, user=UserOut.from_orm_user(user))
        )
