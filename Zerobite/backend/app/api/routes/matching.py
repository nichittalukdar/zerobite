from fastapi import APIRouter, HTTPException, Query
from app.api.deps import CurrentUser, DbSession
from app.models.donation import Donation
from app.services.matching_service import recommend_receivers

router = APIRouter()


@router.get("/matching/{donation_id}")
@router.get("/donations/{donation_id}/recommendations")
def match_donation(
    donation_id: int,
    db: DbSession,
    user: CurrentUser,
    max_distance_km: float = Query(default=20, gt=0, le=200),
):
    if user.role not in {"donor", "admin"}:
        raise HTTPException(status_code=403, detail="Only donors and admins can request matching.")
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found.")
    if user.role != "admin" and donation.donor_id != user.id:
        raise HTTPException(status_code=403, detail="You can only request recommendations for your own donations.")
    try:
        matches = recommend_receivers(db, donation_id, max_distance_km)
    except ValueError as exc:
        message = str(exc)
        code = 404 if message == "Donation not found." else 409
        raise HTTPException(status_code=code, detail=message) from exc
    return {"donation_id": donation_id, "count": len(matches), "recommendations": matches}
