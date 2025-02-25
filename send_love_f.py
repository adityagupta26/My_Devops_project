from flask import Flask, request, jsonify
import random
import os
from twilio.rest import Client

app = Flask(__name__)

# Load credentials securely using environment variables
ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER')

# Initialize Twilio client
twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# List of love and caring messages
messages = [
    "You're amazing just the way you are! 💖",
    "Sending you a big virtual hug! 🤗",
    "You are loved more than you know. 💕",
    "Take a deep breath, everything will be okay. 🌸",
    "Believe in yourself, because I believe in you! ✨",
    "You're stronger than you think. Keep going! 💪",
    "Never forget how special you are. 💝",
    "A smile suits you best! Keep shining. 😊",
    "You matter. The world is better with you in it. 🌍❤️",
    "You are enough, just as you are. 🌿"
]

@app.route('/send_love', methods=['POST'])
def send_love():
    data = request.json
    user_number = data.get("user_number")
    
    if not user_number:
        return jsonify({"error": "User number is required"}), 400
    
    # Choose a random love message
    response = random.choice(messages)
    
    # Send message via Twilio
    twilio_client.messages.create(
        body=response,
        from_=TWILIO_PHONE_NUMBER,
        to=user_number  # Send as SMS
    )
    
    return jsonify({"message": "Response sent successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
