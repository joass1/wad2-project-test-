from datetime import datetime, timezone, timedelta ,time
from collections import defaultdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from google.cloud import firestore
from pydantic import BaseModel, Field

from ..deps.auth import require_user
from ...core.firebase import db

router = APIRouter(prefix="/study-sessions", tags=["study-sessions"])


# ============================================================================
# STUDY SESSION MODELS (Unchanged)
# ============================================================================

class StudySessionCreate(BaseModel):
    duration_minutes: int = Field(..., ge=1, le=480, description="Session duration in minutes")
    subject: Optional[str] = Field(None, description="Subject or topic studied")
    task: Optional[str] = Field(None, description="Specific task or topic")
    task_id: Optional[str] = Field(None, description="Reference to task tracker task ID")
    notes: Optional[str] = Field(None, description="Additional notes")
    session_type: str = Field(default="focus", description="Type of session (focus, break, etc.)")


class StudySessionStart(BaseModel):
    """Model for starting a new session"""
    planned_duration_minutes: int = Field(..., ge=1, le=480, description="Planned session duration in minutes")
    subject: Optional[str] = Field(None, description="Subject or topic studied")
    task: Optional[str] = Field(None, description="Specific task or topic")
    task_id: Optional[str] = Field(None, description="Reference to task tracker task ID")
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
    task_id: Optional[str] = Field(None, description="Updated task ID")


class StudySessionResponse(BaseModel):
    id: str
    planned_duration_minutes: int
    actual_duration_minutes: Optional[int] = None
    time_remaining_seconds: Optional[int] = None
    subject: Optional[str] = None
    task: Optional[str] = None
    task_id: Optional[str] = None
    notes: Optional[str] = None
    session_type: str
    status: str  # 'active', 'paused', 'completed', 'cancelled'
    started_at: str
    paused_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str
    updated_at: str
    date: str
    # Enhanced tracking fields
    pause_count: int = 0
    reset_count: int = 0
    total_paused_duration_minutes: float = 0.0  # Cumulative paused time in minutes

class DailyHours(BaseModel):
    """Represents study hours for a single day."""
    date: str
    hours: float

class SubjectHours(BaseModel):
    """Represents total study hours for a single subject."""
    subject: str
    hours: float

class StudyStatsResponse(BaseModel):
    total_hours: float
    total_sessions: int
    average_session_length: float
    sessions_this_week: int
    sessions_this_month: int
    completed_sessions: int
    paused_sessions: int
    active_sessions: int
    # Enhanced stats
    total_pauses_today: int = 0
    total_resets_today: int = 0
    sessions_started_today: int = 0
    sessions_completed_today: int = 0
    study_streak: int = 0
    daily_hours_past_week: List[DailyHours] = []
    subject_hours_past_week: List[SubjectHours] = []

class DailySessionMetrics(BaseModel):
    """Model for daily session metrics"""
    date: str
    sessions_started: int
    sessions_completed: int
    total_pauses: int
    total_resets: int


def _study_sessions_collection(uid: str):
    """Get reference to user's study sessions collection"""
    return db.collection("users").document(uid).collection("studySessions")


def _daily_metrics_collection(uid: str):
    """Get reference to user's daily metrics collection"""
    return db.collection("users").document(uid).collection("dailyMetrics")

def _add_study_time_to_task(uid: str, task_id: str, minutes: int):
    """Add study time to a task"""
    from google.cloud.firestore import Increment
    task_ref = db.collection("users").document(uid).collection("tasks").document(task_id)
    task_doc = task_ref.get()
    
    if task_doc.exists:
        task_ref.update({
            "totalStudyMinutes": Increment(minutes),
            "updatedAt": datetime.now(timezone.utc)
        })

class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Subject name")
    color: Optional[str] = Field(default="#4CAF50", description="Color hex code")
    icon: Optional[str] = Field(default="📚", description="Icon emoji")
    description: Optional[str] = Field(default=None, description="Subject description")


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None


class SubjectResponse(BaseModel):
    id: str
    name: str
    icon: Optional[str]
    color: Optional[str]
    description: Optional[str]
    created_at: str
    updated_at: str


def _subjects_collection(uid: str):
    """Get reference to user's subjects collection"""
    return db.collection("users").document(uid).collection("subjects")

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


# ============================================================================
# BACKGROUND PREFERENCE ENDPOINTS (UPDATED SECTION)
# ============================================================================

class BackgroundPreference(BaseModel):
    background_id: str = "none"

class BackgroundResponse(BaseModel):
    background_id: str
    
SUCCESS_RESPONSE = {"ok": True, "message": "Operation completed successfully"} # Defined earlier, but ensuring access

def _background_doc_ref(uid: str):
    """Get reference to user's dedicated background settings document 
       in the userSettings subcollection."""
    return db.collection("users").document(uid).collection("userSettings").document("backgrounds")


@router.get("/backgrounds", response_model=BackgroundResponse) # <-- FIX: Removed /preferences/
def get_background_preference(user: dict = Depends(require_user)):
    """Get the user's saved background ID"""
    uid = user["uid"]
    doc_snapshot = _background_doc_ref(uid).get()
    
    if doc_snapshot.exists:
        stored_id = doc_snapshot.to_dict().get("background_id", "none")
        return BackgroundResponse(background_id=stored_id)
    
    # Return default if document does not exist
    return BackgroundResponse(background_id="none")


@router.put("/backgrounds", response_model=Dict[str, Any]) # <-- FIX: Removed /preferences/
def update_background_preference(
    payload: BackgroundPreference, user: dict = Depends(require_user)
):
    """Update the user's background ID"""
    uid = user["uid"]
    
    # Save the new background_id into the dedicated document
    _background_doc_ref(uid).set(
        {"background_id": payload.background_id},
        merge=True,
    )
    
    return SUCCESS_RESPONSE


@router.post("/subjects", response_model=SubjectResponse, status_code=201)
def create_subject(
    payload: SubjectCreate,
    user: dict = Depends(require_user)
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
    """Get all subjects"""
    uid = user["uid"]
    
    subjects = _subjects_collection(uid).stream()
    
    result = []
    for subject in subjects:
        subject_data = subject.to_dict()
        subject_data["id"] = subject.id
        subject_data["created_at"] = subject_data["created_at"].isoformat()
        subject_data["updated_at"] = subject_data["updated_at"].isoformat()
        
        # Ensure icon field exists with default value
        if "icon" not in subject_data:
            subject_data["icon"] = "📚"
        
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

# ============================================================================
# STUDY SESSION ENDPOINTS WITH STATE TRACKING (Unchanged below this line)
# ============================================================================

@router.post("/start", response_model=StudySessionResponse)
def start_study_session(
    payload: StudySessionStart, user: dict = Depends(require_user)
):
    """Start a new study session with initial state"""
    uid = user["uid"]
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    
    # Create session document with initial 'active' status and tracking fields
    session_data = {
        "planned_duration_minutes": payload.planned_duration_minutes,
        "actual_duration_minutes": None,  # Will be updated when paused/completed
        "time_remaining_seconds": payload.planned_duration_minutes * 60,  # Full duration initially
        "subject": payload.subject,
        "task": payload.task,
        "task_id": payload.task_id,
        "notes": payload.notes,
        "session_type": payload.session_type,
        "status": "active",
        "started_at": now,
        "paused_at": None,
        "completed_at": None,
        "created_at": now,
        "updated_at": now,
        "date": today,
        "year": now.year,
        "month": now.month,
        # Enhanced tracking fields
        "pause_count": 0,
        "reset_count": 0,
        "total_paused_duration_minutes": 0.0,
    }
    
    doc_ref = _study_sessions_collection(uid).add(session_data)
    session_id = doc_ref[1].id

    
    # Update daily metrics - increment sessions_started
    _update_daily_metrics(uid, today, sessions_started_increment=1)
    
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
    
    session_data = session_doc.to_dict()
    update_data = payload.model_dump(exclude_unset=True)
    
    if not update_data:
        # No fields to update
        session_data["id"] = session_id
        return _format_session_response(session_data, session_id)
    
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    update_data["updated_at"] = now
    
    # Handle status changes with tracking
    if "status" in update_data:
        status = update_data["status"]
        current_status = session_data.get("status")
        
        if status == "paused" and current_status != "paused":
            # Increment pause count
            current_pause_count = session_data.get("pause_count", 0)
            update_data["pause_count"] = current_pause_count + 1
            update_data["paused_at"] = now
            
            # Update daily metrics
            _update_daily_metrics(uid, today, pauses_increment=1)
            
        elif status == "completed":
            update_data["completed_at"] = now
            
            # Update daily metrics - increment sessions completed
            _update_daily_metrics(uid, today, sessions_completed_increment=1)
            
        elif status == "active":
            # Resuming from pause - calculate pause duration and add to total
            if current_status == "paused":
                paused_at_time = session_data.get("paused_at")
                if paused_at_time:
                    # Calculate how long the session was paused
                    if isinstance(paused_at_time, datetime):
                        pause_duration_minutes = (now - paused_at_time).total_seconds() / 60
                    elif isinstance(paused_at_time, str):
                        # Parse ISO format string
                        try:
                            paused_dt = datetime.fromisoformat(paused_at_time.replace('Z', '+00:00'))
                            pause_duration_minutes = (now - paused_dt).total_seconds() / 60
                        except (ValueError, AttributeError):
                            pause_duration_minutes = 0
                    else:
                        pause_duration_minutes = 0
                    
                    # Add to cumulative paused duration
                    current_paused_duration = session_data.get("total_paused_duration_minutes", 0.0)
                    update_data["total_paused_duration_minutes"] = current_paused_duration + pause_duration_minutes
                
                update_data["paused_at"] = None
    
    # If session completed and has task_id, update task's total study time
    if update_data.get("status") == "completed" and session_data.get("task_id"):
        try:
            task_id = session_data["task_id"]
            duration = update_data.get("actual_duration_minutes") or session_data.get("planned_duration_minutes", 0)
            _add_study_time_to_task(uid, task_id, duration)
        except Exception as e:
            print(f"Error updating task study time: {e}")
    
    session_ref.update(update_data)
    
    # Get updated document
    updated_doc = session_ref.get()
    session_data = updated_doc.to_dict()
    session_data["id"] = session_id
    
    return _format_session_response(session_data, session_id)


@router.post("/{session_id}/reset", response_model=StudySessionResponse)
def reset_study_session(
    session_id: str,
    user: dict = Depends(require_user)
):
    """Reset a study session (track reset count)"""
    uid = user["uid"]
    
    session_ref = _study_sessions_collection(uid).document(session_id)
    session_doc = session_ref.get()
    
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session_data = session_doc.to_dict()
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    
    # Increment reset count
    current_reset_count = session_data.get("reset_count", 0)
    
    update_data = {
        "reset_count": current_reset_count + 1,
        "status": "active",  # Reset puts it back to active
        "time_remaining_seconds": session_data.get("planned_duration_minutes", 25) * 60,
        "paused_at": None,
        "updated_at": now,
    }
    
    session_ref.update(update_data)
    
    # Update daily metrics
    _update_daily_metrics(uid, today, resets_increment=1)
    
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
    today = now.strftime("%Y-%m-%d")
    
    # Create session document as completed
    session_data = {
        "planned_duration_minutes": payload.duration_minutes,
        "actual_duration_minutes": payload.duration_minutes,
        "time_remaining_seconds": 0,
        "subject": payload.subject,
        "task": payload.task,
        "task_id": payload.task_id,
        "notes": payload.notes,
        "session_type": payload.session_type,
        "status": "completed",
        "started_at": now - timedelta(minutes=payload.duration_minutes),
        "paused_at": None,
        "completed_at": now,
        "created_at": now,
        "updated_at": now,
        "date": today,
        "year": now.year,
        "month": now.month,
        "pause_count": 0,
        "reset_count": 0,
        "total_paused_duration_minutes": 0.0,
    }
    
    doc_ref = _study_sessions_collection(uid).add(session_data)
    session_id = doc_ref[1].id
    
    # Update daily metrics
    _update_daily_metrics(uid, today, sessions_started_increment=1, sessions_completed_increment=1)
    
    # Get the created document to return
    created_doc = doc_ref[1].get()
    session_dict = created_doc.to_dict()
    session_dict["id"] = session_id
    
    return _format_session_response(session_dict, session_id)


def _update_daily_metrics(
    uid: str,
    date: str,
    sessions_started_increment: int = 0,
    sessions_completed_increment: int = 0,
    pauses_increment: int = 0,
    resets_increment: int = 0
):
    """Update daily metrics in Firestore"""
    metrics_ref = _daily_metrics_collection(uid).document(date)
    
    # Use transaction to ensure atomic updates
    try:
        metrics_doc = metrics_ref.get()
        
        if metrics_doc.exists:
            current_data = metrics_doc.to_dict()
            update_data = {
                "sessions_started": current_data.get("sessions_started", 0) + sessions_started_increment,
                "sessions_completed": current_data.get("sessions_completed", 0) + sessions_completed_increment,
                "total_pauses": current_data.get("total_pauses", 0) + pauses_increment,
                "total_resets": current_data.get("total_resets", 0) + resets_increment,
                "updated_at": datetime.now(timezone.utc),
            }
            metrics_ref.update(update_data)
        else:
            # Create new metrics document
            metrics_ref.set({
                "date": date,
                "sessions_started": sessions_started_increment,
                "sessions_completed": sessions_completed_increment,
                "total_pauses": pauses_increment,
                "total_resets": resets_increment,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })
    except Exception as e:
        # Log error but don't fail the request
        print(f"Error updating daily metrics: {e}")


def _get_daily_metrics(uid: str, date: str) -> DailySessionMetrics:
    """Helper function to get daily metrics without dependency injection"""
    metrics_ref = _daily_metrics_collection(uid).document(date)
    metrics_doc = metrics_ref.get()
    
    if not metrics_doc.exists:
        # Return empty metrics
        return DailySessionMetrics(
            date=date,
            sessions_started=0,
            sessions_completed=0,
            total_pauses=0,
            total_resets=0
        )
    
    metrics_data = metrics_doc.to_dict()
    return DailySessionMetrics(
        date=date,
        sessions_started=metrics_data.get("sessions_started", 0),
        sessions_completed=metrics_data.get("sessions_completed", 0),
        total_pauses=metrics_data.get("total_pauses", 0),
        total_resets=metrics_data.get("total_resets", 0)
    )


@router.get("/metrics/daily", response_model=DailySessionMetrics)
def get_daily_metrics(
    date: Optional[str] = None,
    user: dict = Depends(require_user)
):
    """Get daily session metrics for a specific date (defaults to today)"""
    uid = user["uid"]
    
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    metrics_ref = _daily_metrics_collection(uid).document(date)
    metrics_doc = metrics_ref.get()
    
    if not metrics_doc.exists:
        # Return empty metrics
        return DailySessionMetrics(
            date=date,
            sessions_started=0,
            sessions_completed=0,
            total_pauses=0,
            total_resets=0
        )
    
    metrics_data = metrics_doc.to_dict()
    return DailySessionMetrics(
        date=date,
        sessions_started=metrics_data.get("sessions_started", 0),
        sessions_completed=metrics_data.get("sessions_completed", 0),
        total_pauses=metrics_data.get("total_pauses", 0),
        total_resets=metrics_data.get("total_resets", 0)
    )


class TodaySummaryResponse(BaseModel):
    date: str
    total_minutes: int
    sessions_completed: int
    sessions_started: int


class TimerStatsResponse(BaseModel):
    """Model for timer page stats - today's session metrics"""
    date: str
    sessions_completed: int
    sessions_paused: int
    total_pause_count: int
    total_study_minutes: int
    total_study_hours: float
    sessions_started: int
    total_started_minutes: int  # Total planned minutes for all sessions started today
    total_paused_minutes: int  # Total minutes spent in paused state today
    focus_score: float  # 100% - (paused_minutes / started_minutes * 100%)


@router.get("/today-summary", response_model=TodaySummaryResponse)
def get_today_summary(user: dict = Depends(require_user)):
    """Return today's total completed study minutes and session counts."""
    uid = user["uid"]
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    # Sum durations for today's completed sessions
    sessions_ref = _study_sessions_collection(uid)
    query = sessions_ref.where("date", "==", today)

    total_minutes = 0
    completed_count = 0
    for doc in query.stream():
        data = doc.to_dict() or {}
        status = data.get("status")
        minutes = data.get("actual_duration_minutes") or 0
        if status == "completed" and isinstance(minutes, (int, float)):
            total_minutes += int(minutes)
            completed_count += 1

    # Get sessions_started from daily metrics
    metrics = _get_daily_metrics(uid, today)

    return TodaySummaryResponse(
        date=today,
        total_minutes=total_minutes,
        sessions_completed=completed_count,
        sessions_started=metrics.sessions_started,
    )


@router.get("/timer-stats", response_model=TimerStatsResponse)
def get_timer_stats(user: dict = Depends(require_user)):
    """Get comprehensive stats for the timer page - today's session statistics
    
    Calculates:
    - Total minutes of all sessions started today (planned durations)
    - Total paused minutes (from completed and paused sessions)
    - Focus score: 100% - (paused_minutes / started_minutes * 100%)
    """
    uid = user["uid"]
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    
    # Query today's sessions
    sessions_ref = _study_sessions_collection(uid)
    sessions_query = sessions_ref.where("date", "==", today)
    
    # Initialize counters
    total_study_minutes = 0  # From completed sessions only
    total_started_minutes = 0  # Sum of all planned durations
    total_paused_minutes = 0  # Cumulative paused time
    completed_count = 0
    paused_count = 0
    
    # Process each session
    print(f"DEBUG: Processing sessions for date: {today}")
    for doc in sessions_query.stream():
        data = doc.to_dict() or {}
        status = data.get("status")
        planned_minutes = data.get("planned_duration_minutes", 0)
        actual_minutes = data.get("actual_duration_minutes")
        total_paused_duration = data.get("total_paused_duration_minutes", 0.0)
        paused_at = data.get("paused_at")
        session_id = doc.id
        
        # Sum all planned durations for sessions started today
        if isinstance(planned_minutes, (int, float)) and planned_minutes > 0:
            total_started_minutes += planned_minutes  # Use float instead of int for precision
            print(f"DEBUG: Session {session_id[:8]}...: status={status}, planned={planned_minutes} min ({planned_minutes*60:.0f} sec), adding to total_started")
        
        # Process based on status
        if status == "completed":
            # Count completed sessions and their actual study time
            if isinstance(actual_minutes, (int, float)) and actual_minutes > 0:
                total_study_minutes += int(actual_minutes)
            completed_count += 1
            
            # Use tracked paused duration for completed sessions
            # Cap to planned duration to prevent unrealistic values
            paused_duration_to_use = total_paused_duration if isinstance(total_paused_duration, (int, float)) else 0.0
            if isinstance(planned_minutes, (int, float)) and planned_minutes > 0:
                original_paused = paused_duration_to_use
                paused_duration_to_use = min(paused_duration_to_use, float(planned_minutes))
                if original_paused > planned_minutes:
                    print(f"DEBUG: Capped paused time for completed session {session_id[:8]}...: {original_paused:.2f} -> {paused_duration_to_use:.2f} (planned: {planned_minutes})")
            
            total_paused_minutes += paused_duration_to_use
            paused_sec = paused_duration_to_use * 60
            print(f"DEBUG: Completed session {session_id[:8]}...: paused={paused_duration_to_use:.2f} min ({paused_sec:.1f} sec)")
        
        elif status == "paused":
            paused_count += 1
            
            # For currently paused sessions: use tracked paused duration + current pause time
            paused_duration_so_far = total_paused_duration if isinstance(total_paused_duration, (int, float)) else 0.0
            
            # Add current pause duration (from paused_at to now)
            # But cap it at the planned duration to prevent unrealistic values from old paused sessions
            current_pause_minutes = 0.0
            if paused_at:
                if isinstance(paused_at, datetime):
                    current_pause_minutes = (now - paused_at).total_seconds() / 60
                elif isinstance(paused_at, str):
                    # Parse ISO format string
                    try:
                        paused_dt = datetime.fromisoformat(paused_at.replace('Z', '+00:00'))
                        current_pause_minutes = (now - paused_dt).total_seconds() / 60
                    except (ValueError, AttributeError):
                        current_pause_minutes = 0.0
            
                # Cap current pause duration at planned duration to prevent unrealistic values
                # (e.g., if session was paused days ago and never resumed)
                original_current_pause = current_pause_minutes
                if isinstance(planned_minutes, (int, float)) and planned_minutes > 0:
                    current_pause_minutes = min(current_pause_minutes, float(planned_minutes))
                    if original_current_pause > planned_minutes:
                        print(f"DEBUG: Capped current pause time for session {session_id[:8]}...: {original_current_pause:.2f} -> {current_pause_minutes:.2f} (planned: {planned_minutes})")
            
            session_paused_total = paused_duration_so_far + current_pause_minutes
            
            # Cap total paused time to planned duration (logical limit: can't pause more than session length)
            if isinstance(planned_minutes, (int, float)) and planned_minutes > 0:
                original_total = session_paused_total
                session_paused_total = min(session_paused_total, float(planned_minutes))
                if original_total > planned_minutes:
                    print(f"DEBUG: Capped total paused time for session {session_id[:8]}...: {original_total:.2f} -> {session_paused_total:.2f} (planned: {planned_minutes})")
            
            total_paused_minutes += session_paused_total
            paused_sec_total = session_paused_total * 60
            print(f"DEBUG: Paused session {session_id[:8]}...: planned={planned_minutes} min, paused={session_paused_total:.2f} min ({paused_sec_total:.1f} sec)")
        
        elif status == "active":
            # Active sessions may have paused time if they were paused and resumed
            # Include their tracked paused duration in the calculation
            # Cap to planned duration to prevent unrealistic values
            if isinstance(total_paused_duration, (int, float)) and total_paused_duration > 0:
                paused_duration_to_use = total_paused_duration
                if isinstance(planned_minutes, (int, float)) and planned_minutes > 0:
                    original_paused = paused_duration_to_use
                    paused_duration_to_use = min(paused_duration_to_use, float(planned_minutes))
                    if original_paused > planned_minutes:
                        print(f"DEBUG: Capped paused time for active session {session_id[:8]}...: {original_paused:.2f} -> {paused_duration_to_use:.2f} (planned: {planned_minutes})")
                
                total_paused_minutes += paused_duration_to_use
                paused_sec = paused_duration_to_use * 60
                print(f"DEBUG: Active session {session_id[:8]}...: paused={paused_duration_to_use:.2f} min ({paused_sec:.1f} sec)")
    
    # Get additional metrics from daily metrics
    metrics = _get_daily_metrics(uid, today)
    
    # Calculate focus score: (timer running seconds - paused seconds) / total session seconds * 100
    # Formula: (total_started_minutes - total_paused_minutes) / total_started_minutes * 100
    # If paused seconds >= total session seconds, focus score is 0
    if total_started_minutes > 0:
        # Convert to seconds for more precise calculation (especially for short sessions)
        total_started_seconds = float(total_started_minutes) * 60
        total_paused_seconds = float(total_paused_minutes) * 60
        
        # Debug logging (show both minutes and seconds)
        print(f"DEBUG Focus Score Calculation:")
        print(f"  total_started: {total_started_minutes} minutes ({total_started_seconds:.1f} seconds)")
        print(f"  total_paused: {total_paused_minutes:.2f} minutes ({total_paused_seconds:.1f} seconds)")
        print(f"  paused >= started: {total_paused_seconds >= total_started_seconds}")
        
        # Check if paused time exceeds or equals total session time
        if total_paused_seconds >= total_started_seconds:
            focus_score = 0.0
            print(f"  Result: 0% (paused time >= total session time)")
        else:
            # Calculate: (running time - paused time) / total session time * 100
            # Use seconds for precision, especially important for short sessions
            running_seconds = total_started_seconds - total_paused_seconds
            focus_score = round((running_seconds / total_started_seconds) * 100, 1)
            print(f"  running: {running_seconds:.1f} seconds ({running_seconds/60:.2f} minutes)")
            print(f"  Result: {focus_score}%")
    else:
        focus_score = 100.0  # No sessions started, perfect focus!
        print(f"DEBUG Focus Score: 100% (no sessions started)")
    
    # Calculate hours from minutes
    total_study_hours = round(total_study_minutes / 60, 2)
    
    return TimerStatsResponse(
        date=today,
        sessions_completed=completed_count,
        sessions_paused=paused_count,
        total_pause_count=metrics.total_pauses,
        total_study_minutes=total_study_minutes,
        total_study_hours=total_study_hours,
        sessions_started=metrics.sessions_started,
        total_started_minutes=total_started_minutes,
        total_paused_minutes=int(total_paused_minutes),
        focus_score=focus_score,
    )


@router.get("/current", response_model=Optional[StudySessionResponse])
def get_current_session(user: dict = Depends(require_user)):
    """Get the current active or paused session if one exists"""
    uid = user["uid"]
    
    # Query for sessions with status 'active' or 'paused', ordered by started_at desc
    sessions_ref = _study_sessions_collection(uid)
    active_sessions = sessions_ref.where("status", "in", ["active", "paused"]).order_by(
        "started_at", direction=firestore.Query.DESCENDING
    ).limit(1).stream()
    
    for session in active_sessions:
        session_data = session.to_dict()
        session_data["id"] = session.id
        return _format_session_response(session_data, session.id)
    
    return None


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
    
    # Ensure tracking fields exist
    if "pause_count" not in session_data:
        session_data["pause_count"] = 0
    if "reset_count" not in session_data:
        session_data["reset_count"] = 0
    if "total_paused_duration_minutes" not in session_data:
        session_data["total_paused_duration_minutes"] = 0.0
    
    return StudySessionResponse(**session_data)


@router.get("/stats", response_model=StudyStatsResponse)
@router.get("/stats/summary", response_model=StudyStatsResponse)
def get_study_stats(user: dict = Depends(require_user)):
    try:
        uid = user["uid"]
        
        LOCAL_TZ = timezone(timedelta(hours=8))
        now_utc = datetime.now(timezone.utc)
        now_local = now_utc.astimezone(LOCAL_TZ)

        today = now_local.strftime("%Y-%m-%d")
        
        today_dt_local = datetime.combine(now_local.date(), time.min, tzinfo=LOCAL_TZ)
        today_dt = today_dt_local.astimezone(timezone.utc)

        week_ago_dt = today_dt - timedelta(days=7) 
        week_ago = week_ago_dt.strftime("%Y-%m-%d")
        
        month_ago_dt = today_dt - timedelta(days=30)
        month_ago = month_ago_dt.strftime("%Y-%m-%d")
        
        sessions_ref = _study_sessions_collection(uid)
        all_sessions = sessions_ref.stream()
        
        start_date_local = today_dt_local - timedelta(days=6)
        daily_minutes = {
            (start_date_local + timedelta(days=i)).strftime("%Y-%m-%d"): 0 
            for i in range(7) 
        }
        subject_minutes_past_week = defaultdict(int) 
        completed_study_dates = set() 
        
        total_minutes = 0
        total_sessions = 0
        completed_sessions = 0
        paused_sessions = 0
        active_sessions = 0
        sessions_this_week = 0
        sessions_this_month = 0
        
        for session in all_sessions:
            session_data = session.to_dict()
            total_sessions += 1
            
            duration = session_data.get("actual_duration_minutes")
            # Fall back to duration_minutes for legacy sessions
            if duration is None:
                duration = session_data.get("duration_minutes", 0)
            
            session_date = session_data.get("date", "").strip() if session_data.get("date") else ""
            status = session_data.get("status")
            
            # Only count completed sessions with actual duration for total study hours
            if status == "completed" and duration is not None and isinstance(duration, (int, float)) and duration > 0:
                total_minutes += duration 
                completed_sessions += 1
                if session_date:
                    completed_study_dates.add(session_date) 
                if session_date >= week_ago: 
                    if session_date in daily_minutes:
                        daily_minutes[session_date] += duration
                        
                    # Only count sessions with a valid subject (filter out Uncategorized/legacy data)
                    subject = session_data.get("subject")
                    if subject and subject.strip():  # Only add if subject exists and is not empty
                        subject_minutes_past_week[subject] += duration
            elif status == "paused":
                paused_sessions += 1
            elif status == "active":
                active_sessions += 1
            
            if session_date >= week_ago:
                sessions_this_week += 1
            if session_date >= month_ago:
                sessions_this_month += 1

        completed_dates_dt = set()

        for d in completed_study_dates:
            try:
                # Handle datetime or string with time part like "2025-10-31T00:00:00Z"
                normalized_date = datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
                completed_dates_dt.add(normalized_date)
            except Exception as e:
                print(f"DEBUG: Failed to parse study date '{d}': {e}")
        # Initialize streak counter
        study_streak = 0
        today_date = now_local.date()
        # If the user didn't study today, start from yesterday
        current_date_dt = today_date
        if today_date not in completed_dates_dt:
            current_date_dt -= timedelta(days=1)

        # Count backward as long as consecutive days exist
        while current_date_dt in completed_dates_dt:
            study_streak += 1
            current_date_dt -= timedelta(days=1)
        daily_metrics = _get_daily_metrics(uid, today) 
        
        daily_hours_list = [
            {"date": date, "hours": round(minutes / 60, 2)}
            for date, minutes in sorted(daily_minutes.items()) 
        ]
        subject_hours_list = [
            {"subject": subject, "hours": round(minutes / 60, 2)}
            for subject, minutes in subject_minutes_past_week.items()
            if minutes > 0 and subject and subject.lower() != "uncategorized"
        ]
        
        return StudyStatsResponse(
            total_hours=round(total_minutes / 60, 2),
            total_sessions=total_sessions,
            average_session_length=round(total_minutes / total_sessions, 2) if total_sessions > 0 else 0,
            sessions_this_week=sessions_this_week,
            sessions_this_month=sessions_this_month,
            completed_sessions=completed_sessions,
            paused_sessions=paused_sessions,
            active_sessions=active_sessions,
            study_streak=study_streak, 
            daily_hours_past_week=daily_hours_list, 
            subject_hours_past_week=subject_hours_list,
            total_pauses_today=daily_metrics.total_pauses,
            total_resets_today=daily_metrics.total_resets,
            sessions_started_today=daily_metrics.sessions_started,
            sessions_completed_today=daily_metrics.sessions_completed,
        )
    except Exception as e:
        print(f"ERROR in get_study_stats: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error calculating study stats: {str(e)}")


@router.get("/", response_model=List[StudySessionResponse])
def list_study_sessions(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    date: Optional[str] = None,
    user: dict = Depends(require_user)
):
    """Get study sessions with optional filtering"""
    uid = user["uid"]
    
    sessions_ref = _study_sessions_collection(uid)
    query = sessions_ref
    
    if status:
        query = query.where("status", "==", status)
    
    if date:
        query = query.where("date", "==", date)
    
    query = query.order_by("started_at", direction=firestore.Query.DESCENDING)
    query = query.limit(limit).offset(skip)
    
    sessions = query.stream()
    
    result = []
    for session in sessions:
        session_data = session.to_dict()
        session_data["id"] = session.id
        result.append(_format_session_response(session_data, session.id))
    
    return result


@router.get("/{session_id}", response_model=StudySessionResponse)
def get_study_session(
    session_id: str,
    user: dict = Depends(require_user)
):
    """Get a specific study session"""
    uid = user["uid"]
    
    session_ref = _study_sessions_collection(uid).document(session_id)
    session_doc = session_ref.get()
    
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session_data = session_doc.to_dict()
    session_data["id"] = session_id
    
    return _format_session_response(session_data, session_id)


@router.delete("/{session_id}")
def delete_study_session(
    session_id: str,
    user: dict = Depends(require_user)
):
    """Delete a study session"""
    uid = user["uid"]
    
    session_ref = _study_sessions_collection(uid).document(session_id)
    session_doc = session_ref.get()
    
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session_ref.delete()
    return {"message": "Study session deleted successfully"}