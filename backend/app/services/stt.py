"""Speech-to-text service."""

from typing import BinaryIO


async def transcribe_audio(audio_file: BinaryIO) -> str:
    """
    Transcribe audio to text.
    
    TODO: Implement actual STT using:
    - OpenAI Whisper API
    - Google Cloud Speech-to-Text
    - AssemblyAI
    """
    # Stub response
    return "This is a placeholder transcription of the audio response."


async def transcribe_audio_streaming(audio_stream: BinaryIO) -> str:
    """
    Transcribe audio in real-time streaming mode.
    
    TODO: Implement streaming transcription
    """
    return await transcribe_audio(audio_stream)
