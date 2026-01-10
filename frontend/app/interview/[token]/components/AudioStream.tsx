"use client";

import { useEffect, useRef, useImperativeHandle, forwardRef } from "react";

interface AudioStreamProps {
  onTranscript: (text: string) => void;
  onRecordingChange: (isRecording: boolean) => void;
  interviewToken: string;
}

export interface AudioStreamRef {
  startRecording: () => void;
  stopRecording: () => void;
}

export const AudioStream = forwardRef<AudioStreamRef, AudioStreamProps>(
  ({ onTranscript, onRecordingChange, interviewToken }, ref) => {
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

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
                if (message.audio) {
                  console.log("🔊 AI audio data received");
                }
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

          // Set up MediaRecorder
          mediaRecorderRef.current = new MediaRecorder(stream, {
            mimeType: "audio/webm",
          });

          mediaRecorderRef.current.ondataavailable = (event) => {
            if (event.data.size > 0) {
              audioChunksRef.current.push(event.data);
            }
          };

          mediaRecorderRef.current.onstop = () => {
            // When recording stops, send all accumulated audio to backend
            if (audioChunksRef.current.length > 0 && ws.readyState === WebSocket.OPEN) {
              const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
              console.log("🎤 Sending audio blob:", audioBlob.size, "bytes");

              // Send message to indicate recording complete
              ws.send(JSON.stringify({ type: "audio_complete" }));

              // Send the audio blob
              ws.send(audioBlob);

              // Clear chunks for next recording
              audioChunksRef.current = [];
            }
            onRecordingChange(false);
          };
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
      };
    }, [interviewToken]); // Only re-run if interviewToken changes

    // Expose start/stop methods to parent via ref
    useImperativeHandle(ref, () => ({
      startRecording: () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === "inactive") {
          audioChunksRef.current = [];
          mediaRecorderRef.current.start(100); // Collect in 100ms chunks
          onRecordingChange(true);
          console.log("🎙️ Recording started");
        }
      },
      stopRecording: () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
          mediaRecorderRef.current.stop();
          console.log("⏹️ Recording stopped");
        }
      },
    }));

    // This component is invisible - just handles audio
    return null;
  }
);

AudioStream.displayName = "AudioStream";
