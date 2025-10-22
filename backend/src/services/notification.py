from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.notification import Notification
from models.user import User

def get_user_notifications(db: Session, user_id: str, limit: int = 50, offset: int = 0) -> list[Notification]:
    """Get user's notifications, ordered by created_at desc."""
    notifications = db.query(Notification).filter_by(user_id=user_id).order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    return notifications

def mark_notification_read(db: Session, notification_id: str, user_id: str) -> Notification:
    """Mark a specific notification as read (only if owned by user)."""
    notification = db.query(Notification).filter_by(id=notification_id, user_id=user_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True # type: ignore
    db.commit()
    db.refresh(notification)
    return notification

def mark_all_notifications_read(db: Session, user_id: str) -> int:
    """Mark all user's notifications as read, return count updated."""
    count = db.query(Notification).filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.commit()
    return count

def create_notification(db: Session, user_id: str, type: str, title: str, message: str) -> Notification:
    """Create a new notification for a user."""
    from models.notification import NotificationType
    notification = Notification(
        user_id=user_id,
        type=NotificationType(type),
        title=title,
        message=message,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
