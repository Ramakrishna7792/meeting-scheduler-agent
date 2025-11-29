import re
from dateparser.search import search_dates     # ✅ FIXED HERE
import dateparser
from datetime import timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")

def extract_emails(text: str) -> List[str]:
    return EMAIL_RE.findall(text)

def extract_duration(text: str) -> int:
    # look for "30 minute" or "1 hour"
    m = re.search(r"(\d+)\s*(minute|min|mins|minutes)", text, re.I)
    if m:
        return int(m.group(1))

    m = re.search(r"(\d+)\s*(hour|hr|hrs|hours)", text, re.I)
    if m:
        return int(m.group(1)) * 60

    return 30  # default

def find_date_window(text: str, base_timezone="Asia/Kolkata"):
    settings = {
        "PREFER_DATES_FROM": "future",
        "RETURN_AS_TIMEZONE_AWARE": True
    }

    # ❌ Old (broken):
    # result = dateparser.search.search_dates(text, settings=settings)

    # ✅ New:
    result = search_dates(text, settings=settings)

    if result:
        dt = result[0][1]
        return dt

    # fallback: tomorrow 10 AM
    dt = dateparser.parse("tomorrow 10:00", settings=settings)
    return dt

def propose_slots(prompt: str, n_slots: int = 3) -> List[Dict]:
    duration_min = extract_duration(prompt)
    emails = extract_emails(prompt)
    start_dt = find_date_window(prompt)

    if start_dt is None:
        raise ValueError("Could not parse a date from the request.")

    slots = []

    # normalize to hour
    cursor = start_dt.replace(minute=0, second=0, microsecond=0)

    if start_dt.minute not in (0,):
        cursor = start_dt

    for i in range(n_slots):
        start = cursor + timedelta(hours=i)
        end = start + timedelta(minutes=duration_min)
        slots.append({
            "start_iso": start.isoformat(),
            "end_iso": end.isoformat(),
            "human": f"{start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%H:%M')} (Asia/Kolkata)"
        })

    return {
        "summary": "Meeting",
        "duration_min": duration_min,
        "emails": emails,
        "slots": slots
    }
