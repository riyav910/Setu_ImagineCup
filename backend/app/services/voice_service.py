import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = None
api_key = os.getenv("GROQ_API_KEY")

if api_key:
    client = Groq(api_key=api_key)

def transcribe_audio(audio_file):
    """
    Takes an audio file (bytes) and uses Groq (Whisper) to:
    1. Transcribe it (speech -> text)
    2. Translate it (Hindi/etc -> English)
    """
    if not client:
        print("⚠️ Groq API Key missing for Voice.")
        return None

    try:
        # Groq requires a filename with extension to know the format
        # We can pass a tuple (filename, file_bytes)
        transcription = client.audio.translations.create(
            file=("input.wav", audio_file), # Force generic filename
            model="whisper-large-v3", # The smartest model
            response_format="json",
            temperature=0.0
        )
        return transcription.text
    except Exception as e:
        print(f"❌ Voice Error: {e}")
        return None