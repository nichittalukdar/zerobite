from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import CurrentUser, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserPublic
from app.services.auth_service import authenticate_user, register_user

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: DbSession):
    try:
        return register_user(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: DbSession):
    user = authenticate_user(db, str(data.email), data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(subject=user.id), user=user)


@router.get("/me", response_model=UserPublic)
def get_my_account(user: CurrentUser):
    return user
