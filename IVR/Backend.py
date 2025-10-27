

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import logging



app = FastAPI(title="Air India IVR API Middleware")



@app.get("/")
def read_root():
return {"message": "Hello! Welcome to Air India IVR API."}

@app.get("/home")
def first_home():
return {
"message": "Welcome to Air India Customer Support IVR. Press 1 for Main Menu, Press 2 for Booking Menu."
}

@app.get("/booking_menu")
def booking_menu():
return {
"menu": "Booking Menu",
"options": [
"1. Domestic Booking",
"2. International Booking"
]
}

@app.get("/status_menu")
def status_menu():
return {
"menu": "Status Menu",
"options": ["Enter the flight ID to check the status."]
}

@app.get("/domestic_booking")
def domestic_booking():
return {"message": "Domestic booking flow started."}

@app.get("/international_booking")
def international_booking():
return {"message": "International booking flow started."}


class BookingMenu(BaseModel):
booking_id: str
trans_id: str
passenger_fullname: str
passenger_contact: str

booking_db = []



@app.post("/handle-key")
def handle_key(Digits: str = "", menu: str = "main-menu"):
if menu == "main-menu":
if Digits == "1":
return booking_menu()
elif Digits == "2":
return status_menu()
else:
raise HTTPException(status_code=400, detail="Invalid input in main menu.")
elif menu == "booking-menu":
if Digits == "1":
return domestic_booking()
elif Digits == "2":
return international_booking()
else:
raise HTTPException(status_code=400, detail="Invalid input in booking menu.")
else:
raise HTTPException(status_code=400, detail="Invalid menu name.")


@app.put("/update_booking/{booking_id}")
def update_booking(booking_id: str, details: BookingMenu):
return {
"message": f"Booking {booking_id} updated successfully.",
"data": details
}



flights = [
{"flight_id": "AI1", "origin": "Mumbai", "destination": "Chennai", "status": "Confirmed"},
{"flight_id": "AI2", "origin": "Chennai", "destination": "Kochi", "status": "Delayed"},
{"flight_id": "AI3", "origin": "Delhi", "destination": "Mumbai", "status": "Cancelled"},
{"flight_id": "AI4", "origin": "Kochi", "destination": "Bengaluru", "status": "Confirmed"},
{"flight_id": "AI5", "origin": "Hyderabad", "destination": "Goa", "status": "Delayed"}
]

@app.get("/flight/{flight_id}")
def get_flight(flight_id: str):
for f in flights:
if f["flight_id"] == flight_id:
return f
raise HTTPException(status_code=404, detail="Flight not found.")

@app.get("/status/{flight_id}")
def get_flight_status(flight_id: str):
for f in flights:
if f["flight_id"] == flight_id:
return {
"status": f["status"],
"origin": f["origin"],
"destination": f["destination"]
}
raise HTTPException(status_code=404, detail="Flight not found.")

@app.get("/active_flights")
def active_flights():
return {"active_flights": flights}

@app.delete("/cancel_booking/{booking_id}")
def cancel_booking(booking_id: str):
for b in booking_db:
if b["booking_id"] == booking_id:
booking_db.remove(b)
return {"message": "Booking cancelled successfully."}
raise HTTPException(status_code=404, detail="Booking not found.")


logging.basicConfig(level=logging.INFO)

@app.exception_handler(Exception)
def handle_exceptions(request, exc):
logging.error(f"Error occurred: {exc}")
return JSONResponse(status_code=500, content={"detail": "Internal server error"})

call_sessions = {}

@app.post("/ivr/step1")
def step1(call_id: str, origin: str):
call_sessions[call_id] = {"origin": origin}
return {"message": "Origin saved. Please provide destination."}

@app.post("/ivr/step2")
def step2(call_id: str, destination: str):
session = call_sessions.get(call_id)
if not session:
raise HTTPException(status_code=400, detail="Invalid call session.")
session["destination"] = destination