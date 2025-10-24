from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
import requests

app = Flask(__name__)

# Endpoint Twilio calls when a user dials your number
@app.route("/ivr", methods=['POST'])
def ivr():
    # Get caller info
    from_number = request.values.get('From')
    user_input = request.values.get('SpeechResult', '')  # If using speech recognition

    # Send input to AI
    ai_reply = send_to_ai(user_input)

    # Build Twilio Voice response
    resp = VoiceResponse()
    resp.say(f"Hello! Caller {from_number}. AI says: {ai_reply}", voice='alice')
    return str(resp)

def send_to_ai(user_input):
    ai_api_url = 'https://your-ai-stack-endpoint.com/process'
    payload = {'text': user_input}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(ai_api_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('reply', "Sorry, I didn't get that.")
    return "Sorry, something went wrong."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)