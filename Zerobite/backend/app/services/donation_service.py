from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.donation import Donation


def ensure_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def create_donation(db: Session, donor_id: int, data) -> Donation:
    expiry = ensure_utc(data.expiry_at)
    if expiry <= datetime.now(timezone.utc):
        raise ValueError("Expiry time must be in the future.")
    payload = data.model_dump()
    payload["expiry_at"] = expiry
    if payload.get("photo_url") is not None:
        payload["photo_url"] = str(payload["photo_url"])
    payload["name"] = payload["name"].strip()
    payload["category"] = payload["category"].strip().lower()
    payload["unit"] = payload["unit"].strip()
    donation = Donation(donor_id=donor_id, **payload)
    db.add(donation)
    db.commit()
    db.refresh(donation)
    return donation


def list_available_donations(db: Session):
    now = datetime.now(timezone.utc)
    return db.scalars(
        select(Donation)
        .where(Donation.status == "available", Donation.expiry_at > now)
        .order_by(Donation.created_at.desc())
    ).all()
