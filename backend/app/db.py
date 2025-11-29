# backend/app/db.py
# Demo mode: simple stubs so backend never crashes even without Supabase
def save_meeting(meeting_data):
    print("DB stub - save_meeting:", meeting_data)
    return {"status": "ok", "demo": True}

def save_user(user_data):
    print("DB stub - save_user:", user_data)
    return {"status": "ok", "demo": True}

def get_user(email):
    print("DB stub - get_user:", email)
    return {"data": []}
