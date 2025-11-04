from __future__ import annotations

from datetime import date, datetime, timezone, timedelta
from typing import Any, Dict, Iterable, List, Literal, Optional, cast
from collections import defaultdict
import traceback
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from ..deps.auth import require_user
from ...core.firebase import db

router = APIRouter(prefix="/tasks", tags=["tasks"])

StatusLiteral = Literal["todo", "inProgress", "done"]
PriorityLiteral = Literal["high", "medium", "low"]


def _tasks_collection(uid: str):
    """Return the Firestore collection reference for a user's tasks."""

    return db.collection("users").document(uid).collection("tasks")


def _utc_now() -> datetime:
    """Get the current UTC timestamp."""

    return datetime.now(timezone.utc)


def _isoformat(value: datetime | str | None) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        # Assume already ISO 8601; return as-is
        return value
    iso = value.astimezone(timezone.utc).isoformat()
    return iso.replace("+00:00", "Z")


def _serialize_task_doc(doc) -> Dict[str, Any]:
    """Normalize a Firestore document snapshot into a plain task dictionary."""

    data = doc.to_dict() or {}
    data["id"] = doc.id

    for key in ("createdAt", "updatedAt"):
        if key in data and isinstance(data[key], datetime):
            data[key] = _isoformat(data[key])

    # Ensure consistent optional fields
    data.setdefault("category", "General")
    data.setdefault("dueDate", None)
    data.setdefault("totalStudyMinutes", 0)
    data.setdefault("subjectId", None)
    data.setdefault("topic", None)

    return data

def _to_task_response(data: Dict[str, Any]) -> TaskResponse:
    # Ensure totalStudyMinutes is an int, defaulting to 0 if None or invalid
    total_study_mins = data.get("totalStudyMinutes")
    if total_study_mins is None:
        total_study_mins = 0
    else:
        try:
            total_study_mins = int(total_study_mins)
        except (ValueError, TypeError):
            total_study_mins = 0
    
    # Build response data dict, ensuring all required fields are present
    response_data = {
        "id": str(data.get("id", "")),
        "title": str(data.get("title", "")),
        "status": data.get("status", "todo"),
        "priority": data.get("priority", "medium"),
        "dueDate": data.get("dueDate"),
        "category": data.get("category", "General"),
        "createdAt": data.get("createdAt"),
        "updatedAt": data.get("updatedAt"),
        "subjectId": data.get("subjectId"),
        "topic": data.get("topic"),
        "totalStudyMinutes": total_study_mins,
    }
    
    return TaskResponse(**response_data)


def _filter_tasks(
    items: Iterable[Dict[str, Any]],
    status: StatusLiteral | None = None,
    priority: PriorityLiteral | None = None,
) -> List[Dict[str, Any]]:
    """Filter tasks by optional ``status`` and ``priority`` values."""
    filtered = []
    for item in items:
        if status and item.get("status") != status:
            continue
        if priority and item.get("priority") != priority:
            continue
        filtered.append(item)
    return filtered


def _sort_tasks(tasks: List[Dict[str, Any]], sort_by: str) -> None:
    if sort_by == "priority":
        order = {"high": 0, "medium": 1, "low": 2}
        tasks.sort(key=lambda t: order.get(str(t.get("priority") or ""), 99))
    elif sort_by == "dueDate":
        tasks.sort(
            key=lambda t: (
                t.get("dueDate") is None,
                t.get("dueDate") or "",
                t.get("createdAt") or "",
            )
        )
    else:
        tasks.sort(key=lambda t: t.get("createdAt") or "", reverse=True)


def _parse_due_date(value: Optional[str]) -> Optional[date]:
    """Parse ``YYYY-MM-DD`` strings into a date; return ``None`` on failure."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _calculate_stats(tasks: List[Dict[str, Any]]) -> Dict[str, int]:
    today = _utc_now().date()

    total = len(tasks)
    completed = sum(1 for task in tasks if task.get("status") == "done")
    due_today = 0
    overdue = 0

    for task in tasks:
        if task.get("status") == "done":
            continue
        due = _parse_due_date(task.get("dueDate"))
        if due is None:
            continue
        if due == today:
            due_today += 1
        elif due < today:
            overdue += 1

    return {
        "total": total,
        "completed": completed,
        "dueToday": due_today,
        "overdue": overdue,
    }


def _normalize_filter(value: Optional[str], allowed: Iterable[str]) -> Optional[str]:
    """Normalize query filter values coming from the UI.

    - None/empty/"all" means no filtering
    - Otherwise must be in allowed
    """
    if value in (None, "", "all"):
        return None
    if str(value) not in set(allowed):
        raise HTTPException(status_code=400, detail="Invalid filter value")
    return str(value)


class TaskBase(BaseModel):
    """Base properties shared by create/update/response task schemas."""

    model_config = ConfigDict(extra="ignore")

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Short, descriptive title for the task",
        examples=["Study chapter 3"],
    )
    status: StatusLiteral = Field(
        "todo", description="Current workflow state of the task"
    )
    priority: PriorityLiteral = Field(
        "medium", description="Relative urgency or importance"
    )
    dueDate: str | None = Field(
        default=None,
        description="Due date in YYYY-MM-DD format or null when unset",
        examples=["2024-10-31"],
    )
    category: str | None = Field(
        default="General",
        max_length=120,
        description="Optional grouping label shown in the UI",
        examples=["Personal"],
    )
    totalStudyMinutes: int | None = Field(
        default=0,
        description="Total study time logged for this task in minutes"
    )
    # Optional links to study context
    subjectId: str | None = Field(
        default=None,
        description="Optional subject identifier to tag this task with a subject",
    )
    topic: str | None = Field(
        default=None,
        max_length=255,
        description="Optional recurring topic/area label (e.g., 'Practice Paper')",
    )


class TaskCreate(TaskBase):
    """Payload accepted when creating a task."""


class TaskUpdate(BaseModel):
    """Fields that can be updated on an existing task."""

    model_config = ConfigDict(extra="ignore")

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated title. Leave unset to keep current value.",
    )
    status: StatusLiteral | None = Field(
        default=None,
        description="Updated workflow state. Leave unset to keep current value.",
    )
    priority: PriorityLiteral | None = Field(
        default=None,
        description="Updated priority bucket. Leave unset to keep current value.",
    )
    dueDate: str | None = Field(
        default=None,
        description="New due date in YYYY-MM-DD format, or null to clear it.",
    )
    category: str | None = Field(
        default=None,
        max_length=120,
        description="Updated category label. Leave unset to keep current value.",
    )
    subjectId: str | None = Field(
        default=None,
        description="Updated subject identifier. Leave unset to keep current value.",
    )
    topic: str | None = Field(
        default=None,
        max_length=255,
        description="Updated recurring topic/area label. Leave unset to keep current value.",
    )


class TaskResponse(TaskBase):
    """Task payload returned by the API including metadata fields."""

    id: str = Field(description="Firestore document identifier for the task")
    createdAt: str | None = Field(
        default=None,
        description="ISO-8601 timestamp (UTC) representing when the task was created",
    )
    updatedAt: str | None = Field(
        default=None,
        description="ISO-8601 timestamp (UTC) representing the last update timestamp",
    )
    totalStudyMinutes: int = Field(
        default=0,
        description="Total study time logged for this task in minutes"
    )

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.id = str(data.get("id", ""))
        self.createdAt = _isoformat(data.get("createdAt"))
        self.updatedAt = _isoformat(data.get("updatedAt"))


class TaskListResponse(BaseModel):
    """Response returned when listing tasks, including aggregate stats."""

    tasks: List[TaskResponse] = Field(
        description="Filtered list of tasks for the authenticated user"
    )
    stats: Dict[str, int] = Field(
        description="Summary statistics derived from the returned tasks"
    )


@router.get(
    "/",
    response_model=TaskListResponse,
    summary="List tasks",
    response_description="Tasks matching the supplied filters along with summary stats.",
)
def list_tasks(
    status: Optional[str] = Query(default=None, description='Task status or "all"'),
    priority: Optional[str] = Query(default=None, description='Task priority or "all"'),
    sortBy: str = Query(
        default="dueDate",
        pattern="^(dueDate|priority)$",
        description="Sort key: dueDate, priority",
    ),
    user: dict = Depends(require_user),
):
    """Return all tasks for the authenticated user optionally filtered by status and priority."""

    uid = user["uid"]
    snapshots = _tasks_collection(uid).stream()
    tasks_data = [_serialize_task_doc(doc) for doc in snapshots]

    status_norm = cast(
        StatusLiteral | None, _normalize_filter(status, ["todo", "inProgress", "done"])
    )
    priority_norm = cast(
        PriorityLiteral | None, _normalize_filter(priority, ["high", "medium", "low"])
    )

    tasks_data = _filter_tasks(
        tasks_data,
        status=status_norm,
        priority=priority_norm,
    )
    _sort_tasks(tasks_data, sortBy)

    # Convert tasks to TaskResponse objects, with error handling
    task_responses = []
    for task_data in tasks_data:
        try:
            task_responses.append(_to_task_response(task_data))
        except Exception as e:
            # Log the error and skip this task to prevent 500 errors
            print(f"Error converting task to response: {e}")
            print(f"Task data: {task_data}")
            print(traceback.format_exc())
            continue
    
    return TaskListResponse(
        tasks=task_responses, stats=_calculate_stats(tasks_data)
    )


@router.post(
    "/add-task",
    response_model=TaskResponse,
    status_code=201,
    summary="Create task",
    response_description="Details for the newly created task, including its generated id.",
)
def create_task(payload: TaskCreate, user: dict = Depends(require_user)):
    """Add a new task to the authenticated user's tasks collection."""
    uid = user["uid"]
    tasks_ref = _tasks_collection(uid)
    now = _utc_now()

    data = payload.model_dump()
    data["createdAt"] = now
    data["updatedAt"] = now
    data["totalStudyMinutes"] = 0

    doc_ref = tasks_ref.document()
    doc_ref.set(data)

    stored = doc_ref.get()
    return _to_task_response(_serialize_task_doc(stored))


@router.get(
    "/stats",
    response_model=Dict[str, int],
    summary="Get task stats",
    response_description="Counts of total, completed, due-today, and overdue tasks.",
)
def get_task_stats(user: dict = Depends(require_user)):
    """Return aggregate statistics for the authenticated user's tasks."""

    uid = user["uid"]
    snapshots = _tasks_collection(uid).stream()
    tasks = [_serialize_task_doc(doc) for doc in snapshots]
    return _calculate_stats(tasks)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
    response_description="Updated task after applying the provided field changes.",
)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    user: dict = Depends(require_user),
):
    """Apply partial updates to an existing task."""

    uid = user["uid"]
    doc_ref = _tasks_collection(uid).document(task_id)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        raise HTTPException(status_code=404, detail="Task not found.")

    # Get all fields from payload that were explicitly set
    payload_dict = payload.model_dump(exclude_unset=True)
    update_fields = {}
    
    # Only include fields that were explicitly provided in the request
    for field_name in ["title", "status", "priority", "dueDate", "subjectId", "topic"]:
        if field_name in payload_dict:
            update_fields[field_name] = payload_dict[field_name]
    
    # If no fields to update, return current task
    if not update_fields:
        try:
            return _to_task_response(_serialize_task_doc(snapshot))
        except Exception as e:
            print(f"Error returning current task: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error processing task: {str(e)}")

    update_fields["updatedAt"] = _utc_now()
    
    try:
        doc_ref.update(update_fields)
        refreshed = doc_ref.get()
        return _to_task_response(_serialize_task_doc(refreshed))
    except Exception as e:
        print(f"Error updating task: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


@router.delete(
    "/{task_id}",
    response_model=Dict[str, bool],
    summary="Delete task",
    response_description="Confirmation that the task was successfully removed.",
)
def delete_task(task_id: str, user: dict = Depends(require_user)):
    """Remove a task from the authenticated user's collection."""

    uid = user["uid"]
    doc_ref = _tasks_collection(uid).document(task_id)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        raise HTTPException(status_code=404, detail="Task not found.")
    doc_ref.delete()
    return {"success": True}

class TaskDailyStatsResponse(BaseModel):
    date: str
    created: int
    completed: int

@router.get(
    "/weekly-activity",
    response_model=List[TaskDailyStatsResponse],
    summary="Get task creation and completion counts for each day in the past week",
    response_description="Returns a list of objects with ISO date, created count, and completed count per day for the last 7 days.",
)
def get_weekly_activity(user: dict = Depends(require_user)):
    uid = user["uid"]
    today = _utc_now().date()
    start_date = today - timedelta(days=6)

    # Prepare dicts for counts
    created_counts = defaultdict(int)
    completed_counts = defaultdict(int)

    snapshots = _tasks_collection(uid).stream()
    for doc in snapshots:
        data = _serialize_task_doc(doc)

        # count created tasks
        created_at = data.get("createdAt")
        if created_at:
            created_at_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
            if start_date <= created_at_date <= today:
                created_counts[created_at_date] += 1

        # count completed tasks (status done AND updatedAt after done)
        if data.get("status") == "done":
            updated_at = data.get("updatedAt")
            if updated_at:
                updated_at_date = datetime.fromisoformat(updated_at.replace("Z", "+00:00")).date()
                if start_date <= updated_at_date <= today:
                    completed_counts[updated_at_date] += 1

    # Build response: list of past 7 days
    results = []
    for delta in range(7):
        d = start_date + timedelta(days=delta)
        results.append(
            TaskDailyStatsResponse(
                date=d.isoformat(),
                created=created_counts.get(d, 0),
                completed=completed_counts.get(d, 0),
            )
        )
    return results