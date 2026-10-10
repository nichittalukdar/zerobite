from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.api.deps import CurrentUser, DbSession
from app.models.notification import Notification
from app.schemas.notification import NotificationPublic

router = APIRouter()


@router.get("/", response_model=list[NotificationPublic])
def list_notifications(db: DbSession, user: CurrentUser, unread_only: bool = False):
    stmt = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    return db.scalars(stmt.order_by(Notification.created_at.desc()).limit(100)).all()


@router.patch("/{notification_id}/read", response_model=NotificationPublic)
def mark_notification_read(notification_id: int, db: DbSession, user: CurrentUser):
    notification = db.get(Notification, notification_id)
    if notification is None or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found.")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
