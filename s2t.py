import os
import shutil
from faster_whisper import WhisperModel

try:
    model = WhisperModel("base", device="cpu", compute_type="int8")
except Exception as e:
    print("Error loading Faster-Whisper model:", e)

def get_next_filename(folder="./audio_files", prefix="temp", ext="wav"):
    os.makedirs(folder, exist_ok=True)
    i = 1
    while os.path.exists(os.path.join(folder, f"{prefix}{i}.{ext}")):
        i += 1
    return os.path.join(folder, f"{prefix}{i}.{ext}")

def listen_to_user_whisper(audio_path: str) -> str:
    try:
        # Transcribe directly from the file path
        segments, info = model.transcribe(audio_path)
        text = "".join([segment.text for segment in segments]).strip()

        # Save a copy for history/debugging
        new_filename = get_next_filename(folder="audio_files")
        shutil.copy(audio_path, new_filename)

        return text

    except Exception as e:
        print("Error during transcription:", e)
        return ""
