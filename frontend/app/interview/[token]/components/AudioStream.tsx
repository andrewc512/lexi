"use client";

import { useEffect, useRef, useState } from "react";

interface AudioStreamProps {
  isMuted: boolean;
  onTranscript: (text: string) => void;
}

export function AudioStream({ isMuted, onTranscript }: AudioStreamProps) {
  const [isListening, setIsListening] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    // TODO: Initialize audio stream
    const initAudio = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;
        setIsListening(true);

        // TODO: Set up WebSocket connection for real-time STT
        // TODO: Stream audio chunks to backend
        
        mediaRecorderRef.current = new MediaRecorder(stream);
        mediaRecorderRef.current.ondataavailable = (event) => {
          if (event.data.size > 0) {
            // TODO: Send audio chunk to backend via WebSocket
            console.log("Audio chunk:", event.data.size, "bytes");
          }
        };

        // Start recording in chunks
        mediaRecorderRef.current.start(1000); // 1 second chunks
      } catch (error) {
        console.error("Failed to access microphone:", error);
      }
    };

    initAudio();

    return () => {
      // Cleanup
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  useEffect(() => {
    // Handle mute/unmute
    if (streamRef.current) {
      streamRef.current.getAudioTracks().forEach((track) => {
        track.enabled = !isMuted;
      });
    }
  }, [isMuted]);

  // Simulate receiving transcription (for demo)
  useEffect(() => {
    if (isMuted || !isListening) return;

    // TODO: Replace with actual WebSocket transcript events
    const demoInterval = setInterval(() => {
      // Simulate user speech detection
      // In real implementation, this comes from STT service
    }, 5000);

    return () => clearInterval(demoInterval);
  }, [isMuted, isListening, onTranscript]);

  // This component is invisible - just handles audio
  return null;
}
