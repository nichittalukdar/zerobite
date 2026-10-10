from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from app.api.deps import CurrentUser, DbSession
from app.models.claim import Claim
from app.models.delivery import Delivery
from app.models.donation import Donation
from app.models.user import User
from app.schemas.delivery import DeliveryAssign, DeliveryPublic, DeliveryStatusUpdate
from app.services.notification_service import create_notification

router = APIRouter()


@router.post("/claims/{claim_id}/assign", response_model=DeliveryPublic, status_code=status.HTTP_201_CREATED)
def assign_volunteer(claim_id: int, data: DeliveryAssign, db: DbSession, user: CurrentUser):
    claim = db.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found.")
    donation = db.get(Donation, claim.donation_id)
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found.")
    if user.role != "admin" and not (user.role == "donor" and donation.donor_id == user.id):
        raise HTTPException(status_code=403, detail="Only the donor or admin can assign a volunteer.")
    if claim.status != "accepted":
        raise HTTPException(status_code=409, detail="Only accepted claims can be assigned for delivery.")
    volunteer = db.get(User, data.volunteer_id)
    if volunteer is None or not volunteer.is_active or volunteer.role != "volunteer":
        raise HTTPException(status_code=422, detail="A valid active volunteer is required.")
    delivery = db.scalar(select(Delivery).where(Delivery.claim_id == claim.id))
    if delivery is None:
        delivery = Delivery(claim_id=claim.id, volunteer_id=volunteer.id, status="assigned")
        db.add(delivery)
    else:
        if delivery.status in {"picked_up", "delivered"}:
            raise HTTPException(status_code=409, detail="This delivery can no longer be reassigned.")
        delivery.volunteer_id = volunteer.id
        delivery.status = "assigned"
    create_notification(db, volunteer.id, "Delivery assigned", f"You have been assigned pickup for {donation.name}.", "delivery_assigned")
    create_notification(db, claim.receiver_id, "Volunteer assigned", f"A volunteer has been assigned for {donation.name}.", "volunteer_assigned")
    db.commit()
    db.refresh(delivery)
    return delivery


@router.get("/mine", response_model=list[DeliveryPublic])
def my_deliveries(db: DbSession, user: CurrentUser):
    stmt = select(Delivery).join(Claim).join(Donation)
    if user.role == "volunteer":
        stmt = stmt.where(Delivery.volunteer_id == user.id)
    elif user.role == "donor":
        stmt = stmt.where(Donation.donor_id == user.id)
    elif user.role == "receiver":
        stmt = stmt.where(Claim.receiver_id == user.id)
    elif user.role != "admin":
        raise HTTPException(status_code=403, detail="Unsupported role.")
    return db.scalars(stmt.order_by(Delivery.created_at.desc())).all()


@router.put("/{delivery_id}/status", response_model=DeliveryPublic)
def update_delivery_status(delivery_id: int, data: DeliveryStatusUpdate, db: DbSession, user: CurrentUser):
    delivery = db.get(Delivery, delivery_id)
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found.")
    claim = db.get(Claim, delivery.claim_id)
    donation = db.get(Donation, claim.donation_id) if claim else None
    if claim is None or donation is None:
        raise HTTPException(status_code=409, detail="Delivery has incomplete claim data.")
    if user.role != "admin" and not (user.role == "volunteer" and delivery.volunteer_id == user.id):
        raise HTTPException(status_code=403, detail="Only the assigned volunteer or admin can update delivery status.")

    new_status = data.status
    allowed = {
        "assigned": {"picked_up", "cancelled"},
        "picked_up": {"delivered"},
        "delivered": set(),
        "cancelled": set(),
    }
    if new_status not in allowed.get(delivery.status, set()):
        raise HTTPException(status_code=409, detail=f"Cannot change delivery from {delivery.status} to {new_status}.")

    delivery.status = new_status
    now = datetime.now(timezone.utc)
    if new_status == "picked_up":
        delivery.picked_up_at = now
    elif new_status == "delivered":
        delivery.delivered_at = now
        if donation.status == "claimed":
            donation.status = "delivered"
    elif new_status == "cancelled":
        claim.status = "cancelled"
        if donation.status == "claimed":
            donation.status = "available"
        elif donation.status == "available":
            donation.quantity += claim.quantity
    for recipient_id in {donation.donor_id, claim.receiver_id}:
        create_notification(db, recipient_id, "Delivery status updated", f"Delivery for {donation.name} is now {new_status.replace('_', ' ')}.", f"delivery_{new_status}")
    db.commit()
    db.refresh(delivery)
    return delivery
