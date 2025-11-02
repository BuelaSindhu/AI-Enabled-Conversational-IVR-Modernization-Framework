from fastapi import APIRouter, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from app.db.database import get_connection
from app.db import refunds_db

router = APIRouter(prefix="/refunds", tags=["Refunds"])

# -------------------------------------------------------------------------
# 1️⃣ Step 1 — Ask user for PNR number to check refund status
# -------------------------------------------------------------------------
@router.post("/")
async def ask_for_refund_status(request: Request):
    """
    Entry point when user is redirected to refund department.
    Prompts the caller to say their PNR number.
    """
    response = VoiceResponse()
    response.say(
        "Welcome to the Indian Railways refund and cancellation department.",
        voice="man", language="en-IN"
    )
    response.pause(length=1)
    response.say(
        "Please say your P N R number clearly after the beep to check your refund status.",
        voice="man", language="en-IN"
    )

    response.record(
        timeout=6,
        transcribe=True,
        max_length=15,
        play_beep=True,
        action="/refunds/process_refund_status"  # Next step
    )

    return Response(content=str(response), media_type="application/xml")

# -------------------------------------------------------------------------
# 2️⃣ Step 2 — Process transcription and fetch refund info from DB
# -------------------------------------------------------------------------
@router.post("/process_refund_status")
async def process_refund_status(request: Request):
    """
    Process user's spoken PNR number, check database, and return refund info.
    """
    form = await request.form()
    transcription_text = form.get("TranscriptionText")
    recording_url = form.get("RecordingUrl")

    response = VoiceResponse()

    # --- If Twilio couldn’t capture anything ---
    if not transcription_text:
        response.say(
            "Sorry, I could not understand your P N R number. Let's try again.",
            voice="man", language="en-IN"
        )
        response.redirect("/refunds")  # retry asking
        return Response(content=str(response), media_type="application/xml")

    # Clean the spoken text (remove spaces, ensure digits only)
    pnr_number = "".join(ch for ch in transcription_text if ch.isdigit())
    print(f"💰 Refund status requested for PNR: {pnr_number}")
    print(f"🎧 Recording URL: {recording_url}")

    # --- Connect to DB and fetch refund details ---
    try:
        conn = get_connection()
        refund_info = refunds_db.get_refund_status(conn, pnr_number)
        conn.close()
    except Exception as e:
        print("❌ Database error while fetching refund info:", e)
        response.say(
            "We are unable to fetch your refund details at the moment. Please try again later.",
            voice="man", language="en-IN"
        )
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    # --- If refund record found ---
    if refund_info:
        passenger = refund_info["passenger_name"]
        amount = refund_info["amount"]
        mode = refund_info["payment_mode"]
        status = refund_info["refund_status"]
        date = refund_info["refund_date"]
        remarks = refund_info["remarks"]

        response.say(
            f"Refund details found for P N R number {pnr_number}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say(
            f"Passenger name {passenger}. Refund amount of {amount} rupees, "
            f"paid via {mode}, is currently {status} as of {date}.",
            voice="man", language="en-IN"
        )
        if remarks:
            response.say(remarks, voice="man", language="en-IN")
        response.pause(length=1)
        response.say("Thank you for calling the refund department. Goodbye.", voice="man", language="en-IN")
        response.hangup()

    else:
        # --- No matching record ---
        response.say(
            f"Sorry, no refund record was found for P N R number {pnr_number}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say(
            "Please check your P N R number and try again.",
            voice="man", language="en-IN"
        )
        response.redirect("/refunds")  # Retry once more

    return Response(content=str(response), media_type="application/xml")