"use client";

interface ConsentScreenProps {
  token: string;
  onConsent: () => void;
}

export function ConsentScreen({ token, onConsent }: ConsentScreenProps) {
  // TODO: Validate token with backend

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-xl bg-white p-8 rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-4">Welcome to Your Interview</h1>
        <div className="space-y-4 text-gray-600 mb-8">
          <p>Before we begin, please note:</p>
          <ul className="list-disc pl-5 space-y-2">
            <li>This interview will be recorded</li>
            <li>You will be asked a series of questions</li>
            <li>Please ensure you are in a quiet environment</li>
            <li>The interview will take approximately 30 minutes</li>
          </ul>
        </div>
        <button
          onClick={onConsent}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
        >
          I Agree &amp; Start Interview
        </button>
      </div>
    </div>
  );
}
