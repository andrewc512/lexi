"use client";

import { useEffect, useRef } from "react";

interface AIVoiceProps {
  isPlaying: boolean;
  onSpeakingChange: (isSpeaking: boolean) => void;
}

export function AIVoice({ isPlaying, onSpeakingChange }: AIVoiceProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // TODO: Initialize audio playback for AI responses
    // This will receive audio from TTS service
  }, []);

  const playAudio = async (audioUrl: string) => {
    // TODO: Implement audio playback
    if (audioRef.current) {
      audioRef.current.src = audioUrl;
      audioRef.current.play();
      onSpeakingChange(true);
    }
  };

  const handleAudioEnd = () => {
    onSpeakingChange(false);
  };

  // TODO: Listen for AI response events via WebSocket
  // When AI response audio is received, play it

  return (
    <audio
      ref={audioRef}
      onEnded={handleAudioEnd}
      onPause={handleAudioEnd}
      className="hidden"
    />
  );
}
