from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
import os
from app.api.deps import get_current_user

router = APIRouter(tags=["tts"])

class TTSRequest(BaseModel):
    text: str

@router.post("/tts")
async def generate_tts(payload: TTSRequest, user_id: str = Depends(get_current_user)):
    api_key = os.getenv("GOOGLE_TTS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="TTS API key not configured")
        
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
    
    data = {
        "input": {"text": payload.text},
        "voice": {"languageCode": "en-US", "name": "en-US-Standard-A"},
        "audioConfig": {"audioEncoding": "MP3"}
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=data)
        
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"TTS Error: {resp.text}")
        
    result = resp.json()
    return {"audioContent": result.get("audioContent")}
