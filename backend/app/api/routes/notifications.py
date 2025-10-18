from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from google.cloud import firestore

from ..deps.auth import require_user
from ...core.firebase import db

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationSettings(BaseModel):
    notifications: bool = True
    study_reminders: bool = True
    daily_checkin: bool = True
    achievement_notifications: bool = False
    social_updates: bool = False


class NotificationCreate(BaseModel):
    type: str = Field(..., description="Notification category identifier")
    title: str
    message: str
    scheduled_for: Optional[datetime] = None
    action_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationReadUpdate(BaseModel):
    is_read: bool = True


class NotificationResponse(BaseModel):
    id: str
    type: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    is_read: bool = False
    created_at: Optional[str] = None
    scheduled_for: Optional[str] = None
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


SUCCESS_RESPONSE = {"ok": True, "message": "Operation completed successfully"}


def _user_doc(uid: str):
    return db.collection("users").document(uid)


def _notifications_collection(uid: str):
    return _user_doc(uid).collection("notifications")


def _isoformat(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def _serialize_notification(doc) -> Dict[str, Any]:
    data = doc.to_dict() or {}
    created_at = data.get("created_at")
    scheduled_for = data.get("scheduled_for")

    return {
        "id": doc.id,
        "type": data.get("type"),
        "title": data.get("title"),
        "message": data.get("message"),
        "is_read": data.get("is_read", False),
        "created_at": _isoformat(created_at),
        "scheduled_for": _isoformat(scheduled_for),
        "action_url": data.get("action_url"),
        "metadata": data.get("metadata") or {},
    }


# Routes


@router.get("/settings", response_model=NotificationSettings)
def get_notification_settings(user: dict = Depends(require_user)):
    uid = user["uid"]
    doc_snapshot = _user_doc(uid).get()

    if not doc_snapshot.exists:
        return NotificationSettings()

    stored = (doc_snapshot.to_dict() or {}).get("notification_settings") or {}
    return NotificationSettings(**{**NotificationSettings().model_dump(), **stored})


@router.put("/settings", response_model=Dict[str, Any])
def update_notification_settings(
    payload: NotificationSettings, user: dict = Depends(require_user)
):
    uid = user["uid"]
    _user_doc(uid).set({"notification_settings": payload.model_dump()}, merge=True)
    return SUCCESS_RESPONSE


@router.get("/", response_model=List[NotificationResponse])
def list_notifications(user: dict = Depends(require_user)):
    uid = user["uid"]
    notifications_ref = _notifications_collection(uid)
    query = notifications_ref.order_by(
        "created_at", direction=firestore.Query.DESCENDING
    )
    docs = query.stream()
    return [_serialize_notification(doc) for doc in docs]


@router.post("/", response_model=NotificationResponse)
def create_notification(
    payload: NotificationCreate, user: dict = Depends(require_user)
):
    uid = user["uid"]
    now = datetime.now(timezone.utc)
    data = {
        "type": payload.type,
        "title": payload.title,
        "message": payload.message,
        "is_read": False,
        "created_at": now,
        "scheduled_for": payload.scheduled_for,
        "action_url": payload.action_url,
        "metadata": payload.metadata or {},
    }

    doc_ref = _notifications_collection(uid).document()
    doc_ref.set(data)
    stored_doc = doc_ref.get()
    return _serialize_notification(stored_doc)


@router.put("/{notification_id}/read", response_model=Dict[str, Any])
def mark_notification_read(
    notification_id: str,
    payload: NotificationReadUpdate,
    user: dict = Depends(require_user),
):
    uid = user["uid"]
    doc_ref = _notifications_collection(uid).document(notification_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Notification not found")

    doc_ref.update({"is_read": payload.is_read})
    return SUCCESS_RESPONSE


@router.put("/read-all", response_model=Dict[str, Any])
def mark_all_notifications_read(user: dict = Depends(require_user)):
    uid = user["uid"]
    notifications_ref = _notifications_collection(uid)
    unread_query = notifications_ref.where("is_read", "==", False)
    unread_docs = list(unread_query.stream())

    if not unread_docs:
        return SUCCESS_RESPONSE

    batch = db.batch()
    for doc in unread_docs:
        batch.update(doc.reference, {"is_read": True})
    batch.commit()

    return SUCCESS_RESPONSE


@router.delete("/{notification_id}", response_model=Dict[str, Any])
def delete_notification(notification_id: str, user: dict = Depends(require_user)):
    uid = user["uid"]
    doc_ref = _notifications_collection(uid).document(notification_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Notification not found")

    doc_ref.delete()
    return SUCCESS_RESPONSE


@router.get("/unread-count", response_model=Dict[str, int])
def get_unread_notification_count(user: dict = Depends(require_user)):
    uid = user["uid"]
    unread_query = _notifications_collection(uid).where("is_read", "==", False)
    total = sum(1 for _ in unread_query.stream())
    return {"count": total}
