
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.models.claim import Claim
from app.models.donation import Donation
from app.schemas.claim import ClaimCreate, ClaimPublic
from app.services.claim_service import (
    create_claim,
    list_my_claims,
    update_claim_status,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ClaimPublic,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: ClaimCreate,
    db: DbSession,
    user: CurrentUser,
):
    if user.role != "receiver":
        raise HTTPException(
            status_code=403,
            detail="Only receivers can claim donations.",
        )

    try:
        return create_claim(
            db, user, data.donation_id, data.quantity
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/mine", response_model=list[ClaimPublic])
def mine(db: DbSession, user: CurrentUser):
    if user.role != "receiver":
        raise HTTPException(status_code=403, detail="Receiver role required.")
    return list_my_claims(db, user.id)


@router.get("/{claim_id}", response_model=ClaimPublic)
def get_claim(claim_id: int, db: DbSession, user: CurrentUser):
    claim = db.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found.")

    donation = db.get(Donation, claim.donation_id)

    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found.")

    if (
        user.role != "admin"
        and user.id not in {claim.receiver_id, donation.donor_id}
    ):
        raise HTTPException(status_code=403, detail="Access denied.")

    return claim


@router.post("/{claim_id}/accept", response_model=ClaimPublic)
def accept(claim_id: int, db: DbSession, user: CurrentUser):
    try:
        return update_claim_status(db, claim_id, user, "accepted")
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/{claim_id}/reject", response_model=ClaimPublic)
def reject(claim_id: int, db: DbSession, user: CurrentUser):
    try:
        return update_claim_status(db, claim_id, user, "rejected")
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/{claim_id}/cancel", response_model=ClaimPublic)
def cancel(claim_id: int, db: DbSession, user: CurrentUser):
    try:
        return update_claim_status(db, claim_id, user, "cancelled")
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))