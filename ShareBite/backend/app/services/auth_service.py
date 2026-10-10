from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from app.models.user import User


def register_user(db: Session, data) -> User:
    email = str(data.email).strip().lower()
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise ValueError("An account with this email already exists.")

    user = User(
        name=data.name.strip(), email=email,
        password_hash=hash_password(data.password), role=data.role,
        phone=data.phone, latitude=data.latitude, longitude=data.longitude,
        needed_quantity=data.needed_quantity, need_priority=data.need_priority,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("An account with this email already exists.") from exc
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    normalized_email = email.strip().lower()
    user = db.scalar(select(User).where(User.email == normalized_email))
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        return None
    return user
