"""
Text-to-Speech service for generating interviewer audio responses.

Converts text responses to natural-sounding speech for the interviewer agent.
"""

from typing import Optional
import base64
from openai import AsyncOpenAI
from app.core.config import settings

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def text_to_speech(text: str, voice: str = "alloy") -> Optional[str]:
    """
    Convert text to speech audio.

    Args:
        text: The interviewer's text response
        voice: Voice to use (for OpenAI TTS: alloy, echo, fable, onyx, nova, shimmer)

    Returns:
        Base64-encoded audio data (MP3 format), or None if TTS failed

    Note: Returns base64-encoded audio for WebSocket transmission.
    Frontend can decode and play using: new Audio(`data:audio/mp3;base64,${audioData}`)
    """
    try:
        # Generate speech using OpenAI TTS
        response = await client.audio.speech.create(
            model="tts-1",  # Fast, lower latency
            voice=voice,
            input=text,
            response_format="mp3"
        )

        # Get audio bytes
        audio_bytes = response.content

        # Encode as base64 for WebSocket transmission
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        return audio_base64

    except Exception as e:
        print(f"Error generating TTS audio: {e}")
        return None


async def text_to_speech_streaming(text: str, voice: str = "alloy"):
    """
    Stream text-to-speech audio for real-time playback.

    Useful for WebSocket implementations where you want to stream audio
    to the client as it's generated.

    TODO: Implement streaming TTS for WebSocket support
    """
    # STUB: Not implemented yet
    pass
