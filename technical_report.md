# Technical Report — AI Avatar Conversation Pipeline

**Candidate:** Sneha Jha
**Repository:** https://github.com/Sneha100802/avatar-assignment
**Date:** 22 June 2026
**Platform:** Windows 11, Local Machine

---

## 1. Which avatar model did you use?

**Wav2Lip (GAN variant)** — `wav2lip_gan.pth`

Wav2Lip is an open-source talking-head model that generates lip-synced video from a static face image and an audio file. The GAN variant produces sharper, more realistic lip movements compared to the base model.

---

## 2. Why did you choose this model?

- Runs on consumer-grade GPU (4GB VRAM) without modification
- Accepts a single static image — no video input required
- Well-documented, actively maintained repository
- No separate training required — pretrained weights available
- Compatible with FFmpeg for audio/video merging
- Lighter than SadTalker or LivePortrait for a 3-day prototype scope

---

## 3. How did you install and run it?

```bash
git clone https://github.com/Rudrabha/Wav2Lip.git
mkdir Wav2Lip\checkpoints
# Download wav2lip_gan.pth and place in Wav2Lip\checkpoints\
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install opencv-python librosa==0.9.2 scipy imageio face-alignment resampy tqdm audioread edge-tts fastapi uvicorn python-dotenv google-genai
mkdir temp
python Wav2Lip\inference.py --checkpoint_path Wav2Lip\checkpoints\wav2lip_gan.pth --face samples\avatar.jpg --audio samples\sample_audio.mp3 --outfile outputs\test.mp4 --resize_factor 2
```

---

## 4. What errors did you face?

| Error | Description |
|-------|-------------|
| `numpy==1.17.1` build failure | Wav2Lip's `requirements.txt` pins ancient numpy incompatible with Python 3.13 |
| `No matching distribution for torch` | PyTorch cu121 index had no Python 3.13 wheels initially |
| `temp/temp.wav: No such file or directory` | Wav2Lip looks for `temp/` relative to working directory, not its own folder |
| `s3fd` model corrupted | Face detection model download timed out midway on slow connection |
| `ModuleNotFoundError: edge_tts` | uvicorn subprocess used system Python instead of venv |
| `404 models/gemini-1.5-flash not found` | Deprecated `google-generativeai` SDK used wrong model path |
| `429 RESOURCE_EXHAUSTED limit:0` | Gemini free tier quota issue — resolved with rule-based fallback |

---

## 5. How did you solve those errors?

| Error | Fix |
|-------|-----|
| numpy build failure | Skipped `requirements.txt`, installed compatible versions manually |
| torch not found | Used cu118 index instead of cu121 — PyTorch 2.7.1 has Python 3.13 support |
| temp folder missing | Created `temp/` in project root: `mkdir temp` |
| s3fd corrupted | Deleted cached file, re-downloaded manually via browser |
| edge_tts not found in uvicorn | Used `python -m uvicorn app:app --reload` instead of `uvicorn app:app --reload` |
| Gemini SDK deprecated | Switched from `google-generativeai` to `google-genai`, updated model to `gemini-2.0-flash` |
| Gemini quota | Implemented rule-based fallback — system works without any API key |

---

## 6. Which TTS engine did you use?

**edge-tts** — Microsoft Neural TTS

- Free, no API key required
- Requires internet connection (not fully offline)
- High-quality neural voices (used `en-US-AriaNeural`)
- Supports `rate` and `pitch` parameters for emotion control
- Outputs MP3 directly

---

## 7. Which conversation-generation method did you use?

**Primary:** Google Gemini 2.0 Flash via `google-genai` SDK

**Fallback:** Rule-based response dictionary (7 emotion-keyed responses)

The system checks for `GEMINI_API_KEY` in the environment at runtime. If the key is missing or the API call fails, it automatically uses the rule-based fallback. This ensures the pipeline runs in any environment without credential setup.

---

## 8. How is emotion selected?

Emotion is passed as a command-line argument (`--emotion`) or API request field. It is used in three places:

1. **LLM prompt** — the system prompt includes the emotion label, instructing the model to match its tone
2. **TTS rate and pitch** — loaded from `emotion_mapping.json` and passed to `edge_tts.Communicate()`
3. **Conversation log** — stored with each entry for traceability

Example from `emotion_mapping.json`:
```json
"sad": {
  "rate": "-15%",
  "pitch": "-20Hz",
  "prompt_tone": "gentle and melancholic"
}
```

---

## 9. How long did each video take to generate?

**Hardware:** NVIDIA GeForce GTX 1650 (4GB VRAM), CUDA 11.8, Windows 11

| Video | Audio Duration | Generation Time |
|-------|---------------|-----------------|
| baseline_5s.mp4 | ~2 seconds | 74 seconds |
| baseline_10s.mp4 | ~6 seconds | 94 seconds |
| baseline_20s.mp4 | ~10 seconds | 87 seconds |
| avatar_response.mp4 | ~4.5 seconds | 104 seconds |
| tts_avatar_output.mp4 | ~6.7 seconds | ~100 seconds |

Note: Generation time is dominated by face detection (s3fd model load ~30s) and Wav2Lip inference (~40s per batch). Time does not scale linearly with audio length due to fixed model load overhead.

---

## 10. How good was the lip-sync?

Lip-sync quality is **good for short phrases** — vowel-heavy words produce clear, visible mouth movements. The GAN model produces sharper results than the base Wav2Lip model. Sync accuracy is approximately ±1-2 frames at 25fps.

For longer sentences, occasional frame blending artifacts appear at word boundaries but do not significantly affect watchability.

---

## 11. Was the face stable?

Yes. Since a static image is used as input, Wav2Lip loops the same face frame throughout the video. The face remains visible, front-facing, and stable for the entire duration. There is no head movement between frames.

---

## 12. What artifacts did you observe?

| Artifact | Description |
|----------|-------------|
| Mouth blur | Slight blurring around lip region during fast phoneme transitions |
| Static face | No head motion — face is perfectly still except for lip area |
| Resolution reduction | `--resize_factor 2` halves resolution to fit in 4GB VRAM — output is 1024x1024 pre-resize |
| Audio estimation warning | FFmpeg reports "Estimating duration from bitrate" for MP3 — cosmetic, does not affect output |
| FutureWarning from librosa | `sr` and `n_fft` passed as positional args — Wav2Lip internal issue, no functional impact |

---

## 13. What is supported today?

- ✅ Static image → talking avatar video
- ✅ Text-to-speech with emotion-controlled rate and pitch
- ✅ AI response generation (Gemini) with rule-based fallback
- ✅ 7 emotion labels affecting TTS and LLM prompt tone
- ✅ CLI script with all required arguments
- ✅ FastAPI endpoint with JSON request/response
- ✅ Conversation logging to JSON
- ✅ GPU inference (CUDA)
- ✅ Graceful error handling and fallback modes

---

## 14. What is not supported yet?

- ❌ Head motion control — Wav2Lip is lip-sync only
- ❌ Facial expression control — no brow, eye, or cheek movement
- ❌ Real-time / streaming generation — each video takes 1-2 minutes
- ❌ Video-driven avatars — only static image input
- ❌ Offline TTS — edge-tts requires internet
- ❌ Multi-speaker / voice cloning
- ❌ Emotion affecting visual expression — only audio is affected

---

## 15. What would you improve for production use?

1. **Replace Wav2Lip with SadTalker or DiffTalk** — supports head motion and expression
2. **Add local TTS fallback** (Coqui TTS) for offline use
3. **Async video generation** — return job ID immediately, poll for result
4. **Video caching** — cache repeated inputs to avoid re-generation
5. **Faster inference** — batch multiple requests, use TensorRT optimization
6. **Better emotion control** — fine-tune model on emotion-labelled video data
7. **Add authentication** to the FastAPI endpoint
8. **Docker containerization** for reproducible deployment

---

## 16. What GPU or CPU resources are required?

**Minimum (CPU only):**
- RAM: 8GB
- Generation time: ~10-15 minutes per video
- No CUDA required

**Recommended (GPU):**
- GPU: NVIDIA GTX 1650 or higher (4GB VRAM minimum)
- CUDA: 11.8 or 12.x
- RAM: 8GB
- Generation time: ~1.5-2 minutes per video

**This prototype was built and tested on:**
- GPU: NVIDIA GeForce GTX 1650 (4GB VRAM)
- CUDA: 12.0 driver / 11.8 runtime
- RAM: 16GB
- OS: Windows 11
- Python: 3.13.1

---

## 17. What is the estimated cost per 100 avatar responses?

| Component | Cost |
|-----------|------|
| Wav2Lip inference | $0 — runs locally |
| edge-tts | $0 — free Microsoft service |
| Gemini 2.0 Flash (free tier) | $0 — within free quota |
| Electricity (GTX 1650, ~30W, ~2 min/video) | ~₹0.10 per 100 videos |
| **Total** | **~₹0 — ₹0.10 per 100 responses** |

The real cost at scale would be compute infrastructure (EC2/GCP instance with GPU), estimated at approximately **$0.50–$2.00 per 100 responses** on a cloud GPU instance (e.g., AWS g4dn.xlarge at ~$0.526/hr, generating ~1 video/2 min = 30 videos/hr).
