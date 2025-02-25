import os
from twilio.rest import Client

def send_love_message(to, message, use_whatsapp=False):
    # Fetch credentials from environment variables
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    
    # Set Twilio sender number
    twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    if use_whatsapp:
        to = f'whatsapp:{to}'
        twilio_phone_number = 'whatsapp:+17013531805'  # Use hardcoded Twilio WhatsApp number
    
    client = Client(account_sid, auth_token)
    
    try:
        message = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=to
        )
        print(f"✅ Message sent! ID: {message.sid}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    recipient = input("Enter recipient phone number (with country code): ")
    msg = input("Enter your love message: ")
    use_whatsapp = input("Send via WhatsApp? (yes/no): ").strip().lower() == 'yes'
    
    send_love_message(recipient, msg, use_whatsapp)
