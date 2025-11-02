from fastapi import APIRouter, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from app.db.database import get_connection
from app.db import train_schedule_db

router = APIRouter(prefix="/train_schedule", tags=["Train Schedule"])

# -------------------------------------------------------------------------
# 1️⃣ Step 1 — Ask for train number
# -------------------------------------------------------------------------
@router.post("/")
async def ask_for_train_number(request: Request):
    """
    Entry point when user is redirected to train schedule department.
    Prompts the caller to say the train number clearly after the beep.
    """
    response = VoiceResponse()
    response.say(
        "Welcome to the Indian Railways train schedule department.",
        voice="man", language="en-IN"
    )
    response.pause(length=1)
    response.say(
        "Please say your train number clearly after the beep, "
        "for example, say one two six two seven for Karnataka Express.",
        voice="man", language="en-IN"
    )

    response.record(
        timeout=6,
        transcribe=True,
        max_length=10,
        play_beep=True,
        action="/train_schedule/process_train_number"  # Next step
    )

    return Response(content=str(response), media_type="application/xml")


# -------------------------------------------------------------------------
# 2️⃣ Step 2 — Process the transcription and fetch schedule info
# -------------------------------------------------------------------------
@router.post("/process_train_number")
async def process_train_number(request: Request):
    """
    Process the user's spoken train number and fetch schedule from DB.
    """
    form = await request.form()
    transcription_text = form.get("TranscriptionText")
    recording_url = form.get("RecordingUrl")

    response = VoiceResponse()

    # --- Handle no speech or unclear input ---
    if not transcription_text:
        response.say(
            "Sorry, I could not understand your train number. Let's try again.",
            voice="man", language="en-IN"
        )
        response.redirect("/train_schedule")
        return Response(content=str(response), media_type="application/xml")

    # Extract digits only (Twilio may transcribe numbers in words)
    train_number = "".join(ch for ch in transcription_text if ch.isdigit())
    print(f"🚆 Train schedule requested for Train No: {train_number}")
    print(f"🎧 Recording URL: {recording_url}")

    # --- Database lookup ---
    try:
        conn = get_connection()
        train_info = train_schedule_db.get_train_schedule(conn, train_number)
        conn.close()
    except Exception as e:
        print("❌ Database error while fetching train schedule:", e)
        response.say(
            "We are facing technical issues fetching the train schedule. Please try again later.",
            voice="man", language="en-IN"
        )
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    # --- If found ---
    if train_info:
        train_name = train_info["train_name"]
        source = train_info["source"]
        destination = train_info["destination"]
        departure = train_info["departure_time"]
        arrival = train_info["arrival_time"]
        duration = train_info["travel_duration"]
        days = train_info["days_of_operation"]

        response.say(
            f"Train number {train_number}, {train_name}, runs from {source} to {destination}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say(
            f"It departs from {source} at {departure}, and arrives at {destination} at {arrival}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say(
            f"Total travel time is {duration}. This train operates on {days}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say(
            "Thank you for calling the train schedule department. Have a pleasant journey.",
            voice="man", language="en-IN"
        )
        response.hangup()

    else:
        # --- No record found ---
        response.say(
            f"Sorry, I could not find any schedule for train number {train_number}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say(
            "Please check your train number and try again.",
            voice="man", language="en-IN"
        )
        response.redirect("/train_schedule")

    return Response(content=str(response), media_type="application/xml")