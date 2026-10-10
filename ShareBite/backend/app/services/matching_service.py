from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.donation import Donation
from app.models.user import User


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * earth_radius_km * asin(min(1.0, sqrt(a)))


def location_score(distance: float, max_distance_km: float = 20.0) -> float:
    return max(0.0, min(100.0, 100.0 * (1 - distance / max_distance_km)))


def quantity_score(available: float, needed: float | None) -> float:
    # Unknown receiver needs get a neutral score rather than pretending the need equals the donation.
    if needed is None or needed <= 0:
        return 70.0
    return min(available, needed) / max(available, needed) * 100.0


def expiry_score(expiry_at: datetime) -> float:
    if expiry_at.tzinfo is None:
        expiry_at = expiry_at.replace(tzinfo=timezone.utc)
    hours_left = (expiry_at - datetime.now(timezone.utc)).total_seconds() / 3600
    if hours_left <= 0:
        return 0.0
    if hours_left <= 2:
        return 100.0
    if hours_left <= 4:
        return 90.0
    if hours_left <= 8:
        return 75.0
    if hours_left <= 24:
        return 50.0
    return 30.0


def need_score(priority: str) -> float:
    return {"low": 40.0, "medium": 70.0, "high": 90.0, "urgent": 100.0}.get(priority.lower(), 70.0)


def recommend_receivers(db: Session, donation_id: int, max_distance_km: float = 20.0):
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise ValueError("Donation not found.")
    if donation.status != "available":
        raise ValueError("Donation is not available.")
    if donation.latitude is None or donation.longitude is None:
        raise ValueError("Donation needs coordinates for matching.")
    exp = expiry_score(donation.expiry_at)
    if exp == 0:
        raise ValueError("Donation has expired.")

    receivers = db.scalars(select(User).where(
        User.role == "receiver", User.is_active.is_(True),
        User.latitude.is_not(None), User.longitude.is_not(None),
    )).all()
    results = []
    for receiver in receivers:
        distance = distance_km(donation.latitude, donation.longitude, receiver.latitude, receiver.longitude)
        if distance > max_distance_km:
            continue
        loc = location_score(distance, max_distance_km)
        qty = quantity_score(donation.quantity, receiver.needed_quantity)
        urgency = exp
        need = need_score(receiver.need_priority)
        score = loc * 0.30 + qty * 0.20 + urgency * 0.25 + need * 0.25
        results.append({
            "receiver_id": receiver.id,
            "receiver_name": receiver.name,
            "distance_km": round(distance, 2),
            "location_score": round(loc, 2),
            "quantity_score": round(qty, 2),
            "expiry_score": round(urgency, 2),
            "need_score": round(need, 2),
            "match_score": round(score, 2),
        })
    return sorted(results, key=lambda item: item["match_score"], reverse=True)
