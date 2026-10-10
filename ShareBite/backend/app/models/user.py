from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role in ('donor', 'receiver', 'volunteer', 'admin')", name="ck_users_role"),
        CheckConstraint("need_priority in ('low', 'medium', 'high', 'urgent')", name="ck_users_need_priority"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="receiver", nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    needed_quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    need_priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    donations = relationship("Donation", back_populates="donor", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="receiver")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    assigned_deliveries = relationship("Delivery", back_populates="volunteer", foreign_keys="Delivery.volunteer_id")
