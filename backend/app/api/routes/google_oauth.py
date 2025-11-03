from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import os
import time
import secrets
import requests
from typing import Optional

from ..deps.auth import require_user
from ...core.firebase import db
from ...core.google_calendar import call_google_calendar_api


router = APIRouter(prefix="/google/oauth", tags=["google-oauth"])


def _get_env(name: str):
    value = os.environ.get(name)
    if not value:
        raise HTTPException(status_code=500, detail=f"Missing server env: {name}")
    return value


@router.get("/start")
def start_oauth(user=Depends(require_user)):
    """Start Google OAuth for Calendar access. Returns the Google consent URL."""
    client_id = _get_env("GOOGLE_OAUTH_CLIENT_ID")
    redirect_uri = _get_env("GOOGLE_OAUTH_REDIRECT_URI")
    scopes = os.environ.get(
        "GOOGLE_OAUTH_SCOPES", "https://www.googleapis.com/auth/calendar"
    )

    uid = user["uid"]
    state = f"{uid}:{int(time.time())}:{secrets.token_urlsafe(16)}"
    db.collection("oauth_state").document(uid).set({"state": state, "ts": time.time()})

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "access_type": "offline",
        "include_granted_scopes": "true",
        "scope": scopes,
        "state": state,
        "prompt": "consent",
    }

    authorize_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return {"authorizeUrl": authorize_url}


@router.get("/callback")
def oauth_callback(code: str, state: str):
    """Google redirects here with code+state. Exchanges code for tokens and stores them."""
    client_id = _get_env("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = _get_env("GOOGLE_OAUTH_CLIENT_SECRET")
    redirect_uri = _get_env("GOOGLE_OAUTH_REDIRECT_URI")

    try:
        # Extract uid from state and validate stored state
        uid = state.split(":", 1)[0]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid state format")

    state_doc = db.collection("oauth_state").document(uid).get()
    if not state_doc.exists:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    state_data = state_doc.to_dict() or {}
    if state_data.get("state") != state:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    try:
        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        token_resp.raise_for_status()
        payload = token_resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Token exchange failed: {e}")

    expires_in = int(payload.get("expires_in", 0))
    token_expiry = int(time.time()) + expires_in if expires_in else None

    db.collection("users").document(uid).collection("integrations").document(
        "googleCalendar"
    ).set(
        {
            "connected": True,
            "accessToken": payload.get("access_token"),
            "refreshToken": payload.get("refresh_token"),
            "tokenExpiry": token_expiry,
            "tokenType": payload.get("token_type"),
            "updatedAt": time.time(),
        },
        merge=True,
    )

    # Optional: cleanup state
    db.collection("oauth_state").document(uid).delete()

    # Redirect back to dashboard (popup will detect this and close)
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:8080")
    redirect_url = f"{frontend_url}/dashboard"
    return RedirectResponse(url=redirect_url)


@router.get("/calendar/status")
def calendar_status(user=Depends(require_user)):
    """Return whether the current user has Google Calendar connected."""
    uid = user["uid"]
    doc = (
        db.collection("users")
        .document(uid)
        .collection("integrations")
        .document("googleCalendar")
        .get()
    )
    if not doc.exists:
        return {"connected": False}
    data = doc.to_dict() or {}
    return {
        "connected": bool(data.get("connected")),
        "hasRefreshToken": bool(data.get("refreshToken")),
    }


@router.delete("/disconnect")
def disconnect_calendar(user=Depends(require_user)):
    """Disconnect Google Calendar integration for the current user."""
    uid = user["uid"]

    # Delete the integration document
    doc_ref = (
        db.collection("users")
        .document(uid)
        .collection("integrations")
        .document("googleCalendar")
    )

    if doc_ref.get().exists:
        doc_ref.delete()
        return {"ok": True, "message": "Google Calendar disconnected successfully"}
    else:
        return {"ok": True, "message": "Google Calendar was not connected"}


@router.get("/calendar/events")
def get_calendar_events(
    user=Depends(require_user),
    timeMin: Optional[str] = Query(
        None, description="RFC3339 timestamp for start time"
    ),
    timeMax: Optional[str] = Query(None, description="RFC3339 timestamp for end time"),
    maxResults: int = Query(
        10, ge=1, le=2500, description="Maximum number of events to return"
    ),
    singleEvents: bool = Query(True, description="Whether to expand recurring events"),
    orderBy: str = Query("startTime", description="Order of the events"),
):
    """Fetch Google Calendar events for the authenticated user."""
    uid = user["uid"]

    try:
        params = {
            "maxResults": maxResults,
            "singleEvents": singleEvents,
            "orderBy": orderBy,
        }
        if timeMin:
            params["timeMin"] = timeMin
        if timeMax:
            params["timeMax"] = timeMax

        print(f"Fetching calendar events for user {uid} with params: {params}")

        # Fetch events from primary calendar
        data = call_google_calendar_api(uid, "calendars/primary/events", **params)

        print(f"Calendar API returned {len(data.get('items', []))} events")
        print(f"Raw response: {data}")

        return data
    except Exception as e:
        print(f"Error fetching calendar events: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch calendar events: {str(e)}"
        )
