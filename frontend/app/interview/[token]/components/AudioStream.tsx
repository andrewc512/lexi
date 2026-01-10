"use client";

import { useEffect, useRef } from "react";

interface AudioStreamProps {
  isMuted: boolean;
  onTranscript: (text: string) => void;
  onSpeakingChange: (isSpeaking: boolean) => void;
  interviewToken: string;
}

export function AudioStream({ isMuted, onTranscript, onSpeakingChange, interviewToken }: AudioStreamProps) {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const speakingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const initAudio = async () => {
      try {
        // Get microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;

        // Set up WebSocket connection
        const wsUrl = `ws://localhost:8000/ws/interview/${interviewToken}`;
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log("✅ WebSocket connected to:", wsUrl);
        };

        ws.onmessage = (event) => {
          // Handle incoming messages from backend
          if (typeof event.data === "string") {
            const message = JSON.parse(event.data);
            console.log("📨 Received message:", message);

            if (message.type === "transcript" && message.speaker === "user") {
              // User's own speech transcribed
              console.log("📝 User transcript:", message.text);
              onTranscript(message.text);
            } else if (message.type === "transcript" && message.speaker === "ai") {
              // AI response transcript - dispatch custom event for parent to handle
              console.log("🤖 AI response:", message.text);
              const wsEvent = new CustomEvent("ws-message", { detail: message });
              window.dispatchEvent(wsEvent);
            } else if (message.type === "error") {
              console.error("❌ Error from server:", message.message);
            }
          }
        };

        ws.onerror = (error) => {
          console.error("❌ WebSocket error:", error);
        };

        ws.onclose = () => {
          console.log("🔌 WebSocket disconnected");
        };

        // Set up MediaRecorder to send audio chunks
        mediaRecorderRef.current = new MediaRecorder(stream, {
          mimeType: "audio/webm",
        });

        mediaRecorderRef.current.ondataavailable = (event) => {
          if (event.data.size > 0 && ws.readyState === WebSocket.OPEN && !isMuted) {
            // Send audio chunk to backend
            ws.send(event.data);

            // Detect if user is speaking based on chunk size
            // Larger chunks typically mean audio activity
            const isSpeaking = event.data.size > 1000;

            if (isSpeaking) {
              onSpeakingChange(true);

              // Clear any existing timeout
              if (speakingTimeoutRef.current) {
                clearTimeout(speakingTimeoutRef.current);
              }

              // Set speaking to false after 2 seconds of no large chunks
              speakingTimeoutRef.current = setTimeout(() => {
                onSpeakingChange(false);
              }, 2000);
            }
          }
        };

        // Start recording in chunks (500ms for more responsive transcription)
        mediaRecorderRef.current.start(500);
      } catch (error) {
        console.error("Failed to access microphone:", error);
      }
    };

    initAudio();

    return () => {
      // Cleanup
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
      if (speakingTimeoutRef.current) {
        clearTimeout(speakingTimeoutRef.current);
      }
      onSpeakingChange(false);
    };
  }, [interviewToken, onSpeakingChange]);

  useEffect(() => {
    // Handle mute/unmute
    if (streamRef.current) {
      streamRef.current.getAudioTracks().forEach((track) => {
        track.enabled = !isMuted;
      });
    }
  }, [isMuted]);

  // This component is invisible - just handles audio
  return null;
}
