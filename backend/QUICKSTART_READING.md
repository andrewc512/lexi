# Quick Start Guide - Reading Assessment

## 5-Minute Setup

### 1. Verify Installation

The reading assessment system is already integrated! Just verify:

```bash
cd /Users/ss/Desktop/sbhacker/lexi/backend

# Test imports
python -c "from app.services.reading_assessment import reading_manager; print('✅ Ready!')"

# Run example
python reading_assessment_example.py
```

### 2. Start the Server

```bash
# Start backend
python -m uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

### 3. Test the WebSocket

#### Option A: Manual Force Trigger (Recommended for Testing)

```bash
# In another terminal, force reading phase immediately
curl -X POST http://localhost:8000/ws/interview/test123/force-reading
```

#### Option B: Wait for Automatic Transition

Connect to WebSocket and wait 3 minutes:
```
ws://localhost:8000/ws/interview/test123
```

### 4. Frontend Integration

Connect your frontend to the WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/interview/test123');

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);

  if (msg.type === 'phase_transition') {
    console.log('🎯 Reading phase started!');
    console.log('Message:', msg.text);
  }

  if (msg.type === 'reading_passage') {
    console.log('📖 Passage:', msg.passage);
    console.log('Language:', msg.language);
    console.log('Difficulty:', msg.difficulty);
  }

  if (msg.type === 'reading_evaluation') {
    console.log('📊 Evaluation:', msg.evaluation);
    console.log('Scores:', {
      comprehension: msg.evaluation.comprehension_score,
      accuracy: msg.evaluation.accuracy_score,
      grammar: msg.evaluation.grammar_score
    });
  }
};
```

## Complete Flow in 30 Seconds

```
1. User connects → Interview starts (timer begins)
   ↓
2. 3 minutes of conversation (existing system)
   ↓
3. System announces: "Now moving to reading portion..."
   ↓
4. Reading passage displayed in target language
   ↓
5. User translates to English (via speech)
   ↓
6. System evaluates and provides scores/feedback
   ↓
7. Next passage (difficulty adjusted)
   ↓
8. Repeat steps 4-7
```

## Message Types Summary

| Type | Direction | Purpose |
|------|-----------|---------|
| `phase_transition` | Backend → Frontend | Announce reading phase |
| `reading_passage` | Backend → Frontend | Show text to translate |
| `reading_evaluation` | Backend → Frontend | Show scores & feedback |
| `audio_complete` + audio | Frontend → Backend | User's translation |

## Configuration

### Change Transition Time

Edit `app/services/reading_assessment.py`:

```python
# Line 22
CONVERSATION_DURATION = 180  # Change to desired seconds
```

Examples:
- 1 minute: `60`
- 5 minutes: `300`
- 10 seconds (testing): `10`

### Change Target Language

Edit `app/api/realtime.py`, replace all instances of:

```python
target_language="Chinese"
```

With your language:
```python
target_language="Spanish"  # or French, German, etc.
```

## Testing Checklist

- [ ] Import works: `python -c "from app.services.reading_assessment import reading_manager; print('OK')"`
- [ ] Example runs: `python reading_assessment_example.py`
- [ ] Server starts: `uvicorn app.main:app --reload`
- [ ] Force endpoint works: `curl -X POST .../force-reading`
- [ ] WebSocket connects: Test with frontend or WebSocket client
- [ ] Phase transition occurs: Check at 3 minutes or via force
- [ ] Passage displays: Verify message type `reading_passage`
- [ ] Audio recording works: Frontend microphone access
- [ ] Evaluation returns: Check scores in `reading_evaluation`

## Common Issues

### "Module not found"
```bash
# Make sure you're in the backend directory
cd /Users/ss/Desktop/sbhacker/lexi/backend

# Verify Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### "No reading passage received"
- Check WebSocket connection is active
- Verify `in_reading_phase = True` is set
- Use force endpoint to trigger manually

### "Evaluation not working"
- Check STT service is running
- Verify audio format is correct (webm/mp3)
- Check console logs for errors

## Next Steps

1. **Test the system**: Run `python reading_assessment_example.py`
2. **Integrate frontend**: See `FRONTEND_INTEGRATION.md`
3. **Customize passages**: Modify difficulty levels in `llm.py`
4. **Add database**: Store evaluations for later analysis
5. **Extend features**: Add more evaluation metrics

## File Reference

| File | Purpose |
|------|---------|
| `app/services/reading_assessment.py` | Core reading logic |
| `app/api/realtime.py` | WebSocket integration |
| `reading_assessment_example.py` | Standalone examples |
| `READING_ASSESSMENT.md` | Full documentation |
| `FRONTEND_INTEGRATION.md` | Frontend guide |
| `READING_ASSESSMENT_SUMMARY.md` | Implementation summary |

## Support

For detailed documentation:
- **How it works**: `READING_ASSESSMENT.md`
- **Frontend code**: `FRONTEND_INTEGRATION.md`
- **Architecture**: `READING_ASSESSMENT_SUMMARY.md`

## Quick Demo

```bash
# Terminal 1: Start server
uvicorn app.main:app --reload

# Terminal 2: Run example
python reading_assessment_example.py

# Terminal 3: Force reading phase
curl -X POST http://localhost:8000/ws/interview/demo/force-reading
```

That's it! The reading assessment system is ready to use. 🎉
