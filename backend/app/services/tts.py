"""
Text-to-Speech service for generating interviewer audio responses.

Converts text responses to natural-sounding speech for the interviewer agent.
"""

from typing import Optional


async def text_to_speech(text: str, voice: str = "alloy") -> Optional[str]:
    """
    Convert text to speech audio.

    Args:
        text: The interviewer's text response
        voice: Voice to use (for OpenAI TTS: alloy, echo, fable, onyx, nova, shimmer)

    Returns:
        URL to the generated audio file, or None if TTS is disabled/failed

    TODO: Implement with OpenAI TTS API or ElevenLabs

    Example (OpenAI):
        from openai import AsyncOpenAI
        client = AsyncOpenAI()

        response = await client.audio.speech.create(
            model="tts-1",  # or "tts-1-hd" for higher quality
            voice=voice,
            input=text
        )

        # Save to file storage (S3, Supabase Storage, etc.)
        audio_bytes = response.content
        audio_url = await storage.upload_audio(audio_bytes, "interview_audio")
        return audio_url
    """

    # STUB: For MVP, you can skip TTS and just use text
    # Return None to indicate no audio generated
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
