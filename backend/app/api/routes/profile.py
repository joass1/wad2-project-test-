from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from google.cloud import firestore

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

DEFAULT_PET_SETTINGS = {
    "selected_pet": None,
    "has_selected_pet": False,
    "pet_name": None,
}

DEFAULT_PET_STATUS = {
    "happiness": 60,
    "health": 60,
    "last_updated": None,  # Timestamp for daily deterioration
    "is_dead": False,
    "soju_count": 0,  # Daily soju consumption counter
    "soju_last_reset": None,  # Last date soju counter was reset
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
    doc_ref = db.collection("users").document(uid)
    doc_snapshot = doc_ref.get()
    if doc_snapshot.exists:
        return {"ok": True, "uid": uid, "message": "profile already exists"}
    if payload.get("avatar") is not None:
        avatar = payload["avatar"]
    else:
        avatar = ""
    # create document in users collection
    db.collection("users").document(uid).set(
        {
            "full_name": payload["name"],
            "email": payload["email"],
            "created_at": datetime.now(timezone.utc),
            "avatar": avatar,
            "coins": 500,  # Default coins for new users
            "notification_settings": deepcopy(DEFAULT_NOTIFICATION_SETTINGS),
            "user_preferences": deepcopy(DEFAULT_USER_PREFERENCES),
            "pet_settings": deepcopy(DEFAULT_PET_SETTINGS),
        },
        merge=True,
    )
    return {"ok": True, "uid": uid, "message": "profile upserted successfully"}


@router.put("/avatar")
def update_avatar(payload: dict, user: dict = Depends(require_user)):
    """Update user's profile avatar (base64 encoded image)"""
    uid = user["uid"]
    avatar = payload.get("avatar")
    
    # Allow null/empty string to remove avatar
    if avatar is None:
        return {"ok": False, "message": "Missing 'avatar' field"}
    
    # Validate base64 string if provided (basic check)
    if avatar and isinstance(avatar, str) and len(avatar) > 0:
        # Check if it looks like a base64 data URL
        if not (avatar.startswith("data:image/") or avatar.startswith("data:") or len(avatar) > 100):
            # If it's not a data URL, assume it's a base64 string (for backward compatibility)
            pass
    
    # Update avatar in Firestore
    db.collection("users").document(uid).set(
        {"avatar": avatar},
        merge=True,
    )
    
    return {"ok": True, "message": "Avatar updated successfully", "avatar": avatar}


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

    return {
        "ok": True,
        "inventory": inventory,
        "message": "Inventory updated successfully",
    }


@router.delete("/account")
def delete_user_account(user: dict = Depends(require_user)):
    """Delete user account and all associated data"""
    uid = user["uid"]
    try:
        # List of collections to clean up
        collections_to_clean = [
            "wellness_checkins",
            "study_sessions",
            "tasks",
            "achievements",
            "notifications",
        ]

        # Delete documents from root collections
        for collection_name in collections_to_clean:
            try:
                # Delete documents where user_id matches
                docs = (
                    db.collection(collection_name).where("user_id", "==", uid).stream()
                )
                for doc in docs:
                    doc.reference.delete()

                # Delete documents where uid matches (alternative field name)
                docs = db.collection(collection_name).where("uid", "==", uid).stream()
                for doc in docs:
                    doc.reference.delete()

                print(f"Cleaned up {collection_name} collection for user {uid}")
            except Exception as e:
                print(f"Error deleting from {collection_name}: {str(e)}")

        # Delete user's subcollections (Firestore doesn't auto-delete these)
        try:
            # Delete notifications subcollection
            notifications_ref = (
                db.collection("users").document(uid).collection("notifications")
            )
            notifications = notifications_ref.stream()
            for notification in notifications:
                notification.reference.delete()
            print(f"Deleted notifications subcollection for user {uid}")

            # Delete study sessions subcollection
            study_sessions_ref = (
                db.collection("users").document(uid).collection("studySessions")
            )
            study_sessions = study_sessions_ref.stream()
            for session in study_sessions:
                session.reference.delete()
            print(f"Deleted studySessions subcollection for user {uid}")

            # Delete wellness checkins subcollection
            wellness_ref = (
                db.collection("users").document(uid).collection("wellness_checkins")
            )
            wellness_checkins = wellness_ref.stream()
            for checkin in wellness_checkins:
                checkin.reference.delete()
            print(f"Deleted wellness_checkins subcollection for user {uid}")

            # Delete achievements subcollection
            achievements_ref = (
                db.collection("users").document(uid).collection("achievements")
            )
            achievements = achievements_ref.stream()
            for achievement in achievements:
                achievement.reference.delete()
            print(f"Deleted achievements subcollection for user {uid}")

        except Exception as e:
            print(f"Error deleting subcollections: {str(e)}")

        # Finally, delete the main user document
        db.collection("users").document(uid).delete()
        print(f"Deleted main user document for user {uid}")

        return {
            "ok": True,
            "message": "All user data has been successfully deleted from the database",
        }

    except Exception as e:
        print(f"Error deleting user account: {str(e)}")
        return {"ok": False, "message": f"Failed to delete user data: {str(e)}"}


@router.post("/seed-test-data")
def seed_test_data(user: dict = Depends(require_user)):
    """Add test data for development/testing (FOR TESTING ONLY)"""
    uid = user["uid"]
    now = datetime.now(timezone.utc)

    try:
        # Add test study session to subcollection
        from datetime import timedelta

        study_time = now - timedelta(hours=2)  # 2 hours ago
        db.collection("users").document(uid).collection("studySessions").add(
            {
                "duration_minutes": 75,
                "subject": "Mathematics",
                "task": "Calculus problems",
                "notes": "Completed chapter 5",
                "session_type": "focus",
                "created_at": study_time,
                "date": study_time.strftime("%Y-%m-%d"),
                "year": study_time.year,
                "month": study_time.month,
            }
        )

        # Add test wellness check-in to subcollection
        from datetime import timedelta

        yesterday = now - timedelta(days=1)
        db.collection("users").document(uid).collection("wellness_checkins").add(
            {
                "date": yesterday.strftime("%Y-%m-%d"),
                "mood": 8,  # Excellent mood
                "energy": 7,
                "sleep": 8,
                "stress": 2,
                "notes": "Feeling great today!",
            }
        )

        # Add test achievement to subcollection
        db.collection("users").document(uid).collection("achievements").add(
            {
                "achievement_id": "test_achievement",
                "title": "Test Achievement",
                "description": "This is a test achievement",
                "icon": "🎯",
                "earned": True,
                "claimed": True,
                "claimed_at": now - timedelta(days=3),
                "unlocked_at": now - timedelta(days=3),
                "progress": 1,
                "required": 1,
                "category": "test",
            }
        )

        return {
            "ok": True,
            "message": "Test data created successfully! Refresh your recent activity.",
        }

    except Exception as e:
        print(f"Error seeding test data: {e}")
        return {"ok": False, "message": f"Failed to seed test data: {str(e)}"}


@router.post("/test-wellness-checkin")
def create_test_wellness_checkin(user: dict = Depends(require_user)):
    """Create a test wellness check-in for testing recent activity"""
    uid = user["uid"]
    now = datetime.now(timezone.utc)

    try:
        from datetime import timedelta

        # Create check-in for yesterday
        yesterday = now - timedelta(days=1)
        db.collection("users").document(uid).collection("wellness_checkins").add(
            {
                "date": yesterday.strftime("%Y-%m-%d"),
                "mood": 9,  # Excellent mood
                "energy": 8,
                "sleep": 9,
                "stress": 1,
                "notes": "Test wellness check-in for recent activity!",
            }
        )

        return {
            "ok": True,
            "message": "Test wellness check-in created! Check recent activity.",
        }
    except Exception as e:
        return {"ok": False, "message": f"Failed to create wellness check-in: {str(e)}"}


@router.post("/test-achievement")
def create_test_achievement(user: dict = Depends(require_user)):
    """Create a test achievement for testing recent activity"""
    uid = user["uid"]
    now = datetime.now(timezone.utc)

    try:
        from datetime import timedelta

        # Create achievement from 2 days ago
        achievement_time = now - timedelta(days=2)
        db.collection("users").document(uid).collection("achievements").add(
            {
                "achievement_id": f"test_achievement_{int(now.timestamp())}",
                "title": "Test Achievement",
                "description": "This is a test achievement for recent activity",
                "icon": "🎯",
                "earned": True,
                "claimed": True,
                "claimed_at": achievement_time,
                "unlocked_at": achievement_time,
                "progress": 1,
                "required": 1,
                "category": "test",
            }
        )

        return {
            "ok": True,
            "message": "Test achievement created! Check recent activity.",
        }
    except Exception as e:
        return {"ok": False, "message": f"Failed to create achievement: {str(e)}"}


@router.post("/earn-and-claim-achievement")
def earn_and_claim_real_achievement(user: dict = Depends(require_user)):
    """Earn and claim a real achievement for testing recent activity"""
    uid = user["uid"]
    now = datetime.now(timezone.utc)

    try:
        from datetime import timedelta

        # Create the "early_bird" achievement (easiest to earn)
        achievement_time = now - timedelta(hours=1)  # 1 hour ago

        # First, create the achievement as earned
        doc_ref = (
            db.collection("users")
            .document(uid)
            .collection("achievements")
            .document("early_bird")
        )
        doc_ref.set(
            {
                "earned": True,
                "claimed": False,
                "progress": 1,
                "unlocked_at": achievement_time,
                "created_at": achievement_time,
                "updated_at": achievement_time,
            }
        )

        # Then claim it (this sets claimed_at)
        claim_time = now - timedelta(minutes=30)  # 30 minutes ago
        doc_ref.update(
            {
                "claimed": True,
                "claimed_at": claim_time,
                "updated_at": claim_time,
            }
        )

        return {
            "ok": True,
            "message": "Real achievement earned and claimed! Check recent activity.",
        }
    except Exception as e:
        return {"ok": False, "message": f"Failed to create real achievement: {str(e)}"}


@router.get("/debug-achievements")
def debug_achievements(user: dict = Depends(require_user)):
    """Debug endpoint to see what achievements exist in the database"""
    uid = user["uid"]

    try:
        # Get all achievements for this user
        achievements_ref = (
            db.collection("users").document(uid).collection("achievements")
        )
        achievements = achievements_ref.stream()

        achievement_list = []
        for achievement in achievements:
            data = achievement.to_dict()
            achievement_list.append(
                {
                    "id": achievement.id,
                    "earned": data.get("earned", False),
                    "claimed": data.get("claimed", False),
                    "claimed_at": data.get("claimed_at"),
                    "unlocked_at": data.get("unlocked_at"),
                    "progress": data.get("progress", 0),
                }
            )

        return {
            "ok": True,
            "achievements": achievement_list,
            "count": len(achievement_list),
        }
    except Exception as e:
        return {"ok": False, "message": f"Failed to fetch achievements: {str(e)}"}


@router.get("/recent-activity")
def get_recent_activity(user: dict = Depends(require_user)):
    """Get user's recent activity from various collections"""
    uid = user["uid"]
    activities = []

    try:
        # Fetch recent study sessions from subcollection
        try:
            study_sessions = (
                db.collection("users")
                .document(uid)
                .collection("studySessions")
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(5)
                .stream()
            )

            for session in study_sessions:
                data = session.to_dict()
                created_at = data.get("created_at")
                duration = data.get("duration_minutes", 0)
                subject = data.get("subject", "")

                # Build title with subject if available
                title = f"Completed study session ({duration} min)"
                if subject:
                    title = f"Studied {subject} ({duration} min)"

                activities.append(
                    {
                        "type": "study_session",
                        "icon": "🕐",
                        "color": "blue",
                        "title": title,
                        "timestamp": created_at,
                    }
                )
        except Exception as e:
            print(f"Error fetching study sessions: {e}")

        # Fetch recent wellness check-ins from subcollection
        try:
            wellness_checkins = (
                db.collection("users")
                .document(uid)
                .collection("wellness_checkins")
                .order_by("date", direction=firestore.Query.DESCENDING)
                .limit(5)
                .stream()
            )

            for checkin in wellness_checkins:
                data = checkin.to_dict()
                date = data.get("date")
                mood = data.get("mood", 5)  # Default to 5 if not set

                # Convert mood number to text
                mood_text = ""
                if mood >= 8:
                    mood_text = "excellent"
                elif mood >= 6:
                    mood_text = "good"
                elif mood >= 4:
                    mood_text = "okay"
                else:
                    mood_text = "low"

                timestamp = None
                if date:
                    try:
                        timestamp = datetime.strptime(date, "%Y-%m-%d").replace(
                            tzinfo=timezone.utc
                        )
                    except Exception as date_error:
                        print(f"Error converting date {date}: {date_error}")

                activities.append(
                    {
                        "type": "wellness_checkin",
                        "icon": "❤️",
                        "color": "green",
                        "title": f"Daily wellness check-in - {mood_text} mood",
                        "timestamp": timestamp,
                    }
                )
        except Exception as e:
            print(f"Error fetching wellness check-ins: {e}")

        # Fetch recent achievements from subcollection
        try:
            # First get all claimed achievements (without ordering to avoid index requirement)
            achievements = (
                db.collection("users")
                .document(uid)
                .collection("achievements")
                .where("claimed", "==", True)
                .stream()
            )

            achievement_count = 0
            achievement_activities = []

            for achievement in achievements:
                data = achievement.to_dict()
                claimed_at = data.get("claimed_at")
                achievement_id = achievement.id

                # Get title and icon from achievements config
                from ...api.routes.achievements import ACHIEVEMENTS_CONFIG

                config = ACHIEVEMENTS_CONFIG.get(achievement_id, {})
                title = config.get("title", "Achievement")
                icon = config.get("icon", "🏆")

                achievement_activities.append(
                    {
                        "type": "achievement",
                        "icon": icon,
                        "color": "purple",
                        "title": f'Unlocked "{title}" achievement',
                        "timestamp": claimed_at,
                    }
                )
                achievement_count += 1

            # Sort achievements by claimed_at and limit to 5 most recent
            achievement_activities.sort(
                key=lambda x: x["timestamp"]
                or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )
            achievement_activities = achievement_activities[:5]

            # Add to main activities list
            activities.extend(achievement_activities)

        except Exception as e:
            print(f"Error fetching achievements: {e}")

        # Sort all activities by timestamp (most recent first)
        activities = [a for a in activities if a.get("timestamp")]
        activities.sort(key=lambda x: x["timestamp"], reverse=True)

        # Limit to most recent 5 activities
        activities = activities[:5]

        # Convert timestamps to ISO format
        for activity in activities:
            timestamp = activity.get("timestamp")
            if timestamp:
                # Ensure timezone awareness
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                activity["timestamp"] = timestamp.isoformat()

        return {"activities": activities}

    except Exception as e:
        print(f"Error fetching recent activity: {e}")
        return {"activities": []}


@router.get("/pet-selection-status")
def get_pet_selection_status(user: dict = Depends(require_user)):
    """Check if user has selected a pet (for first-time user detection)"""
    uid = user["uid"]
    doc_snapshot = db.collection("users").document(uid).get()

    if not doc_snapshot.exists:
        return {"has_selected_pet": False, "selected_pet": None, "pet_name": None}

    user_data = doc_snapshot.to_dict() or {}
    pet_settings = user_data.get("pet_settings", {})

    return {
        "has_selected_pet": pet_settings.get("has_selected_pet", False),
        "selected_pet": pet_settings.get("selected_pet", None),
        "pet_name": pet_settings.get("pet_name", None),
    }


@router.post("/select-pet")
def select_pet(payload: dict, user: dict = Depends(require_user)):
    """Set user's selected pet"""
    uid = user["uid"]
    pet_key = payload.get("pet_key")

    if not pet_key:
        return {"ok": False, "message": "Missing 'pet_key' field"}

    # Validate pet key (you can add validation against your pet catalog here)
    valid_pets = ["catBlack", "catGrey", "catNew", "dogBlonde", "dogGrey", "dogLight"]
    if pet_key not in valid_pets:
        return {"ok": False, "message": "Invalid pet selection"}

    # Update user's pet settings
    db.collection("users").document(uid).set(
        {
            "pet_settings": {
                "selected_pet": pet_key,
                "has_selected_pet": True,
                "selected_at": datetime.now(timezone.utc),
            }
        },
        merge=True,
    )

    return {"ok": True, "message": "Pet selected successfully", "selected_pet": pet_key}


@router.put("/pet-name")
def update_pet_name(payload: dict, user: dict = Depends(require_user)):
    """Update user's pet name"""
    uid = user["uid"]
    pet_name = payload.get("pet_name")

    if not pet_name:
        return {"ok": False, "message": "Missing 'pet_name' field"}

    # Validate pet name (basic validation)
    if len(pet_name.strip()) == 0:
        return {"ok": False, "message": "Pet name cannot be empty"}

    if len(pet_name) > 20:
        return {"ok": False, "message": "Pet name must be 20 characters or less"}

    # Update user's pet settings
    db.collection("users").document(uid).set(
        {"pet_settings": {"pet_name": pet_name.strip()}},
        merge=True,
    )

    return {
        "ok": True,
        "message": "Pet name updated successfully",
        "pet_name": pet_name.strip(),
    }


def calculate_daily_deterioration(last_updated, current_time):
    """Calculate how much stats should deteriorate based on days passed"""
    if not last_updated:
        return 0

    # Calculate days passed
    time_diff = current_time - last_updated
    days_passed = time_diff.total_seconds() / (24 * 60 * 60)

    # Deteriorate 15 points per day (requires feeding daily)
    deterioration = int(days_passed * 15)

    return deterioration


@router.get("/pet-status")
def get_pet_status(user: dict = Depends(require_user)):
    """Get pet status with automatic daily deterioration"""
    uid = user["uid"]
    doc_snapshot = db.collection("users").document(uid).get()

    if not doc_snapshot.exists:
        # Initialize with default status
        now = datetime.now(timezone.utc)
        db.collection("users").document(uid).set(
            {"pet_status": {**DEFAULT_PET_STATUS, "last_updated": now}},
            merge=True,
        )
        return DEFAULT_PET_STATUS

    user_data = doc_snapshot.to_dict() or {}
    pet_status = user_data.get("pet_status", DEFAULT_PET_STATUS)

    # Apply daily deterioration
    now = datetime.now(timezone.utc)
    last_updated = pet_status.get("last_updated")

    # Check if soju counter needs to be reset (new day)
    soju_last_reset = pet_status.get("soju_last_reset")
    today_date = now.date()
    needs_soju_reset = False

    if soju_last_reset:
        last_reset_date = (
            soju_last_reset.date()
            if hasattr(soju_last_reset, "date")
            else datetime.fromisoformat(str(soju_last_reset)).date()
        )
        if last_reset_date < today_date:
            needs_soju_reset = True
    else:
        needs_soju_reset = True

    if last_updated and not pet_status.get("is_dead", False):
        deterioration = calculate_daily_deterioration(last_updated, now)

        if deterioration > 0 or needs_soju_reset:
            # Apply deterioration
            new_happiness = max(0, pet_status.get("happiness", 100) - deterioration)
            new_health = max(0, pet_status.get("health", 100) - deterioration)

            # Check if pet died
            is_dead = new_happiness == 0 or new_health == 0

            # Update database with new values
            updated_status = {
                "happiness": new_happiness,
                "health": new_health,
                "last_updated": now,
                "is_dead": is_dead,
                "soju_count": 0
                if needs_soju_reset
                else pet_status.get("soju_count", 0),
                "soju_last_reset": now
                if needs_soju_reset
                else pet_status.get("soju_last_reset"),
            }

            db.collection("users").document(uid).set(
                {"pet_status": updated_status},
                merge=True,
            )

            return updated_status
    elif needs_soju_reset:
        # Reset soju counter even if no deterioration
        updated_status = {**pet_status, "soju_count": 0, "soju_last_reset": now}

        db.collection("users").document(uid).set(
            {"pet_status": updated_status},
            merge=True,
        )

        return updated_status

    return pet_status


@router.put("/pet-status")
def update_pet_status(payload: dict, user: dict = Depends(require_user)):
    """Update pet status (happiness/health/soju_count)"""
    uid = user["uid"]
    happiness = payload.get("happiness")
    health = payload.get("health")
    soju_count = payload.get("soju_count")

    if happiness is None or health is None:
        return {"ok": False, "message": "Missing 'happiness' or 'health' field"}

    # Validate values
    if not isinstance(happiness, (int, float)) or not isinstance(health, (int, float)):
        return {"ok": False, "message": "Health and happiness must be numbers"}

    happiness = max(0, min(100, int(happiness)))
    health = max(0, min(100, int(health)))

    # Check if pet is revived
    is_dead = happiness == 0 or health == 0

    now = datetime.now(timezone.utc)
    updated_status = {
        "happiness": happiness,
        "health": health,
        "last_updated": now,
        "is_dead": is_dead,
    }

    # Include soju_count if provided
    if soju_count is not None:
        updated_status["soju_count"] = int(soju_count)
        updated_status["soju_last_reset"] = now

    db.collection("users").document(uid).set(
        {"pet_status": updated_status},
        merge=True,
    )

    return {
        "ok": True,
        "message": "Pet status updated successfully",
        "pet_status": updated_status,
    }
