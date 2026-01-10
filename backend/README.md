# Lexi - Language Proficiency Assessment Backend

A stateless, agentic language proficiency testing system built with FastAPI. Evaluates users' language skills through adaptive speaking and translation exercises.

---

## Overview

Lexi assesses language proficiency (Spanish, French, etc.) through:
1. **Speaking Test** - User speaks in target language → Grammar/fluency evaluation
2. **Translation Test** - User translates passages → Accuracy evaluation

The agent **adapts difficulty in real-time** based on performance and assigns CEFR levels (A1-C2).

---

## Architecture

### **Stateless Agent Design**

```
User Audio/Text → API → Agent → LLM (Evaluate) → Next Exercise → User
                    ↓
                Database (Session State)
```

**Key Components:**
- `services/agent.py` - Stateless orchestrator (no internal state)
- `services/llm.py` - LLM evaluation & exercise generation
- `services/stt.py` - Multi-language speech-to-text
- `api/session.py` - REST endpoints
- `models/session.py` - Session state models

**State Storage:**
- All state stored in `SessionState` model
- Persisted in Supabase between requests
- Agent is pure function: `(audio/text + old_state) → (evaluation + new_state)`

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create `.env` file:

```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# OpenAI (for Whisper STT + LLM evaluation)
OPENAI_API_KEY=your_openai_key

# Anthropic (alternative for LLM)
ANTHROPIC_API_KEY=your_anthropic_key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 3. Run Database Migrations

```bash
# Copy the SQL from database/migrations/001_create_session_states.sql
# Paste into Supabase SQL Editor and run
```

### 4. Start Server

```bash
uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

API docs at: http://localhost:8000/docs

---

## API Endpoints

### **Start Assessment**

```http
POST /session/start/{assessment_id}
Content-Type: multipart/form-data

target_language: "Spanish"

Response:
{
  "agent_response": {
    "text": "Welcome! Please answer in Spanish:",
    "speaking_prompt": "What is your name and where are you from?",
    "difficulty_level": 1,
    "should_continue": true
  },
  "session_state": { ... },
  "exercises_completed": 0,
  "current_phase": "speaking_test"
}
```

### **Submit Exercise**

```http
POST /session/exercise/{assessment_id}
Content-Type: multipart/form-data

# For speaking or audio translation:
audio: <audio file>

# OR for text translation:
translation_text: "The cat sleeps on the sofa"

Response:
{
  "agent_response": {
    "text": "Good job!",
    "evaluation": {
      "grammar_score": 75.0,
      "fluency_score": 80.0,
      "feedback": "Watch verb conjugations",
      "errors": ["'yo va' should be 'yo voy'"]
    },
    "speaking_prompt": "Describe your daily routine",
    "difficulty_level": 2
  },
  "session_state": { ... },
  "exercises_completed": 1
}
```

### **Get Results**

```http
GET /session/results/{assessment_id}

Response:
{
  "proficiency_level": "B1",
  "overall_grammar_score": 78.5,
  "overall_fluency_score": 72.0,
  "exercises_completed": 10,
  "strengths": ["Natural flow", "Good vocabulary"],
  "areas_for_improvement": ["Subjunctive mood", "Complex structures"]
}
```

---

## How It Works

### **Agent Flow**

```
1. User starts assessment for Spanish

2. SPEAKING TEST (5 exercises):
   - Difficulty 1: "What is your name?"
     → User speaks in Spanish
     → Score: 85% → Difficulty +1

   - Difficulty 2: "Describe your day"
     → User speaks
     → Score: 60% → Difficulty stays same

   ... continues until 5 exercises ...

   → Agent switches to translation test

3. TRANSLATION TEST (5 exercises):
   - Difficulty 3: Show Spanish passage
     → User translates to English
     → Score: 90% → Difficulty +1

   ... continues until 5 exercises ...

4. FINAL EVALUATION:
   - Calculate average scores
   - Assign CEFR level (A1-C2)
   - Return detailed feedback
```

### **Adaptive Difficulty**

```
Score 90%+ → Difficulty +1 (harder)
Score <60% → Difficulty -1 (easier)
Score 60-90% → Stay at current level

Difficulty 1-3:  Beginner (A1-A2)
Difficulty 4-6:  Intermediate (B1-B2)
Difficulty 7-10: Advanced (C1-C2)
```

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── session.py         # Assessment endpoints
│   │   ├── interviews.py      # Legacy interview endpoints
│   │   ├── ai.py             # Standalone AI utilities
│   │   ├── email.py          # Email service
│   │   └── health.py         # Health checks
│   │
│   ├── models/
│   │   ├── session.py        # SessionState, LanguageExercise, AgentResponse
│   │   ├── interview.py      # Legacy interview models
│   │   └── evaluation.py     # Evaluation models
│   │
│   ├── services/
│   │   ├── agent.py          # Language assessment agent (STATELESS)
│   │   ├── llm.py            # LLM evaluation & generation
│   │   ├── stt.py            # Speech-to-text (multi-language)
│   │   ├── tts.py            # Text-to-speech
│   │   ├── supabase.py       # Database CRUD
│   │   ├── email.py          # Email sending
│   │   └── evaluation.py     # Legacy evaluation
│   │
│   ├── core/
│   │   ├── config.py         # Settings
│   │   └── security.py       # Security utilities
│   │
│   └── utils/
│       └── tokens.py         # Token generation
│
├── database/
│   └── migrations/
│       └── 001_create_session_states.sql
│
├── main.py                   # FastAPI app
├── requirements.txt          # Dependencies
├── README.md                # This file
├── LANGUAGE_ASSESSMENT_ARCHITECTURE.md  # Detailed architecture
└── .env.example             # Environment template
```

---

## Implementation Status

### ✅ **Completed**

- Stateless agent architecture
- Session state models
- API endpoints (start, submit exercise, get results)
- LLM service stubs with difficulty progression
- STT service with multi-language support
- Database schema & migrations
- Adaptive difficulty logic

### ⚠️ **To Implement (TODOs)**

#### **Critical (Core Functionality):**

1. **LLM Integration** - `services/llm.py`
   ```python
   # Replace stubs with real Anthropic/OpenAI calls
   async def evaluate_speaking_exercise(transcript, language, difficulty)
   async def evaluate_translation_exercise(passage, translation, ...)
   async def generate_speaking_prompt(language, difficulty)
   async def generate_translation_passage(language, difficulty)
   ```

2. **STT Integration** - `services/stt.py`
   ```python
   # Implement OpenAI Whisper
   from openai import AsyncOpenAI

   async def transcribe_audio(audio_bytes, language):
       client = AsyncOpenAI()
       response = await client.audio.transcriptions.create(...)
       return response.text
   ```

3. **Database Integration** - `services/supabase.py`
   ```python
   # Implement CRUD operations
   async def create_session_state(session_state)
   async def get_session_state(assessment_id)
   async def update_session_state(assessment_id, session_state)
   ```

4. **Uncomment Database Calls** - `api/session.py`
   ```python
   # Replace mock data with real DB calls
   session_state = await supabase.get_session_state(assessment_id)
   await supabase.update_session_state(assessment_id, updated_state)
   ```

#### **Optional (Enhancements):**

5. **TTS** - `services/tts.py` (for audio feedback)
6. **Authentication** - User management
7. **Audio Storage** - S3/Supabase Storage for audio files
8. **Real-time Streaming** - WebSocket support
9. **Multi-language Exercise Generation** - Generate passages IN the target language

---

## Database Schema

### **session_states** (Core table)

```sql
assessment_id         TEXT PRIMARY KEY
target_language       TEXT NOT NULL
current_phase         TEXT (intro, speaking_test, translation_test, complete)
current_difficulty    INTEGER (1-10)
exercises_completed   JSONB (array of LanguageExercise)
speaking_exercises_done    INTEGER
translation_exercises_done INTEGER
overall_grammar_score      FLOAT
overall_fluency_score      FLOAT
overall_proficiency_level  TEXT (A1, A2, B1, B2, C1, C2)
insights              TEXT[]
started_at            TIMESTAMP
last_updated          TIMESTAMP
```

### **assessments** (Metadata)

```sql
id                    TEXT PRIMARY KEY
user_id               TEXT
target_language       TEXT
status                TEXT (pending, in_progress, completed)
proficiency_level     TEXT (A1-C2)
overall_grammar_score FLOAT
overall_fluency_score FLOAT
created_at            TIMESTAMP
completed_at          TIMESTAMP
```

### **exercises** (Optional - detailed storage)

```sql
id                TEXT PRIMARY KEY
assessment_id     TEXT (FK)
exercise_type     TEXT (speaking, translation)
difficulty_level  INTEGER
prompt            TEXT
passage           TEXT
transcript        TEXT
grammar_score     FLOAT
fluency_score     FLOAT
accuracy_score    FLOAT
feedback          TEXT
errors            JSONB
created_at        TIMESTAMP
```

---

## Configuration

### **Environment Variables**

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anon/service key | Yes |
| `OPENAI_API_KEY` | OpenAI API key (for Whisper + GPT) | Optional* |
| `ANTHROPIC_API_KEY` | Anthropic API key (for Claude) | Optional* |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | No |

\* Need at least one LLM provider

### **Supported Languages**

Currently configured for:
- Spanish, French, German, Italian, Portuguese
- Chinese, Japanese, Korean
- English, Arabic, Russian, Hindi

Add more in `services/stt.py → LANGUAGE_CODES`

---

## Testing

### **Manual Testing (with cURL)**

```bash
# Start assessment
curl -X POST http://localhost:8000/session/start/test_001 \
  -F "target_language=Spanish"

# Submit speaking exercise
curl -X POST http://localhost:8000/session/exercise/test_001 \
  -F "audio=@my_audio.wav"

# Submit translation (text)
curl -X POST http://localhost:8000/session/exercise/test_001 \
  -F "translation_text=The cat sleeps on the sofa"

# Get results
curl http://localhost:8000/session/results/test_001
```

### **Testing with Stubs**

The system works end-to-end with mock data:
- STT returns mock transcriptions
- LLM returns mock scores
- Database calls are commented out (in-memory state)

You can test the full flow before implementing external services!

---

## Key Design Decisions

### **Why Stateless Agent?**

**Benefits:**
- ✅ Scalable (millions of concurrent assessments)
- ✅ Crash-resistant (state in DB, not memory)
- ✅ Easy to debug (state is explicit)
- ✅ Resumable (can continue after server restart)

**How it works:**
```python
# Agent is pure function
async def process_exercise(session_state, audio):
    # 1. Evaluate previous exercise
    # 2. Decide next exercise
    # 3. Return (response, new_state)
    return agent_response, updated_state

# Caller handles persistence
state = await db.get_state(id)
response, new_state = await agent.process_exercise(state, audio)
await db.update_state(id, new_state)
```

### **Why Turn-Based (not WebSocket)?**

- Simpler to implement and debug
- Natural pauses for thinking
- Easier to record and evaluate
- Can upgrade to WebSocket later without changing agent

### **Why JSONB for exercises?**

- Flexible schema (exercises may evolve)
- Fast querying with GIN indexes
- No migrations needed for new exercise fields

---

## Next Steps

1. **Implement LLM integration** → Get real grammar checks working
2. **Implement STT** → Transcribe actual audio
3. **Connect database** → Persistent state storage
4. **Test end-to-end** → Full assessment flow
5. **Add authentication** → Multi-user support
6. **Deploy** → Production environment

---

## Documentation

- **Architecture Guide**: `LANGUAGE_ASSESSMENT_ARCHITECTURE.md`
- **Database Migrations**: `database/migrations/`
- **API Docs**: http://localhost:8000/docs (when running)

---

## Contributing

When implementing TODOs:
1. Keep agent stateless (no internal state)
2. All state in `SessionState` model
3. Pass state in/out of functions
4. Store state in database between requests

---

## License

MIT

---

**Built with:**
- FastAPI 0.111.0
- Supabase 2.4.0
- Pydantic 2.7.1
- OpenAI Whisper (STT)
- Anthropic Claude / OpenAI GPT (LLM)
