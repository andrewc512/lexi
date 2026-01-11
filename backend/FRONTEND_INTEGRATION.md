# Frontend Integration Guide - Reading Assessment

## Overview

This guide shows how to integrate the reading assessment system into your frontend application.

## WebSocket Connection

### Initial Setup

```typescript
// Connect to interview WebSocket
const interviewId = "unique-interview-id";
const ws = new WebSocket(`ws://localhost:8000/ws/interview/${interviewId}`);

// Track current phase
let currentPhase: 'conversation' | 'reading' = 'conversation';
let currentPassage: string | null = null;
```

## Message Handlers

### Complete Message Handler

```typescript
interface WSMessage {
  type: 'transcript' | 'phase_transition' | 'reading_passage' | 'reading_evaluation' | 'error';
  speaker?: 'user' | 'ai';
  text?: string;
  audio?: string;  // base64 encoded
  new_phase?: string;
  passage?: string;
  language?: string;
  difficulty?: number;
  instruction?: string;
  evaluation?: ReadingEvaluation;
}

interface ReadingEvaluation {
  comprehension_score: number;
  accuracy_score: number;
  grammar_score: number;
  feedback: string;
  errors: string[];
  correct_translation: string;
  strengths: string[];
  transcript: string;
}

ws.onmessage = (event) => {
  const message: WSMessage = JSON.parse(event.data);

  switch (message.type) {
    case 'transcript':
      handleTranscript(message);
      break;

    case 'phase_transition':
      handlePhaseTransition(message);
      break;

    case 'reading_passage':
      handleReadingPassage(message);
      break;

    case 'reading_evaluation':
      handleReadingEvaluation(message);
      break;

    case 'error':
      handleError(message);
      break;
  }
};
```

### Handler Implementations

```typescript
function handleTranscript(message: WSMessage) {
  // Display conversation transcript
  const { speaker, text, audio } = message;

  addMessageToChat(speaker, text);

  if (audio && speaker === 'ai') {
    playAudio(audio);
  }
}

function handlePhaseTransition(message: WSMessage) {
  // Switch to reading interface
  currentPhase = 'reading';

  // Show transition message
  addMessageToChat('ai', message.text!);

  if (message.audio) {
    playAudio(message.audio);
  }

  // Update UI to show reading mode
  showReadingInterface();
}

function handleReadingPassage(message: WSMessage) {
  // Display passage in target language
  currentPassage = message.passage!;

  displayPassage({
    text: message.passage!,
    language: message.language!,
    difficulty: message.difficulty!,
    instruction: message.instruction!
  });
}

function handleReadingEvaluation(message: WSMessage) {
  const { evaluation, text, audio } = message;

  // Show feedback message
  addMessageToChat('ai', text!);

  if (audio) {
    playAudio(audio);
  }

  // Display detailed evaluation
  if (evaluation) {
    showEvaluationResults(evaluation);
  }
}

function handleError(message: WSMessage) {
  console.error('WebSocket error:', message);
  showErrorNotification(message.text || 'An error occurred');
}
```

## UI Components

### Reading Passage Display

```typescript
interface PassageData {
  text: string;
  language: string;
  difficulty: number;
  instruction: string;
}

function displayPassage(data: PassageData) {
  const container = document.getElementById('reading-container');

  container.innerHTML = `
    <div class="reading-passage">
      <div class="passage-header">
        <span class="language-badge">${data.language}</span>
        <span class="difficulty-badge">Difficulty: ${data.difficulty}/10</span>
      </div>

      <div class="instruction">
        ${data.instruction}
      </div>

      <div class="passage-text" lang="${data.language}">
        ${data.text}
      </div>

      <button id="record-translation" class="btn-primary">
        🎤 Record Translation
      </button>
    </div>
  `;

  // Add record button handler
  document.getElementById('record-translation')!.addEventListener('click', startRecording);
}
```

### Evaluation Results Display

```typescript
function showEvaluationResults(evaluation: ReadingEvaluation) {
  const container = document.getElementById('evaluation-results');

  container.innerHTML = `
    <div class="evaluation-card">
      <h3>Translation Evaluation</h3>

      <div class="scores">
        <div class="score-item">
          <span class="score-label">Comprehension</span>
          <span class="score-value">${evaluation.comprehension_score.toFixed(0)}%</span>
          <div class="score-bar">
            <div class="score-fill" style="width: ${evaluation.comprehension_score}%"></div>
          </div>
        </div>

        <div class="score-item">
          <span class="score-label">Accuracy</span>
          <span class="score-value">${evaluation.accuracy_score.toFixed(0)}%</span>
          <div class="score-bar">
            <div class="score-fill" style="width: ${evaluation.accuracy_score}%"></div>
          </div>
        </div>

        <div class="score-item">
          <span class="score-label">Grammar</span>
          <span class="score-value">${evaluation.grammar_score.toFixed(0)}%</span>
          <div class="score-bar">
            <div class="score-fill" style="width: ${evaluation.grammar_score}%"></div>
          </div>
        </div>
      </div>

      <div class="feedback-section">
        <h4>Feedback</h4>
        <p>${evaluation.feedback}</p>
      </div>

      ${evaluation.strengths.length > 0 ? `
        <div class="strengths-section">
          <h4>✅ Strengths</h4>
          <ul>
            ${evaluation.strengths.map(s => `<li>${s}</li>`).join('')}
          </ul>
        </div>
      ` : ''}

      ${evaluation.errors.length > 0 ? `
        <div class="errors-section">
          <h4>⚠️ Areas for Improvement</h4>
          <ul>
            ${evaluation.errors.map(e => `<li>${e}</li>`).join('')}
          </ul>
        </div>
      ` : ''}

      <div class="translation-comparison">
        <div class="user-translation">
          <h4>Your Translation</h4>
          <p>${evaluation.transcript}</p>
        </div>
        <div class="correct-translation">
          <h4>Suggested Translation</h4>
          <p>${evaluation.correct_translation}</p>
        </div>
      </div>
    </div>
  `;

  // Auto-hide after 10 seconds
  setTimeout(() => {
    container.style.opacity = '0';
  }, 10000);
}
```

## Audio Recording

### Record Translation

```typescript
let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];

async function startRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    sendTranslation(audioBlob);
  };

  mediaRecorder.start();

  // Update UI
  updateRecordButton('recording');
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    updateRecordButton('idle');
  }
}

function sendTranslation(audioBlob: Blob) {
  // Signal that audio is complete
  ws.send(JSON.stringify({ type: 'audio_complete' }));

  // Send audio data
  ws.send(audioBlob);

  // Show loading indicator
  showLoadingIndicator('Processing your translation...');
}
```

## Audio Playback

```typescript
function playAudio(base64Audio: string) {
  const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);

  audio.play().catch(err => {
    console.error('Failed to play audio:', err);
  });

  // Optional: Show audio visualization
  audio.onplay = () => {
    showAudioPlaying();
  };

  audio.onended = () => {
    hideAudioPlaying();
  };
}
```

## UI State Management

### Phase Transitions

```typescript
function showReadingInterface() {
  // Hide conversation interface
  document.getElementById('conversation-container')!.style.display = 'none';

  // Show reading interface
  document.getElementById('reading-container')!.style.display = 'block';

  // Update progress indicator
  updateProgressBar('reading');
}

function showConversationInterface() {
  document.getElementById('conversation-container')!.style.display = 'block';
  document.getElementById('reading-container')!.style.display = 'none';
  updateProgressBar('conversation');
}
```

### Timer Display

```typescript
// Show countdown to reading phase
let startTime = Date.now();
const READING_PHASE_TIME = 180000; // 3 minutes in ms

function updateTimer() {
  if (currentPhase !== 'conversation') return;

  const elapsed = Date.now() - startTime;
  const remaining = READING_PHASE_TIME - elapsed;

  if (remaining <= 0) {
    document.getElementById('timer')!.textContent = 'Reading phase starting...';
    return;
  }

  const minutes = Math.floor(remaining / 60000);
  const seconds = Math.floor((remaining % 60000) / 1000);

  document.getElementById('timer')!.textContent =
    `Reading phase in ${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// Update timer every second
setInterval(updateTimer, 1000);
```

## CSS Styling (Example)

```css
/* Reading passage container */
.reading-passage {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.passage-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.language-badge, .difficulty-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  background: #e3f2fd;
  color: #1976d2;
  font-size: 0.875rem;
  font-weight: 500;
}

.instruction {
  padding: 1rem;
  background: #f5f5f5;
  border-left: 4px solid #2196f3;
  margin-bottom: 1.5rem;
  font-style: italic;
}

.passage-text {
  font-size: 1.25rem;
  line-height: 1.8;
  padding: 1.5rem;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  min-height: 120px;
}

/* Evaluation results */
.evaluation-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin: 1rem 0;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.score-item {
  margin-bottom: 1rem;
}

.score-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  transition: width 0.5s ease;
}

.feedback-section, .strengths-section, .errors-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

.translation-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1.5rem;
}

/* Record button */
.btn-primary {
  width: 100%;
  padding: 1rem 2rem;
  font-size: 1.125rem;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-primary.recording {
  background: #f44336;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
```

## React Example

```tsx
import React, { useState, useEffect, useRef } from 'react';

interface ReadingPhaseProps {
  websocket: WebSocket;
}

export function ReadingPhase({ websocket }: ReadingPhaseProps) {
  const [passage, setPassage] = useState<string>('');
  const [language, setLanguage] = useState<string>('');
  const [evaluation, setEvaluation] = useState<ReadingEvaluation | null>(null);
  const [isRecording, setIsRecording] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  useEffect(() => {
    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'reading_passage') {
        setPassage(message.passage);
        setLanguage(message.language);
        setEvaluation(null);
      }

      if (message.type === 'reading_evaluation') {
        setEvaluation(message.evaluation);
        if (message.audio) {
          playAudio(message.audio);
        }
      }
    };
  }, [websocket]);

  const handleRecord = async () => {
    if (!isRecording) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        websocket.send(JSON.stringify({ type: 'audio_complete' }));
        websocket.send(blob);
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } else {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="reading-phase">
      <div className="passage-display">
        <span className="language-badge">{language}</span>
        <p className="passage-text">{passage}</p>
      </div>

      <button onClick={handleRecord} className={isRecording ? 'recording' : ''}>
        {isRecording ? '⏹️ Stop Recording' : '🎤 Record Translation'}
      </button>

      {evaluation && (
        <div className="evaluation-results">
          <h3>Evaluation</h3>
          <p>Comprehension: {evaluation.comprehension_score}%</p>
          <p>Accuracy: {evaluation.accuracy_score}%</p>
          <p>Grammar: {evaluation.grammar_score}%</p>
          <p>{evaluation.feedback}</p>
        </div>
      )}
    </div>
  );
}
```

## Testing the Integration

### Manual Test

1. Connect to WebSocket
2. Wait for 3 minutes (or trigger manually)
3. Verify phase transition message appears
4. Check that reading passage displays
5. Record a translation
6. Confirm evaluation feedback appears

### Force Reading Phase (Development)

```typescript
// Trigger reading phase immediately for testing
async function forceReadingPhase() {
  const response = await fetch(`/ws/interview/${interviewId}/force-reading`, {
    method: 'POST'
  });

  const result = await response.json();
  console.log('Reading phase forced:', result);
}
```

## Troubleshooting

**Issue**: No phase transition after 3 minutes
- Check WebSocket connection is active
- Verify backend timer is working
- Use force endpoint to test manually

**Issue**: Audio not playing
- Check audio permissions in browser
- Verify base64 audio data is valid
- Try playing in new Audio() element directly

**Issue**: Recording not working
- Check microphone permissions
- Verify MediaRecorder is supported
- Test with `navigator.mediaDevices.getUserMedia()`

## Next Steps

1. Style the reading interface to match your design
2. Add animations for phase transitions
3. Implement progress tracking
4. Add accessibility features (ARIA labels, keyboard shortcuts)
5. Integrate with your state management (Redux, Zustand, etc.)
