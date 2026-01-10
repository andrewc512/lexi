"use client";

import { useState } from "react";
import { ConsentScreen } from "./components/ConsentScreen";
import { Recorder } from "./components/Recorder";
import { AIQuestion } from "./components/AIQuestion";
import { Timer } from "./components/Timer";

type InterviewState = "consent" | "interview" | "complete";

export default function InterviewPage({
  params,
}: {
  params: { token: string };
}) {
  const [state, setState] = useState<InterviewState>("consent");
  const [currentQuestion, setCurrentQuestion] = useState(0);

  const handleConsent = () => {
    setState("interview");
  };

  const handleComplete = () => {
    setState("complete");
  };

  if (state === "consent") {
    return <ConsentScreen token={params.token} onConsent={handleConsent} />;
  }

  if (state === "complete") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Interview Complete</h1>
          <p className="text-gray-600">Thank you for your time!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">Interview Session</h1>
          <Timer onExpire={handleComplete} />
        </div>

        <div className="space-y-8">
          <AIQuestion questionNumber={currentQuestion} />
          <Recorder
            onSubmit={() => {
              if (currentQuestion >= 4) {
                handleComplete();
              } else {
                setCurrentQuestion((q) => q + 1);
              }
            }}
          />
        </div>
      </div>
    </div>
  );
}
