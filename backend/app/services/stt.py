"""
Speech-to-text service with multi-language support.

Supports transcription for language assessment exercises.
"""

from typing import Optional
from openai import AsyncOpenAI
import io
from app.core.config import settings

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Language code mapping for STT services
LANGUAGE_CODES = {
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "English": "en",
    "Arabic": "ar",
    "Russian": "ru",
    "Hindi": "hi"
}


async def transcribe_audio(
    audio_bytes: bytes,
    language: str = "English"
) -> str:
    """
    Transcribe audio to text with language-specific models.

    Args:
        audio_bytes: Raw audio data
        language: Target language for transcription (e.g., "Spanish", "French")

    Returns:
        Transcribed text
    """
    try:
        # Get language code
        language_code = LANGUAGE_CODES.get(language, "en")

        # Create file-like object
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.webm"  # Whisper accepts webm format

        # Transcribe using OpenAI Whisper
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language_code,
            response_format="text"
        )

        return response.strip() if response else ""

    except Exception as e:
        print(f"Error transcribing audio: {e}")
        # Fallback to empty string on error
        return ""


async def transcribe_audio_streaming(
    audio_stream: bytes,
    language: str = "English"
) -> str:
    """
    Transcribe audio in real-time streaming mode.

    Useful for WebSocket implementations where audio chunks
    are streamed continuously.

    TODO: Implement streaming transcription with Deepgram or AssemblyAI
    """
    # For now, just use regular transcription
    return await transcribe_audio(audio_stream, language)


async def detect_language(audio_bytes: bytes) -> str:
    """
    Detect the language being spoken in the audio.

    Returns language name (e.g., "Spanish", "French")
    """
    try:
        # Create file-like object
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.webm"

        # Transcribe with verbose output to get language detection
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json"
        )

        # response.language contains detected language code
        detected_code = response.language

        # Map back to language name
        for lang_name, code in LANGUAGE_CODES.items():
            if code == detected_code:
                return lang_name

        return "English"

    except Exception as e:
        print(f"Error detecting language: {e}")
        # Default to English on error
        return "English"
