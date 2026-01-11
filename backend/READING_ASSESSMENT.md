# Reading Assessment System

## Overview

The reading assessment system is integrated into the language interview process to evaluate a user's reading comprehension and translation abilities. The system automatically transitions from a conversational phase to a reading evaluation phase after 3 minutes.

## System Architecture

### Files

1. **`/app/services/reading_assessment.py`** - Core reading assessment logic
   - `ReadingAssessmentManager` class manages the reading phase
   - Handles passage generation, evaluation, and proficiency calculation

2. **`/app/api/realtime.py`** - WebSocket integration
   - Modified to track interview time and phase
   - Automatically transitions to reading phase at 3 minutes
   - Processes reading translations and provides feedback

### Key Components

#### ReadingAssessmentManager

**Methods:**
- `should_transition_to_reading()` - Checks if 3 minutes have elapsed
- `get_transition_message()` - Returns transition announcement
- `generate_reading_passage()` - Creates text passages in target language
- `evaluate_reading_translation()` - Scores user's English translation
- `process_audio_translation()` - Handles audio input for translations
- `calculate_reading_proficiency()` - Computes final reading level (CEFR)

## Interview Flow

### Phase 1: Conversation (0-3 minutes)
- AI conducts conversation in target language (e.g., Chinese)
- User responds in target language
- System evaluates speaking ability, grammar, and fluency
- Uses existing conversation system from `llm.generate_interview_response()`

### Phase 2: Transition (At 3 minutes)
- System detects 3 minutes have elapsed
- AI announces: *"Alright! We've had a great conversation. Now we're going to move to the reading portion of the evaluation..."*
- Frontend receives `phase_transition` message
- First reading passage is generated and displayed

### Phase 3: Reading Assessment (3+ minutes)
- Text displayed in target language
- User reads and translates to English (via speech or text)
- System evaluates:
  - **Comprehension score** (0-100): Understanding of original text
  - **Accuracy score** (0-100): Correctness of translation
  - **Grammar score** (0-100): English grammar quality
- Difficulty adapts based on performance:
  - Score > 85% → Increase difficulty
  - Score < 60% → Decrease difficulty
- Process repeats with new passages

## WebSocket Message Types

### Sent to Frontend

#### `phase_transition`
```json
{
  "type": "phase_transition",
  "speaker": "ai",
  "text": "Alright! Now we're moving to the reading portion...",
  "audio": "base64_audio_data",
  "new_phase": "reading"
}
```

#### `reading_passage`
```json
{
  "type": "reading_passage",
  "passage": "今天天气很好。我们去公园玩吧。",
  "language": "Chinese",
  "difficulty": 3,
  "instruction": "Please read this text and translate it to English."
}
```

#### `reading_evaluation`
```json
{
  "type": "reading_evaluation",
  "speaker": "ai",
  "text": "Great job! Your translation scored 85% for accuracy...",
  "audio": "base64_audio_data",
  "evaluation": {
    "comprehension_score": 85.0,
    "accuracy_score": 82.0,
    "grammar_score": 88.0,
    "feedback": "Good overall translation...",
    "errors": ["Minor tense inconsistency"],
    "correct_translation": "Suggested translation...",
    "strengths": ["Captured main idea"],
    "transcript": "The weather is very nice today. Let's go to the park."
  }
}
```

### Received from Frontend

Same as conversation phase:
- `audio_complete` signal followed by audio bytes
- Audio transcribed to English translation
- Evaluated against original passage

## Difficulty Levels

**1-10 Scale:**
- **1-3**: Simple sentences (present tense, common words)
- **4-6**: Moderate passages (mixed tenses, everyday topics)
- **7-10**: Complex passages (idioms, cultural references, technical vocabulary)

## CEFR Level Mapping

Final reading proficiency is mapped to CEFR levels:

| Avg Score | Level | Description |
|-----------|-------|-------------|
| 90-100    | C2    | Exceptional, near-native |
| 80-89     | C1    | Strong comprehension |
| 70-79     | B2    | Good reading skills |
| 60-69     | B1    | Adequate comprehension |
| 50-59     | A2    | Basic reading level |
| 0-49      | A1    | Beginner level |

## Integration with Existing System

### Uses Existing Services

1. **STT (Speech-to-Text)**: Transcribes user's English translation
2. **TTS (Text-to-Speech)**: Generates audio for feedback messages
3. **LLM Evaluation**: Reuses `llm.evaluate_translation_exercise()` for scoring

### State Management

Reading assessment state is tracked per WebSocket connection:
- `interview_start_time`: Unix timestamp when interview began
- `in_reading_phase`: Boolean flag
- `current_reading_passage`: Active passage being evaluated
- `reading_evaluations`: List of all reading exercise results
- `reading_difficulty`: Current difficulty level (1-10)

## API Endpoints

### Test Endpoint
```bash
GET /ws/test
```
Returns WebSocket status.

### Force Reading Phase (Testing)
```bash
POST /ws/interview/{interview_id}/force-reading
```
Manually triggers reading phase without waiting 3 minutes.

## Example Usage

### Frontend Implementation

```javascript
// Connect to WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws/interview/${interviewId}`);

// Listen for phase transition
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'phase_transition') {
    console.log('Transitioning to:', data.new_phase);
    // Update UI to show reading interface
  }

  if (data.type === 'reading_passage') {
    // Display passage in target language
    displayPassage(data.passage, data.language);
    showInstruction(data.instruction);
  }

  if (data.type === 'reading_evaluation') {
    // Show evaluation results
    displayFeedback(data.evaluation);
    playAudio(data.audio);
  }
};

// User submits translation (via speech)
function submitTranslation(audioBlob) {
  ws.send(JSON.stringify({ type: 'audio_complete' }));
  ws.send(audioBlob);
}
```

## Configuration

### Timing Constants
Located in `reading_assessment.py`:
```python
CONVERSATION_DURATION = 180  # 3 minutes in seconds
```

Modify this value to adjust when the reading phase begins.

### Target Language
Currently hardcoded to "Chinese" in `realtime.py`. Update these lines to support dynamic language selection:
```python
# Line 89, 115, etc.
target_language="Chinese"
```

Consider passing `target_language` from session state or interview configuration.

## Future Enhancements

1. **Database Persistence**: Save reading evaluations to database
2. **Multi-language Support**: Dynamic target language selection
3. **Advanced Passage Generation**: Use LLM to generate context-aware passages
4. **Image-based Reading**: Include passages with images for context
5. **Timed Reading**: Add time limits for each passage
6. **Reading Speed Metrics**: Track how long user takes to read and respond
7. **Pronunciation Evaluation**: Check pronunciation of target language reading
8. **Summary Tasks**: Ask users to summarize passages instead of translating

## Testing

### Manual Testing

1. Start the backend server
2. Connect via WebSocket to `/ws/interview/test123`
3. Wait 3 minutes for automatic transition
4. OR use force endpoint:
   ```bash
   curl -X POST http://localhost:8000/ws/interview/test123/force-reading
   ```
5. Submit audio or text translations
6. Verify evaluation feedback

### Unit Testing

Test the `ReadingAssessmentManager` independently:

```python
import pytest
from app.services.reading_assessment import reading_manager

@pytest.mark.asyncio
async def test_transition_timing():
    start = time.time()
    # Should not transition immediately
    assert not reading_manager.should_transition_to_reading(start)

    # Should transition after 3 minutes
    assert reading_manager.should_transition_to_reading(start - 181)

@pytest.mark.asyncio
async def test_passage_generation():
    passage = await reading_manager.generate_reading_passage(
        target_language="Spanish",
        difficulty_level=5
    )
    assert "passage" in passage
    assert len(passage["passage"]) > 0
```

## Troubleshooting

### Issue: Reading phase never triggers
- **Check**: Verify `interview_start_time` is set when WebSocket connects
- **Check**: Ensure time check runs on each user message
- **Solution**: Use force endpoint to manually trigger

### Issue: Evaluations not working
- **Check**: STT service is properly transcribing English
- **Check**: LLM evaluation service is responding
- **Solution**: Check logs for evaluation errors

### Issue: Difficulty not adapting
- **Check**: Evaluation scores are being returned correctly
- **Check**: `reading_difficulty` variable is updating
- **Solution**: Add logging to track difficulty adjustments

## Dependencies

- `openai` - For LLM evaluations (via existing `llm.py`)
- `fastapi` - WebSocket support
- `app.services.stt` - Speech transcription
- `app.services.tts` - Audio generation
- `app.services.llm` - Translation evaluation

## License & Credits

Part of the Lexi language assessment platform.
