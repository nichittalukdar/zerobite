from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.claim import Claim
from app.models.donation import Donation
from app.models.user import User
from app.services.notification_service import create_notification


def create_claim(db: Session, receiver: User, donation_id: int, quantity: float) -> Claim:
    donation = db.scalar(select(Donation).where(Donation.id == donation_id).with_for_update())
    if donation is None:
        raise ValueError("Donation not found.")
    if donation.status != "available":
        raise ValueError("Donation is not available.")
    if donation.donor_id == receiver.id:
        raise ValueError("You cannot claim your own donation.")
    expiry = donation.expiry_at
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry <= datetime.now(timezone.utc):
        raise ValueError("Donation has expired.")
    if quantity > donation.quantity:
        raise ValueError("Requested quantity exceeds available quantity.")
    existing = db.scalar(select(Claim).where(
        Claim.donation_id == donation_id, Claim.receiver_id == receiver.id,
        Claim.status.in_(["pending", "accepted"]),
    ))
    if existing:
        raise ValueError("You already have an active claim for this donation.")
    claim = Claim(donation_id=donation_id, receiver_id=receiver.id, quantity=quantity, status="pending")
    db.add(claim)
    create_notification(db, donation.donor_id, "New donation claim", f"{receiver.name} requested {quantity:g} {donation.unit} of {donation.name}.", "claim_created")
    db.commit()
    db.refresh(claim)
    return claim


def list_my_claims(db: Session, receiver_id: int):
    return db.scalars(select(Claim).where(Claim.receiver_id == receiver_id).order_by(Claim.created_at.desc())).all()


def update_claim_status(db: Session, claim_id: int, actor: User, new_status: str) -> Claim:
    claim = db.scalar(select(Claim).where(Claim.id == claim_id).with_for_update())
    if claim is None:
        raise ValueError("Claim not found.")
    donation = db.get(Donation, claim.donation_id)
    if donation is None:
        raise ValueError("Donation not found.")

    if new_status in {"accepted", "rejected"}:
        if actor.role != "admin" and donation.donor_id != actor.id:
            raise PermissionError("Only the donor can decide this claim.")
        if claim.status != "pending":
            raise ValueError("Only pending claims can be decided.")
        if new_status == "accepted":
            if donation.status != "available":
                raise ValueError("Donation is no longer available.")
            if claim.quantity > donation.quantity:
                raise ValueError("Insufficient food quantity.")
            # Claims may reserve only part of a donation. Keep the listing available
            # for the remaining quantity; close it only when this claim takes all food.
            remaining = donation.quantity - claim.quantity
            if remaining <= 1e-6:
                donation.status = "claimed"
            else:
                donation.quantity = remaining
        claim.status = new_status
        create_notification(db, claim.receiver_id, f"Claim {new_status}", f"Your claim for {donation.name} was {new_status}.", f"claim_{new_status}")
    elif new_status == "cancelled":
        if actor.role != "admin" and claim.receiver_id != actor.id:
            raise PermissionError("You can only cancel your own claim.")
        if claim.status != "pending":
            raise ValueError("Only pending claims can be cancelled.")
        claim.status = new_status
        create_notification(db, donation.donor_id, "Claim cancelled", f"A claim for {donation.name} was cancelled.", "claim_cancelled")
    else:
        raise ValueError("Unsupported claim status.")

    db.commit()
    db.refresh(claim)
    return claim
