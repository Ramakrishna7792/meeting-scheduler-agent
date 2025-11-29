# backend/app/scheduler_engine.py

import re
import dateparser
from datetime import timedelta
from typing import List, Dict

EMAIL_RE = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")


def extract_emails(text: str) -> List[str]:
    return EMAIL_RE.findall(text)


def extract_duration(text: str) -> int:
    m = re.search(r"(\d+)\s*(minute|min|mins|minutes)", text, re.I)
    if m: return int(m.group(1))

    m = re.search(r"(\d+)\s*(hour|hr|hrs|hours)", text, re.I)
    if m: return int(m.group(1)) * 60

    return 30  # default


def find_date_window(text: str):
    settings = {"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": True}

    result = dateparser.search.search_dates(text, settings=settings)
    if result:
        return result[0][1]

    return dateparser.parse("tomorrow 10am", settings=settings)


def propose_slots(prompt: str, n_slots: int = 3):
    duration_min = extract_duration(prompt)
    emails = extract_emails(prompt)

    start_dt = find_date_window(prompt)
    if start_dt is None:
        raise ValueError("Could not parse date")

    cursor = start_dt.replace(second=0, microsecond=0)

    slots = []
    for i in range(n_slots):
        start = cursor + timedelta(hours=i)
        end = start + timedelta(minutes=duration_min)
        slots.append({
            "start": start.isoformat(),
            "end": end.isoformat(),
            "human": f"{start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%H:%M')} (Asia/Kolkata)"
        })

    return {
        "summary": "Meeting",
        "emails": emails,
        "slots": slots
    }
