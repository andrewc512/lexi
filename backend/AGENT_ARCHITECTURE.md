# Agentic Interview System - Architecture Guide

## Overview

Your backend now has a **stateless agentic interviewer** that can orchestrate natural interview conversations. The agent takes audio input, decides what to do next, and generates natural responses.

---

## Files Created

### 1. **`models/session.py`** - Session State Models
Defines the data structures for tracking interview sessions.

**Key Models:**

- **`ConversationTurn`** - Single Q&A exchange
  ```python
  {
    "role": "interviewer" | "candidate",
    "content": "What the person said",
    "audio_url": "https://...",
    "timestamp": "2024-01-15T10:00:00Z"
  }
  ```

- **`SessionState`** - Complete interview state (stored in DB)
  ```python
  {
    "interview_id": "int_123",
    "current_phase": "technical" | "behavioral" | "intro" | "closing",
    "conversation_history": [ConversationTurn, ...],
    "topics_covered": ["leadership", "problem-solving"],
    "insights": ["Candidate shows strong analytical skills"],
    "questions_asked": 5,
    "started_at": "...",
    "last_updated": "..."
  }
  ```

- **`AgentAction`** - Decision made by agent
  ```python
  {
    "action_type": "ask_followup" | "new_question" | "clarify" | "conclude",
    "reasoning": "Response was brief - probe deeper",
    "next_phase": "technical"  # or None
  }
  ```

- **`AgentResponse`** - What agent returns
  ```python
  {
    "text": "Can you tell me more about that?",
    "audio_url": "https://...",  # TTS audio (optional)
    "action": AgentAction,
    "should_continue": true
  }
  ```

---

### 2. **`services/agent.py`** - Core Interviewer Agent (STATELESS)

The brain of the operation. Orchestrates the interview loop.

**Main Function:**
```python
async def process_turn(audio_bytes, session_state) -> (response, new_state)
```

**Flow:**
1. **Transcribe** audio → text (uses `stt.py`)
2. **Analyze** response + conversation history
3. **Decide** next action (probe deeper? new question? conclude?)
4. **Generate** natural interviewer response (uses `llm.py`)
5. **Convert** to audio (uses `tts.py`, optional)
6. **Return** response + updated state

**Key Method:**
```python
await interviewer_agent.process_turn(
    audio_bytes=candidate_audio,
    session_state=current_state  # from database
)
# Returns: (agent_response, updated_state)
```

**Also has:**
- `start_interview()` - Generate opening greeting
- `_decide_next_action()` - Agentic decision-making
- `_generate_response()` - Natural language generation

**Why Stateless?**
- Agent has NO internal state
- All state passed in via `SessionState`
- State stored in database (Supabase)
- Can scale to millions of concurrent interviews
- If server crashes, interview can resume from DB

---

### 3. **`services/llm.py`** - LLM Integration (Enhanced)

Added agentic decision-making functions:

**New Functions:**

- **`agent_decide_next_action()`** - Core decision-making
  ```python
  # Analyzes conversation and decides what to do next
  decision = await llm.agent_decide_next_action(
      conversation_history=[...],
      candidate_response="I worked at Google for 3 years",
      current_phase="experience",
      topics_covered=["background"],
      questions_asked=2
  )
  # Returns: {"action_type": "ask_followup", "reasoning": "...", ...}
  ```

- **`generate_interviewer_response()`** - Natural response generation
  ```python
  response = await llm.generate_interviewer_response(
      action=decision,
      conversation_history=[...],
      candidate_response="...",
      current_phase="technical"
  )
  # Returns: "That's interesting! Can you tell me more about..."
  ```

- **`generate_opening_greeting()`** - Start interview
  ```python
  greeting = await llm.generate_opening_greeting()
  # Returns: "Hi! Thanks for joining me today..."
  ```

**Status:** Currently STUBS with mock logic. Need to implement with Anthropic/OpenAI API.

---

### 4. **`services/tts.py`** - Text-to-Speech (NEW)

Converts interviewer text to audio.

**Main Function:**
```python
audio_url = await tts.text_to_speech(
    text="Can you tell me more about that?",
    voice="alloy"  # OpenAI TTS voices
)
# Returns: URL to audio file, or None if disabled
```

**Status:** STUB - returns None (text-only mode). Can implement with OpenAI TTS or ElevenLabs.

---

### 5. **`api/session.py`** - Session Endpoints (NEW)

HTTP endpoints for managing live interviews.

**Endpoints:**

#### `POST /session/start/{interview_id}`
Start a new interview session.
```python
response = await fetch('/session/start/int_123', {method: 'POST'})
# Returns: {
#   "interviewer_response": {...},
#   "session_state": {...},
#   "turn_number": 1
# }
```

#### `POST /session/turn/{interview_id}`
Process one turn of conversation.
```python
formData = new FormData()
formData.append('audio', audioBlob)

response = await fetch('/session/turn/int_123', {
    method: 'POST',
    body: formData
})
# Returns: {
#   "interviewer_response": {
#     "text": "Can you elaborate?",
#     "audio_url": "...",
#     "should_continue": true
#   },
#   "session_state": {...},
#   "turn_number": 3
# }
```

#### `GET /session/state/{interview_id}`
Get current session state (for resuming/debugging).

#### `DELETE /session/state/{interview_id}`
End session and trigger evaluation.

---

### 6. **`main.py`** - Updated
Added session router:
```python
app.include_router(session.router, prefix="/session", tags=["session"])
```

---

## How It Works: Complete Flow

### Starting an Interview

```
Frontend                    Backend
   |                           |
   |-- POST /session/start --> |
   |                           |
   |                      [Agent generates greeting]
   |                      [Store SessionState in DB]
   |                           |
   | <-- Greeting + State ---- |
   |                           |
   [Play audio greeting]
```

### Each Turn

```
Frontend                    Backend                      Agent
   |                           |                           |
   [User speaks]               |                           |
   |                           |                           |
   |-- POST /session/turn ---> |                           |
   |    (audio blob)           |                           |
   |                           |                           |
   |                      [Load SessionState from DB]      |
   |                           |                           |
   |                           |--- process_turn() ------> |
   |                           |                           |
   |                           |                      [Transcribe audio]
   |                           |                      [Analyze response]
   |                           |                      [Decide: followup]
   |                           |                      [Generate question]
   |                           |                      [Create audio]
   |                           |                           |
   |                           | <-- response + state ---- |
   |                           |                           |
   |                      [Save updated state to DB]
   |                           |
   | <-- Interviewer response -|
   |                           |
   [Play audio response]
```

---

## Database Schema Needed

You'll need to create tables in Supabase:

### `session_states`
```sql
CREATE TABLE session_states (
    interview_id TEXT PRIMARY KEY,
    current_phase TEXT,
    conversation_history JSONB,
    topics_covered TEXT[],
    insights TEXT[],
    questions_asked INTEGER,
    started_at TIMESTAMP,
    last_updated TIMESTAMP
);
```

### Helper Functions Needed in `services/supabase.py`

```python
async def create_session_state(state: SessionState)
async def get_session_state(interview_id: str) -> SessionState
async def update_session_state(interview_id: str, state: SessionState)
```

---

## What's Still TODO

### Critical (Implement Next):
1. **STT Integration** - `services/stt.py`
   - Implement with OpenAI Whisper, Deepgram, or AssemblyAI
   - Convert audio bytes → text transcript

2. **LLM Integration** - `services/llm.py`
   - Implement actual Anthropic/OpenAI API calls
   - Replace stub logic with real agentic decision-making

3. **Database Integration** - `services/supabase.py`
   - Create session_states table
   - Implement CRUD operations for SessionState

4. **Audio Storage**
   - Store candidate audio files (Supabase Storage, S3, etc.)
   - Store TTS audio files

### Optional (Can Add Later):
1. **TTS** - `services/tts.py`
   - Implement OpenAI TTS or ElevenLabs
   - For now, text-only mode works fine

2. **WebSocket Support**
   - For real-time streaming audio
   - Lower latency than HTTP polling

3. **Evaluation Pipeline**
   - Auto-trigger evaluation when interview concludes
   - Analyze full conversation for scoring

---

## Example Usage (Frontend)

### Start Interview
```typescript
const startInterview = async (interviewId: string) => {
    const response = await fetch(`/session/start/${interviewId}`, {
        method: 'POST'
    })
    const data = await response.json()

    // Play greeting audio or display text
    playAudio(data.interviewer_response.audio_url)
    // or
    displayText(data.interviewer_response.text)
}
```

### Process Turn
```typescript
const submitAnswer = async (interviewId: string, audioBlob: Blob) => {
    const formData = new FormData()
    formData.append('audio', audioBlob)

    const response = await fetch(`/session/turn/${interviewId}`, {
        method: 'POST',
        body: formData
    })
    const data = await response.json()

    // Display/play interviewer response
    displayText(data.interviewer_response.text)
    playAudio(data.interviewer_response.audio_url)

    // Check if interview concluded
    if (!data.interviewer_response.should_continue) {
        endInterview()
    }
}
```

---

## Key Advantages of This Architecture

1. **Stateless Agent** → Scalable, crash-resistant
2. **Turn-based HTTP** → Simple, easy to debug
3. **Separation of Concerns** → Agent, LLM, STT, TTS all separate
4. **Flexible** → Can add WebSocket later without changing agent
5. **Testable** → Pure functions, easy to unit test
6. **Resumable** → State in DB means interviews can be resumed

---

## Next Steps

1. Implement `services/stt.py` (Whisper/Deepgram)
2. Implement `services/llm.py` with Anthropic API
3. Create Supabase tables and implement DB functions
4. Test the full loop end-to-end
5. (Optional) Add TTS for audio responses

---

## Testing the Agent (Without Integrations)

You can test the flow right now with stubs:

```bash
# Start server
uvicorn app.main:app --reload

# Start interview
curl -X POST http://localhost:8000/session/start/test_123

# Upload audio (will use stub transcription)
curl -X POST http://localhost:8000/session/turn/test_123 \
  -F "audio=@test_audio.wav"
```

The agent will return mock responses, but the full orchestration flow is working!
