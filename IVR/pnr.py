from fastapi import APIRouter, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from app.db.database import get_connection
from app.db import pnr_db

router = APIRouter(prefix="/pnr_status", tags=["PNR Status"])

@router.post("/")
async def ask_pnr_number(request: Request):
    response = VoiceResponse()
    response.say(
        "Welcome to the Indian Railways P N R status department.",
        voice="man", language="en-IN"
    )
    response.pause(length=1)
    response.say(
        "Please say your ten digit P N R number clearly after the beep.",
        voice="man", language="en-IN"
    )

    # Record user input
    response.record(
        timeout=6,
        transcribe=True,
        max_length=15,
        play_beep=True,
        action="/pnr_status/process_pnr"
    )

    return Response(content=str(response), media_type="application/xml")

@router.post("/process_pnr")
async def process_pnr(request: Request):
    form = await request.form()
    transcription_text = form.get("TranscriptionText")
    recording_url = form.get("RecordingUrl")

    response = VoiceResponse()

    # --- If Twilio couldn't transcribe ---
    if not transcription_text:
        response.say(
            "Sorry, I could not capture your P N R number. Let's try again.",
            voice="man", language="en-IN"
        )
        response.redirect("/pnr_status")
        return Response(content=str(response), media_type="application/xml")

    # --- Clean up spoken digits ---
    pnr_number = "".join(ch for ch in transcription_text if ch.isdigit())

    if len(pnr_number) != 10:
        response.say(
            f"The number {pnr_number} you provided does not seem to be a valid ten digit P N R number.",
            voice="man", language="en-IN"
        )
        response.say("Please try again.", voice="man", language="en-IN")
        response.redirect("/pnr_status")
        return Response(content=str(response), media_type="application/xml")

    # --- Try fetching data from DB ---
    try:
        conn = get_connection()
        pnr_details = pnr_db.get_pnr_details(conn, pnr_number)
        conn.close()
    except Exception as e:
        print("❌ Database error:", e)
        response.say(
            "We are facing some technical issues fetching your P N R details. Please try again later.",
            voice="man", language="en-IN"
        )
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    # --- If PNR found ---
    if pnr_details:
        name = pnr_details["passenger_name"]
        train = pnr_details["train_name"]
        date = pnr_details["date_of_journey"]
        status = pnr_details["status"]
        seat = pnr_details["seat_number"]
        coach = pnr_details["coach"]

        response.say(
            f"P N R number {pnr_number} belongs to passenger {name}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say(
            f"You are booked on train {train}, seat number {seat} in coach {coach}, on {date}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        if status.lower() == "confirmed":
            response.say(
                "Your booking status is confirmed. Have a pleasant journey.",
                voice="man", language="en-IN"
            )
        elif "waiting" in status.lower():
            response.say(
                "Your booking is currently on the waiting list. Please check again closer to your journey date.",
                voice="man", language="en-IN"
            )
        elif "rac" in status.lower():
            response.say(
                "Your booking is under R A C status. You will be allotted a seat upon chart preparation.",
                voice="man", language="en-IN"
            )
        else:
            response.say(
                f"Your booking status is {status}.",
                voice="man", language="en-IN"
            )

        response.pause(length=1)
        response.say("Thank you for using Indian Railways P N R status service.", voice="man", language="en-IN")
        response.hangup()

    # --- If no matching record ---
    else:
        response.say(
            f"Sorry, no details found for P N R number {pnr_number}.",
            voice="man", language="en-IN"
        )
        response.pause(length=1)
        response.say("Please verify your number and try again.", voice="man", language="en-IN")
        response.redirect("/pnr_status")

    return Response(content=str(response), media_type="application/xml")