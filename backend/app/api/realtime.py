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

from app.services import stt, llm, tts

router = APIRouter()

# Store active connections and their conversation state
active_connections: dict[str, WebSocket] = {}
conversation_states: dict[str, dict] = {}


@router.websocket("/ws/interview/{interview_id}")
async def interview_websocket(websocket: WebSocket, interview_id: str):
    """
    Main WebSocket endpoint for real-time interview.

    Frontend sends:
      - JSON message: {"type": "audio_complete"} - signals audio recording is complete
      - Binary data: audio blob (after audio_complete message)
    Backend sends:
      - transcripts (JSON): {"type": "transcript", "speaker": "user", "text": "..."}
      - AI transcript (JSON): {"type": "transcript", "speaker": "ai", "text": "..."}
    """
    await websocket.accept()
    active_connections[interview_id] = websocket
    print(f"✅ WebSocket connected for interview: {interview_id}")

    # Initialize conversation state for this interview
    conversation_history: List[dict] = []
    expecting_audio = False

    try:
        # Send initial AI greeting
        greeting = "Hello! Thank you for joining. Let's begin the interview. Tell me a bit about yourself and your background."

        # Generate TTS audio for greeting
        print(f"🔊 Generating TTS audio for greeting...")
        audio_data = await tts.text_to_speech(greeting)

        await websocket.send_json({
            "type": "transcript",
            "speaker": "ai",
            "text": greeting,
            "audio": audio_data  # base64-encoded MP3
        })
        print(f"📤 Sent greeting to {interview_id}")

        conversation_history.append({"role": "assistant", "content": greeting})

        while True:
            # Receive data from frontend
            data = await websocket.receive()

            if "text" in data:
                # JSON message received
                message = json.loads(data["text"])

                if message.get("type") == "audio_complete":
                    # Frontend is about to send audio blob
                    print("📥 Audio recording complete, expecting audio blob next...")
                    expecting_audio = True

                elif message.get("type") == "user_transcript":
                    # Manual transcript input (for testing without STT)
                    user_text = message.get("text", "")
                    conversation_history.append({"role": "user", "content": user_text})

                    # Generate AI response
                    ai_response = await llm.generate_interview_response(
                        conversation_history=conversation_history,
                        target_language="Spanish"
                    )

                    conversation_history.append({"role": "assistant", "content": ai_response})

                    # Generate TTS audio for response
                    print(f"🔊 Generating TTS audio for AI response...")
                    audio_data = await tts.text_to_speech(ai_response)

                    # Send AI transcript with audio
                    await websocket.send_json({
                        "type": "transcript",
                        "speaker": "ai",
                        "text": ai_response,
                        "audio": audio_data
                    })

            elif "bytes" in data:
                # Audio blob received
                if expecting_audio:
                    audio_data = data["bytes"]
                    print(f"🎤 Received audio blob: {len(audio_data)} bytes")

                    try:
                        # Transcribe the audio
                        print(f"🎤 Transcribing audio...")
                        transcript = await stt.transcribe_audio(audio_data, language="Spanish")

                        if transcript and transcript.strip():
                            print(f"📝 User said: {transcript}")
                            
                            # Evaluate the user's Spanish speech
                            print(f"📊 Evaluating speech...")
                            evaluation = await llm.evaluate_speaking_exercise(
                                transcript=transcript,
                                target_language="Spanish",
                                difficulty_level=3
                            )
                            print(f"")
                            print(f"{'='*50}")
                            print(f"📊 EVALUATION RESULTS")
                            print(f"{'='*50}")
                            print(f"Grammar Score: {evaluation['grammar_score']}")
                            print(f"Fluency Score: {evaluation['fluency_score']}")
                            print(f"Feedback: {evaluation['feedback']}")
                            print(f"Errors: {evaluation['errors']}")
                            print(f"Strengths: {evaluation['strengths']}")
                            print(f"{'='*50}")
                            print(f"")
                            
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
                                conversation_history=conversation_history,
                                target_language="Spanish"
                            )

                            conversation_history.append({"role": "assistant", "content": ai_response})

                            print(f"💬 AI response: {ai_response}")

                            # Generate TTS audio for response
                            print(f"🔊 Generating TTS audio for AI response...")
                            audio_data = await tts.text_to_speech(ai_response)

                            # Send AI response with audio to frontend
                            await websocket.send_json({
                                "type": "transcript",
                                "speaker": "ai",
                                "text": ai_response,
                                "audio": audio_data
                            })
                        else:
                            print(f"⚠️ Empty transcript received")
                            await websocket.send_json({
                                "type": "error",
                                "message": "Could not transcribe audio. Please try again."
                            })

                    except Exception as e:
                        print(f"❌ Error processing audio: {e}")
                        import traceback
                        traceback.print_exc()
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to process audio"
                        })

                    expecting_audio = False
                else:
                    print("⚠️ Received unexpected audio data (no audio_complete signal)")

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
