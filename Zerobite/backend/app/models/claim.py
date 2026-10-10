from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Float, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Claim(Base):
    __tablename__ = "claims"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_claims_positive_quantity"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    donation_id: Mapped[int] = mapped_column(ForeignKey("donations.id", ondelete="CASCADE"), index=True, nullable=False)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True, nullable=False)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    donation = relationship("Donation", back_populates="claims")
    receiver = relationship("User", back_populates="claims")
    delivery = relationship("Delivery", back_populates="claim", uselist=False, cascade="all, delete-orphan")
