from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from ..deps.auth import require_user
from ...core.firebase import db

router = APIRouter(prefix="/profile", tags=["profile"])


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
            "notification_settings": {
                "notifications": True,
                "study_reminders": True,
                "daily_checkin": True,
                "achievement_notifications": False,
                "social_updates": False,
            },
            "user_preferences": {
                "daily_study_goal": 120,
                "theme": "system",
                "timezone": "UTC+8",
                "timer_settings": {
                    "focus_duration": 25,
                    "break_duration": 5,
                    "long_break_duration": 15,
                },
            },
        },
        merge=True,
    )
    return {"ok": True, "uid": uid, "message": "profile upserted successfully"}
