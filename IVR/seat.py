from fastapi import APIRouter, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from app.db.database import get_connection
from app.db import seat_db

router = APIRouter(prefix="/seat_availability", tags=["Seat Availability"])

# -------------------------------------------------------------------------
# 1️⃣ Step 1 — Ask for train number
# -------------------------------------------------------------------------
@router.post("/")
async def ask_train_number(request: Request):
    response = VoiceResponse()
    response.say(
        "Welcome to the Indian Railways seat availability department.",
        voice="man", language="en-IN"
    )
    response.pause(length=1)
    response.say(
        "Please say your train number clearly after the beep. "
        "For example, say one two six two seven for Karnataka Express.",
        voice="man", language="en-IN"
    )

    response.record(
        timeout=6,
        transcribe=True,
        max_length=10,
        play_beep=True,
        action="/seat_availability/get_date"
    )

    return Response(content=str(response), media_type="application/xml")


# -------------------------------------------------------------------------
# 2️⃣ Step 2 — Ask for date of journey
# -------------------------------------------------------------------------
@router.post("/get_date")
async def get_date_of_journey(request: Request):
    form = await request.form()
    transcription_text = form.get("TranscriptionText")
    recording_url = form.get("RecordingUrl")

    response = VoiceResponse()

    if not transcription_text:
        response.say(
            "Sorry, I could not understand your train number. Let's try again.",
            voice="man", language="en-IN"
        )
        response.redirect("/seat_availability")
        return Response(content=str(response), media_type="application/xml")

    train_number = "".join(ch for ch in transcription_text if ch.isdigit())
    response.say(
        f"Got it. Your train number is {train_number}.",
        voice="man", language="en-IN"
    )
    response.pause(length=1)
    response.say(
        "Now, please say the date of journey in year month date format, "
        "for example, say two zero two five dash one one dash zero five.",
        voice="man", language="en-IN"
    )

    response.record(
        timeout=6,
        transcribe=True,
        max_length=10,
        play_beep=True,
        action=f"/seat_availability/get_class?train_number={train_number}"
    )

    return Response(content=str(response), media_type="application/xml")


# -------------------------------------------------------------------------
# 3️⃣ Step 3 — Ask for class type
# -------------------------------------------------------------------------
@router.post("/get_class")
async def get_class_type(request: Request):
    form = await request.form()
    transcription_text = form.get("TranscriptionText")
    recording_url = form.get("RecordingUrl")

    request_query = request.query_params
    train_number = request_query.get("train_number")

    response = VoiceResponse()

    if not transcription_text:
        response.say(
            "Sorry, I could not capture your journey date. Let's try again.",
            voice="man", language="en-IN"
        )
        response.redirect("/seat_availability")
        return Response(content=str(response), media_type="application/xml")

    date_of_journey = transcription_text.strip().replace(" ", "")
    response.say(
        f"Okay. You are checking for date {date_of_journey}.",
        voice="man", language="en-IN"
    )
    response.pause(length=1)
    response.say(
        "Please say the class type, like Sleeper, 3A, 2A, or Chair Car.",
        voice="man", language="en-IN"
    )

    response.record(
        timeout=6,
        transcribe=True,
        max_length=10,
        play_beep=True,
        action=f"/seat_availability/check_availability?train_number={train_number}&date_of_journey={date_of_journey}"
    )

    return Response(content=str(response), media_type="application/xml")


# -------------------------------------------------------------------------
# 4️⃣ Step 4 — Check seat availability from DB
# -------------------------------------------------------------------------
@router.post("/check_availability")
async def check_availability(request: Request):
    form = await request.form()
    transcription_text = form.get("TranscriptionText")
    recording_url = form.get("RecordingUrl")

    query = request.query_params
    train_number = query.get("train_number")
    date_of_journey = query.get("date_of_journey")

    response = VoiceResponse()

    if not transcription_text:
        response.say(
            "Sorry, I could not understand the class type. Let's try again.",
            voice="man", language="en-IN"
        )
        response.redirect("/seat_availability")
        return Response(content=str(response), media_type="application/xml")

    class_type = transcription_text.strip().title()

    # --- Fetch from DB ---
    try:
        conn = get_connection()
        seat_info = seat_db.get_seat_availability(conn, train_number, date_of_journey, class_type)
        conn.close()
    except Exception as e:
        print("❌ Database error while fetching seat availability:", e)
        response.say(
            "We are facing some technical issues fetching seat availability. Please try again later.",
            voice="man", language="en-IN"
        )
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    # --- If found ---
    if seat_info:
        train_name = seat_info["train_name"]
        available = seat_info["available_seats"]
        total = seat_info["total_seats"]

        response.say(
            f"Train {train_number}, {train_name}, class {class_type}, on {date_of_journey}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say(
            f"There are {available} seats available out of {total} total seats.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say(
            "Thank you for using Indian Railways seat availability service.",
            voice="man", language="en-IN"
        )
        response.hangup()
    else:
        response.say(
            f"Sorry, no seat availability found for train number {train_number} on {date_of_journey} in class {class_type}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say("Please verify your details and try again.", voice="man", language="en-IN")
        response.redirect("/seat_availability")

    return Response(content=str(response), media_type="application/xml")