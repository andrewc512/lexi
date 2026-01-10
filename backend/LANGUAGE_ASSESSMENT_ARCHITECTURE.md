# Language Proficiency Assessment Agent - Architecture

## Overview

This is an **agentic language assessment system** that evaluates a person's proficiency in a target language through two types of tests:

1. **Speaking Test** - User speaks in the target language → STT → Grammar/fluency evaluation
2. **Translation Test** - User translates passages of increasing difficulty → Accuracy evaluation

The agent adapts difficulty based on performance and provides detailed feedback.

---

## Use Case

**NOT a job interview system** - This is a language learning/assessment platform like Duolingo or IELTS, but with an intelligent agent that:
- Adapts difficulty in real-time
- Provides personalized feedback
- Evaluates grammar, fluency, and translation accuracy
- Assigns CEFR proficiency levels (A1-C2)

---

## System Architecture

### **Two Test Modes:**

#### 1. Speaking Proficiency Test
```
User speaks in Spanish → STT → Transcript → LLM Grammar Check → Score + Feedback
```

**Flow:**
1. Agent gives prompt: "Describe your daily routine" (in English)
2. User responds in Spanish (audio)
3. STT transcribes Spanish audio to text
4. LLM evaluates:
   - Grammar correctness
   - Vocabulary appropriateness
   - Sentence structure
   - Fluency/naturalness
5. Returns score (0-100) + specific errors + feedback
6. Agent decides: increase difficulty, decrease difficulty, or continue

#### 2. Translation Test
```
Display Spanish passage → User translates to English (text or audio) → LLM evaluates accuracy
```

**Flow:**
1. Agent shows Spanish passage on screen (difficulty-appropriate)
2. User translates out loud in English (audio) OR types translation
3. STT transcribes if audio
4. LLM compares user's translation to passage:
   - Translation accuracy
   - Meaning preservation
   - Grammar in English
   - Understanding of idioms/cultural context
5. Returns score + errors + suggested correct translation
6. Agent adjusts difficulty for next passage

---

## Key Models

### **LanguageExercise**
```python
{
    "exercise_id": "ex_001",
    "exercise_type": "speaking" | "translation",
    "difficulty_level": 5,  # 1-10 scale

    # For speaking
    "prompt": "Talk about your favorite hobby",  # in English

    # For translation
    "passage": "El gato duerme en el sofá",  # in Spanish
    "passage_language": "Spanish",

    # User's response
    "audio_url": "https://...",
    "transcript": "The cat sleeps on the sofa",  # STT result
    "translation": "The cat sleeps on the couch",  # their answer

    # Evaluation
    "grammar_score": 85.0,
    "fluency_score": 78.0,
    "accuracy_score": 90.0,  # for translation
    "feedback": "Good job! Watch verb conjugation.",
    "errors": ["'El gato duermen' should be 'duerme'"]
}
```

### **SessionState**
```python
{
    "assessment_id": "assess_123",
    "target_language": "Spanish",  # Language being assessed

    "current_phase": "speaking_test" | "translation_test" | "intro" | "complete",
    "current_difficulty": 5,  # Adjusts based on performance

    "exercises_completed": [LanguageExercise, ...],
    "speaking_exercises_done": 3,
    "translation_exercises_done": 2,

    # Final scores
    "overall_grammar_score": 82.0,
    "overall_fluency_score": 78.0,
    "overall_proficiency_level": "B2"  # CEFR level
}
```

---

## Agent Decision Flow

### **Agent Decides Next Exercise:**

```python
# Agent analyzes performance and decides what to do next
decision = await llm.agent_decide_next_exercise(
    session_state=current_state,
    previous_exercise=last_exercise
)

# Returns:
{
    "action_type": "speaking_prompt" | "translation_prompt" |
                   "increase_difficulty" | "switch_phase" | "conclude",
    "reasoning": "User scored 90% - increasing difficulty",
    "next_phase": "translation_test",  # if switching
    "difficulty_adjustment": +1  # or -1, or 0
}
```

### **Adaptive Difficulty:**

```
User scores 90% → Difficulty +1 (harder)
User scores 50% → Difficulty -1 (easier)
User scores 70% → Difficulty stays same

Difficulty 1-3:  Beginner (A1-A2)
Difficulty 4-6:  Intermediate (B1-B2)
Difficulty 7-10: Advanced (C1-C2)
```

---

## LLM Service Functions

### 1. **Agent Decision-Making**
```python
await llm.agent_decide_next_exercise(session_state, previous_exercise)
```
- Analyzes performance trend
- Decides difficulty adjustment
- Determines when to switch from speaking → translation
- Decides when assessment is complete

### 2. **Speaking Evaluation**
```python
await llm.evaluate_speaking_exercise(
    transcript="Yo vivo en Madrid desde dos años",
    target_language="Spanish",
    difficulty_level=3
)
# Returns: grammar score, fluency score, specific errors, feedback
```

### 3. **Translation Evaluation**
```python
await llm.evaluate_translation_exercise(
    original_passage="El gato negro duerme en el sofá",
    user_translation="The black cat sleeps on the sofa",
    source_language="Spanish",
    target_language="English",
    difficulty_level=2
)
# Returns: accuracy score, grammar score, errors, correct translation
```

### 4. **Exercise Generation**
```python
# Speaking prompts
await llm.generate_speaking_prompt(
    target_language="Spanish",
    difficulty_level=5
)
# Returns: "Explain a challenge you've overcome"

# Translation passages
await llm.generate_translation_passage(
    source_language="Spanish",
    target_language="English",
    difficulty_level=5
)
# Returns: Spanish text of appropriate difficulty
```

### 5. **Final Proficiency Calculation**
```python
await llm.calculate_overall_proficiency(session_state)
# Returns: { "proficiency_level": "B2", "grammar_score": 78, ... }
```

---

## API Endpoints

### Start Assessment
```http
POST /session/start/{assessment_id}
{
    "target_language": "Spanish"
}

Response:
{
    "agent_response": {
        "text": "Welcome! Let's start with speaking exercises.",
        "speaking_prompt": "Tell me about yourself",
        "difficulty_level": 1
    },
    "session_state": { ... }
}
```

### Submit Exercise (Speaking)
```http
POST /session/turn/{assessment_id}
Content-Type: multipart/form-data

audio: <audio file of user speaking in Spanish>

Response:
{
    "agent_response": {
        "text": "Good job! Let's try something harder.",
        "evaluation": {
            "grammar_score": 75,
            "fluency_score": 80,
            "feedback": "Watch verb conjugations",
            "errors": ["'yo va' should be 'yo voy'"]
        },
        "speaking_prompt": "Describe your daily routine",
        "difficulty_level": 2
    },
    "session_state": { ... }
}
```

### Submit Exercise (Translation)
```http
POST /session/turn/{assessment_id}
Content-Type: multipart/form-data

audio: <audio of user translating>
OR
translation_text: "The cat sleeps on the sofa"

Response:
{
    "agent_response": {
        "text": "Excellent translation!",
        "evaluation": {
            "accuracy_score": 95,
            "grammar_score": 90,
            "feedback": "Perfect understanding of meaning"
        },
        "translation_passage": "El perro corre en el parque...",
        "passage_language": "Spanish",
        "difficulty_level": 3
    }
}
```

---

## Complete Flow Example

### **Full Assessment Journey:**

```
1. User starts assessment for Spanish

2. SPEAKING TEST (5 exercises)
   Exercise 1 (Difficulty 1): "What is your name?"
   → User responds in Spanish
   → Score: 85% (good!) → Difficulty +1

   Exercise 2 (Difficulty 2): "Describe your day"
   → User responds
   → Score: 60% (struggled) → Difficulty stays same

   Exercise 3 (Difficulty 2): "Talk about your family"
   → User responds
   → Score: 75% (better) → Difficulty +1

   ... continues until 5 speaking exercises done ...

   → Agent switches to translation test

3. TRANSLATION TEST (5 exercises)
   Exercise 1 (Difficulty 3): "El gato negro..."
   → User translates: "The black cat..."
   → Score: 90% → Difficulty +1

   Exercise 2 (Difficulty 4): More complex passage
   → User translates
   → Score: 85% → Difficulty +1

   ... continues until 5 translation exercises done ...

4. FINAL EVALUATION
   Agent calculates:
   - Average grammar score: 78%
   - Average fluency score: 72%
   - Average translation accuracy: 85%

   → Overall proficiency level: B1

5. RESULTS DISPLAYED
   "Your Spanish proficiency level is B1 (Intermediate).
    Strengths: Good vocabulary, accurate translations
    Areas to improve: Verb conjugations, subjunctive mood"
```

---

## Database Schema

### `assessments` table
```sql
CREATE TABLE assessments (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    target_language TEXT,
    status TEXT,  -- pending, in_progress, complete
    proficiency_level TEXT,  -- A1, A2, B1, B2, C1, C2
    overall_grammar_score FLOAT,
    overall_fluency_score FLOAT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### `session_states` table
```sql
CREATE TABLE session_states (
    assessment_id TEXT PRIMARY KEY,
    target_language TEXT,
    current_phase TEXT,
    current_difficulty INTEGER,
    exercises_completed JSONB,  -- Array of LanguageExercise
    speaking_exercises_done INTEGER,
    translation_exercises_done INTEGER,
    insights TEXT[],
    started_at TIMESTAMP,
    last_updated TIMESTAMP
);
```

### `exercises` table (optional - for storing individual exercises)
```sql
CREATE TABLE exercises (
    id TEXT PRIMARY KEY,
    assessment_id TEXT,
    exercise_type TEXT,  -- speaking, translation
    difficulty_level INTEGER,
    prompt TEXT,
    passage TEXT,
    transcript TEXT,
    translation TEXT,
    grammar_score FLOAT,
    fluency_score FLOAT,
    accuracy_score FLOAT,
    feedback TEXT,
    errors JSONB,
    created_at TIMESTAMP
);
```

---

## Frontend Integration

### Display Logic

**Speaking Test:**
```typescript
// Show prompt in English
<div>Prompt: {agentResponse.speaking_prompt}</div>

// Record audio in Spanish
<AudioRecorder
    onStop={async (blob) => {
        await submitExercise(assessmentId, blob)
    }}
/>

// Show evaluation
<Evaluation
    grammarScore={evaluation.grammar_score}
    fluencyScore={evaluation.fluency_score}
    feedback={evaluation.feedback}
    errors={evaluation.errors}
/>
```

**Translation Test:**
```typescript
// Show Spanish passage
<div className="passage">
    <h3>Translate this passage:</h3>
    <p lang="es">{agentResponse.translation_passage}</p>
</div>

// Option 1: Speak translation
<AudioRecorder
    onStop={async (blob) => {
        await submitTranslation(assessmentId, blob)
    }}
/>

// Option 2: Type translation
<textarea
    placeholder="Enter your translation..."
    onChange={(e) => setTranslation(e.target.value)}
/>
<button onClick={() => submitTranslation(assessmentId, translation)}>
    Submit
</button>

// Show evaluation
<TranslationEvaluation
    accuracyScore={evaluation.accuracy_score}
    feedback={evaluation.feedback}
    correctTranslation={evaluation.correct_translation}
/>
```

---

## Next Steps

### Critical TODOs:

1. **Implement STT** - Transcribe audio in multiple languages
2. **Implement LLM evaluation** - Grammar checking, translation accuracy
3. **Database integration** - Store session state and exercises
4. **Exercise generation** - Generate varied prompts and passages
5. **CEFR scoring** - Proper proficiency level calculation

### Optional Enhancements:

1. **Multi-language support** - Assess Spanish, French, German, etc.
2. **Voice feedback** - TTS to speak evaluation feedback
3. **Progress tracking** - Track improvement over time
4. **Leaderboards** - Compare scores with other learners
5. **Certificates** - Generate proficiency certificates

---

## Key Differences from Interview System

| Interview System | Language Assessment |
|---|---|
| Job candidate evaluation | Language proficiency testing |
| Open-ended Q&A | Structured exercises |
| Behavioral/technical questions | Speaking + Translation tests |
| Subjective evaluation | Objective scoring (grammar, accuracy) |
| Single session | Multiple exercises with difficulty progression |
| No right/wrong answers | Clear correctness criteria |

---

This architecture is **perfect for the agentic approach** because:
- ✅ Adaptive difficulty based on performance
- ✅ Personalized feedback
- ✅ Continuous assessment across multiple exercises
- ✅ Context-aware (remembers previous mistakes)
- ✅ Natural progression (intro → speaking → translation → complete)
