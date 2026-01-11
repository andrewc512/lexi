"use client";

import { useState } from "react";

interface ConsentScreenProps {
  token: string;
  onConsent: () => void;
}

export function ConsentScreen({ token, onConsent }: ConsentScreenProps) {
  const [micPermission, setMicPermission] = useState<"pending" | "granted" | "denied">("pending");
  const [agreed, setAgreed] = useState(false);

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
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-6 shadow-sm">
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
          Interview duration: ~4 minutes
        </p>
      </div>
    </div>
  );
}
