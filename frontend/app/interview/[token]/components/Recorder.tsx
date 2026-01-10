"use client";

import { useState } from "react";

interface RecorderProps {
  onSubmit: () => void;
}

export function Recorder({ onSubmit }: RecorderProps) {
  const [isRecording, setIsRecording] = useState(false);

  const handleToggleRecording = () => {
    // TODO: Implement actual audio recording
    setIsRecording(!isRecording);
  };

  const handleSubmit = () => {
    // TODO: Upload recording to backend
    setIsRecording(false);
    onSubmit();
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="font-medium mb-4">Your Response</h3>
      
      <div className="flex items-center gap-4">
        <button
          onClick={handleToggleRecording}
          className={`px-6 py-3 rounded-lg ${
            isRecording
              ? "bg-red-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          {isRecording ? "Stop Recording" : "Start Recording"}
        </button>

        {isRecording && (
          <span className="text-red-600 animate-pulse">● Recording...</span>
        )}
      </div>

      <button
        onClick={handleSubmit}
        disabled={isRecording}
        className="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        Submit Answer
      </button>
    </div>
  );
}
