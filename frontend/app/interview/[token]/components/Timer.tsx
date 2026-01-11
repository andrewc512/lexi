"use client";

import { useEffect, useState } from "react";
import { INTERVIEW_DURATION_MINUTES } from "@/lib/constants";

interface TimerProps {
  onExpire: () => void;
}

export function Timer({ onExpire }: TimerProps) {
  const [timeLeft, setTimeLeft] = useState(INTERVIEW_DURATION_MINUTES * 60);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          onExpire();
          return 0;
        }
        return prev - 1;
      });
      setElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [onExpire]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  };

  const isLowTime = timeLeft < 300; // Less than 5 minutes

  return (
    <div className="flex items-center gap-2">
      <span className={`font-mono text-sm font-medium ${isLowTime ? "text-red-600" : "text-gray-700"}`}>
        {formatTime(elapsed)}
      </span>
      <span className="text-gray-400">/</span>
      <span className="text-gray-500 font-mono text-sm">
        {formatTime(INTERVIEW_DURATION_MINUTES * 60)}
      </span>
    </div>
  );
}
