"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { ConsentScreen } from "./components/ConsentScreen";
import { AudioStream, AudioStreamRef } from "./components/AudioStream";
import { AIVoice } from "./components/AIVoice";
import { TranscriptPanel } from "./components/TranscriptPanel";
import { Controls } from "./components/Controls";
import { Timer } from "./components/Timer";

type InterviewState = "consent" | "interview" | "complete";

interface TranscriptEntry {
  id: string;
  speaker: "ai" | "user";
  text: string;
  timestamp: Date;
}

export default function InterviewPage({
  params,
}: {
  params: { token: string };
}) {
  const [state, setState] = useState<InterviewState>("consent");
  const [isRecording, setIsRecording] = useState(false);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const audioStreamRef = useRef<AudioStreamRef>(null);

  const handleConsent = () => {
    setState("interview");
    // WebSocket will be initialized in AudioStream component
    // It will send the initial greeting
  };

  const handleComplete = () => {
    setState("complete");
  };

  const handleStartRecording = () => {
    audioStreamRef.current?.startRecording();
  };

  const handleStopRecording = () => {
    audioStreamRef.current?.stopRecording();
  };

  const handleUserSpeech = useCallback((text: string) => {
    setTranscript((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        speaker: "user" as const,
        text,
        timestamp: new Date(),
      },
    ]);
  }, []);

  const handleAIResponse = useCallback((text: string, audioData?: string) => {
    setTranscript((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        speaker: "ai" as const,
        text,
        timestamp: new Date(),
      },
    ]);

    // Play audio if available
    if (audioData) {
      console.log("🔊 Playing AI audio");
      setIsAISpeaking(true);
      const audio = new Audio(`data:audio/mp3;base64,${audioData}`);

      audio.onended = () => {
        setIsAISpeaking(false);
      };

      audio.onerror = (e) => {
        console.error("Error playing audio:", e);
        setIsAISpeaking(false);
      };

      audio.play().catch((e) => {
        console.error("Failed to play audio:", e);
        setIsAISpeaking(false);
      });
    } else {
      // Fallback: simulate AI speaking duration based on text length if no audio
      setIsAISpeaking(true);
      const speakingDuration = Math.max(2000, text.length * 50); // ~50ms per character
      setTimeout(() => setIsAISpeaking(false), speakingDuration);
    }
  }, []);

  // Set up WebSocket message listener
  useEffect(() => {
    if (state !== "interview") return;

    // We need to wait for the WebSocket to be created in AudioStream
    // For now, we'll handle AI responses via a custom event
    const handleWSMessage = (event: CustomEvent) => {
      const message = event.detail;
      if (message.type === "transcript") {
        if (message.speaker === "ai") {
          handleAIResponse(message.text, message.audio);
        } else if (message.speaker === "user") {
          // User transcript is already handled in handleUserSpeech
          // but we could add it here for consistency
        }
      }
    };

    window.addEventListener("ws-message" as any, handleWSMessage as any);

    return () => {
      window.removeEventListener("ws-message" as any, handleWSMessage as any);
    };
  }, [state]);

  if (state === "consent") {
    return <ConsentScreen token={params.token} onConsent={handleConsent} />;
  }

  if (state === "complete") {
    return (
      <div className="min-h-screen bg-[#1a1a1a] flex items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-semibold text-white mb-4">Interview Complete</h1>
          <p className="text-gray-400">Thank you for your time. We&apos;ll be in touch soon.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-[#1a1a1a] flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <h1 className="text-white font-medium">Lexi Interview</h1>
          <span className="text-gray-500 text-sm">|</span>
          <Timer onExpire={handleComplete} />
        </div>
        <div className="flex items-center gap-4">
          {isRecording && (
            <span className="flex items-center gap-2 text-red-500 text-sm font-medium">
              <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              Recording...
            </span>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Video/Avatar area */}
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="relative">
            {/* AI Avatar */}
            <div 
              className={`w-64 h-64 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center transition-all duration-300 ${
                isAISpeaking ? "ring-4 ring-blue-400 ring-opacity-60 scale-105" : ""
              }`}
            >
              <div className="text-center">
                <div className="text-6xl mb-2">🤖</div>
                <span className="text-white font-medium">Lexi AI</span>
              </div>
            </div>
            
            {/* Speaking indicator */}
            {isAISpeaking && (
              <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-1">
                <span className="w-1 h-3 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: "0ms" }} />
                <span className="w-1 h-4 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: "150ms" }} />
                <span className="w-1 h-3 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: "300ms" }} />
                <span className="w-1 h-5 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: "450ms" }} />
                <span className="w-1 h-3 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: "600ms" }} />
              </div>
            )}
          </div>
        </div>

        {/* Transcript sidebar */}
        <TranscriptPanel transcript={transcript} />
      </main>

      {/* Controls */}
      <footer className="p-6 border-t border-gray-800">
        <div className="flex items-center justify-center gap-4">
          {/* Recording button */}
          {!isRecording ? (
            <button
              onClick={handleStartRecording}
              disabled={isAISpeaking}
              className="px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium flex items-center gap-3 transition-colors"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
              </svg>
              Record Response
            </button>
          ) : (
            <button
              onClick={handleStopRecording}
              className="px-8 py-4 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium flex items-center gap-3 transition-colors"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="6" width="12" height="12" rx="2" />
              </svg>
              Stop Recording
            </button>
          )}

          {/* End Interview button */}
          <button
            onClick={handleComplete}
            className="px-6 py-4 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors"
          >
            End Interview
          </button>
        </div>
      </footer>

      {/* Audio components (invisible) */}
      <AudioStream
        ref={audioStreamRef}
        onTranscript={handleUserSpeech}
        onRecordingChange={setIsRecording}
        interviewToken={params.token}
      />
      <AIVoice
        isPlaying={isAISpeaking}
        onSpeakingChange={setIsAISpeaking}
      />
    </div>
  );
}
