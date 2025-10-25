from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from google.cloud import firestore
from pydantic import BaseModel, Field

from ..deps.auth import require_user
from ...core.firebase import db

router = APIRouter(prefix="/study-sessions", tags=["study-sessions"])


# ============================================================================
# STUDY SESSION MODELS
# ============================================================================

class StudySessionCreate(BaseModel):
    duration_minutes: int = Field(..., ge=1, le=480, description="Session duration in minutes")
    subject: Optional[str] = Field(None, description="Subject or topic studied")
    task: Optional[str] = Field(None, description="Specific task or topic")
    notes: Optional[str] = Field(None, description="Additional notes")
    session_type: str = Field(default="focus", description="Type of session (focus, break, etc.)")


class StudySessionStart(BaseModel):
    """Model for starting a new session"""
    planned_duration_minutes: int = Field(..., ge=1, le=480, description="Planned session duration in minutes")
    subject: Optional[str] = Field(None, description="Subject or topic studied")
    task: Optional[str] = Field(None, description="Specific task or topic")
    notes: Optional[str] = Field(None, description="Additional notes")
    session_type: str = Field(default="focus", description="Type of session (focus, break, etc.)")


class StudySessionUpdate(BaseModel):
    """Model for updating session state"""
    status: Optional[str] = Field(None, description="Session status: 'active', 'paused', 'completed', 'cancelled'")
    actual_duration_minutes: Optional[int] = Field(None, description="Actual time spent (updated on pause/complete)")
    time_remaining_seconds: Optional[int] = Field(None, description="Time remaining when paused")
    notes: Optional[str] = Field(None, description="Updated notes")
    subject: Optional[str] = Field(None, description="Updated subject")
    task: Optional[str] = Field(None, description="Updated task")


class StudySessionResponse(BaseModel):
    id: str
    planned_duration_minutes: int
    actual_duration_minutes: Optional[int] = None
    time_remaining_seconds: Optional[int] = None
    subject: Optional[str] = None
    task: Optional[str] = None
    notes: Optional[str] = None
    session_type: str
    status: str  # 'active', 'paused', 'completed', 'cancelled'
    started_at: str
    paused_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str
    updated_at: str
    date: str


class StudyStatsResponse(BaseModel):
    total_hours: float
    total_sessions: int
    average_session_length: float
    sessions_this_week: int
    sessions_this_month: int
    completed_sessions: int
    paused_sessions: int
    active_sessions: int


def _study_sessions_collection(uid: str):
    """Get reference to user's study sessions collection"""
    return db.collection("users").document(uid).collection("studySessions")


# ============================================================================
# STUDY SESSION ENDPOINTS WITH STATE TRACKING
# ============================================================================

@router.post("/start", response_model=StudySessionResponse)
def start_study_session(
    payload: StudySessionStart, user: dict = Depends(require_user)
):
    """Start a new study session with initial state"""
    uid = user["uid"]
    now = datetime.now(timezone.utc)
    
    # Create session document with initial 'active' status
    session_data = {
        "planned_duration_minutes": payload.planned_duration_minutes,
        "actual_duration_minutes": None,  # Will be updated when paused/completed
        "time_remaining_seconds": payload.planned_duration_minutes * 60,  # Full duration initially
        "subject": payload.subject,
        "task": payload.task,
        "notes": payload.notes,
        "session_type": payload.session_type,
        "status": "active",
        "started_at": now,
        "paused_at": None,
        "completed_at": None,
        "created_at": now,
        "updated_at": now,
        "date": now.strftime("%Y-%m-%d"),
        "year": now.year,
        "month": now.month,
    }
    
    doc_ref = _study_sessions_collection(uid).add(session_data)
    session_id = doc_ref[1].id
    
    # Get the created document to return
    created_doc = doc_ref[1].get()
    session_dict = created_doc.to_dict()
    session_dict["id"] = session_id
    session_dict["started_at"] = session_dict["started_at"].isoformat()
    session_dict["created_at"] = session_dict["created_at"].isoformat()
    session_dict["updated_at"] = session_dict["updated_at"].isoformat()
    
    return StudySessionResponse(**session_dict)


@router.patch("/{session_id}", response_model=StudySessionResponse)
def update_study_session(
    session_id: str,
    payload: StudySessionUpdate,
    user: dict = Depends(require_user)
):
    """Update a study session (pause, resume, complete, or update details)"""
    uid = user["uid"]
    
    session_ref = _study_sessions_collection(uid).document(session_id)
    session_doc = session_ref.get()
    
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        # No fields to update
        session_data = session_doc.to_dict()
        session_data["id"] = session_id
        return _format_session_response(session_data, session_id)
    
    now = datetime.now(timezone.utc)
    update_data["updated_at"] = now
    
    # Handle status changes
    if "status" in update_data:
        status = update_data["status"]
        
        if status == "paused":
            update_data["paused_at"] = now
            # Actual duration should be provided by frontend
            
        elif status == "completed":
            update_data["completed_at"] = now
            # Actual duration should be provided by frontend
            
        elif status == "active":
            # Resuming from pause
            update_data["paused_at"] = None
    
    session_ref.update(update_data)
    
    # Get updated document
    updated_doc = session_ref.get()
    session_data = updated_doc.to_dict()
    session_data["id"] = session_id
    
    return _format_session_response(session_data, session_id)


@router.post("/", response_model=StudySessionResponse)
def create_study_session(
    payload: StudySessionCreate, user: dict = Depends(require_user)
):
    """Create a completed study session record (legacy endpoint for backward compatibility)"""
    uid = user["uid"]
    now = datetime.now(timezone.utc)
    
    # Create session document as completed
    session_data = {
        "planned_duration_minutes": payload.duration_minutes,
        "actual_duration_minutes": payload.duration_minutes,
        "time_remaining_seconds": 0,
        "subject": payload.subject,
        "task": payload.task,
        "notes": payload.notes,
        "session_type": payload.session_type,
        "status": "completed",
        "started_at": now - timedelta(minutes=payload.duration_minutes),
        "paused_at": None,
        "completed_at": now,
        "created_at": now,
        "updated_at": now,
        "date": now.strftime("%Y-%m-%d"),
        "year": now.year,
        "month": now.month,
    }
    
    doc_ref = _study_sessions_collection(uid).add(session_data)
    session_id = doc_ref[1].id
    
    # Get the created document to return
    created_doc = doc_ref[1].get()
    session_dict = created_doc.to_dict()
    session_dict["id"] = session_id
    
    return _format_session_response(session_dict, session_id)


def _format_session_response(session_data: dict, session_id: str) -> StudySessionResponse:
    """Helper to format session data for response"""
    # Convert datetime objects to ISO strings
    session_data["id"] = session_id
    
    if isinstance(session_data.get("started_at"), datetime):
        session_data["started_at"] = session_data["started_at"].isoformat()
    
    if isinstance(session_data.get("paused_at"), datetime):
        session_data["paused_at"] = session_data["paused_at"].isoformat()
    elif session_data.get("paused_at") is None:
        session_data["paused_at"] = None
    
    if isinstance(session_data.get("completed_at"), datetime):
        session_data["completed_at"] = session_data["completed_at"].isoformat()
    elif session_data.get("completed_at") is None:
        session_data["completed_at"] = None
    
    if isinstance(session_data.get("created_at"), datetime):
        session_data["created_at"] = session_data["created_at"].isoformat()
    
    if isinstance(session_data.get("updated_at"), datetime):
        session_data["updated_at"] = session_data["updated_at"].isoformat()
    
    return StudySessionResponse(**session_data)


@router.get("/active", response_model=Optional[StudySessionResponse])
def get_active_session(user: dict = Depends(require_user)):
    """Get the currently active or paused session"""
    uid = user["uid"]
    
    sessions_ref = _study_sessions_collection(uid)
    # Query for active or paused sessions
    active_sessions = sessions_ref.where("status", "in", ["active", "paused"]).limit(1).stream()
    
    for session in active_sessions:
        session_data = session.to_dict()
        session_data["id"] = session.id
        return _format_session_response(session_data, session.id)
    
    return None


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
    completed_sessions = 0
    paused_sessions = 0
    active_sessions = 0
    
    # Get current date for filtering
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    for session in sessions:
        session_data = session.to_dict()
        status = session_data.get("status", "completed")
        
        # Count by status
        if status == "completed":
            completed_sessions += 1
        elif status == "paused":
            paused_sessions += 1
        elif status == "active":
            active_sessions += 1
        
        # Only count completed sessions for statistics
        if status == "completed":
            duration = session_data.get("actual_duration_minutes") or session_data.get("planned_duration_minutes", 0)
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
        completed_sessions=completed_sessions,
        paused_sessions=paused_sessions,
        active_sessions=active_sessions,
    )


@router.get("/", response_model=List[StudySessionResponse])
def list_study_sessions(
    limit: int = 50,
    status: Optional[str] = None,
    user: dict = Depends(require_user)
):
    """List study sessions for the authenticated user, optionally filtered by status"""
    uid = user["uid"]
    
    sessions_ref = _study_sessions_collection(uid)
    
    if status:
        sessions = sessions_ref.where("status", "==", status).order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit).stream()
    else:
        sessions = sessions_ref.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit).stream()
    
    result = []
    for session in sessions:
        session_data = session.to_dict()
        session_data["id"] = session.id
        result.append(_format_session_response(session_data, session.id))
    
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


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

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
    # Query only completed sessions in the last 7 days
    sessions_query = sessions_ref.where("created_at", ">=", seven_days_ago).where("status", "==", "completed")
    sessions = sessions_query.stream()

    daily_hours = defaultdict(float)
    subject_hours = defaultdict(float)

    for session in sessions:
        data = session.to_dict()
        created_at = data.get("created_at")
        duration_minutes = data.get("actual_duration_minutes") or data.get("planned_duration_minutes", 0)
        duration_hours = duration_minutes / 60
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
        # Only count completed sessions for streak
        if data.get("status", "completed") == "completed":
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


# ============================================================================
# SUBJECTS ENDPOINTS
# ============================================================================

class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Subject name")
    color: Optional[str] = Field(default="#4CAF50", description="Color hex code")
    icon: Optional[str] = Field(default="📚", description="Emoji icon")
    description: Optional[str] = Field(default=None, description="Subject description")


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None


class SubjectResponse(BaseModel):
    id: str
    name: str
    color: str
    icon: str
    description: Optional[str]
    created_at: str
    updated_at: str


def _subjects_collection(uid: str):
    """Get reference to user's subjects collection"""
    return db.collection("users").document(uid).collection("subjects")


@router.post("/subjects", response_model=SubjectResponse, status_code=201)
def create_subject(
    payload: SubjectCreate, user: dict = Depends(require_user)
):
    """Create a new subject"""
    uid = user["uid"]
    
    now = datetime.now(timezone.utc)
    subject_data = {
        **payload.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    
    doc_ref = _subjects_collection(uid).document()
    doc_ref.set(subject_data)
    
    created_doc = doc_ref.get()
    subject_dict = created_doc.to_dict()
    subject_dict["id"] = doc_ref.id
    subject_dict["created_at"] = subject_dict["created_at"].isoformat()
    subject_dict["updated_at"] = subject_dict["updated_at"].isoformat()
    
    return SubjectResponse(**subject_dict)


@router.get("/subjects", response_model=List[SubjectResponse])
def list_subjects(user: dict = Depends(require_user)):
    """Get all subjects for the user"""
    uid = user["uid"]
    
    subjects_ref = _subjects_collection(uid)
    subjects = subjects_ref.order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    
    result = []
    for subject in subjects:
        subject_data = subject.to_dict()
        subject_data["id"] = subject.id
        subject_data["created_at"] = subject_data["created_at"].isoformat()
        subject_data["updated_at"] = subject_data["updated_at"].isoformat()
        result.append(SubjectResponse(**subject_data))
    
    return result


@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: str,
    user: dict = Depends(require_user)
):
    """Get a specific subject"""
    uid = user["uid"]
    
    subject_ref = _subjects_collection(uid).document(subject_id)
    subject_doc = subject_ref.get()
    
    if not subject_doc.exists:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    subject_data = subject_doc.to_dict()
    subject_data["id"] = subject_id
    subject_data["created_at"] = subject_data["created_at"].isoformat()
    subject_data["updated_at"] = subject_data["updated_at"].isoformat()
    
    return SubjectResponse(**subject_data)


@router.patch("/subjects/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: str,
    payload: SubjectUpdate,
    user: dict = Depends(require_user)
):
    """Update a subject"""
    uid = user["uid"]
    
    subject_ref = _subjects_collection(uid).document(subject_id)
    subject_doc = subject_ref.get()
    
    if not subject_doc.exists:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        # No fields to update, return current
        subject_data = subject_doc.to_dict()
        subject_data["id"] = subject_id
        subject_data["created_at"] = subject_data["created_at"].isoformat()
        subject_data["updated_at"] = subject_data["updated_at"].isoformat()
        return SubjectResponse(**subject_data)
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    subject_ref.update(update_data)
    
    updated_doc = subject_ref.get()
    subject_data = updated_doc.to_dict()
    subject_data["id"] = subject_id
    subject_data["created_at"] = subject_data["created_at"].isoformat()
    subject_data["updated_at"] = subject_data["updated_at"].isoformat()
    
    return SubjectResponse(**subject_data)


@router.delete("/subjects/{subject_id}")
def delete_subject(
    subject_id: str,
    user: dict = Depends(require_user)
):
    """Delete a subject"""
    uid = user["uid"]
    
    subject_ref = _subjects_collection(uid).document(subject_id)
    subject_doc = subject_ref.get()
    
    if not subject_doc.exists:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    subject_ref.delete()
    return {"message": "Subject deleted successfully"}


# ============================================================================
# RECURRING TOPICS ENDPOINTS (for subjects)
# ============================================================================

class RecurringTopicCreate(BaseModel):
    subject_id: Optional[str] = Field(None, description="ID of the parent subject (optional)")
    title: str = Field(..., min_length=1, max_length=200, description="Topic title")
    description: Optional[str] = Field(default=None, description="Topic description")
    recurrence: Optional[str] = Field(default="weekly", description="Recurrence pattern")


class RecurringTopicUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    recurrence: Optional[str] = None
    subject_id: Optional[str] = None


class RecurringTopicResponse(BaseModel):
    id: str
    subject_id: Optional[str]
    title: str
    description: Optional[str]
    recurrence: str
    created_at: str
    updated_at: str


def _recurring_topics_collection(uid: str):
    """Get reference to user's recurring topics collection"""
    return db.collection("users").document(uid).collection("recurringTopics")


@router.post("/recurring-topics", response_model=RecurringTopicResponse, status_code=201)
def create_recurring_topic(
    payload: RecurringTopicCreate,
    user: dict = Depends(require_user)
):
    """Create a new recurring topic"""
    uid = user["uid"]
    
    # Verify subject exists if provided
    if payload.subject_id:
        subject_ref = _subjects_collection(uid).document(payload.subject_id)
        if not subject_ref.get().exists:
            raise HTTPException(status_code=404, detail="Subject not found")
    
    now = datetime.now(timezone.utc)
    topic_data = {
        **payload.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    
    doc_ref = _recurring_topics_collection(uid).document()
    doc_ref.set(topic_data)
    
    created_doc = doc_ref.get()
    topic_dict = created_doc.to_dict()
    topic_dict["id"] = doc_ref.id
    topic_dict["created_at"] = topic_dict["created_at"].isoformat()
    topic_dict["updated_at"] = topic_dict["updated_at"].isoformat()
    
    return RecurringTopicResponse(**topic_dict)


@router.get("/recurring-topics", response_model=List[RecurringTopicResponse])
def list_recurring_topics(
    subject_id: Optional[str] = None,
    user: dict = Depends(require_user)
):
    """Get all recurring topics, optionally filtered by subject"""
    uid = user["uid"]
    
    topics_ref = _recurring_topics_collection(uid)
    
    if subject_id:
        topics = topics_ref.where("subject_id", "==", subject_id).stream()
    else:
        topics = topics_ref.stream()
    
    result = []
    for topic in topics:
        topic_data = topic.to_dict()
        topic_data["id"] = topic.id
        topic_data["created_at"] = topic_data["created_at"].isoformat()
        topic_data["updated_at"] = topic_data["updated_at"].isoformat()
        result.append(RecurringTopicResponse(**topic_data))
    
    return result


@router.patch("/recurring-topics/{topic_id}", response_model=RecurringTopicResponse)
def update_recurring_topic(
    topic_id: str,
    payload: RecurringTopicUpdate,
    user: dict = Depends(require_user)
):
    """Update a recurring topic"""
    uid = user["uid"]
    
    topic_ref = _recurring_topics_collection(uid).document(topic_id)
    topic_doc = topic_ref.get()
    
    if not topic_doc.exists:
        raise HTTPException(status_code=404, detail="Recurring topic not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        topic_data = topic_doc.to_dict()
        topic_data["id"] = topic_id
        topic_data["created_at"] = topic_data["created_at"].isoformat()
        topic_data["updated_at"] = topic_data["updated_at"].isoformat()
        return RecurringTopicResponse(**topic_data)
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    topic_ref.update(update_data)
    
    updated_doc = topic_ref.get()
    topic_data = updated_doc.to_dict()
    topic_data["id"] = topic_id
    topic_data["created_at"] = topic_data["created_at"].isoformat()
    topic_data["updated_at"] = topic_data["updated_at"].isoformat()
    
    return RecurringTopicResponse(**topic_data)


@router.delete("/recurring-topics/{topic_id}")
def delete_recurring_topic(
    topic_id: str,
    user: dict = Depends(require_user)
):
    """Delete a recurring topic"""
    uid = user["uid"]
    
    topic_ref = _recurring_topics_collection(uid).document(topic_id)
    topic_doc = topic_ref.get()
    
    if not topic_doc.exists:
        raise HTTPException(status_code=404, detail="Recurring topic not found")
    
    topic_ref.delete()
    return {"message": "Recurring topic deleted successfully"}