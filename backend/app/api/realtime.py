"""
WebSocket endpoint for real-time interview conversation.

This is the main file your backend friend needs to implement.

Flow:
1. Frontend connects via WebSocket
2. Frontend streams audio chunks (1 second intervals)
3. Backend transcribes audio via STT (Deepgram recommended)
4. Backend detects end of speech
5. Backend sends transcript to LLM for response
6. Backend converts response to audio via TTS
7. Backend streams audio back to frontend
8. Repeat
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json

router = APIRouter()

# Store active connections
active_connections: dict[str, WebSocket] = {}


@router.websocket("/ws/interview/{interview_id}")
async def interview_websocket(websocket: WebSocket, interview_id: str):
    """
    Main WebSocket endpoint for real-time interview.
    
    Frontend sends: audio chunks (binary)
    Backend sends: 
      - transcripts (JSON): {"type": "transcript", "speaker": "user", "text": "..."}
      - AI audio (binary)
      - AI transcript (JSON): {"type": "transcript", "speaker": "ai", "text": "..."}
    """
    await websocket.accept()
    active_connections[interview_id] = websocket
    
    # TODO: Initialize conversation context for this interview
    conversation_history: List[dict] = []
    
    try:
        # Send initial AI greeting
        greeting = "Hello! Thank you for joining. Let's begin the interview. Tell me a bit about yourself and your background."
        await websocket.send_json({
            "type": "transcript",
            "speaker": "ai", 
            "text": greeting
        })
        
        # TODO: Convert greeting to audio and send
        # audio_greeting = await tts_service.synthesize(greeting)
        # await websocket.send_bytes(audio_greeting)
        
        conversation_history.append({"role": "assistant", "content": greeting})
        
        while True:
            # Receive data from frontend
            data = await websocket.receive()
            
            if "bytes" in data:
                # Audio chunk received
                audio_chunk = data["bytes"]
                
                # TODO: Stream to STT service
                # transcript = await stt_service.transcribe_chunk(audio_chunk)
                
                # TODO: Implement voice activity detection (VAD)
                # When user stops speaking:
                #   1. Get full transcript
                #   2. Send to LLM
                #   3. Get response
                #   4. Convert to audio
                #   5. Stream back
                
                # Stub: Echo back that we received audio
                await websocket.send_json({
                    "type": "status",
                    "message": f"Received {len(audio_chunk)} bytes"
                })
                
            elif "text" in data:
                # Text message (for testing/debugging)
                message = json.loads(data["text"])
                
                if message.get("type") == "user_transcript":
                    # Manual transcript input (for testing without STT)
                    user_text = message.get("text", "")
                    conversation_history.append({"role": "user", "content": user_text})
                    
                    # TODO: Get AI response from LLM
                    # ai_response = await llm_service.generate_response(conversation_history)
                    ai_response = "That's interesting. Can you tell me more about that experience?"
                    
                    conversation_history.append({"role": "assistant", "content": ai_response})
                    
                    # Send AI transcript
                    await websocket.send_json({
                        "type": "transcript",
                        "speaker": "ai",
                        "text": ai_response
                    })
                    
                    # TODO: Convert to audio and send
                    # audio_response = await tts_service.synthesize(ai_response)
                    # await websocket.send_bytes(audio_response)
                    
    except WebSocketDisconnect:
        del active_connections[interview_id]
        # TODO: Save conversation to database
        print(f"Interview {interview_id} disconnected")


@router.get("/ws/test")
async def websocket_test():
    """Test endpoint to verify WebSocket route is registered."""
    return {"status": "WebSocket endpoint available at /ws/interview/{interview_id}"}
