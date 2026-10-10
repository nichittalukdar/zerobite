from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Donation(Base):
    __tablename__ = "donations"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_donations_positive_quantity"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    donor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    pickup_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(30), default="meals", nullable=False)
    expiry_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="available", index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    donor = relationship("User", back_populates="donations")
    claims = relationship("Claim", back_populates="donation", cascade="all, delete-orphan")
