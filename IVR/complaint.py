from fastapi import APIRouter, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from app.db import database, complaints_db

router = APIRouter(prefix="/complaints", tags=["Complaints"])

# -------------------------------------------------------------------------
# 1️⃣  Ask the user to record their complaint
# -------------------------------------------------------------------------
@router.post("/")
async def complaint_entry(request: Request):
    """
    Entry point when Twilio redirects here from the main IVR.
    Asks the user to state their complaint after the beep.
    """
    response = VoiceResponse()
    response.say(
        "You are now connected to the Indian Railways Complaints Department.",
        voice="man"
    )
    response.pause(length=1)
    response.say(
        "Please state your name, P N R number, and describe your complaint clearly after the beep.",
        voice="man"
    )

    response.record(
        timeout=5,
        transcribe=True,
        max_length=30,
        play_beep=True,
        action="/complaints/record_complete"
    )

    return Response(content=str(response), media_type="application/xml")


# -------------------------------------------------------------------------
# 2️⃣  Twilio sends recorded audio + transcription here
# -------------------------------------------------------------------------
@router.post("/record_complete")
async def record_complete(request: Request):
    """
    Handles the transcribed voice input and stores it as a complaint in the database.
    """
    form = await request.form()
    transcription_text = form.get("TranscriptionText")
    recording_url = form.get("RecordingUrl")

    print("\n--- Complaint Received ---")
    print(f"Recording: {recording_url}")
    print(f"Transcript: {transcription_text}")
    print("---------------------------\n")

    response = VoiceResponse()

    if not transcription_text:
        response.say(
            "Sorry, I could not hear your complaint properly. Please try again later.",
            voice="man"
        )
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    # Basic parsing (you can later replace this with NLP extraction)
    # Example input: "My name is Rahul Sharma, P N R 1234567890, train was dirty"
    words = transcription_text.lower()
    pnr = ""
    name = "Unknown Passenger"
    description = transcription_text.strip()

    # Extract PNR number (look for a 10-digit sequence)
    import re
    pnr_match = re.search(r"\b\d{10}\b", words)
    if pnr_match:
        pnr = pnr_match.group()

    # Try to extract name after "my name is"
    name_match = re.search(r"my name is ([a-z ]+)", words)
    if name_match:
        name = name_match.group(1).title()

    # Store in database
    try:
        conn = database.get_connection()
        complaint_id = complaints_db.register_complaint(
            conn,
            passenger_name=name,
            pnr_number=pnr or "Unknown",
            contact_number="Not Provided",
            category="General",
            description=description
        )
        conn.close()

        response.say(
            f"Thank you {name}. Your complaint has been registered successfully. "
            f"Your complaint ID is {complaint_id}. We will review it soon.",
            voice="man"
        )

    except Exception as e:
        print("Database Error:", e)
        response.say(
            "Sorry, there was a problem registering your complaint. Please try again later.",
            voice="man"
        )

    response.hangup()
    return Response(content=str(response), media_type="application/xml")


# -------------------------------------------------------------------------
# 3️⃣  Optional: Fetch complaint details by PNR
# -------------------------------------------------------------------------
@router.post("/get_status")
async def get_complaint_status(request: Request):
    """
    Retrieve complaints for a given PNR number.
    """
    form = await request.form()
    transcription_text = form.get("TranscriptionText", "")
    response = VoiceResponse()

    import re
    pnr_match = re.search(r"\b\d{10}\b", transcription_text)
    if not pnr_match:
        response.say("Please provide a valid ten digit P N R number.", voice="man")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    pnr_number = pnr_match.group()

    conn = database.get_connection()
    complaints = complaints_db.get_complaint_details(conn, pnr_number)
    conn.close()

    if not complaints:
        response.say(f"No complaints found for P N R number {pnr_number}.", voice="man")
    else:
        response.say(
            f"You have {len(complaints)} complaint record{'s' if len(complaints) > 1 else ''}.",
            voice="man"
        )
        for c in complaints:
            response.say(
                f"Complaint ID {c['complaint_id']} on {c['complaint_date']} "
                f"is currently {c['status']}. {c['resolution_remarks'] or 'Pending review.'}",
                voice="man"
            )

    response.hangup()
    return Response(content=str(response), media_type="application/xml")