"use client";

import { useEffect, useState } from "react";
import { INTERVIEW_DURATION_MINUTES } from "@/lib/constants";

interface TimerProps {
  onExpire: () => void;
}

export function Timer({ onExpire }: TimerProps) {
  const [timeLeft, setTimeLeft] = useState(INTERVIEW_DURATION_MINUTES * 60);

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
    }, 1000);

    return () => clearInterval(interval);
  }, [onExpire]);

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return (
    <div className="text-xl font-mono">
      {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
    </div>
  );
}
