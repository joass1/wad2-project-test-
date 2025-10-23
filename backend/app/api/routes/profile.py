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
            "coins": 500,  # Default coins for new users
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


@router.get("/coins")
def get_user_coins(user: dict = Depends(require_user)):
    """Get the user's current coin balance"""
    uid = user["uid"]
    doc_snapshot = db.collection("users").document(uid).get()

    if not doc_snapshot.exists:
        raise Exception("User profile not found")

    user_data = doc_snapshot.to_dict() or {}
    if "coins" not in user_data:
        raise Exception("Coins field not found in user profile")

    return {"coins": user_data["coins"]}


@router.put("/coins")
def update_user_coins(payload: dict, user: dict = Depends(require_user)):
    """Update the user's coin balance"""
    uid = user["uid"]
    new_coins = payload.get("coins")

    if new_coins is None:
        return {"ok": False, "message": "Missing 'coins' field"}

    if not isinstance(new_coins, int) or new_coins < 0:
        return {"ok": False, "message": "Coins must be a non-negative integer"}

    db.collection("users").document(uid).set(
        {"coins": new_coins},
        merge=True,
    )

    return {"ok": True, "coins": new_coins, "message": "Coins updated successfully"}


@router.get("/inventory")
def get_user_inventory(user: dict = Depends(require_user)):
    """Get the user's inventory"""
    uid = user["uid"]
    doc_snapshot = db.collection("users").document(uid).get()

    if not doc_snapshot.exists:
        raise Exception("User profile not found")

    user_data = doc_snapshot.to_dict() or {}
    inventory = user_data.get("inventory", [])

    return {"inventory": inventory}


@router.put("/inventory")
def update_user_inventory(payload: dict, user: dict = Depends(require_user)):
    """Update the user's inventory"""
    uid = user["uid"]
    inventory = payload.get("inventory")

    if inventory is None:
        return {"ok": False, "message": "Missing 'inventory' field"}

    if not isinstance(inventory, list):
        return {"ok": False, "message": "Inventory must be an array"}

    # Validate inventory items
    for item in inventory:
        if not isinstance(item, dict):
            return {"ok": False, "message": "Each inventory item must be an object"}
        if "icon" not in item or "name" not in item or "count" not in item:
            return {"ok": False, "message": "Each item must have icon, name, and count"}
        if not isinstance(item["count"], int) or item["count"] < 1:
            return {"ok": False, "message": "Item count must be a positive integer"}

    db.collection("users").document(uid).set(
        {"inventory": inventory},
        merge=True,
    )

    return {"ok": True, "inventory": inventory, "message": "Inventory updated successfully"}
