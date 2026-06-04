from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import io
import json
import datetime
import database
import agent

app = FastAPI(title="Trip-Guilder-Bot API", version="1.0.0")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    vibe: Optional[str] = ""
    num_people: Optional[int] = 2
    chat_history: Optional[List[Dict[str, Any]]] = []

class LogRequest(BaseModel):
    event_type: str
    spot_id: Optional[int] = None
    old_time_slot: Optional[str] = ""
    new_time_slot: Optional[str] = ""
    reason: Optional[str] = ""
    vibe: Optional[str] = ""
    num_people: Optional[int] = 2

class CalendarEvent(BaseModel):
    name: str
    time_slot: str
    address: str
    description: str

class ExportRequest(BaseModel):
    events: List[CalendarEvent]

@app.on_event("startup")
def startup_db():
    # Ensure DB is created
    database.init_db()

@app.get("/api/spots")
def get_spots():
    try:
        return database.get_all_spots()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    try:
        response = agent.run_agent(
            query=request.query,
            vibe=request.vibe,
            num_people=request.num_people,
            chat_history=request.chat_history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/log")
def log_endpoint(request: LogRequest):
    try:
        # Save to SQLite DB
        database.log_event(
            event_type=request.event_type,
            spot_id=request.spot_id,
            old_time_slot=request.old_time_slot,
            new_time_slot=request.new_time_slot,
            reason=request.reason,
            vibe=request.vibe,
            num_people=request.num_people
        )
        # Print JSON log to console as required
        console_log = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "event_type": request.event_type,
            "data": {
                "spot_id": request.spot_id,
                "old_time_slot": request.old_time_slot,
                "new_time_slot": request.new_time_slot,
                "reason_if_any": request.reason,
                "user_context": {
                    "vibe": request.vibe,
                    "num_people": request.num_people
                }
            }
        }
        print("LEARNING_LOOP_LOG:", json.dumps(console_log, ensure_ascii=False))
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export-calendar")
def export_calendar(request: ExportRequest):
    try:
        ics_content = []
        ics_content.append("BEGIN:VCALENDAR")
        ics_content.append("VERSION:2.0")
        ics_content.append("PRODID:-//Trip-Guilder-Bot//NONSGML Itinerary//EN")
        ics_content.append("CALSCALE:GREGORIAN")
        ics_content.append("METHOD:PUBLISH")
        
        # Assume scheduling for the next Saturday
        today = datetime.date.today()
        # Find next Saturday (weekday 5)
        days_ahead = 5 - today.weekday()
        if days_ahead <= 0: # Already Saturday or Sunday
            days_ahead += 7
        target_date = today + datetime.timedelta(days=days_ahead)
        date_str = target_date.strftime("%Y%m%d")
        
        for idx, event in enumerate(request.events):
            time_slot = event.time_slot
            # Parse timeslot, e.g. "15:00 - 17:00"
            try:
                start_time, end_time = [t.strip() for t in time_slot.split("-")]
                sh, sm = start_time.split(":")
                eh, em = end_time.split(":")
                dtstart = f"{date_str}T{sh}{sm}00"
                dtend = f"{date_str}T{eh}{em}00"
            except:
                # Default hours if parsing fails
                dtstart = f"{date_str}T{10 + idx*2:02d}0000"
                dtend = f"{date_str}T{12 + idx*2:02d}0000"
                
            uid = f"event-{idx}-{datetime.datetime.now().timestamp()}@tripguilderbot.local"
            dtstamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            
            ics_content.append("BEGIN:VEVENT")
            ics_content.append(f"UID:{uid}")
            ics_content.append(f"DTSTAMP:{dtstamp}")
            ics_content.append(f"DTSTART;TZID=Asia/Ho_Chi_Minh:{dtstart}")
            ics_content.append(f"DTEND;TZID=Asia/Ho_Chi_Minh:{dtend}")
            ics_content.append(f"SUMMARY:{event.name}")
            ics_content.append(f"DESCRIPTION:{event.description}")
            ics_content.append(f"LOCATION:{event.address}")
            ics_content.append("END:VEVENT")
            
        ics_content.append("END:VCALENDAR")
        full_ics = "\r\n".join(ics_content)
        
        return Response(
            content=full_ics,
            media_type="text/calendar",
            headers={"Content-Disposition": f"attachment; filename=hanoi_date_plan_{date_str}.ics"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.staticfiles import StaticFiles

# Mount static files to serve the frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
