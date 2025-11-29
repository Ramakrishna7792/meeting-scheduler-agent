# backend/app/calendar_tool.py

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from backend.app.config import (
    DEMO_MODE,
    DEMO_REFRESH_TOKEN,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET
)
import logging

logger = logging.getLogger("calendar")


class GoogleCalendarTool:
    def __init__(self, token_dict: dict):
        logger.info("========================================")
        logger.info("📌 DEBUG: GoogleCalendarTool Initialized")
        logger.info("DEMO MODE = %s", DEMO_MODE)

        if DEMO_MODE:
            logger.info("⚡ DEMO MODE ACTIVE — Using server refresh token.")
            token_dict = {
                "refresh_token": DEMO_REFRESH_TOKEN,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "token_uri": "https://oauth2.googleapis.com/token",
            }

        # Validate required fields
        for k in ("refresh_token", "client_id", "client_secret"):
            if not token_dict.get(k):
                raise ValueError(f"Missing required OAuth field: {k}")

        logger.info("✅ TOKEN DICT VALIDATED SUCCESSFULLY")

        self.creds = Credentials.from_authorized_user_info(token_dict)
        logger.info("🛠 Building Google Calendar service...")
        self.service = build("calendar", "v3", credentials=self.creds)
        logger.info("✅ Google Calendar service ready")

    def create_event(self, summary, start, end):
        event = {
            "summary": summary,
            "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end, "timeZone": "Asia/Kolkata"},
        }

        logger.info("📝 Creating Google Calendar Event: %s", event)

        created = self.service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        return created
