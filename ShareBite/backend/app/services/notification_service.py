from sqlalchemy.orm import Session
from app.models.notification import Notification


def create_notification(db: Session, user_id: int, title: str, message: str, event_type: str) -> Notification:
    notification = Notification(
        user_id=user_id, title=title, message=message, event_type=event_type
    )
    db.add(notification)
    return notification
