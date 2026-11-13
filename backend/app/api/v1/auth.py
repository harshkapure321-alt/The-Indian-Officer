from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import (
    DUMMY_HASH,
    REFRESH,
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair, UserOut
from app.schemas.common import Envelope

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _token_pair(user: User) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/register", response_model=Envelope[UserOut], status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

    user = User(name=body.name, email=email, hashed_password=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # two simultaneous registrations
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")
    db.refresh(user)
    return Envelope(data=UserOut.model_validate(user), message="Account created")


@router.post("/login", response_model=Envelope[TokenPair])
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    # Always run a bcrypt check so response time doesn't reveal whether the email exists.
    password_ok = verify_password(body.password, user.hashed_password if user else DUMMY_HASH)
    if user is None or not password_ok:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated")
    return Envelope(data=_token_pair(user), message="Login successful")


@router.post("/refresh", response_model=Envelope[TokenPair])
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        user_id = decode_token(body.refresh_token, REFRESH)
    except TokenError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Envelope(data=_token_pair(user), message="Token refreshed")


@router.get("/me", response_model=Envelope[UserOut])
def me(user: User = Depends(get_current_user)):
    return Envelope(data=UserOut.model_validate(user))
