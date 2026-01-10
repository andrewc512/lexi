# Lexi Interview System - Setup Guide

## Quick Start

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Environment Setup

Your `.env` file is already configured with your OpenAI API key in `backend/.env`

Frontend environment is ready in `frontend/.env.local`

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

You should see:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
```

### 5. Test the Interview

Open your browser and go to:
```
http://localhost:3000/interview/test-token-123
```

## How It Works

### The Flow:

1. **Consent Screen** - User accepts terms and grants microphone access
2. **Interview Starts** - WebSocket connection established
3. **AI Greeting** - Initial prompt from Lexi appears
4. **Continuous Recording** - Your voice is captured in 500ms chunks
5. **Voice Detection** - System detects when you stop speaking (2 seconds of silence)
6. **Transcription** - OpenAI Whisper transcribes your speech
7. **AI Response** - GPT-4 generates a contextual follow-up question
8. **Visual Feedback** - Transcript appears, AI avatar animates while "speaking"
9. **Loop** - Process repeats for natural conversation

### What's Implemented:

✅ Real-time WebSocket audio streaming
✅ OpenAI Whisper speech-to-text
✅ GPT-4 intelligent interviewer responses
✅ Voice activity detection
✅ Live transcript display
✅ AI speaking animations
✅ Mute/unmute controls
✅ Interview timer

### API Costs (approximate):

- **Whisper STT**: ~$0.006 per minute of audio
- **GPT-4 Responses**: ~$0.03 per 1K tokens (roughly $0.01 per response)
- **Estimated cost**: ~$0.10-0.20 per 10-minute interview

## Troubleshooting

### Backend won't start:
```bash
# Make sure you're in the backend directory
cd backend

# Check if port 8000 is available
lsof -i :8000

# Install dependencies again
pip install -r requirements.txt
```

### Frontend won't start:
```bash
# Make sure you're in the frontend directory
cd frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### WebSocket connection fails:
- Check that backend is running on port 8000
- Check browser console for errors
- Ensure `.env.local` has correct WebSocket URL

### Microphone not working:
- Grant browser microphone permissions
- Check browser console for getUserMedia errors
- Try HTTPS in production (HTTP is OK for localhost)

### No transcription appearing:
- Check backend logs for errors
- Verify OpenAI API key is correct in `.env`
- Check OpenAI API usage/billing dashboard
- Look for error messages in browser console

## Next Steps

### Customize the Interviewer:

Edit the system prompt in [backend/app/services/llm.py](backend/app/services/llm.py:37-46) to change Lexi's personality and interview style.

### Add Text-to-Speech:

Uncomment TTS code in [backend/app/api/realtime.py](backend/app/api/realtime.py) and implement OpenAI TTS in [backend/app/services/tts.py](backend/app/services/tts.py).

### Improve Voice Detection:

Replace basic VAD in [backend/app/api/realtime.py](backend/app/api/realtime.py:69-128) with WebRTC VAD or Silero VAD for better accuracy.

### Save Interviews:

Implement database storage in the WebSocket disconnect handler to save conversation history.

## Support

- Backend API docs: http://localhost:8000/docs
- WebSocket test: http://localhost:8000/ws/test
