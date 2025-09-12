from twilio.rest import Client
from twilio.twiml import VoiceResponse
import config

def create_twiml_emergency_call(emergency_script: str) -> str:
    response = VoiceResponse()
    
    response.say(
        emergency_script,
        voice='alice',
        language='en-US'
    )
    
    response.pause(length=2)
    
    response.say(
        "Press 1 to repeat this message, or stay on the line for emergency services.",
        voice='alice',
        language='en-US'
    )
    
    gather = response.gather(
        action='/api/twilio/gather',
        method='POST',
        num_digits=1,
        timeout=10
    )
    
    response.say(
        "Thank you. This emergency call has been logged. Emergency services have been notified.",
        voice='alice',
        language='en-US'
    )
    
    response.hangup()
    
    return str(response)

def initiate_twilio_emergency_call(phone_number: str, emergency_script: str) -> dict:
    if not all([config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN, config.TWILIO_PHONE]):
        raise Exception("Twilio credentials not properly configured")
    
    try:
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        
        twiml = create_twiml_emergency_call(emergency_script)
        
        call = client.calls.create(
            twiml=twiml,
            to=phone_number,
            from_=config.TWILIO_PHONE,
            record=True,
            timeout=30
        )
        
        return {
            "success": True,
            "call_id": call.sid,
            "status": call.status,
            "provider": "twilio",
            "message": "Emergency call initiated via Twilio"
        }
        
    except Exception as e:
        raise Exception(f"Twilio emergency call failed: {str(e)}")

def create_emergency_voice_message(data: dict, incident_type: str = "medical_emergency") -> str:
    passenger = data["passenger"]
    driver = data["driver"]
    vehicle = data["vehicle"]
    location = data["location"]
    
    simplified_script = f"""
    Emergency Alert from RideGuard Safety System.
    
    This is a {incident_type.replace('_', ' ')} emergency.
    
    Passenger {passenger['name']} requires immediate assistance.
    
    Location: {location['address']}.
    
    Vehicle: {vehicle['color']} {vehicle['make']} {vehicle['model']}, license plate {vehicle['plate']}.
    
    Driver: {driver['name']}, phone {driver['phone']}.
    
    Passenger phone: {passenger['phone']}.
    
    Please dispatch emergency services immediately.
    
    Repeating location: {location['address']}.
    
    This is an automated emergency call from RideGuard.
    """
    
    return simplified_script.strip()

async def twilio_emergency_fallback(phone_number: str, data: dict, incident_type: str = "medical_emergency") -> dict:
    emergency_message = create_emergency_voice_message(data, incident_type)
    
    try:
        result = initiate_twilio_emergency_call(phone_number, emergency_message)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "provider": "twilio",
            "message": "Twilio fallback call failed"
        }