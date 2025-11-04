from copy import deepcopy
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any, Dict, List, Tuple, cast, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import firestore
from pydantic import BaseModel, ConfigDict, Field

from ..deps.auth import require_user
from ...core.firebase import db

router = APIRouter(prefix="/wellness", tags=["wellness"])

BASE_OVERVIEW = {
    "streak": 0,
    "longestStreak": 0,
    "totalCheckIns": 0,
    "lastCheckInDate": None,
}

BASE_TODAY_CHECKIN = {
    "date": None,
    "completed": False,
    "data": None,
}

BASE_SUMMARY = {
    "overview": deepcopy(BASE_OVERVIEW),
    "todayCheckIn": deepcopy(BASE_TODAY_CHECKIN),
    "checkInDates": [],
}


class CheckInPayload(BaseModel):
    date: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    mood: int = Field(..., ge=0, le=10)
    energy: int = Field(..., ge=0, le=10)
    sleep: int = Field(..., ge=0, le=10)
    stress: int = Field(..., ge=0, le=10)
    notes: str | None = None
    timezone: str | None = Field(None, description="User's timezone (e.g., 'Asia/Singapore')")

class OverviewResponse(BaseModel):
    streak: int = 0
    longestStreak: int = 0
    totalCheckIns: int = 0
    lastCheckInDate: str | None = Field(
        None, description="Most recent check-in date in YYYY-MM-DD format"
    )


class CheckInEntry(BaseModel):
    date: str
    mood: int
    energy: int
    sleep: int
    stress: int
    notes: str | None = None
    timestamp: str | None = Field(
        None,
        description="ISO-8601 timestamp (UTC) logging when the check-in was stored",
    )


class MonthlyCheckinsResponse(BaseModel):
    checkIns: List[CheckInEntry]
    checkInDates: List[str]


class PetHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    date: str
    mood: str | None = None
    meals: int | None = Field(
        None, description="Number of meals fed to the pet on the specified date"
    )
    walks: int | None = Field(
        None, description="Number of walks taken on the specified date"
    )
    playTime: str | None = Field(
        None, description="How long the pet played (e.g., '45 mins')"
    )
    growthStage: str | None = Field(
        None, description="Narrative stage label for the pet on the specified date"
    )


class CheckInResult(BaseModel):
    id: str
    date: str
    timestamp: str


class SubmitCheckInResponse(BaseModel):
    success: bool
    checkIn: CheckInResult
    updatedStreak: int
    updatedTotalCheckIns: int


def _summary_doc(uid: str):
    return (
        db.collection("users").document(uid).collection("wellness").document("summary")
    )


def _checkins_collection(uid: str):
    return db.collection("users").document(uid).collection("wellness_checkins")


def _pet_history_collection(uid: str):
    return db.collection("users").document(uid).collection("wellness_pet_history")


def _isoformat(dt: datetime | None) -> str | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD."
        ) from exc


def _safe_parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return _parse_date(value)
    except HTTPException:
        return None


def _resolve_month_year(month: str | None, year: int | None) -> Tuple[int, int]:
    if month:
        month = month.strip()

    inferred_year = year
    month_component: str | None = month

    if month and "-" in month:
        parts = month.split("-", 1)
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid month format.")
        inferred_year = inferred_year or int(parts[0])
        month_component = parts[1]

    if not month_component or inferred_year is None:
        raise HTTPException(
            status_code=400,
            detail="Both month and year query parameters are required.",
        )

    try:
        month_int = int(month_component)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Month must be a number.") from exc

    if month_int < 1 or month_int > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12.")

    return month_int, inferred_year


def _merge_summary(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    summary = deepcopy(BASE_SUMMARY)
    if not raw:
        return summary

    overview = raw.get("overview") or {}
    summary["overview"].update(
        {k: v for k, v in overview.items() if k in summary["overview"]}
    )

    today = raw.get("todayCheckIn") or {}
    summary["todayCheckIn"].update(
        {k: v for k, v in today.items() if k in summary["todayCheckIn"]}
    )

    checkin_dates = raw.get("checkInDates")
    if isinstance(checkin_dates, list):
        summary["checkInDates"] = checkin_dates

    return summary


def _ensure_summary(
    uid: str, transaction: firestore.Transaction | None = None
) -> Dict[str, Any]:
    doc_ref = _summary_doc(uid)
    snapshot = doc_ref.get(transaction=transaction) if transaction else doc_ref.get()
    if snapshot.exists:
        return _merge_summary(snapshot.to_dict() or {})

    summary = deepcopy(BASE_SUMMARY)
    if transaction:
        transaction.set(doc_ref, summary)
    else:
        doc_ref.set(summary)
    return summary


def _serialize_checkin(doc) -> CheckInEntry:
    data: Dict[str, Any] = doc.to_dict() or {}

    timestamp_value = data.get("timestamp")
    if isinstance(timestamp_value, datetime):
        timestamp_str = _isoformat(timestamp_value)
    elif isinstance(timestamp_value, str):
        timestamp_str = timestamp_value
    else:
        timestamp_str = None

    return CheckInEntry(
        date=str(data.get("date") or ""),
        mood=int(data.get("mood") or 0),
        energy=int(data.get("energy") or 0),
        sleep=int(data.get("sleep") or 0),
        stress=int(data.get("stress") or 0),
        notes=cast(str | None, data.get("notes")),
        timestamp=timestamp_str,
    )


@router.get(
    "/overview",
    response_model=OverviewResponse,
    summary="Get wellness overview",
)
def get_wellness_overview(user: dict = Depends(require_user)):
    """Return streak and cumulative check-in stats for the authenticated user."""
    uid = user["uid"]
    summary = _ensure_summary(uid)
    return OverviewResponse(**summary["overview"])


@router.get(
    "/checkins",
    response_model=MonthlyCheckinsResponse,
    summary="List check-ins for a selected month",
)
def get_monthly_checkins(
    month: str | None = Query(
        None,
        description="Target month. Accepts numeric values (e.g., 10) or YYYY-MM format.",
    ),
    year: int | None = Query(None, description="Target year (e.g., 2025)."),
    user: dict = Depends(require_user),
):
    """Return all check-ins that fall within the requested month."""
    uid = user["uid"]
    month_int, year_int = _resolve_month_year(month, year)
    checkins_ref = _checkins_collection(uid)
    query = (
        checkins_ref.where("year", "==", year_int)
        .where("month", "==", month_int)
        .order_by("date", direction=firestore.Query.DESCENDING)
    )
    checkins = [_serialize_checkin(doc) for doc in query.stream()]
    checkin_dates = [entry.date for entry in checkins if entry.date]

    return MonthlyCheckinsResponse(
        checkIns=checkins,
        checkInDates=checkin_dates,
    )


@router.get(
    "/pet-history",
    response_model=PetHistoryResponse,
    summary="Get pet history for a specific date",
)
def get_pet_history(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    user: dict = Depends(require_user),
):
    """Return the recorded pet stats for the provided date."""
    uid = user["uid"]
    target_date = _parse_date(date)
    formatted_date = target_date.strftime("%Y-%m-%d")

    doc = _pet_history_collection(uid).document(formatted_date).get()
    if not doc.exists:
        raise HTTPException(
            status_code=404, detail="No pet history for the requested date."
        )

    payload = cast(Dict[str, Any], doc.to_dict() or {})
    payload["date"] = formatted_date
    return PetHistoryResponse(**payload)


@router.delete(
    "/reset",
    response_model=Dict[str, str],
    summary="Reset wellness data",
)
def reset_wellness_data(user: dict = Depends(require_user)):
    """Reset all wellness data (streaks, check-ins, pet history) for the authenticated user."""
    uid = user["uid"]
    
    print(f"DEBUG: Resetting wellness data for user {uid}")
    
    # Delete all wellness check-ins
    checkins_ref = _checkins_collection(uid)
    checkins = checkins_ref.stream()
    checkin_count = 0
    for checkin in checkins:
        checkin.reference.delete()
        checkin_count += 1
    print(f"DEBUG: Deleted {checkin_count} check-ins")
    
    # Delete all pet history
    pet_history_ref = _pet_history_collection(uid)
    pet_history = pet_history_ref.stream()
    pet_count = 0
    for pet in pet_history:
        pet.reference.delete()
        pet_count += 1
    print(f"DEBUG: Deleted {pet_count} pet history records")
    
    # Delete the summary document (if it exists)
    summary_ref = _summary_doc(uid)
    summary_snapshot = summary_ref.get()
    if summary_snapshot.exists:
        summary_ref.delete()
        print(f"DEBUG: Deleted summary document")
    else:
        print(f"DEBUG: No summary document found to delete")
    
    return {"message": "All wellness data has been reset successfully"}


@router.post(
    "/checkin",
    response_model=SubmitCheckInResponse,
    summary="Submit a wellness check-in",
)
def submit_checkin(payload: CheckInPayload, user: dict = Depends(require_user)):
    """Create or update the current user's check-in for the supplied date."""
    try:
        uid = user["uid"]
        new_date = _parse_date(payload.date)

        # Validate timezone
        try:
            user_tz = ZoneInfo(payload.timezone or "UTC")
            user_now = datetime.now(user_tz).date()
            
            # Prevent future date check-ins
            if new_date > user_now:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot check in for future dates."
                )
        except ZoneInfoNotFoundError as tz_error:
            print(f"DEBUG: Invalid timezone '{payload.timezone}': {tz_error}")
            # If timezone is invalid, fall back to UTC
            user_now = datetime.now(timezone.utc).date()
            if new_date > user_now:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot check in for future dates."
                )
        except Exception as e:
            print(f"DEBUG: Unexpected error during timezone validation: {e}")
            # Fallback to UTC for any other unexpected errors
            user_now = datetime.now(timezone.utc).date()
            if new_date > user_now:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot check in for future dates."
                )
            
        timestamp = datetime.now(timezone.utc)
        print(f"DEBUG: Processing check-in for user {uid}, date {payload.date}")

        checkins_ref = _checkins_collection(uid)
        checkin_doc = checkins_ref.document(payload.date)
        summary_doc = _summary_doc(uid)
        print(f"DEBUG: Created Firebase references")

        transaction = db.transaction()
        print(f"DEBUG: Created transaction")
    except Exception as e:
        print(f"DEBUG: Error in setup: {e}")
        raise HTTPException(status_code=500, detail=f"Setup error: {str(e)}")

    # Check if document exists before transaction
    existing_doc = checkin_doc.get()
    is_new_entry = not existing_doc.exists

    # Prevent duplicate check-ins for the same date
    if existing_doc.exists:
        print(f"DEBUG: Check-in already exists for user {uid} on {payload.date}")
        raise HTTPException(
            status_code=400, 
            detail=f"You've already checked in for {payload.date}. You can only check in once per day."
        )

    @firestore.transactional
    def _perform(transaction: firestore.Transaction):
        summary = _ensure_summary(uid, transaction=transaction)
        overview = summary["overview"]
        today_checkin = summary["todayCheckIn"]
        checkin_dates: List[str] = list(summary.get("checkInDates") or [])

        checkin_record = {
            **payload.model_dump(),
            "date": payload.date,
            "timestamp": timestamp,
            "year": new_date.year,
            "month": new_date.month,
        }
        transaction.set(checkin_doc, checkin_record)

        if is_new_entry:
            overview["totalCheckIns"] = int(overview.get("totalCheckIns") or 0) + 1

        last_date_str = overview.get("lastCheckInDate")
        last_date = _safe_parse_date(last_date_str)

        if not last_date or new_date > last_date:
            if last_date:
                delta_days = (new_date - last_date).days
                if delta_days == 1:
                    # Consecutive day - increment streak
                    current_streak = int(overview.get("streak") or 0) + 1
                    overview["streak"] = min(current_streak, 7) 
                    
                    # Update longest streak if current streak is higher
                    longest_streak = int(overview.get("longestStreak") or 0)
                    if current_streak > longest_streak:
                        overview["longestStreak"] = current_streak
                else:
                    # Gap in days - reset streak to 1
                    overview["streak"] = 1
                    # Check if this single day beats the longest streak
                    longest_streak = int(overview.get("longestStreak") or 0)
                    if longest_streak == 0:
                        overview["longestStreak"] = 1
            else:
                # First check-in
                overview["streak"] = 1
                overview["longestStreak"] = 1
            overview["lastCheckInDate"] = payload.date
        elif new_date == last_date:
            # Same day - keep current streak
            overview["streak"] = int(overview.get("streak") or 0)

        if payload.date not in checkin_dates:
            checkin_dates.append(payload.date)
        summary["checkInDates"] = sorted(checkin_dates, reverse=True)

        if today_checkin.get("date") in (None, payload.date):
            summary["todayCheckIn"] = {
                "date": payload.date,
                "completed": True,
                "data": payload.model_dump(),
            }

        transaction.set(summary_doc, summary)

        return {
            "overview": overview,
        }

    try:
        print(f"DEBUG: Executing transaction")
        result = _perform(transaction)
        overview = result["overview"]
        print(f"DEBUG: Transaction completed successfully")
    except Exception as e:
        print(f"DEBUG: Error executing transaction: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Transaction error: {str(e)}")

    return SubmitCheckInResponse(
        success=True,
        checkIn=CheckInResult(
            id=checkin_doc.id,
            date=payload.date,
            timestamp=_isoformat(timestamp) or timestamp.isoformat(),
        ),
        updatedStreak=overview.get("streak", 0),
        updatedTotalCheckIns=overview.get("totalCheckIns", 0),
    )

class WeeklyCheckinsResponse(BaseModel):
    checkIns: List[dict]
    checkInDates: List[datetime]
    startDate: Optional[str] = None
    endDate: Optional[str] = None

@router.get("/checkins/weekly", response_model=WeeklyCheckinsResponse)
def get_weekly_checkins(
    user: dict = Depends(require_user),
):
    """Return all check-ins from the past 7 days (including today)."""
    uid = user["uid"]
    checkins_ref = _checkins_collection(uid)

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=6)
    query = (
        checkins_ref
        .where(filter=firestore.FieldFilter("timestamp", ">=", seven_days_ago))
        .where(filter=firestore.FieldFilter("timestamp", "<=", now))
        .order_by("timestamp", direction=firestore.Query.ASCENDING)
    )

    checkins = [_serialize_checkin(doc) for doc in query.stream()]
    checkin_dates = [entry.date for entry in checkins if entry.date]

    return WeeklyCheckinsResponse(
        checkIns=[checkin.model_dump() for checkin in checkins],  # serialize cleanly
        checkInDates=checkin_dates,
        startDate=seven_days_ago.date().isoformat(),
        endDate=now.date().isoformat(),
    )