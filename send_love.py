from flask import Flask, request, jsonify
import random
from twilio.rest import Client
from deepseek import DeepSeek

app = Flask(__name__)

# Twilio credentials (replace with your own)
ACCOUNT_SID = 'AC379747970908ee29c137799bcac31418'
AUTH_TOKEN = '6b7efbef7fd2eadd07e58c9dadd202e7'
WHATSAPP_NUMBER = '9315218933'

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Initialize DeepSeek AI (configure API key if required)
deepseek_client = deepseek(api_key='sk-kk2wMZoGX-G8j7yV8FDL3')

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
    user_message = data.get("message", "")
    
    if not user_number:
        return jsonify({"error": "User number is required"}), 400
    
    if user_message:
        response = deepseek_client.respond(user_message)
    else:
        response = random.choice(messages)
    
    twilio_client.messages.create(
        body=response,
        from_=WHATSAPP_NUMBER,
        to=f'whatsapp:{user_number}'
    )
    
    return jsonify({"message": "Response sent successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
