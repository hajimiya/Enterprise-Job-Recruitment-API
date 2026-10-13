
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hmac
import os
from fastapi import Header
from app.database import get_db
from app.models import Notification
from app.schemas import NotificationCreate, NotificationResponse
from app.security import get_current_user, require_admin

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)

INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN")


@router.post(
    "/internal",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_internal_notification(
    data: NotificationCreate,
    x_internal_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not INTERNAL_SERVICE_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Internal service token is not configured",
        )

    if (
        not x_internal_token
        or not hmac.compare_digest(
            x_internal_token,
            INTERNAL_SERVICE_TOKEN,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid internal service token",
        )

    notification = Notification(**data.model_dump())
    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification

@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    data: NotificationCreate,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    notification = Notification(**data.model_dump())

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


@router.get("/", response_model=list[NotificationResponse])
def list_notifications(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user["user_id"])
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user["user_id"],
        )
        .first()
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return notification


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user["user_id"],
        )
        .first()
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    db.delete(notification)
    db.commit()
