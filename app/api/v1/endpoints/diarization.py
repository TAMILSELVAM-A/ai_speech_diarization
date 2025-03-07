from fastapi import APIRouter, File, UploadFile, HTTPException
from app.core.diarization import diarize_audio
from typing import List, Dict
import tempfile
import os

router = APIRouter()

@router.post("/diarize", response_model=List[Dict[str, str]])
async def diarize_audio_endpoint(audio: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(await audio.read())
            temp_audio_path = temp_audio.name

        result = diarize_audio(temp_audio_path)

        os.remove(temp_audio_path)

        return result
    except Exception as e:
        print(f"error {e}")
        raise HTTPException(status_code=500, detail=str(e))
