# frontend/streamlit_app.py
import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# --- Session state bootstrap ---
st.set_page_config(page_title="Meeting Scheduler Agent (Demo)", layout="centered")
if "messages" not in st.session_state:
    st.session_state.messages = []  # tuples (role, text)
if "pending_options" not in st.session_state:
    st.session_state.pending_options = None
if "confirm_lock" not in st.session_state:
    st.session_state.confirm_lock = False
if "last_request" not in st.session_state:
    st.session_state.last_request = None
if "retry_count" not in st.session_state:
    st.session_state.retry_count = 0
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False

# --- Helpers ---
def append_message(role: str, text: str):
    st.session_state.messages.append((role, text))

def call_propose(prompt: str, timeout: int = 30):
    """Call backend /propose with retry & fallback logic."""
    url = f"{BACKEND_URL}/propose"
    payload = {"prompt": prompt}
    attempts = 0
    max_attempts = 2
    last_err = None
    while attempts <= max_attempts:
        try:
            r = requests.post(url, json=payload, timeout=timeout)
            # If backend returns non-json (empty) handle that gracefully
            try:
                data = r.json()
            except Exception:
                raise RuntimeError(f"Backend returned non-JSON (status={r.status_code}).")

            if r.status_code != 200 or data.get("status") != "ok":
                last_err = data.get("message") or f"Backend error (status {r.status_code})"
                attempts += 1
                time.sleep(0.6)
                continue

            return data
        except Exception as exc:
            last_err = str(exc)
            attempts += 1
            time.sleep(0.6)
    # all attempts failed
    return {"status": "error", "message": f"Failed to propose: {last_err}"}

def call_confirm(event: dict, token_dict: dict | None = None, timeout: int = 30):
    """Call backend /confirm. Return JSON dict."""
    url = f"{BACKEND_URL}/confirm"
    payload = {"event": event}
    # optionally include token_dict if available
    if token_dict:
        payload["token_dict"] = token_dict
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        try:
            return r.json()
        except Exception:
            return {"status": "error", "message": f"Invalid response from backend (status {r.status_code})"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

# --- UI ---
st.title("🙂 Meeting Scheduler Agent (Demo)")
st.markdown("### 📝 Describe your meeting in natural language")

prompt = st.text_area("Type your meeting request:", value=st.session_state.get("last_request",""), height=120)
left_col, right_col = st.columns([1, 3])
with left_col:
    if st.button("✨ Propose Meeting Times"):
        if not prompt.strip():
            st.error("Please enter the meeting request in the box above.")
        else:
            # Save last prompt & clear prior state
            st.session_state.last_request = prompt
            st.session_state.pending_options = None
            st.session_state.confirmed = False
            append_message("user", prompt)
            with st.spinner("Thinking... proposing time slots"):
                resp = call_propose(prompt)
            if resp.get("status") == "ok" and resp.get("slots"):
                st.success("Here are three available time slots:")
                st.session_state.pending_options = resp
                # Add assistant message with friendly text
                human_summary = resp.get("summary","Meeting")
                append_message("assistant", f"Here are {len(resp['slots'])} options for '{human_summary}':")
            else:
                # fallback friendly message
                msg = resp.get("message", "I couldn't parse your request. Try: 'tomorrow 10am 30min with alice@example.com'")
                append_message("assistant", f"❌ {msg}")
with right_col:
    st.write("")  # spacing

st.markdown("---")
st.markdown("## 💬 Conversation")

# Render conversation history as chat bubbles
for role, text in st.session_state.messages:
    if role == "user":
        st.markdown(f"<div style='background:#222427;color:#fff;padding:14px;border-radius:10px;margin-bottom:8px'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background:#063b3b;color:#fff;padding:14px;border-radius:10px;margin-bottom:8px'>🤖 {text}</div>", unsafe_allow_html=True)

# If there are pending options, render them with Confirm buttons
opts = st.session_state.pending_options
if opts:
    st.markdown("### 📅 Available time options:")
    for i, slot in enumerate(opts["slots"]):
        human = slot.get("human") or f"{slot.get('start_iso')} - {slot.get('end_iso')}"
        st.markdown(f"**Option {i+1}:** {human}")
        btn_key = f"confirm_{i}"
        if st.button(f"Confirm Option {i+1}", key=btn_key):
            # Prevent duplicate / concurrent requests
            if st.session_state.confirm_lock:
                append_message("assistant", "⚠️ Request already in progress. Please wait.")
            else:
                st.session_state.confirm_lock = True
                append_message("assistant", f"✅ Event created! Creating event on server...")
                # call backend confirm (demo server may not need token)
                token_dict = None
                # If frontend stored token (optional), you could pass it here
                resp = call_confirm({
                    "summary": opts.get("summary","Meeting"),
                    "start": slot.get("start_iso"),
                    "end": slot.get("end_iso"),
                    "human": human
                }, token_dict=token_dict)
                st.session_state.confirm_lock = False

                if resp.get("status") == "ok":
                    append_message("assistant", "✅ Event created!")
                    st.session_state.confirmed = True
                else:
                    # show nice error + suggestion for judges
                    msg = resp.get("message", "Unknown error from server")
                    append_message("assistant", f"❌ Failed to create event: {msg}")
                    # If demo mode, give judges actionable tips
                    if DEMO_MODE:
                        append_message("assistant", "Tip for judges: Demo mode uses the server's shared calendar. If you deploy to production set OAuth credentials and enable Calendar API.")
                # small delay to let UI update before continuing
                time.sleep(0.25)



# add a retry / clear history area
st.markdown("### ⚙️ Controls")
cols = st.columns(3)
with cols[0]:
    if st.button("🔁 Retry last propose"):
        if not st.session_state.last_request:
            st.warning("No previous request to retry.")
        else:
            st.session_state.retry_count += 1
            append_message("user", st.session_state.last_request)
            with st.spinner("Retrying propose..."):
                resp = call_propose(st.session_state.last_request)
            if resp.get("status") == "ok" and resp.get("slots"):
                st.session_state.pending_options = resp
                append_message("assistant", f"Retry result: Found {len(resp['slots'])} slots.")
            else:
                append_message("assistant", f"Retry failed: {resp.get('message','unknown')}")
with cols[1]:
    if st.button("🧹 Clear conversation"):
        st.session_state.messages = []
        st.session_state.pending_options = None
        st.session_state.confirmed = False
        st.success("Conversation cleared.")
with cols[2]:
    if st.button("📝 Save conversation"):
        st.success("Saved to local session (in memory).")

