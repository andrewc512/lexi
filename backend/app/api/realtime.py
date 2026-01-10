"""
WebSocket endpoint for real-time interview conversation.

Flow:
1. Frontend connects via WebSocket
2. Frontend streams audio chunks (500ms intervals)
3. Backend accumulates audio and transcribes via STT
4. Backend detects end of speech (voice activity detection)
5. Backend sends full transcript to LLM for response
6. Backend converts response to audio via TTS (optional for now)
7. Backend sends response back to frontend
8. Repeat
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from io import BytesIO

from app.services import stt, llm

router = APIRouter()

# Store active connections and their conversation state
active_connections: dict[str, WebSocket] = {}
conversation_states: dict[str, dict] = {}


@router.websocket("/ws/interview/{interview_id}")
async def interview_websocket(websocket: WebSocket, interview_id: str):
    """
    Main WebSocket endpoint for real-time interview.

    Frontend sends: audio chunks (binary)
    Backend sends:
      - transcripts (JSON): {"type": "transcript", "speaker": "user", "text": "..."}
      - AI transcript (JSON): {"type": "transcript", "speaker": "ai", "text": "..."}
    """
    await websocket.accept()
    active_connections[interview_id] = websocket
    print(f"✅ WebSocket connected for interview: {interview_id}")

    # Initialize conversation state for this interview
    conversation_history: List[dict] = []
    audio_buffer = BytesIO()
    silence_counter = 0
    is_speaking = False
    SILENCE_THRESHOLD = 4  # Number of silent chunks before processing (4 * 500ms = 2 seconds)

    try:
        # Send initial AI greeting
        greeting = "Hello! Thank you for joining. Let's begin the interview. Tell me a bit about yourself and your background."
        await websocket.send_json({
            "type": "transcript",
            "speaker": "ai",
            "text": greeting
        })
        print(f"📤 Sent greeting to {interview_id}")

        conversation_history.append({"role": "assistant", "content": greeting})

        while True:
            # Receive data from frontend
            data = await websocket.receive()

            if "bytes" in data:
                # Audio chunk received
                audio_chunk = data["bytes"]

                # Always accumulate audio when user is speaking or just started
                # Simple VAD: Check if audio chunk has meaningful data
                # WebM chunks typically have size variance - small chunks = silence
                is_voice_detected = len(audio_chunk) > 1000  # More realistic threshold for 500ms WebM chunks

                if is_voice_detected:
                    # User is speaking
                    is_speaking = True
                    silence_counter = 0
                    audio_buffer.write(audio_chunk)
                    print(f"Voice detected, buffer size: {len(audio_buffer.getvalue())} bytes")
                else:
                    # Potential silence detected
                    if is_speaking:
                        # Still accumulate the chunk in case it's just a brief pause
                        audio_buffer.write(audio_chunk)
                        silence_counter += 1
                        print(f"Silence counter: {silence_counter}/{SILENCE_THRESHOLD}")

                        # Check if user stopped speaking
                        if silence_counter >= SILENCE_THRESHOLD:
                            # Process accumulated audio
                            audio_data = audio_buffer.getvalue()

                            if len(audio_data) > 0:
                                # Transcribe the audio
                                try:
                                    print(f"🎤 Transcribing {len(audio_data)} bytes of audio...")
                                    transcript = await stt.transcribe_audio(audio_data)

                                    if transcript and transcript.strip():
                                        print(f"📝 User said: {transcript}")
                                        # Send user transcript to frontend
                                        await websocket.send_json({
                                            "type": "transcript",
                                            "speaker": "user",
                                            "text": transcript
                                        })

                                        # Add to conversation history
                                        conversation_history.append({"role": "user", "content": transcript})

                                        # Generate AI response using LLM
                                        print(f"🤖 Generating AI response...")
                                        ai_response = await llm.generate_interview_response(
                                            conversation_history=conversation_history
                                        )

                                        conversation_history.append({"role": "assistant", "content": ai_response})

                                        print(f"💬 AI response: {ai_response}")
                                        # Send AI response to frontend
                                        await websocket.send_json({
                                            "type": "transcript",
                                            "speaker": "ai",
                                            "text": ai_response
                                        })
                                    else:
                                        print(f"⚠️ Empty transcript received")

                                except Exception as e:
                                    print(f"❌ Error processing audio: {e}")
                                    import traceback
                                    traceback.print_exc()
                                    await websocket.send_json({
                                        "type": "error",
                                        "message": "Failed to process audio"
                                    })

                            # Reset buffer and state
                            audio_buffer = BytesIO()
                            is_speaking = False
                            silence_counter = 0

            elif "text" in data:
                # Text message (for testing/debugging)
                message = json.loads(data["text"])

                if message.get("type") == "user_transcript":
                    # Manual transcript input (for testing without STT)
                    user_text = message.get("text", "")
                    conversation_history.append({"role": "user", "content": user_text})

                    # Generate AI response
                    ai_response = await llm.generate_interview_response(
                        conversation_history=conversation_history
                    )

                    conversation_history.append({"role": "assistant", "content": ai_response})

                    # Send AI transcript
                    await websocket.send_json({
                        "type": "transcript",
                        "speaker": "ai",
                        "text": ai_response
                    })

    except WebSocketDisconnect:
        if interview_id in active_connections:
            del active_connections[interview_id]
        # TODO: Save conversation to database
        print(f"Interview {interview_id} disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
        if interview_id in active_connections:
            del active_connections[interview_id]


@router.get("/ws/test")
async def websocket_test():
    """Test endpoint to verify WebSocket route is registered."""
    return {"status": "WebSocket endpoint available at /ws/interview/{interview_id}"}
