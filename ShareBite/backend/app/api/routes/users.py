from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.api.deps import CurrentUser, DbSession, require_roles
from app.models.user import User
from app.schemas.user import UserPublic

router = APIRouter()


@router.get("/me", response_model=UserPublic)
def get_my_profile(user: CurrentUser):
    return user


@router.get("/", response_model=list[UserPublic])
def list_users(db: DbSession, admin: User = Depends(require_roles("admin"))):
    return db.scalars(select(User).order_by(User.id)).all()


@router.patch("/me/location", response_model=UserPublic)
def update_my_location(
    data: dict,
    db: DbSession,
    user: CurrentUser,
):
    # Strictly validate coordinates rather than accepting arbitrary profile edits.
    from pydantic import ValidationError, BaseModel, Field, model_validator
    class LocationUpdate(BaseModel):
        latitude: float = Field(ge=-90, le=90)
        longitude: float = Field(ge=-180, le=180)
    try:
        payload = LocationUpdate.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    user.latitude, user.longitude = payload.latitude, payload.longitude
    db.commit()
    db.refresh(user)
    return user
