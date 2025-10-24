from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from google.cloud import firestore
from pydantic import BaseModel, Field

from ..deps.auth import require_user
from ...core.firebase import db

router = APIRouter(prefix="/study-sessions", tags=["study-sessions"])


class StudySessionCreate(BaseModel):
    duration_minutes: int = Field(..., ge=1, le=480, description="Session duration in minutes")
    subject: Optional[str] = Field(None, description="Subject or topic studied")
    task: Optional[str] = Field(None, description="Specific task or topic")
    notes: Optional[str] = Field(None, description="Additional notes")
    session_type: str = Field(default="focus", description="Type of session (focus, break, etc.)")


class StudySessionResponse(BaseModel):
    id: str
    duration_minutes: int
    subject: Optional[str] = None
    task: Optional[str] = None
    notes: Optional[str] = None
    session_type: str
    created_at: str
    date: str


class StudyStatsResponse(BaseModel):
    total_hours: float
    total_sessions: int
    average_session_length: float
    sessions_this_week: int
    sessions_this_month: int


def _study_sessions_collection(uid: str):
    """Get reference to user's study sessions collection"""
    return db.collection("users").document(uid).collection("studySessions")


@router.post("/", response_model=StudySessionResponse)
def create_study_session(
    payload: StudySessionCreate, user: dict = Depends(require_user)
):
    """Create a new study session record"""
    uid = user["uid"]
    
    # Create session document
    session_data = {
        **payload.model_dump(),
        "created_at": datetime.now(timezone.utc),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "year": datetime.now(timezone.utc).year,
        "month": datetime.now(timezone.utc).month,
    }
    
    doc_ref = _study_sessions_collection(uid).add(session_data)
    session_id = doc_ref[1].id
    
    # Get the created document to return
    created_doc = doc_ref[1].get()
    session_dict = created_doc.to_dict()
    session_dict["id"] = session_id
    session_dict["created_at"] = session_dict["created_at"].isoformat()
    
    return StudySessionResponse(**session_dict)


@router.get("/stats", response_model=StudyStatsResponse)
def get_study_stats(user: dict = Depends(require_user)):
    """Get study statistics for the authenticated user"""
    uid = user["uid"]
    
    # Get all study sessions
    sessions_ref = _study_sessions_collection(uid)
    sessions = sessions_ref.stream()
    
    total_minutes = 0
    total_sessions = 0
    sessions_this_week = 0
    sessions_this_month = 0
    
    # Get current date for filtering
    now = datetime.now(timezone.utc)
    week_ago = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = week_ago.replace(day=week_ago.day - 7)
    month_ago = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_ago = month_ago.replace(month=month_ago.month - 1)
    
    for session in sessions:
        session_data = session.to_dict()
        duration = session_data.get("duration_minutes", 0)
        created_at = session_data.get("created_at")
        
        if isinstance(created_at, datetime):
            # Count sessions this week
            if created_at >= week_ago:
                sessions_this_week += 1
            
            # Count sessions this month
            if created_at >= month_ago:
                sessions_this_month += 1
        
        total_minutes += duration
        total_sessions += 1
    
    # Calculate statistics
    total_hours = round(total_minutes / 60, 1)
    average_session_length = round(total_minutes / total_sessions, 1) if total_sessions > 0 else 0
    
    return StudyStatsResponse(
        total_hours=total_hours,
        total_sessions=total_sessions,
        average_session_length=average_session_length,
        sessions_this_week=sessions_this_week,
        sessions_this_month=sessions_this_month,
    )


@router.get("/", response_model=List[StudySessionResponse])
def list_study_sessions(
    limit: int = 50,
    user: dict = Depends(require_user)
):
    """List recent study sessions for the authenticated user"""
    uid = user["uid"]
    
    sessions_ref = _study_sessions_collection(uid)
    sessions = sessions_ref.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit).stream()
    
    result = []
    for session in sessions:
        session_data = session.to_dict()
        session_data["id"] = session.id
        session_data["created_at"] = session_data["created_at"].isoformat()
        result.append(StudySessionResponse(**session_data))
    
    return result


@router.delete(
    "/reset",
    response_model=Dict[str, str],
    summary="Reset all study sessions",
)
def reset_study_sessions(user: dict = Depends(require_user)):
    """Reset all study sessions for the authenticated user."""
    uid = user["uid"]
    
    print(f"DEBUG: Resetting study sessions for user {uid}")
    
    # Delete all study sessions
    sessions_ref = _study_sessions_collection(uid)
    sessions = sessions_ref.stream()
    session_count = 0
    for session in sessions:
        session.reference.delete()
        session_count += 1
    print(f"DEBUG: Deleted {session_count} study sessions")
    
    return {"message": "All study sessions have been reset successfully"}


@router.delete("/{session_id}")
def delete_study_session(
    session_id: str, user: dict = Depends(require_user)
):
    """Delete a study session"""
    uid = user["uid"]
    
    session_ref = _study_sessions_collection(uid).document(session_id)
    session_doc = session_ref.get()
    
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session_ref.delete()
    return {"message": "Study session deleted successfully"}

class WeeklyStudySummaryResponse(BaseModel):
    daily_hours: dict[str, float]  # {"2025-10-17": 2.5, ...}
    subject_hours: dict[str, float]  # {"Math": 3.0, "Physics": 1.5}

@router.get("/weekly-summary", response_model=WeeklyStudySummaryResponse)
def get_weekly_study_summary(user: dict = Depends(require_user)):
    """Get study hours per day and per subject for the last 7 days (optimized)"""
    uid = user["uid"]
    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = now - timedelta(days=7)

    sessions_ref = _study_sessions_collection(uid)
    # Query only sessions in the last 7 days
    sessions_query = sessions_ref.where("created_at", ">=", seven_days_ago)
    sessions = sessions_query.stream()

    daily_hours = defaultdict(float)
    subject_hours = defaultdict(float)

    for session in sessions:
        data = session.to_dict()
        created_at = data.get("created_at")
        duration_hours = data.get("duration_minutes", 0) / 60
        subject = data.get("subject") or "Unspecified"

        if isinstance(created_at, datetime):
            day_str = created_at.strftime("%Y-%m-%d")
            daily_hours[day_str] += duration_hours
            subject_hours[subject] += duration_hours

    # Fill in missing days with 0 hours
    for i in range(7):
        day = (seven_days_ago + timedelta(days=i)).strftime("%Y-%m-%d")
        daily_hours.setdefault(day, 0.0)

    return WeeklyStudySummaryResponse(
        daily_hours=dict(sorted(daily_hours.items())),
        subject_hours=dict(sorted(subject_hours.items()))
    )

class StudyStreakResponse(BaseModel):
    current_streak: int
    
@router.get("/streak", response_model=StudyStreakResponse)
def get_study_streak(user: dict = Depends(require_user)):
    """Get the user's current study streak (consecutive days including today)."""
    uid = user["uid"]

    sessions_ref = _study_sessions_collection(uid)
    sessions = sessions_ref.stream()

    # Collect unique study dates (in UTC)
    study_dates = set()
    for session in sessions:
        data = session.to_dict()
        if "date" in data:
            study_dates.add(data["date"])
        elif "created_at" in data and isinstance(data["created_at"], datetime):
            study_dates.add(data["created_at"].strftime("%Y-%m-%d"))

    if not study_dates:
        return StudyStreakResponse(current_streak=0)

    # Sort study dates (newest last)
    sorted_dates = sorted(datetime.strptime(d, "%Y-%m-%d").date() for d in study_dates)

    today = datetime.now(timezone.utc).date()
    streak = 0

    # Start from today and count backward while dates are consecutive
    for i in range(len(sorted_dates) - 1, -1, -1):
        date = sorted_dates[i]
        diff = (today - date).days
        if diff == streak:  # continuous streak
            streak += 1
        elif diff > streak:
            break  # gap found → streak ended

    return StudyStreakResponse(current_streak=streak)
