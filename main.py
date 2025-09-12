import os
import json
import requests
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

app = FastAPI(title="RideGuard Emergency AI Assistant")

# Добавляем CORS для работы с внешними доменами
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Получаем порт из окружения для Railway
PORT = int(os.environ.get("PORT", 8000))

app.mount("/static", StaticFiles(directory="static"), name="static")

class EmergencyRequest(BaseModel):
    incident_type: str = "medical_emergency"
    severity: str = "high"
    additional_info: Optional[str] = None

def load_test_data():
    try:
        with open("test_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Test data file not found")

def create_emergency_script(data: dict, incident_type: str = "medical_emergency") -> str:
    passenger = data["passenger"]
    driver = data["driver"]
    vehicle = data["vehicle"]
    location = data["location"]
    
    script = f"""
URGENT EMERGENCY CALL - RIDEGUARD SAFETY ALERT

This is an automated emergency call from RideGuard Safety System.

INCIDENT DETAILS:
- Emergency Type: {incident_type.replace('_', ' ').title()}
- Time: {datetime.now().strftime('%H:%M %Z')}
- Severity: HIGH PRIORITY

PASSENGER INFORMATION:
- Name: {passenger['name']}
- Phone: {passenger['phone']}

DRIVER INFORMATION:
- Name: {driver['name']}
- Phone: {driver['phone']}
- License: {driver['license']}

VEHICLE INFORMATION:
- Vehicle: {vehicle['year']} {vehicle['make']} {vehicle['model']}
- Color: {vehicle['color']}
- License Plate: {vehicle['plate']}

LOCATION:
- Address: {location['address']}
- GPS Coordinates: {location['gps_lat']}, {location['gps_lng']}

IMMEDIATE ACTION REQUIRED:
Please dispatch emergency services to the location immediately. The passenger requires medical attention. 
Driver and vehicle information provided for identification.

This is an automated call. For urgent follow-up, contact passenger at {passenger['phone']} or driver at {driver['phone']}.

Thank you.
"""
    return script.strip()

async def initiate_bland_call(phone_number: str, emergency_script: str) -> dict:
    # Проверяем конфигурацию
    bland_api_key = os.getenv("BLAND_API_KEY")
    if not bland_api_key:
        raise HTTPException(status_code=500, detail="BLAND_API_KEY not configured! Add it in Railway dashboard.")
    
    headers = {
        "Authorization": bland_api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "phone_number": phone_number,
        "task": emergency_script,
        "voice": "maya",
        "reduce_latency": True,
        "wait_for_greeting": True,
        "record": True,
        "max_duration": 180,
        "language": "en"
    }
    
    try:
        response = requests.post("https://api.bland.ai/v1/calls", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate call: {str(e)}")

async def send_sms_notification(phone_number: str, message: str) -> bool:
    # SMS functionality removed for Railway deployment
    return False

@app.get("/")
async def serve_demo():
    return FileResponse("static/demo.html")

@app.get("/api/test")
async def test_server():
    return {
        "status": "online",
        "service": "RideGuard Emergency AI Assistant",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/emergency")
async def trigger_emergency(request: EmergencyRequest):
    try:
        data = load_test_data()
        
        emergency_script = create_emergency_script(data, request.incident_type)
        
        emergency_phone = os.getenv("EMERGENCY_PHONE")
        if not emergency_phone:
            raise HTTPException(status_code=500, detail="EMERGENCY_PHONE not configured! Add it in Railway dashboard.")
        
        call_response = await initiate_bland_call(emergency_phone, emergency_script)
        
        sms_sent = await send_sms_notification(
            emergency_phone,
            f"RideGuard EMERGENCY: {request.incident_type.replace('_', ' ').title()} reported. "
            f"Location: {data['location']['address']}. Check voice call for details."
        )
        
        return JSONResponse({
            "success": True,
            "message": "Emergency call initiated successfully",
            "call_id": call_response.get("call_id"),
            "emergency_phone": emergency_phone,
            "incident_type": request.incident_type,
            "timestamp": datetime.now().isoformat(),
            "sms_sent": sms_sent,
            "data_used": {
                "passenger": data["passenger"]["name"],
                "driver": data["driver"]["name"],
                "location": data["location"]["address"],
                "vehicle": f"{data['vehicle']['make']} {data['vehicle']['model']} ({data['vehicle']['plate']})"
            }
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency call failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    emergency_phone = os.getenv("EMERGENCY_PHONE", "NOT SET")
    bland_api_key = os.getenv("BLAND_API_KEY")
    print(f"🚀 Starting Emergency AI Assistant on port {port}...")
    print(f"📞 Will call: {emergency_phone}")
    print(f"🔑 API Key: {'✓ Configured' if bland_api_key else '✗ Missing'}")
    uvicorn.run(app, host="0.0.0.0", port=port)