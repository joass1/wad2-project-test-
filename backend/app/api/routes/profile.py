from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..deps.auth import require_user
from ...core.firebase import db

router = APIRouter(prefix="/profile", tags=["profile"])

SUCCESS_RESPONSE = {"ok": True, "message": "Operation completed successfully"}

DEFAULT_NOTIFICATION_SETTINGS = {
    "notifications": True,
    "study_reminders": True,
    "daily_checkin": True,
    "achievement_notifications": False,
    "social_updates": False,
}

DEFAULT_USER_PREFERENCES = {
    "daily_study_goal": 120,
    "theme": "system",
    "timezone": "UTC+8",
    "timer_settings": {
        "focus_duration": 25,
        "break_duration": 5,
        "long_break_duration": 15,
    },
}


class TimerSettings(BaseModel):
    focus_duration: int = 25
    break_duration: int = 5
    long_break_duration: int = 15


class UserPreferences(BaseModel):
    daily_study_goal: int = 120
    theme: str = "system"
    timezone: str = "UTC+8"
    timer_settings: TimerSettings = Field(default_factory=TimerSettings)


@router.post("/")
# verify user id token before upserting profile
def upsert_profile(payload: dict, user: dict = Depends(require_user)):
    uid = user["uid"]
    # create document in users collection
    db.collection("users").document(uid).set(
        {
            "full_name": payload["name"],
            "email": payload["email"],
            "created_at": datetime.now(timezone.utc),
            "avatar": "",
            "notification_settings": deepcopy(DEFAULT_NOTIFICATION_SETTINGS),
            "user_preferences": deepcopy(DEFAULT_USER_PREFERENCES),
        },
        merge=True,
    )
    return {"ok": True, "uid": uid, "message": "profile upserted successfully"}


@router.get("/preferences", response_model=UserPreferences)
def get_user_preferences(user: dict = Depends(require_user)):
    uid = user["uid"]
    doc_snapshot = db.collection("users").document(uid).get()

    stored: Dict[str, Any] = {}
    if doc_snapshot.exists:
        stored = (doc_snapshot.to_dict() or {}).get("user_preferences") or {}

    merged = {**DEFAULT_USER_PREFERENCES, **stored}
    merged["timer_settings"] = {
        **DEFAULT_USER_PREFERENCES["timer_settings"],
        **(stored.get("timer_settings") or {}),
    }

    return UserPreferences(**merged)


@router.put("/preferences", response_model=Dict[str, Any])
def update_user_preferences(
    payload: UserPreferences, user: dict = Depends(require_user)
):
    uid = user["uid"]
    db.collection("users").document(uid).set(
        {"user_preferences": payload.model_dump()},
        merge=True,
    )
    return SUCCESS_RESPONSE
