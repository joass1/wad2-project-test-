from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..deps.auth import require_user
from ...core.firebase import db
from ...core.notification_sender import send_achievement_notification

router = APIRouter(prefix="/achievements", tags=["achievements"])


class AchievementResponse(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    earned: bool  # Achievement criteria met
    claimed: bool  # User has claimed the reward
    unlocked_at: str | None = None
    claimed_at: str | None = None
    progress: int = 0
    required: int = 0
    category: str


class AchievementsOverviewResponse(BaseModel):
    achievements: List[AchievementResponse]
    total_unlocked: int
    total_achievements: int
    completion_percentage: int


# Define all achievements with their criteria
ACHIEVEMENTS_CONFIG = {
    "early_bird": {
        "title": "Early Bird",
        "description": "Joined StudyBuddy",
        "icon": "⭐",
        "category": "general",
        "required": 1,
        "check": lambda stats: 1 if stats.get("has_account") else 0,
    },
    "first_steps": {
        "title": "First Steps",
        "description": "Completed first study session",
        "icon": "👣",
        "category": "study",
        "required": 1,
        "check": lambda stats: stats.get("total_study_sessions", 0),
    },
    "dedicated_learner": {
        "title": "Dedicated Learner",
        "description": "Studied for 10 hours total",
        "icon": "📚",
        "category": "study",
        "required": 10,
        "check": lambda stats: int(stats.get("total_study_hours", 0)),
    },
    "streak_master": {
        "title": "Streak Master",
        "description": "Maintain a 7-day study streak",
        "icon": "🔥",
        "category": "consistency",
        "required": 7,
        "check": lambda stats: stats.get("longest_streak", 0),
    },
    "wellness_warrior": {
        "title": "Wellness Warrior",
        "description": "Complete 5 wellness check-ins",
        "icon": "❤️",
        "category": "wellness",
        "required": 5,
        "check": lambda stats: stats.get("total_checkins", 0),
    },
    "challenge_champion": {
        "title": "Challenge Champion",
        "description": "Complete 10 tasks",
        "icon": "🏆",
        "category": "tasks",
        "required": 10,
        "check": lambda stats: stats.get("completed_tasks", 0),
    },
}


def _achievements_collection(uid: str):
    """Get reference to user's achievements collection"""
    return db.collection("users").document(uid).collection("achievements")


async def _get_user_stats(uid: str) -> Dict[str, Any]:
    """Gather all user statistics for achievement checking"""
    stats = {
        "has_account": True,  # If they can access this, they have an account
        "total_study_sessions": 0,
        "total_study_hours": 0,
        "longest_streak": 0,
        "total_checkins": 0,
        "completed_tasks": 0,
    }
    
    # Get study sessions stats
    try:
        study_sessions = db.collection("users").document(uid).collection("studySessions").stream()
        total_minutes = 0
        session_count = 0
        for session in study_sessions:
            session_data = session.to_dict()
            total_minutes += session_data.get("duration_minutes", 0)
            session_count += 1
        stats["total_study_sessions"] = session_count
        stats["total_study_hours"] = total_minutes / 60
    except Exception:
        pass
    
    # Get wellness stats
    try:
        wellness_summary = (
            db.collection("users")
            .document(uid)
            .collection("wellness")
            .document("summary")
            .get()
        )
        if wellness_summary.exists:
            wellness_data = wellness_summary.to_dict() or {}
            overview = wellness_data.get("overview", {})
            stats["longest_streak"] = overview.get("longestStreak", 0)
            stats["total_checkins"] = overview.get("totalCheckIns", 0)
    except Exception:
        pass
    
    # Get tasks stats
    try:
        tasks = db.collection("users").document(uid).collection("tasks").stream()
        completed_count = 0
        for task in tasks:
            task_data = task.to_dict()
            if task_data.get("status") == "done":
                completed_count += 1
        stats["completed_tasks"] = completed_count
    except Exception:
        pass
    
    # TODO: Add social buddies count when social features are implemented
    # TODO: Add pet care days tracking
    
    return stats


async def _check_and_unlock_achievements(uid: str, stats: Dict[str, Any]) -> Dict[str, Any]:
    """Check user progress and mark achievements as earned (not claimed)"""
    achievements_ref = _achievements_collection(uid)
    claimed_count = 0
    newly_earned = []
    
    for achievement_id, config in ACHIEVEMENTS_CONFIG.items():
        doc_ref = achievements_ref.document(achievement_id)
        doc = doc_ref.get()
        
        # Calculate current progress
        current_progress = config["check"](stats)
        is_earned = current_progress >= config["required"]
        
        if doc.exists:
            achievement_data = doc.to_dict() or {}
            was_earned = achievement_data.get("earned", False)
            is_claimed = achievement_data.get("claimed", False)
            
            # Update progress
            doc_ref.update({
                "progress": current_progress,
                "earned": is_earned,
                "unlocked_at": datetime.now(timezone.utc) if (is_earned and not was_earned) else achievement_data.get("unlocked_at"),
                "updated_at": datetime.now(timezone.utc),
            })
            
            if is_earned and not was_earned:
                newly_earned.append(config["title"])
            
            if is_claimed:
                claimed_count += 1
        else:
            # Create new achievement record
            doc_ref.set({
                "earned": is_earned,
                "claimed": False,
                "progress": current_progress,
                "unlocked_at": datetime.now(timezone.utc) if is_earned else None,
                "claimed_at": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })
            
            if is_earned:
                newly_earned.append(config["title"])
    
    return {
        "claimed_count": claimed_count,
        "newly_earned": newly_earned,
    }


@router.get("/", response_model=AchievementsOverviewResponse)
async def get_achievements(user: dict = Depends(require_user)):
    """Get all achievements with current progress for the authenticated user"""
    uid = user["uid"]
    
    # Get user stats
    stats = await _get_user_stats(uid)
    
    # Check and unlock achievements
    unlock_result = await _check_and_unlock_achievements(uid, stats)
    
    # Get all achievement records
    achievements_ref = _achievements_collection(uid)
    achievements_docs = achievements_ref.stream()
    
    # Create achievement map
    achievement_map = {}
    for doc in achievements_docs:
        achievement_map[doc.id] = doc.to_dict()
    
    # Build response
    achievements_list = []
    for achievement_id, config in ACHIEVEMENTS_CONFIG.items():
        achievement_data = achievement_map.get(achievement_id, {})
        
        # Calculate progress
        current_progress = config["check"](stats)
        
        achievements_list.append(AchievementResponse(
            id=achievement_id,
            title=config["title"],
            description=config["description"],
            icon=config["icon"],
            category=config["category"],
            earned=achievement_data.get("earned", False),
            claimed=achievement_data.get("claimed", False),
            unlocked_at=achievement_data.get("unlocked_at").isoformat() if achievement_data.get("unlocked_at") else None,
            claimed_at=achievement_data.get("claimed_at").isoformat() if achievement_data.get("claimed_at") else None,
            progress=min(current_progress, config["required"]),
            required=config["required"],
        ))
    
    total_achievements = len(ACHIEVEMENTS_CONFIG)
    completion_percentage = int((unlock_result["claimed_count"] / total_achievements) * 100)
    
    return AchievementsOverviewResponse(
        achievements=achievements_list,
        total_unlocked=unlock_result["claimed_count"],
        total_achievements=total_achievements,
        completion_percentage=completion_percentage,
    )


@router.post("/check")
async def check_achievements(user: dict = Depends(require_user)):
    """Manually trigger achievement check and return newly earned achievements"""
    uid = user["uid"]
    
    stats = await _get_user_stats(uid)
    unlock_result = await _check_and_unlock_achievements(uid, stats)
    
    return {
        "message": f"Checked achievements. {len(unlock_result['newly_earned'])} newly earned.",
        "newly_earned": unlock_result["newly_earned"],
        "total_claimed": unlock_result["claimed_count"],
    }


@router.post("/{achievement_id}/claim")
async def claim_achievement(achievement_id: str, user: dict = Depends(require_user)):
    """Claim an earned achievement"""
    uid = user["uid"]
    
    # Check if achievement exists in config
    if achievement_id not in ACHIEVEMENTS_CONFIG:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    # Get achievement document
    doc_ref = _achievements_collection(uid).document(achievement_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Achievement not earned yet")
    
    achievement_data = doc.to_dict() or {}
    
    # Check if achievement is earned
    if not achievement_data.get("earned", False):
        raise HTTPException(status_code=400, detail="Achievement not earned yet")
    
    # Check if already claimed
    if achievement_data.get("claimed", False):
        raise HTTPException(status_code=400, detail="Achievement already claimed")
    
    # Claim the achievement
    doc_ref.update({
        "claimed": True,
        "claimed_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    
    config = ACHIEVEMENTS_CONFIG[achievement_id]
    
    # Send achievement notification (in-app + email)
    send_achievement_notification(
        uid=uid,
        achievement_title=config["title"],
        achievement_icon=config["icon"],
        achievement_description=config["description"],
        achievement_id=achievement_id,
    )
    
    return {
        "message": f"Successfully claimed '{config['title']}'!",
        "achievement": {
            "id": achievement_id,
            "title": config["title"],
            "icon": config["icon"],
            "claimed_at": datetime.now(timezone.utc).isoformat(),
        }
    }


@router.post("/{achievement_id}/unclaim")
async def unclaim_achievement(achievement_id: str, user: dict = Depends(require_user)):
    """Unclaim an achievement (for testing purposes)"""
    uid = user["uid"]
    
    # Check if achievement exists in config
    if achievement_id not in ACHIEVEMENTS_CONFIG:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    # Get achievement document
    doc_ref = _achievements_collection(uid).document(achievement_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    achievement_data = doc.to_dict() or {}
    
    # Check if already unclaimed
    if not achievement_data.get("claimed", False):
        raise HTTPException(status_code=400, detail="Achievement is not claimed")
    
    # Unclaim the achievement
    doc_ref.update({
        "claimed": False,
        "claimed_at": None,
        "updated_at": datetime.now(timezone.utc),
    })
    
    config = ACHIEVEMENTS_CONFIG[achievement_id]
    
    return {
        "message": f"Successfully unclaimed '{config['title']}' for testing!",
        "achievement": {
            "id": achievement_id,
            "title": config["title"],
            "icon": config["icon"],
        }
    }

