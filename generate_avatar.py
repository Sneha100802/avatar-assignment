import argparse
import os
import sys
import time

from conversation_engine import generate_response, log_conversation
from tts_module import text_to_speech


def run_wav2lip(image_path: str, audio_path: str, output_path: str):
    checkpoint = "Wav2Lip/checkpoints/wav2lip_gan.pth"
    cmd = (
        f'python Wav2Lip/inference.py '
        f'--checkpoint_path "{checkpoint}" '
        f'--face "{image_path}" '
        f'--audio "{audio_path}" '
        f'--outfile "{output_path}" '
        f'--resize_factor 2'
    )
    print(f"[WAV2LIP] Running inference...")
    ret = os.system(cmd)
    if ret != 0:
        raise RuntimeError("Wav2Lip inference failed. Check image/audio paths and checkpoint.")


def main():
    parser = argparse.ArgumentParser(description="AI Avatar Conversation Pipeline")
    parser.add_argument("--image",     required=True,  help="Path to avatar image")
    parser.add_argument("--user-text", required=True,  help="User message")
    parser.add_argument("--emotion",   required=True,
                        choices=["neutral","happy","sad","angry","confident","teasing","intense"],
                        help="Emotion label")
    parser.add_argument("--output",    required=True,  help="Output video path")
    parser.add_argument("--voice",     default="en-US-AriaNeural", help="TTS voice")
    parser.add_argument("--debug",     action="store_true", help="Print extra info")
    args = parser.parse_args()

    # Validate inputs
    if not os.path.exists(args.image):
        print(f"[ERROR] Image not found: {args.image}")
        sys.exit(1)

    os.makedirs("outputs", exist_ok=True)

    print(f"\n{'='*50}")
    print(f"User: {args.user_text}")
    print(f"Emotion: {args.emotion}")
    print(f"{'='*50}\n")

    start = time.time()

    # Step 1 - Generate AI response
    print("[STEP 1] Generating AI response...")
    response_text = generate_response(args.user_text, args.emotion)
    print(f"Avatar: {response_text}\n")

    # Step 2 - Text to Speech
    print("[STEP 2] Converting response to speech...")
    audio_path = "outputs/response_audio.mp3"
    text_to_speech(response_text, audio_path, emotion=args.emotion, voice=args.voice)

    # Step 3 - Generate avatar video
    print("\n[STEP 3] Generating talking avatar video...")
    run_wav2lip(args.image, audio_path, args.output)

    # Step 4 - Log conversation
    elapsed = round(time.time() - start, 2)
    log_conversation(args.user_text, response_text, args.emotion, audio_path, args.output, elapsed)

    print(f"\n{'='*50}")
    print(f"Done in {elapsed} seconds")
    print(f"Output video: {args.output}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()