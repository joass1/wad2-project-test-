from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..deps.auth import require_user
from ...core.firebase import db

router = APIRouter(prefix="/minigame", tags=["minigame"])


class WeaponData(BaseModel):
    """Weapon data structure"""
    type: str
    damage: int
    fireRate: int
    projectileSpeed: float
    range: int


class MinigameProgress(BaseModel):
    """Minigame progress data"""
    wave: int = Field(..., ge=1, description="Current wave number")
    level: int = Field(..., ge=1, description="Player level")
    weapons: list[WeaponData] = Field(default_factory=list, description="Unlocked weapons")
    max_health: int = Field(..., ge=1, description="Maximum health")
    speed: float = Field(..., ge=0, description="Movement speed")
    time_played_today: int = Field(default=0, ge=0, description="Time played today in milliseconds")
    died_today: bool = Field(default=False, description="Whether player died today")
    last_played: str = Field(..., description="ISO timestamp of last play")


class MinigameProgressResponse(BaseModel):
    """Response containing minigame progress"""
    progress: Optional[MinigameProgress] = None


class MinigameUpdateResponse(BaseModel):
    """Response for save/delete operations"""
    ok: bool
    message: str


def _minigame_doc(uid: str):
    """Get reference to user's minigame progress document"""
    return db.collection("users").document(uid).collection("minigame").document("progress")


@router.get("/progress", response_model=MinigameProgressResponse, summary="Get minigame progress")
def get_minigame_progress(user: dict = Depends(require_user)):
    """
    Get the user's minigame progress.

    Returns None if no progress exists (first time playing).
    """
    uid = user["uid"]
    doc = _minigame_doc(uid).get()

    if not doc.exists:
        return MinigameProgressResponse(progress=None)

    data = doc.to_dict()
    return MinigameProgressResponse(progress=MinigameProgress(**data))


@router.post("/progress", response_model=MinigameUpdateResponse, summary="Save minigame progress")
def save_minigame_progress(
    payload: MinigameProgress,
    user: dict = Depends(require_user)
):
    """
    Save or update the user's minigame progress.

    This endpoint handles both creating new progress and updating existing progress.
    """
    uid = user["uid"]
    doc_ref = _minigame_doc(uid)

    data = payload.model_dump()
    data["updated_at"] = datetime.now(timezone.utc)

    # Use merge=True to update existing or create new
    doc_ref.set(data, merge=True)

    return MinigameUpdateResponse(
        ok=True,
        message="Progress saved successfully"
    )


@router.delete("/progress", response_model=MinigameUpdateResponse, summary="Clear minigame progress")
def clear_minigame_progress(user: dict = Depends(require_user)):
    """
    Clear the user's minigame progress.

    Useful for testing or resetting the game state.
    """
    uid = user["uid"]
    doc_ref = _minigame_doc(uid)

    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="No progress found to clear")

    doc_ref.delete()

    return MinigameUpdateResponse(
        ok=True,
        message="Progress cleared successfully"
    )
