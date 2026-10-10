from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import CurrentUser
from app.core.database import get_db
from app.models.donation import Donation
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationPublic, DonationUpdate
from app.services.donation_service import create_donation, list_available_donations, ensure_utc

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


def _can_manage(donation: Donation, user: User) -> bool:
    return user.role == "admin" or (user.role == "donor" and donation.donor_id == user.id)


@router.post("/", response_model=DonationPublic, status_code=status.HTTP_201_CREATED)
def create_donation_endpoint(data: DonationCreate, db: DbSession, user: CurrentUser):
    if user.role not in {"donor", "admin"}:
        raise HTTPException(status_code=403, detail="Only donors can create donations.")
    try:
        return create_donation(db, user.id, data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/", response_model=list[DonationPublic])
def list_donations(db: DbSession, user: CurrentUser):
    return list_available_donations(db)


@router.get("/mine", response_model=list[DonationPublic])
def list_my_donations(db: DbSession, user: CurrentUser):
    if user.role not in {"donor", "admin"}:
        raise HTTPException(status_code=403, detail="Donor role required.")
    stmt = select(Donation).order_by(Donation.created_at.desc())
    if user.role != "admin":
        stmt = stmt.where(Donation.donor_id == user.id)
    return db.scalars(stmt).all()


@router.get("/{donation_id}", response_model=DonationPublic)
def get_donation(donation_id: int, db: DbSession, user: CurrentUser):
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found.")
    if donation.status != "available" and not _can_manage(donation, user):
        raise HTTPException(status_code=404, detail="Donation not found.")
    return donation


@router.patch("/{donation_id}", response_model=DonationPublic)
def update_donation(donation_id: int, data: DonationUpdate, db: DbSession, user: CurrentUser):
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found.")
    if not _can_manage(donation, user):
        raise HTTPException(status_code=403, detail="You cannot edit this donation.")
    if donation.status != "available":
        raise HTTPException(status_code=409, detail="Only available donations can be edited.")
    changes = data.model_dump(exclude_unset=True)
    if "expiry_at" in changes and changes["expiry_at"] is not None:
        expiry = ensure_utc(changes["expiry_at"])
        if expiry <= datetime.now(timezone.utc):
            raise HTTPException(status_code=422, detail="Expiry time must be in the future.")
        changes["expiry_at"] = expiry
    if "photo_url" in changes and changes["photo_url"] is not None:
        changes["photo_url"] = str(changes["photo_url"])
    for field, value in changes.items():
        if isinstance(value, str) and field in {"name", "category", "unit"}:
            value = value.strip()
        if field == "category" and value:
            value = value.lower()
        setattr(donation, field, value)
    if (donation.latitude is None) != (donation.longitude is None):
        raise HTTPException(status_code=422, detail="latitude and longitude must be provided together.")
    db.commit()
    db.refresh(donation)
    return donation


@router.delete("/{donation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_donation(donation_id: int, db: DbSession, user: CurrentUser):
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found.")
    if not _can_manage(donation, user):
        raise HTTPException(status_code=403, detail="You cannot delete this donation.")
    if donation.status != "available":
        raise HTTPException(status_code=409, detail="Only available donations can be deleted.")
    db.delete(donation)
    db.commit()
    return None
