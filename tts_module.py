import edge_tts
import asyncio
import json
import os

def load_emotion_settings(emotion: str) -> dict:
    with open("emotion_mapping.json", "r") as f:
        mapping = json.load(f)
    return mapping.get(emotion, mapping["neutral"])

async def _generate(text: str, voice: str, rate: str, pitch: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)

def text_to_speech(text: str, output_path: str, emotion: str = "neutral", voice: str = "en-US-AriaNeural") -> str:
    settings = load_emotion_settings(emotion)
    rate = settings["rate"]
    pitch = settings["pitch"]
    
    print(f"[TTS] Voice: {voice} | Rate: {rate} | Pitch: {pitch}")
    asyncio.run(_generate(text, voice, rate, pitch, output_path))
    print(f"[TTS] Audio saved to: {output_path}")
    return output_path

# Quick test
if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    text_to_speech(
        "I do not speak to impress people. I speak only when silence becomes heavier than truth.",
        "outputs/tts_audio.mp3",
        emotion="confident"
    )