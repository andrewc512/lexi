"use client";

import { useState } from "react";

interface ConsentScreenProps {
  token: string;
  onConsent: () => void;
}

export function ConsentScreen({ token, onConsent }: ConsentScreenProps) {
  const [micPermission, setMicPermission] = useState<"pending" | "granted" | "denied">("pending");
  const [agreed, setAgreed] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);

  const requestMicPermission = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      setMicPermission("granted");
    } catch (error) {
      setMicPermission("denied");
      console.error("Microphone permission denied:", error);
    }
  };

  const canStart = micPermission === "granted" && agreed;

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-8">
      <div className="max-w-lg w-full">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            </div>
            <span className="text-2xl font-semibold text-gray-900">Lexi</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Ready to Begin?</h1>
          <p className="text-gray-600">Complete these steps before starting your interview</p>
          <button
            onClick={() => setShowInstructions(true)}
            className="mt-3 text-blue-600 hover:text-blue-700 text-sm font-medium underline"
          >
            View Interview Instructions
          </button>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-6 shadow-sm">
          {/* Quiet environment warning */}
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start gap-3">
            <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="text-amber-900 font-semibold text-sm mb-1">Quiet Environment Required</p>
              <p className="text-amber-800 text-sm">
                Please ensure you&apos;re in a quiet environment with minimal background noise before starting the interview.
              </p>
            </div>
          </div>

          {/* Microphone permission */}
          <div className="flex items-start gap-4">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
              micPermission === "granted"
                ? "bg-green-100 text-green-600"
                : micPermission === "denied"
                ? "bg-red-100 text-red-600"
                : "bg-gray-100 text-gray-500"
            }`}>
              {micPermission === "granted" ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              )}
            </div>
            <div className="flex-1">
              <h3 className="text-gray-900 font-semibold mb-1">Microphone Access</h3>
              <p className="text-gray-600 text-sm mb-3">
                We need access to your microphone for the voice conversation.
              </p>
              {micPermission === "pending" && (
                <button
                  onClick={requestMicPermission}
                  className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Allow Microphone
                </button>
              )}
              {micPermission === "denied" && (
                <p className="text-red-600 text-sm font-medium">
                  Microphone access denied. Please enable it in your browser settings.
                </p>
              )}
            </div>
          </div>

          {/* Consent checkbox */}
          <div className="flex items-start gap-4">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
              agreed ? "bg-green-100 text-green-600" : "bg-gray-100 text-gray-500"
            }`}>
              {agreed ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              )}
            </div>
            <div className="flex-1">
              <h3 className="text-gray-900 font-semibold mb-1">Recording Consent</h3>
              <p className="text-gray-600 text-sm mb-3">
                This interview will be recorded and transcribed for evaluation purposes.
              </p>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={agreed}
                  onChange={(e) => setAgreed(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-gray-700 text-sm">I agree to be recorded</span>
              </label>
            </div>
          </div>
        </div>

        {/* Start button */}
        <button
          onClick={onConsent}
          disabled={!canStart}
          className="w-full mt-6 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Start Interview
        </button>

        <p className="text-center text-gray-500 text-sm mt-4">
          Interview duration: ~1 minute
        </p>
      </div>

      {/* Instructions Modal */}
      {showInstructions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Interview Instructions</h2>
              <button
                onClick={() => setShowInstructions(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="px-6 py-6 space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-blue-900 font-semibold mb-2 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  What to Expect
                </h3>
                <p className="text-blue-800 text-sm">
                  This interview consists of two main parts designed to assess your language skills.
                </p>
              </div>

              <div>
                <h3 className="text-gray-900 font-semibold mb-3 flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 bg-blue-600 text-white rounded-full text-sm">1</span>
                  Conversation with AI
                </h3>
                <p className="text-gray-700 ml-8">
                  You&apos;ll have a natural conversation with an AI assistant. Speak clearly and respond to the questions asked. This helps us assess your conversational fluency and comprehension.
                </p>
              </div>

              <div>
                <h3 className="text-gray-900 font-semibold mb-3 flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 bg-blue-600 text-white rounded-full text-sm">2</span>
                  Translation Tasks
                </h3>
                <p className="text-gray-700 ml-8">
                  You&apos;ll be given words or phrases and asked to say their meaning in English. Focus on accuracy and clarity in your translations.
                </p>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <h3 className="text-amber-900 font-semibold mb-2 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Important Reminders
                </h3>
                <ul className="text-amber-800 text-sm space-y-2 ml-6 list-disc">
                  <li>Ensure you&apos;re in a <strong>quiet environment</strong> with minimal background noise</li>
                  <li>Speak clearly and at a normal pace</li>
                  <li>Your microphone should be working properly</li>
                  <li>The entire interview will be recorded and transcribed</li>
                </ul>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-gray-900 font-semibold mb-2">Tips for Success</h3>
                <ul className="text-gray-700 text-sm space-y-1 ml-6 list-disc">
                  <li>Take your time to think before responding</li>
                  <li>If you don&apos;t understand something, it&apos;s okay to ask for clarification</li>
                  <li>Stay relaxed and be yourself</li>
                </ul>
              </div>
            </div>

            <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4">
              <button
                onClick={() => setShowInstructions(false)}
                className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
              >
                Got it, close instructions
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
