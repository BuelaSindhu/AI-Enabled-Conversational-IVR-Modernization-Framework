from fastapi import APIRouter, Request
from fastapi.responses import Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from app.db.database import get_connection
from app.db import emergency_db
from app.core.config import settings
import datetime

router = APIRouter(prefix="/emergency", tags=["Emergency"])

# Initialize Twilio Client (for optional SMS alert)
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# -------------------------------------------------------------------------
# 1️⃣ Step 1 — Ask user to describe emergency
# -------------------------------------------------------------------------
@router.post("/")
async def ask_for_emergency(request: Request):
    """
    Called when Twilio redirects to /emergency.
    Asks user to describe their emergency situation.
    """
    response = VoiceResponse()
    response.say(
        "You have reached the Indian Railways emergency helpline.",
        voice="man", language="en-IN"
    )
    response.pause(length=1)
    response.say(
        "Please describe your emergency clearly after the beep. "
        "Include details such as your train number, station name, or type of emergency.",
        voice="man", language="en-IN"
    )
    response.record(
        timeout=6,
        transcribe=True,
        max_length=25,
        play_beep=True,
        action="/emergency/process_emergency"  # Next step
    )

    return Response(content=str(response), media_type="application/xml")

# -------------------------------------------------------------------------
# 2️⃣ Step 2 — Process emergency message and store it
# -------------------------------------------------------------------------
@router.post("/process_emergency")
async def process_emergency(request: Request):
    """
    Handle emergency message transcription, save to DB, and send alert.
    """
    form = await request.form()
    transcription_text = form.get("TranscriptionText")
    recording_url = form.get("RecordingUrl")

    response = VoiceResponse()

    # --- Handle missing input ---
    if not transcription_text:
        response.say(
            "Sorry, I could not understand your message. Please describe your emergency again.",
            voice="man", language="en-IN"
        )
        response.redirect("/emergency")
        return Response(content=str(response), media_type="application/xml")

    emergency_text = transcription_text.strip()
    print(f"🚨 Emergency reported: {emergency_text}")
    print(f"🎧 Recording URL: {recording_url}")

    # --- Store in database ---
    try:
        conn = get_connection()
        emergency_db.insert_emergency(
            conn=conn,
            description=emergency_text,
            recording_url=recording_url,
            reported_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        conn.close()

        # --- Optional: Send SMS alert to control room ---
        try:
            alert_number = "+911234567890"  # Replace with actual emergency contact
            client.messages.create(
                to=alert_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                body=f"🚨 Emergency Alert: {emergency_text[:150]}..."
            )
            print("📩 SMS alert sent successfully.")
        except Exception as sms_error:
            print("⚠️ Could not send SMS alert:", sms_error)

        # --- Acknowledge to caller ---
        response.say(
            "Your emergency has been reported. Help is being notified immediately.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say(
            "Please remain calm. Railway authorities are taking necessary action. Goodbye.",
            voice="man", language="en-IN"
        )
        response.hangup()

    except Exception as db_error:
        print("❌ Error saving emergency:", db_error)
        response.say(
            "Sorry, we encountered an issue while recording your emergency. Please call again immediately.",
            voice="man", language="en-IN"
        )
        response.hangup()

    return Response(content=str(response), media_type="application/xml")