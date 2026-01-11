"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { ConsentScreen } from "./components/ConsentScreen";
import { AudioStream, AudioStreamRef } from "./components/AudioStream";
import { AIVoice } from "./components/AIVoice";
import { TranscriptPanel } from "./components/TranscriptPanel";
import { Timer } from "./components/Timer";
import { ReadingPassage } from "./components/ReadingPassage";

type InterviewState = "consent" | "interview" | "complete";
type InterviewPhase = "conversation" | "reading";

interface TranscriptEntry {
  id: string;
  speaker: "ai" | "user";
  text: string;
  timestamp: Date;
}

interface ReadingPassageData {
  passage: string;
  language: string;
  difficulty: number;
  instruction: string;
}

export default function InterviewPage({
  params,
}: {
  params: { token: string };
}) {
  const [state, setState] = useState<InterviewState>("consent");
  const [phase, setPhase] = useState<InterviewPhase>("conversation");
  const [isRecording, setIsRecording] = useState(false);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [readingPassage, setReadingPassage] = useState<ReadingPassageData | null>(null);
  const audioStreamRef = useRef<AudioStreamRef>(null);

  const handleConsent = () => {
    setState("interview");
    // WebSocket will be initialized in AudioStream component
    // It will send the initial greeting
  };

  const handleComplete = () => {
    setState("complete");
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
        // Auto-start recording after AI finishes speaking
        console.log("🎙️ AI finished speaking, auto-starting recording");
        audioStreamRef.current?.autoStartRecording();
      };

      audio.onerror = (e) => {
        console.error("Error playing audio:", e);
        setIsAISpeaking(false);
        // Auto-start recording even on error
        audioStreamRef.current?.autoStartRecording();
      };

      audio.play().catch((e) => {
        console.error("Failed to play audio:", e);
        setIsAISpeaking(false);
        // Auto-start recording even on error
        audioStreamRef.current?.autoStartRecording();
      });
    } else {
      // Fallback: simulate AI speaking duration based on text length if no audio
      setIsAISpeaking(true);
      const speakingDuration = Math.max(2000, text.length * 50); // ~50ms per character
      setTimeout(() => {
        setIsAISpeaking(false);
        // Auto-start recording after simulated speaking
        audioStreamRef.current?.autoStartRecording();
      }, speakingDuration);
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
      } else if (message.type === "phase_transition") {
        // Handle phase transition (e.g., to reading)
        console.log("Phase transition to:", message.new_phase);
        if (message.new_phase === "reading") {
          setPhase("reading");
        }
        // Play the transition message audio
        if (message.text) {
          handleAIResponse(message.text, message.audio);
        }
      } else if (message.type === "reading_passage") {
        // Display reading passage
        console.log("Received reading passage");
        setReadingPassage({
          passage: message.passage,
          language: message.language,
          difficulty: message.difficulty,
          instruction: message.instruction,
        });
      } else if (message.type === "reading_evaluation") {
        // Handle reading evaluation feedback
        console.log("Reading evaluation:", message.evaluation);
        if (message.text) {
          handleAIResponse(message.text, message.audio);
        }
      }
    };

    window.addEventListener("ws-message" as any, handleWSMessage as any);

    return () => {
      window.removeEventListener("ws-message" as any, handleWSMessage as any);
    };
  }, [state, handleAIResponse]);

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
    <div className="h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-white">
        <div className="flex items-center gap-4">
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            </div>
            <span className="text-xl font-semibold text-gray-900">Lexi</span>
          </div>
          <span className="text-gray-300 text-sm">|</span>
          <Timer onExpire={handleComplete} />
        </div>
        <div className="flex items-center gap-4">
          {isRecording && (
            <span className="flex items-center gap-2 text-red-600 text-sm font-medium">
              <span className="w-2 h-2 bg-red-600 rounded-full animate-pulse" />
              Recording...
            </span>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Video/Avatar area */}
        <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
          {phase === "reading" && readingPassage ? (
            // Reading phase - show passage
            <ReadingPassage
              passage={readingPassage.passage}
              language={readingPassage.language}
              difficulty={readingPassage.difficulty}
              instruction={readingPassage.instruction}
            />
          ) : (
            // Conversation phase - show AI avatar
            <div className="relative">
              {/* AI Avatar */}
              <div
                className={`w-64 h-64 rounded-full bg-blue-600 flex items-center justify-center transition-all duration-300 ${
                  isAISpeaking ? "ring-8 ring-blue-200 scale-105" : "ring-4 ring-blue-100"
                }`}
              >
                <div className="text-center">
                  <div className="text-7xl mb-2">💬</div>
                  <span className="text-white font-semibold text-lg">Lexi AI</span>
                </div>
              </div>

              {/* Speaking indicator */}
              {isAISpeaking && (
                <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-1">
                  <span className="w-1 h-3 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: "0ms" }} />
                  <span className="w-1 h-4 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: "150ms" }} />
                  <span className="w-1 h-3 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: "300ms" }} />
                  <span className="w-1 h-5 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: "450ms" }} />
                  <span className="w-1 h-3 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: "600ms" }} />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Transcript sidebar */}
        <TranscriptPanel transcript={transcript} />
      </main>

      {/* Controls */}
      <footer className="p-6 border-t border-gray-200 bg-white">
        <div className="flex items-center justify-center gap-4">
          {/* Stop Recording button - only shown when recording */}
          {isRecording && (
            <button
              onClick={handleStopRecording}
              className="px-8 py-4 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold flex items-center gap-3 transition-colors shadow-sm"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="6" width="12" height="12" rx="2" />
              </svg>
              Stop Recording
            </button>
          )}

          {/* AI is speaking indicator */}
          {isAISpeaking && !isRecording && (
            <div className="px-8 py-4 bg-gray-100 text-gray-700 rounded-lg font-medium flex items-center gap-3 border border-gray-200">
              <svg className="w-6 h-6 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
              </svg>
              AI is speaking...
            </div>
          )}

          {/* End Interview button */}
          <button
            onClick={handleComplete}
            className="px-6 py-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors border border-gray-200"
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
