import os
import pickle
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDENTIALS_FILE = "google_oauth.json"
TOKEN_FILE = "token.pkl"


def get_calendar_service() -> Resource:
    creds: Credentials | None = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)


def create_event(
    summary: str,
    start_time: datetime,
    duration_minutes: int = 30,
    description: str = "",
    location: str = "",
    attendees: list[str] | None = None,
) -> dict:
    """
    Create a new calendar event.
    """
    service = get_calendar_service()
    end_time = start_time + timedelta(minutes=duration_minutes)

    event = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC",
        },
    }

    if attendees:
        event["attendees"] = [{"email": email} for email in attendees]

    return service.events().insert(calendarId="primary", body=event).execute()


def update_event(
    event_id: str,
    summary: str | None = None,
    start_time: datetime | None = None,
    duration_minutes: int | None = None,
    description: str | None = None,
    location: str | None = None,
    attendees: list[str] | None = None,
) -> dict:
    """
    Update an existing calendar event.

    Parameters with None values will not be updated.
    """
    service = get_calendar_service()

    current_event = (
        service.events().get(calendarId="primary", eventId=event_id).execute()
    )

    if summary:
        current_event["summary"] = summary

    if location:
        current_event["location"] = location

    if description:
        current_event["description"] = description

    if start_time:
        current_event["start"]["dateTime"] = start_time.isoformat()

        if duration_minutes:
            end_time = start_time + timedelta(minutes=duration_minutes)
            current_event["end"]["dateTime"] = end_time.isoformat()

    elif duration_minutes:
        current_start = datetime.fromisoformat(
            current_event["start"]["dateTime"].replace("Z", "+00:00")
        )
        end_time = current_start + timedelta(minutes=duration_minutes)
        current_event["end"]["dateTime"] = end_time.isoformat()

    if attendees:
        current_event["attendees"] = [{"email": email} for email in attendees]

    print(current_event)
    return (
        service.events()
        .update(calendarId="primary", eventId=event_id, body=current_event)
        .execute()
    )
