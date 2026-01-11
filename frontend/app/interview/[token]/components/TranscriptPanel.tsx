"use client";

import { useEffect, useRef } from "react";

interface TranscriptEntry {
  id: string;
  speaker: "ai" | "user";
  text: string;
  timestamp: Date;
}

interface TranscriptPanelProps {
  transcript: TranscriptEntry[];
}

export function TranscriptPanel({ transcript }: TranscriptPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom on new entries
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [transcript]);

  return (
    <aside className="w-80 bg-white border-l border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-gray-900 font-semibold">Live Transcript</h2>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {transcript.length === 0 ? (
          <p className="text-gray-500 text-sm text-center">
            Conversation will appear here...
          </p>
        ) : (
          transcript.map((entry) => (
            <div key={entry.id} className="space-y-1">
              <div className="flex items-center gap-2">
                <span
                  className={`text-xs font-semibold ${
                    entry.speaker === "ai" ? "text-blue-600" : "text-gray-700"
                  }`}
                >
                  {entry.speaker === "ai" ? "Lexi AI" : "You"}
                </span>
                <span className="text-gray-400 text-xs">
                  {entry.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
              <p className="text-gray-700 text-sm leading-relaxed">
                {entry.text}
              </p>
            </div>
          ))
        )}
      </div>

      <div className="p-4 border-t border-gray-200">
        <p className="text-gray-500 text-xs text-center">
          Transcript is generated in real-time
        </p>
      </div>
    </aside>
  );
}
