import time
import os
from fastapi import FastAPI
from pydantic import BaseModel
from conversation_engine import generate_response, log_conversation
from tts_module import text_to_speech
from generate_avatar import run_wav2lip

app = FastAPI(title="AI Avatar Conversation API")

class AvatarRequest(BaseModel):
    image_path: str
    user_text: str
    emotion: str

class AvatarResponse(BaseModel):
    status: str
    response_text: str
    emotion: str
    audio_path: str
    video_path: str
    generation_time_seconds: float

@app.get("/")
def root():
    return {"message": "AI Avatar Conversation API is running"}

@app.post("/generate-avatar", response_model=AvatarResponse)
def generate_avatar(req: AvatarRequest):
    if not os.path.exists(req.image_path):
        return {"status": "error", "message": f"Image not found: {req.image_path}"}

    valid_emotions = ["neutral","happy","sad","angry","confident","teasing","intense"]
    if req.emotion not in valid_emotions:
        return {"status": "error", "message": f"Invalid emotion. Choose from: {valid_emotions}"}

    os.makedirs("outputs", exist_ok=True)
    start = time.time()

    response_text = generate_response(req.user_text, req.emotion)
    audio_path = "outputs/response_audio.mp3"
    text_to_speech(response_text, audio_path, emotion=req.emotion)
    video_path = "outputs/avatar_response.mp4"
    run_wav2lip(req.image_path, audio_path, video_path)

    elapsed = round(time.time() - start, 2)
    log_conversation(req.user_text, response_text, req.emotion, audio_path, video_path, elapsed)

    return AvatarResponse(
        status="success",
        response_text=response_text,
        emotion=req.emotion,
        audio_path=audio_path,
        video_path=video_path,
        generation_time_seconds=elapsed
    )