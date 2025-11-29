✅ Instructions to Run Locally
1. Clone the repository
git clone https://github.com/Ramakrishna7792/meeting-scheduler-agent.git
cd meeting-scheduler-agent

2. Create and activate virtual environment

Windows

python -m venv venv
venv\Scripts\activate

Mac/Linux

python3 -m venv venv
source venv/bin/activate

3. Install all project dependencies
pip install -r requirements.txt

4. Create a .env file

Create a new file named .env in the project root and add:

DEMO_MODE=true
DEMO_REFRESH_TOKEN=YOUR_REFRESH_TOKEN
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET
GROQ_API_KEY=YOUR_GROQ_API_KEY



5. Start the backend (FastAPI)
uvicorn backend.app.main:app --reload --port 8000

This starts the API server at:
👉 http://localhost:8000

6. Start the frontend (Streamlit UI)

In another terminal:
streamlit run frontend/streamlit_app.py


The UI opens at:
👉 http://localhost:8501

7. Use the agent

In the chat interface, type:

"Schedule a 30-minute meeting tomorrow with alice@example.com"

The agent will:

1️⃣ Understand your request
2️⃣ Extract date, duration, and email
3️⃣ Propose available time slots
4️⃣ Upon confirmation → create the event in Google Calendar
