import os
import json
import datetime
from dotenv import load_dotenv

load_dotenv()

RULE_BASED_RESPONSES = {
    "neutral":    "I am here, and I am listening carefully.",
    "happy":      "This moment feels light, and I want to hold onto it.",
    "sad":        "Some things are heavy to say, but I will not look away from them.",
    "angry":      "I am not angry. I am disappointed because silence often says more than words.",
    "confident":  "I know exactly what I mean, and I will not soften it for anyone.",
    "teasing":    "Oh, you really want to know? Maybe I will tell you. Maybe I will not.",
    "intense":    "I am serious because some truths cannot be spoken lightly.",
}

def generate_response(user_text: str, emotion: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""You are a thoughtful AI avatar named Aria.
Respond in 2-3 short sentences only.
Your current emotion is: {emotion}.
Match your tone to this emotion.

User said: {user_text}"""
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            print(f"[LLM] Response generated via Gemini")
            return response.text.strip()
        except Exception as e:
            print(f"[LLM] Gemini failed: {e} — using fallback")

    print(f"[LLM] No API key — using rule-based fallback")
    return RULE_BASED_RESPONSES.get(emotion, RULE_BASED_RESPONSES["neutral"])

def log_conversation(user_text, response_text, emotion, audio_path, video_path, gen_time, log_path="outputs/conversation_log.json"):
    entry = {
        "user_text": user_text,
        "response_text": response_text,
        "emotion": emotion,
        "audio_path": audio_path,
        "video_path": video_path,
        "generation_time_seconds": gen_time,
        "timestamp": datetime.datetime.now().isoformat()
    }

    history = []
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            history = json.load(f)

    history.append(entry)

    with open(log_path, "w") as f:
        json.dump(history, f, indent=2)

    print(f"[LOG] Conversation saved to {log_path}")

# Quick test
if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    test_questions = [
        ("Who are you?", "confident"),
        ("Why do you look so serious?", "intense"),
        ("Tell me something emotional in one sentence.", "sad"),
    ]

    for question, emotion in test_questions:
        print(f"\nUser: {question}")
        response = generate_response(question, emotion)
        print(f"Avatar ({emotion}): {response}")
        log_conversation(question, response, emotion, "outputs/tts_audio.mp3", "outputs/tts_avatar_output.mp4", 0.0)