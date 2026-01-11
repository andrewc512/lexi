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
from typing import List, Optional
import json
import asyncio
from io import BytesIO
import time

from app.services import stt, llm, tts
from app.services.reading_assessment import reading_manager
from app.services.supabase import get_interview_by_id, update_interview_status, update_interview_evaluation
from app.core.config import settings

router = APIRouter()

# Store active connections and their conversation state
active_connections: dict[str, WebSocket] = {}
conversation_states: dict[str, dict] = {}


async def _save_partial_evaluation(
    interview_id: str,
    speaking_evaluations: list,
    reading_evaluations: list,
    reading_manager,
    feedback_msg: str
):
    """Save evaluation data from whatever exercises were completed."""
    if not speaking_evaluations and not reading_evaluations:
        print(f"No evaluations to save for interview {interview_id}")
        return
    
    # Calculate speaking scores
    grammar_scores = []
    fluency_scores = []
    
    for eval in speaking_evaluations:
        if eval.get("grammar_score") is not None:
            grammar_scores.append(eval["grammar_score"])
        if eval.get("fluency_score") is not None:
            fluency_scores.append(eval["fluency_score"])
    
    # Calculate reading proficiency if available
    reading_proficiency = {}
    if reading_evaluations:
        reading_proficiency = reading_manager.calculate_reading_proficiency(reading_evaluations)
        print(f"📊 Final Reading Proficiency: {reading_proficiency}")
    
    # Combine scores
    avg_grammar = sum(grammar_scores) / len(grammar_scores) if grammar_scores else None
    avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else None
    
    # Use reading scores if available, otherwise use speaking scores
    final_grammar = reading_proficiency.get("grammar_score") or avg_grammar
    final_fluency = reading_proficiency.get("fluency_score") or avg_fluency
    
    # Calculate overall score (average of grammar and fluency, scaled to 100)
    scores = [s for s in [final_grammar, final_fluency] if s is not None]
    overall_score = (sum(scores) / len(scores)) * 10 if scores else 0  # Scale from 0-10 to 0-100
    
    evaluation_data = {
        "overall_score": round(overall_score, 1),
        "grammar_score": round(final_grammar, 1) if final_grammar else None,
        "fluency_score": round(final_fluency, 1) if final_fluency else None,
        "proficiency_level": reading_proficiency.get("proficiency_level"),
        "reading_level": reading_proficiency.get("reading_level"),
        "feedback": feedback_msg,
        "speaking_exercises": len(speaking_evaluations),
        "reading_exercises": len(reading_evaluations),
        "total_exercises": len(speaking_evaluations) + len(reading_evaluations),
        "completed": False
    }
    
    await update_interview_evaluation(interview_id, evaluation_data)
    print(f"📊 Saved partial evaluation for interview {interview_id}")


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

    # Fetch interview details from Supabase to get the language
    interview_data = await get_interview_by_id(interview_id)
    
    if interview_data:
        target_language = interview_data.get("language_name", settings.DEFAULT_TARGET_LANGUAGE)
        candidate_name = interview_data.get("name", "there")
        print(f"📋 Interview loaded: {candidate_name}, Language: {target_language}")
        
        # Update interview status to in_progress
        await update_interview_status(interview_id, "in_progress")
    else:
        # Fallback to default if interview not found
        target_language = settings.DEFAULT_TARGET_LANGUAGE
        candidate_name = "there"
        print(f"⚠️ Interview {interview_id} not found in database, using default language: {target_language}")

    # Initialize conversation state for this interview
    conversation_history: List[dict] = []
    expecting_audio = False

    # Reading assessment state
    interview_start_time = time.time()
    in_reading_phase = False
    reading_start_time: Optional[float] = None
    current_reading_passage: Optional[str] = None
    reading_evaluations: List[dict] = []
    speaking_evaluations: List[dict] = []  # Track speaking evaluations
    reading_difficulty = 3  # Start at moderate difficulty

    try:
        # Send initial AI greeting
        greeting = f"Hello {candidate_name}! Thank you for joining. Let's begin the {target_language} language assessment. Tell me a bit about yourself and your background."

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
                        target_language=target_language
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
                        transcript = await stt.transcribe_audio(audio_data, language=target_language)

                        if transcript and transcript.strip():
                            print(f"📝 User said: {transcript}")
                            
                            # Evaluate the user's speech
                            print(f"📊 Evaluating speech...")
                            evaluation = await llm.evaluate_speaking_exercise(
                                transcript=transcript,
                                target_language=target_language,
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
                            
                            # Track speaking evaluation
                            speaking_evaluations.append(evaluation)
                            
                            # Send user transcript to frontend
                            await websocket.send_json({
                                "type": "transcript",
                                "speaker": "user",
                                "text": transcript
                            })

                            # Add to conversation history
                            conversation_history.append({"role": "user", "content": transcript})

                            # Check if it's time to transition to reading phase
                            if not in_reading_phase and reading_manager.should_transition_to_reading(
                                interview_start_time
                            ):
                                print(f"⏰ 1 minute elapsed - transitioning to reading phase")
                                in_reading_phase = True
                                reading_start_time = time.time()

                                # Send transition message
                                transition_msg = reading_manager.get_transition_message(target_language)
                                conversation_history.append({"role": "assistant", "content": transition_msg})

                                # Generate TTS for transition
                                audio_data = await tts.text_to_speech(transition_msg)

                                await websocket.send_json({
                                    "type": "phase_transition",
                                    "speaker": "ai",
                                    "text": transition_msg,
                                    "audio": audio_data,
                                    "new_phase": "reading"
                                })

                                # Generate first reading passage
                                passage_data = await reading_manager.generate_reading_passage(
                                    target_language=target_language,
                                    difficulty_level=reading_difficulty
                                )

                                current_reading_passage = passage_data["passage"]

                                # Send reading passage to frontend
                                await websocket.send_json({
                                    "type": "reading_passage",
                                    "passage": current_reading_passage,
                                    "language": target_language,
                                    "difficulty": reading_difficulty,
                                    "instruction": "Please read this text and translate it to English."
                                })

                            elif in_reading_phase:
                                # Process reading translation
                                print(f"📖 Processing reading translation...")

                                if current_reading_passage:
                                    evaluation = await reading_manager.evaluate_reading_translation(
                                        original_passage=current_reading_passage,
                                        user_translation=transcript,
                                        target_language=target_language,
                                        difficulty_level=reading_difficulty
                                    )

                                    reading_evaluations.append(evaluation)

                                    # Check if reading phase should end
                                    if reading_start_time and reading_manager.should_end_reading(reading_start_time):
                                        print(f"⏰ Reading phase complete (1:30 elapsed)")

                                        # Calculate final reading proficiency
                                        reading_proficiency = reading_manager.calculate_reading_proficiency(
                                            reading_evaluations
                                        )

                                        # Save evaluation to Supabase
                                        evaluation_data = {
                                            "overall_score": reading_proficiency.get("overall_score", 0),
                                            "grammar_score": reading_proficiency.get("grammar_score"),
                                            "fluency_score": reading_proficiency.get("fluency_score"),
                                            "proficiency_level": reading_proficiency.get("proficiency_level"),
                                            "reading_level": reading_proficiency.get("reading_level"),
                                            "feedback": reading_proficiency.get("feedback", "Assessment completed successfully."),
                                            "total_exercises": len(reading_evaluations)
                                        }
                                        await update_interview_evaluation(interview_id, evaluation_data)

                                        # Send completion message
                                        completion_msg = (
                                            f"Great work! You've completed the assessment. "
                                            f"Your reading level is {reading_proficiency['reading_level']}. "
                                            f"Thank you for participating!"
                                        )

                                        audio_data = await tts.text_to_speech(completion_msg)

                                        await websocket.send_json({
                                            "type": "assessment_complete",
                                            "speaker": "ai",
                                            "text": completion_msg,
                                            "audio": audio_data,
                                            "reading_proficiency": reading_proficiency,
                                            "total_evaluations": len(reading_evaluations)
                                        })

                                        # Wait a moment for the message to be sent
                                        await asyncio.sleep(0.5)

                                        # Clean up and close the connection
                                        if interview_id in active_connections:
                                            del active_connections[interview_id]

                                        print(f"✅ Interview {interview_id} completed successfully")

                                        # Close the WebSocket connection
                                        await websocket.close()
                                        return

                                    # Send evaluation feedback
                                    feedback_msg = (
                                        f"Great job! Your translation scored "
                                        f"{evaluation['accuracy_score']:.0f}% for accuracy. "
                                        f"{evaluation.get('feedback', '')}"
                                    )

                                    audio_data = await tts.text_to_speech(feedback_msg)

                                    await websocket.send_json({
                                        "type": "reading_evaluation",
                                        "speaker": "ai",
                                        "text": feedback_msg,
                                        "audio": audio_data,
                                        "evaluation": evaluation
                                    })

                                    # Generate next reading passage
                                    # Adjust difficulty based on performance
                                    if evaluation['accuracy_score'] > 85:
                                        reading_difficulty = min(10, reading_difficulty + 1)
                                    elif evaluation['accuracy_score'] < 60:
                                        reading_difficulty = max(1, reading_difficulty - 1)

                                    passage_data = await reading_manager.generate_reading_passage(
                                        target_language=target_language,
                                        difficulty_level=reading_difficulty,
                                        previous_passages=[current_reading_passage]
                                    )

                                    current_reading_passage = passage_data["passage"]

                                    await websocket.send_json({
                                        "type": "reading_passage",
                                        "passage": current_reading_passage,
                                        "language": target_language,
                                        "difficulty": reading_difficulty,
                                        "instruction": "Here's the next passage. Please translate it to English."
                                    })

                            else:
                                # Normal conversation phase
                                # Generate AI response using LLM
                                print(f"🤖 Generating AI response...")
                                ai_response = await llm.generate_interview_response(
                                    conversation_history=conversation_history,
                                    target_language=target_language
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

        # Save evaluation data if any exercises were completed
        await _save_partial_evaluation(
            interview_id, speaking_evaluations, reading_evaluations, 
            reading_manager, "Interview disconnected."
        )

        print(f"Interview {interview_id} disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
        if interview_id in active_connections:
            del active_connections[interview_id]
        
        # Save evaluation data even on error
        await _save_partial_evaluation(
            interview_id, speaking_evaluations, reading_evaluations,
            reading_manager, f"Interview ended with error: {str(e)}"
        )


@router.get("/ws/test")
async def websocket_test():
    """Test endpoint to verify WebSocket route is registered."""
    return {"status": "WebSocket endpoint available at /ws/interview/{interview_id}"}


@router.post("/ws/interview/{interview_id}/force-reading")
async def force_reading_phase(interview_id: str):
    """
    Force transition to reading phase (for testing).

    This endpoint allows manual triggering of the reading phase
    without waiting for the 3-minute timer.
    """
    if interview_id not in active_connections:
        return {"error": "Interview not found or not connected"}

    websocket = active_connections[interview_id]

    # Get interview language from database
    interview_data = await get_interview_by_id(interview_id)
    target_language = interview_data.get("language_name", settings.DEFAULT_TARGET_LANGUAGE) if interview_data else settings.DEFAULT_TARGET_LANGUAGE

    try:
        # Send transition message
        transition_msg = reading_manager.get_transition_message(target_language)
        audio_data = await tts.text_to_speech(transition_msg)

        await websocket.send_json({
            "type": "phase_transition",
            "speaker": "ai",
            "text": transition_msg,
            "audio": audio_data,
            "new_phase": "reading"
        })

        # Generate first reading passage
        passage_data = await reading_manager.generate_reading_passage(
            target_language=target_language,
            difficulty_level=3
        )

        await websocket.send_json({
            "type": "reading_passage",
            "passage": passage_data["passage"],
            "language": target_language,
            "difficulty": 3,
            "instruction": "Please read this text and translate it to English."
        })

        return {"status": "Reading phase initiated", "interview_id": interview_id, "language": target_language}

    except Exception as e:
        print(f"Error forcing reading phase: {e}")
        return {"error": str(e)}
