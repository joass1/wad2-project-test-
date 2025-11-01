import os
import time
from typing import Optional, Dict, Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

from ..core.firebase import db


def get_google_tokens(uid: str) -> Optional[Dict[str, Any]]:
    """Retrieve stored Google tokens for a user."""
    doc = (
        db.collection("users")
        .document(uid)
        .collection("integrations")
        .document("googleCalendar")
        .get()
    )
    if not doc.exists:
        return None
    return doc.to_dict()


def save_google_tokens(uid: str, creds: Credentials) -> None:
    """Save updated Google credentials to Firestore."""
    db.collection("users").document(uid).collection("integrations").document(
        "googleCalendar"
    ).update(
        {
            "accessToken": creds.token,
            "refreshToken": creds.refresh_token,
            "tokenExpiry": creds.expiry.timestamp() if creds.expiry else None,
            "updatedAt": time.time(),
        }
    )


def get_google_credentials(uid: str) -> Optional[Credentials]:
    """Get Google OAuth2 credentials for a user, with automatic refresh."""
    tokens = get_google_tokens(uid)
    if not tokens:
        return None

    creds = Credentials(
        token=tokens.get("accessToken"),
        refresh_token=tokens.get("refreshToken"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    )

    # Auto-refresh if needed
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Save refreshed tokens
            save_google_tokens(uid, creds)
        except Exception:
            return None

    return creds


def get_calendar_service(uid: str):
    """Get authenticated Google Calendar service for a user."""
    creds = get_google_credentials(uid)
    if not creds:
        raise Exception("No valid Google Calendar credentials")

    return build("calendar", "v3", credentials=creds)


def call_google_calendar_api(uid: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """
    Call Google Calendar API using official client library.

    Args:
        uid: User ID
        endpoint: API endpoint (e.g., 'events', 'calendars/primary/events')
        **kwargs: Additional parameters for the API call

    Returns:
        API response as dict
    """
    try:
        service = get_calendar_service(uid)

        # Parse endpoint
        parts = endpoint.split("/")
        if len(parts) == 1:
            # Direct method like 'events'
            method_name = parts[0]
            calendar_id = "primary"
        elif len(parts) == 3 and parts[0] == "calendars" and parts[2] == "events":
            # calendars/{calendarId}/events
            calendar_id = parts[1]
            method_name = "events"
        else:
            raise ValueError(f"Unsupported endpoint format: {endpoint}")

        # Call the appropriate method
        if method_name == "events":
            return service.events().list(calendarId=calendar_id, **kwargs).execute()
        else:
            raise ValueError(f"Unsupported method: {method_name}")

    except HttpError as e:
        # Re-raise with more context
        raise Exception(f"Google Calendar API error: {e}")
