"use client";

import { useState, useEffect } from "react";
import { ConsentScreen } from "./components/ConsentScreen";
import { AudioStream } from "./components/AudioStream";
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
  const [isMuted, setIsMuted] = useState(false);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [isUserSpeaking, setIsUserSpeaking] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);

  const handleConsent = () => {
    setState("interview");
    // WebSocket will be initialized in AudioStream component
    // It will send the initial greeting
  };

  const handleComplete = () => {
    setState("complete");
    if (wsConnection) {
      wsConnection.close();
    }
  };

  const addTranscriptEntry = (speaker: "ai" | "user", text: string) => {
    setTranscript((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        speaker,
        text,
        timestamp: new Date(),
      },
    ]);
  };

  const handleUserSpeech = (text: string) => {
    addTranscriptEntry("user", text);
  };

  const handleAIResponse = (text: string) => {
    addTranscriptEntry("ai", text);
    // Trigger AI speaking animation
    setIsAISpeaking(true);
    // Simulate AI speaking duration based on text length
    const speakingDuration = Math.max(2000, text.length * 50); // ~50ms per character
    setTimeout(() => setIsAISpeaking(false), speakingDuration);
  };

  // Set up WebSocket message listener
  useEffect(() => {
    if (state !== "interview") return;

    // We need to wait for the WebSocket to be created in AudioStream
    // For now, we'll handle AI responses via a custom event
    const handleWSMessage = (event: CustomEvent) => {
      const message = event.detail;
      if (message.type === "transcript") {
        if (message.speaker === "ai") {
          handleAIResponse(message.text);
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
          {isUserSpeaking && (
            <span className="flex items-center gap-2 text-green-400 text-sm font-medium">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              You&apos;re speaking...
            </span>
          )}
          <span className="flex items-center gap-2 text-red-500 text-sm">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            Recording
          </span>
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

      {/* User video preview + Controls */}
      <footer className="p-4 border-t border-gray-800">
        <div className="flex items-center justify-center gap-4">
          {/* User preview */}
          <div className="absolute bottom-24 right-8 w-40 h-28 bg-gray-800 rounded-lg overflow-hidden border-2 border-gray-700">
            <div className="w-full h-full flex items-center justify-center text-gray-500">
              <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
              </svg>
            </div>
            {!isMuted && (
              <div className="absolute bottom-2 left-2 flex items-center gap-0.5">
                <span className="w-0.5 h-2 bg-green-400 rounded-full animate-pulse" />
                <span className="w-0.5 h-3 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: "100ms" }} />
                <span className="w-0.5 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: "200ms" }} />
              </div>
            )}
          </div>

          {/* Controls */}
          <Controls
            isMuted={isMuted}
            onToggleMute={() => setIsMuted(!isMuted)}
            onEndCall={handleComplete}
          />
        </div>
      </footer>

      {/* Audio components (invisible) */}
      <AudioStream
        isMuted={isMuted}
        onTranscript={handleUserSpeech}
        onSpeakingChange={setIsUserSpeaking}
        interviewToken={params.token}
      />
      <AIVoice
        isPlaying={isAISpeaking}
        onSpeakingChange={setIsAISpeaking}
      />
    </div>
  );
}
