# AI Avatar Conversation Pipeline

A working proof-of-concept that accepts a user message, generates an AI response,
converts it to speech, and produces a talking avatar video using a static avatar image.

**Repository:** https://github.com/Sneha100802/avatar-assignment

## Pipeline Flow

```
User Text → AI Response → Emotion Mapping → TTS Audio → Talking Avatar Video
```

## Tech Stack

| Component | Tool |
|-----------|------|
| Avatar / Lip-sync | Wav2Lip (GAN model) |
| Text-to-Speech | edge-tts (Microsoft Neural, free, no API key) |
| LLM | Google Gemini 2.0 Flash + rule-based fallback |
| API | FastAPI + Uvicorn |
| GPU | NVIDIA GTX 1650, CUDA 11.8 |
| Python | 3.13.1 |

---

## Project Structure

```
avatar-assignment/
├── README.md
├── setup.md
├── requirements.txt
├── .gitignore
├── .env                        # not committed
├── generate_avatar.py          # end-to-end CLI script
├── conversation_engine.py      # LLM + fallback response generation
├── tts_module.py               # edge-tts wrapper with emotion control
├── emotion_mapping.json        # emotion → TTS settings mapping
├── app.py                      # FastAPI bonus endpoint
├── samples/
│   ├── avatar.jpg              # AI-generated fictional avatar
│   └── sample_audio.wav        # sample audio for baseline tests
├── outputs/
│   ├── baseline_5s.mp4
│   ├── baseline_10s.mp4
│   ├── baseline_20s.mp4
│   ├── tts_audio.mp3
│   ├── tts_avatar_output.mp4
│   ├── avatar_response.mp4
│   └── conversation_log.json
├── report/
│   └── technical_report.md
├── temp/                       # Wav2Lip temp files
└── Wav2Lip/                    # cloned model repo
```

---

## Setup Instructions

### 1. Prerequisites

- Python 3.13
- Git
- FFmpeg installed and added to PATH
  - Download from: https://www.gyan.dev/ffmpeg/builds/ (release essentials zip)
  - Extract to `C:\ffmpeg` and add `C:\ffmpeg\bin` to system PATH
  - Verify: `ffmpeg -version`

### 2. Clone the repository

```bash
git clone https://github.com/Sneha100802/avatar-assignment.git
cd avatar-assignment
```

### 3. Clone Wav2Lip inside the project

```bash
git clone https://github.com/Rudrabha/Wav2Lip.git
```

### 4. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 5. Install PyTorch with CUDA 11.8

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

> For CPU-only: `pip install torch torchvision torchaudio`

### 6. Install project dependencies

```bash
pip install opencv-python
pip install librosa==0.9.2
pip install scipy imageio face-alignment resampy tqdm audioread
pip install edge-tts
pip install groq fastapi uvicorn python-dotenv google-genai
```

### 7. Download Wav2Lip checkpoint

Create the checkpoints folder:
```bash
mkdir Wav2Lip\checkpoints
```

Download `wav2lip_gan.pth` (~435 MB) from:
```
https://github.com/anothermartz/Easy-Wav2Lip/releases/download/Prerequesits/Wav2Lip_GAN.pth
```

Place it at: `Wav2Lip\checkpoints\wav2lip_gan.pth`

### 8. Download face detection model

Download `s3fd-619a316812.pth` (~85 MB) from:
```
https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth
```

Place it at:
```
C:\Users\<your-username>\.cache\torch\hub\checkpoints\s3fd-619a316812.pth
```

### 9. Create temp folder

```bash
mkdir temp
```

### 10. Set up environment variables

Create a `.env` file in the root folder:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free Gemini API key from: https://aistudio.google.com

> If no API key is provided, the system automatically falls back to rule-based responses.

---

## Usage

### Command Line (Mandatory)

```bash
python generate_avatar.py \
  --image samples/avatar.jpg \
  --user-text "Why are you silent?" \
  --emotion confident \
  --output outputs/avatar_response.mp4
```

**Required arguments:**

| Argument | Description |
|----------|-------------|
| `--image` | Path to avatar image |
| `--user-text` | User message |
| `--emotion` | One of: neutral, happy, sad, angry, confident, teasing, intense |
| `--output` | Output video path |

**Optional arguments:**

| Argument | Description |
|----------|-------------|
| `--voice` | TTS voice name (default: en-US-AriaNeural) |
| `--debug` | Print extra debug info |

---

### FastAPI Endpoint (Bonus)

Start the server:
```bash
python -m uvicorn app:app --reload
```

API runs at: http://127.0.0.1:8000
Interactive docs at: http://127.0.0.1:8000/docs

**Endpoint:** `POST /generate-avatar`

**Sample request:**
```json
{
  "image_path": "samples/avatar.jpg",
  "user_text": "Why are you serious?",
  "emotion": "intense"
}
```

**Sample response:**
```json
{
  "status": "success",
  "response_text": "I am serious because some truths cannot be spoken lightly.",
  "emotion": "intense",
  "audio_path": "outputs/response_audio.mp3",
  "video_path": "outputs/avatar_response.mp4",
  "generation_time_seconds": 104.72
}
```

**Sample curl command:**
```bash
curl -X POST http://127.0.0.1:8000/generate-avatar \
  -H "Content-Type: application/json" \
  -d "{\"image_path\": \"samples/avatar.jpg\", \"user_text\": \"Why are you serious?\", \"emotion\": \"intense\"}"
```

---

## Supported Emotions

| Emotion | TTS Rate | TTS Pitch | Prompt Tone |
|---------|----------|-----------|-------------|
| neutral | +0% | +0Hz | calm and balanced |
| happy | +10% | +20Hz | warm and joyful |
| sad | -15% | -20Hz | gentle and melancholic |
| angry | +5% | -10Hz | direct and intense |
| confident | +0% | +0Hz | assertive and clear |
| teasing | +5% | +15Hz | playful and light |
| intense | -10% | -15Hz | serious and heavy |

> Note: Wav2Lip only controls lip-sync. Head motion and facial expressions are not supported.

---

## Output Files

| File | Description |
|------|-------------|
| `outputs/baseline_5s.mp4` | Avatar video from ~2s audio |
| `outputs/baseline_10s.mp4` | Avatar video from ~6s audio |
| `outputs/baseline_20s.mp4` | Avatar video from ~10s audio |
| `outputs/tts_audio.mp3` | TTS generated audio sample |
| `outputs/tts_avatar_output.mp4` | Avatar video from TTS audio |
| `outputs/avatar_response.mp4` | Full pipeline output video |
| `outputs/conversation_log.json` | Full conversation history (JSON) |

---

## Generation Times (GTX 1650, CUDA 11.8)

| Video | Audio Duration | Generation Time |
|-------|---------------|-----------------|
| baseline_5s.mp4 | ~2s | ~74 seconds |
| baseline_10s.mp4 | ~6s | ~94 seconds |
| baseline_20s.mp4 | ~10s | ~87 seconds |
| avatar_response.mp4 | ~4.5s | ~104 seconds |

---

## Limitations

- Wav2Lip does not support head motion or facial expression control — lip-sync only
- edge-tts requires an internet connection (not fully offline)
- Generation is not real-time — each video takes 1–2 minutes on GTX 1650
- Single static image only — no video-driven avatars
- Gemini API free tier has rate limits — rule-based fallback is used automatically

---

## Ethics

All assets used in this project are either AI-generated, self-owned, or open-license.
No celebrity likenesses, cloned voices, copyrighted dialogues, or real person identities were used.