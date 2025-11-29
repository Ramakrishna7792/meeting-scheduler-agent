# backend/app/main.py

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from googleapiclient.errors import HttpError

from backend.app.scheduler_engine import propose_slots
from backend.app.calendar_tool import GoogleCalendarTool
from backend.app.schemas import ProposeRequest, ConfirmRequest
from backend.app.config import DEMO_MODE

logger = logging.getLogger("meeting_agent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
logger.addHandler(handler)

app = FastAPI()


# ===========================
# 🔵 PROPOSE MEETING TIMES
# ===========================
@app.post("/propose")
def propose(req: ProposeRequest):
    try:
        logger.info("📩 Incoming propose request: %s", req.prompt)

        data = propose_slots(req.prompt)

        return {
            "status": "ok",
            "summary": data["summary"],
            "emails": data["emails"],
            "slots": data["slots"]
        }

    except Exception as exc:
        logger.exception("PROPOSE ERROR: %s", exc)
        return {
            "status": "error",
            "message": str(exc)
        }


# ===========================
# 🔵 CONFIRM EVENT (CREATE CALENDAR EVENT)
# ===========================
@app.post("/confirm")
def confirm(payload: ConfirmRequest):
    try:
        event = payload.event
        token_dict = payload.token_dict

        logger.info("📌 Confirm event: %s", event)

        # Instantiate tool (handles DEMO_MODE logic)
        try:
            cal = GoogleCalendarTool(token_dict or {})
        except Exception as exc:
            logger.error("Failed to init GoogleCalendarTool: %s", exc)
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"Invalid OAuth config: {str(exc)}"}
            )

        try:
            created = cal.create_event(
                summary=event["summary"],
                start=event["start"],
                end=event["end"]
            )

            logger.info("🎉 Event Created Successfully: %s", created.get("id"))
            return {"status": "ok", "created": created}

        except HttpError as gerr:
            logger.error("Google API error: %s", gerr)
            detail = gerr.content.decode() if hasattr(gerr, "content") else str(gerr)
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": f"Google API error: {detail}"}
            )

        except Exception as exc:
            logger.exception("Unexpected error")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": str(exc)}
            )

    except Exception as exc:
        logger.exception("Unexpected confirm_event error")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})
